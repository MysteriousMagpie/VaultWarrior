#![cfg_attr(not(debug_assertions), windows_subsystem = "windows")]
use std::process::{Command, Child};
use std::path::Path;
use std::sync::Mutex;
use tauri::{Manager, State};
use serde::Serialize;

struct AppState {
    proc: Mutex<Option<Child>>,
    python_cmd: Mutex<String>,
}

#[derive(Serialize)]
struct BackendInfo { port: u16 }

#[tauri::command]
fn start_backend(state: State<AppState>, python: Option<String>, port: Option<u16>) -> Result<BackendInfo, String> {
    let mut guard = state.proc.lock().unwrap();
    if guard.is_some() {
        return Ok(BackendInfo { port: port.unwrap_or(37999) });
    }
    let py = python.unwrap_or_else(|| "python".to_string());
    {
        let mut pcmd = state.python_cmd.lock().unwrap();
        *pcmd = py.clone();
    }
    let p = port.unwrap_or(37999);
    let port_string = p.to_string();
    // Verify required modules exist before spawning long-running server.
    let check_status = Command::new(&py)
        .args(["-c", "import uvicorn,fastapi" ])
        .status()
        .map_err(|e| format!("Failed to run python check: {e}"))?;
    if !check_status.success() {
        return Err(format!(
            "Python interpreter '{py}' is missing required packages 'fastapi' and/or 'uvicorn'.\nInstall with: {py} -m pip install -e '.[web]' (run in repo root)"
        ));
    }
    // Set PYTHONPATH to repo root so 'webapp' and 'ai' packages resolve.
    let crate_dir = Path::new(env!("CARGO_MANIFEST_DIR"));
    let repo_root = crate_dir.parent().and_then(|p| p.parent()).ok_or("Cannot find repo root")?;
    let mut cmd = Command::new(&py);
    cmd.args(["-m", "uvicorn", "webapp.api:app", "--host", "127.0.0.1", "--port", port_string.as_str()]);
    // Prepend repo root to PYTHONPATH
    if let Ok(existing) = std::env::var("PYTHONPATH") {
        cmd.env("PYTHONPATH", format!("{}:{}", repo_root.display(), existing));
    } else {
        cmd.env("PYTHONPATH", repo_root.display().to_string());
    }
    let child = cmd.spawn().map_err(|e| format!("Failed to spawn backend: {e}"))?;
    *guard = Some(child);
    Ok(BackendInfo { port: p })
}

#[tauri::command]
fn stop_backend(state: State<AppState>) -> Result<(), String> {
    let mut guard = state.proc.lock().unwrap();
    if let Some(mut child) = guard.take() {
        child.kill().ok();
    }
    Ok(())
}

#[derive(Serialize)]
struct Diagnostics {
    backend_running: bool,
    python: String,
    py_ok: bool,
    py_error: Option<String>,
    pythonpath: Option<String>,
}

#[tauri::command]
fn get_diagnostics(state: State<AppState>) -> Result<Diagnostics, String> {
    let backend_running = state.proc.lock().unwrap().is_some();
    let python = state.python_cmd.lock().unwrap().clone();
    let (py_ok, py_error) = match Command::new(&python).args(["-c", "import uvicorn,fastapi"]).status() {
        Ok(s) if s.success() => (true, None),
        Ok(_) => (false, Some("Missing uvicorn and/or fastapi".to_string())),
        Err(e) => (false, Some(format!("Python exec error: {e}"))),
    };
    let pythonpath = std::env::var("PYTHONPATH").ok();
    Ok(Diagnostics { backend_running, python, py_ok, py_error, pythonpath })
}

fn main() {
    tauri::Builder::default()
        .manage(AppState { proc: Mutex::new(None), python_cmd: Mutex::new("python".to_string()) })
        .invoke_handler(tauri::generate_handler![start_backend, stop_backend, get_diagnostics])
        .on_window_event(|event| {
            if let tauri::WindowEvent::CloseRequested { api, .. } = event.event() {
                // ensure backend stopped
                let app_handle = event.window().app_handle();
                let state: State<AppState> = app_handle.state();
                let mut guard = state.proc.lock().unwrap();
                if let Some(mut child) = guard.take() { child.kill().ok(); }
                api.prevent_close(); // allow drop after cleanup
                event.window().close().ok();
            }
        })
        .run(tauri::generate_context!())
        .expect("error while running tauri app");
}
