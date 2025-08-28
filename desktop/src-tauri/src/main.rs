#![cfg_attr(not(debug_assertions), windows_subsystem = "windows")]
use std::process::{Command, Child};
use std::path::Path;
use std::sync::Mutex;
use std::time::{Duration, Instant};
use std::net::TcpStream;
use tauri::{Manager, State};
use serde::Serialize;
#[cfg(unix)]
use std::os::unix::process::CommandExt;

struct AppState {
    proc: Mutex<Option<Child>>,
    python_cmd: Mutex<String>,
    port: Mutex<u16>,
    last_restart: Mutex<Option<Instant>>,
}

#[derive(Serialize, Clone)]
struct BackendInfo { port: u16, started: bool }

fn find_free_port(start: u16) -> u16 {
    for offset in 0..20u16 { // try 20 consecutive ports
        let cand = start + offset;
        if TcpStream::connect(("127.0.0.1", cand)).is_err() { return cand; }
    }
    start
}

fn wait_for_port(port: u16, timeout_ms: u64) -> bool {
    let deadline = Instant::now() + Duration::from_millis(timeout_ms);
    while Instant::now() < deadline {
        if TcpStream::connect(("127.0.0.1", port)).is_ok() { return true; }
        std::thread::sleep(Duration::from_millis(120));
    }
    false
}

#[tauri::command]
fn start_backend(state: State<AppState>, python: Option<String>, port: Option<u16>) -> Result<BackendInfo, String> {
    // Already running? Return stored port.
    if state.proc.lock().unwrap().is_some() {
        let p = *state.port.lock().unwrap();
        return Ok(BackendInfo { port: p, started: false });
    }
    let py = python.unwrap_or_else(|| "python".to_string());
    {
        let mut pcmd = state.python_cmd.lock().unwrap();
        *pcmd = py.clone();
    }
    let base_port = port.unwrap_or(37999);
    let chosen_port = find_free_port(base_port);
    // Verify required modules
    let check_status = Command::new(&py)
        .args(["-c", "import uvicorn,fastapi" ])
        .status()
        .map_err(|e| format!("Failed to run python check: {e}"))?;
    if !check_status.success() {
        return Err(format!("Python '{py}' missing fastapi/uvicorn. Install with: {py} -m pip install -e '.[web]'"));
    }
    let crate_dir = Path::new(env!("CARGO_MANIFEST_DIR"));
    let repo_root = crate_dir.parent().and_then(|p| p.parent()).ok_or("Cannot find repo root")?;
    let mut cmd = Command::new(&py);
    cmd.args(["-m", "uvicorn", "webapp.api:app", "--host", "127.0.0.1", "--port", &chosen_port.to_string()]);
    if let Ok(existing) = std::env::var("PYTHONPATH") {
        cmd.env("PYTHONPATH", format!("{}:{}", repo_root.display(), existing));
    } else {
        cmd.env("PYTHONPATH", repo_root.display().to_string());
    }
    #[cfg(unix)] {
        // Put backend in its own process group so we can signal it cleanly.
        unsafe { cmd.pre_exec(|| { libc::setpgid(0, 0); Ok(()) }) ; }
    }
    let child = cmd.spawn().map_err(|e| format!("Failed to spawn backend: {e}"))?;
    *state.proc.lock().unwrap() = Some(child);
    *state.port.lock().unwrap() = chosen_port;
    *state.last_restart.lock().unwrap() = Some(Instant::now());
    let ready = wait_for_port(chosen_port, 6000);
    Ok(BackendInfo { port: chosen_port, started: true && ready })
}

fn graceful_stop(child: &mut Child) {
    #[cfg(unix)] {
        use nix::sys::signal::{kill, Signal};
        use nix::unistd::Pid;
    let id = child.id();
    // send SIGTERM to process group (negative PGID targets group)
    let _ = kill(Pid::from_raw(-(id as i32)), Signal::SIGTERM);
    }
    // Wait up to 2s then force kill
    let start = Instant::now();
    while start.elapsed() < Duration::from_secs(2) {
        if let Ok(Some(_)) = child.try_wait() { return; }
        std::thread::sleep(Duration::from_millis(100));
    }
    let _ = child.kill();
}

#[tauri::command]
fn stop_backend(state: State<AppState>) -> Result<(), String> {
    let mut guard = state.proc.lock().unwrap();
    if let Some(mut child) = guard.take() {
        graceful_stop(&mut child);
    }
    Ok(())
}

#[tauri::command]
fn restart_backend(state: State<AppState>, python: Option<String>, port: Option<u16>) -> Result<BackendInfo, String> {
    {
        let mut guard = state.proc.lock().unwrap();
        if let Some(mut child) = guard.take() { graceful_stop(&mut child); }
    }
    start_backend(state, python, port)
}

#[derive(Serialize)]
struct Diagnostics {
    backend_running: bool,
    python: String,
    py_ok: bool,
    py_error: Option<String>,
    pythonpath: Option<String>,
    port: u16,
    pid: Option<u32>,
    last_restart_secs: Option<u64>,
}

#[tauri::command]
fn get_diagnostics(state: State<AppState>) -> Result<Diagnostics, String> {
    let guard = state.proc.lock().unwrap();
    let backend_running = guard.is_some();
    let pid = guard.as_ref().map(|c| c.id());
    let python = state.python_cmd.lock().unwrap().clone();
    let (py_ok, py_error) = match Command::new(&python).args(["-c", "import uvicorn,fastapi"]).status() {
        Ok(s) if s.success() => (true, None),
        Ok(_) => (false, Some("Missing uvicorn and/or fastapi".to_string())),
        Err(e) => (false, Some(format!("Python exec error: {e}"))),
    };
    let pythonpath = std::env::var("PYTHONPATH").ok();
    let port = *state.port.lock().unwrap();
    let last_restart_secs = state.last_restart.lock().unwrap().map(|t| t.elapsed().as_secs());
    Ok(Diagnostics { backend_running, python, py_ok, py_error, pythonpath, port, pid, last_restart_secs })
}

#[tauri::command]
fn open_vault_folder() -> Result<(), String> {
    // Best effort: open current working directory (repo root); real vault path resides in Python layer.
    let root = std::env::current_dir().map_err(|e| e.to_string())?;
    opener::open(root).map_err(|e| e.to_string())?;
    Ok(())
}

#[tauri::command]
fn open_logs_dir() -> Result<(), String> {
    // Placeholder: open OS temp dir where we could write future logs.
    let dir = std::env::temp_dir();
    opener::open(dir).map_err(|e| e.to_string())?;
    Ok(())
}

fn main() {
    tauri::Builder::default()
    .manage(AppState { proc: Mutex::new(None), python_cmd: Mutex::new("python".to_string()), port: Mutex::new(0), last_restart: Mutex::new(None) })
    .invoke_handler(tauri::generate_handler![start_backend, stop_backend, restart_backend, get_diagnostics, open_vault_folder, open_logs_dir])
        .on_window_event(|event| {
            if let tauri::WindowEvent::CloseRequested { api, .. } = event.event() {
                // ensure backend stopped
                let app_handle = event.window().app_handle();
                let state: State<AppState> = app_handle.state();
                let mut guard = state.proc.lock().unwrap();
                if let Some(mut child) = guard.take() { graceful_stop(&mut child); }
                api.prevent_close(); // allow drop after cleanup
                event.window().close().ok();
            }
        })
        .run(tauri::generate_context!())
        .expect("error while running tauri app");
}
