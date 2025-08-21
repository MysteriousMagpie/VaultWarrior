#![cfg_attr(not(debug_assertions), windows_subsystem = "windows")]
use std::process::{Command, Child};
use std::sync::Mutex;
use tauri::{Manager, State};
use serde::Serialize;

struct BackendProc(Mutex<Option<Child>>);

#[derive(Serialize)]
struct BackendInfo { port: u16 }

#[tauri::command]
fn start_backend(state: State<BackendProc>, python: Option<String>, port: Option<u16>) -> Result<BackendInfo, String> {
    let mut guard = state.0.lock().unwrap();
    if guard.is_some() {
        return Ok(BackendInfo { port: port.unwrap_or(37999) });
    }
    let py = python.unwrap_or_else(|| "python".to_string());
    let p = port.unwrap_or(37999);
    let port_string = p.to_string();
    let args = ["-m", "uvicorn", "webapp.api:app", "--host", "127.0.0.1", "--port", port_string.as_str()];
    let child = Command::new(py)
        .args(&args)
        .spawn()
        .map_err(|e| format!("Failed to spawn backend: {e}"))?;
    *guard = Some(child);
    Ok(BackendInfo { port: p })
}

#[tauri::command]
fn stop_backend(state: State<BackendProc>) -> Result<(), String> {
    let mut guard = state.0.lock().unwrap();
    if let Some(mut child) = guard.take() {
        child.kill().ok();
    }
    Ok(())
}

fn main() {
    tauri::Builder::default()
        .manage(BackendProc(Mutex::new(None)))
        .invoke_handler(tauri::generate_handler![start_backend, stop_backend])
        .on_window_event(|event| {
            if let tauri::WindowEvent::CloseRequested { api, .. } = event.event() {
                // ensure backend stopped
                let app_handle = event.window().app_handle();
                let state: State<BackendProc> = app_handle.state();
                let mut guard = state.0.lock().unwrap();
                if let Some(mut child) = guard.take() { child.kill().ok(); }
                api.prevent_close(); // allow drop after cleanup
                event.window().close().ok();
            }
        })
        .run(tauri::generate_context!())
        .expect("error while running tauri app");
}
