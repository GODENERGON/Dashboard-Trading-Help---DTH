//! Desktop shell of Dabitur (ADR 0003).
//!
//! Starts the Python engine (`dabitur-backend`, bundled as a resource) on a free loopback
//! port with a random token, hands both to the webview through `backend_config`, and
//! stops the engine when the window closes. The engine never listens on the network.

use std::net::TcpListener;
use std::path::PathBuf;
use std::process::{Child, Command};
use std::sync::Mutex;

use tauri::{Manager, RunEvent};

struct Engine {
    port: u16,
    token: String,
    child: Mutex<Option<Child>>,
}

#[derive(serde::Serialize)]
struct EngineConfig {
    port: u16,
    token: String,
}

#[tauri::command]
fn backend_config(engine: tauri::State<'_, Engine>) -> EngineConfig {
    EngineConfig { port: engine.port, token: engine.token.clone() }
}

fn free_port() -> u16 {
    TcpListener::bind("127.0.0.1:0")
        .and_then(|l| l.local_addr())
        .map(|a| a.port())
        .unwrap_or(8765)
}

fn engine_path(app: &tauri::AppHandle) -> Option<PathBuf> {
    let exe = if cfg!(windows) { "dabitur-backend.exe" } else { "dabitur-backend" };
    let path = app.path().resource_dir().ok()?.join("backend").join(exe);
    path.exists().then_some(path)
}

fn spawn_engine(app: &tauri::AppHandle, port: u16, token: &str) -> Option<Child> {
    let port_arg = port.to_string();
    let mut cmd = match engine_path(app) {
        Some(path) => {
            let mut c = Command::new(path);
            c.args(["--port", &port_arg, "--token", token]);
            c
        }
        // Development: no bundled engine, run it from the Python environment instead.
        None if cfg!(debug_assertions) => {
            let mut c = Command::new(if cfg!(windows) { "python" } else { "python3" });
            c.args(["-m", "dth.sidecar", "--port", &port_arg, "--token", token]);
            c
        }
        None => {
            eprintln!("dabitur: engine not found in resources");
            return None;
        }
    };
    #[cfg(windows)]
    {
        use std::os::windows::process::CommandExt;
        const CREATE_NO_WINDOW: u32 = 0x0800_0000;
        cmd.creation_flags(CREATE_NO_WINDOW);
    }
    cmd.spawn().map_err(|e| eprintln!("dabitur: cannot start engine: {e}")).ok()
}

fn stop_engine(app: &tauri::AppHandle) {
    if let Some(engine) = app.try_state::<Engine>() {
        if let Some(mut child) = engine.child.lock().ok().and_then(|mut c| c.take()) {
            let _ = child.kill();
            let _ = child.wait();
        }
    }
}

#[cfg_attr(mobile, tauri::mobile_entry_point)]
pub fn run() {
    tauri::Builder::default()
        .plugin(tauri_plugin_opener::init())
        .invoke_handler(tauri::generate_handler![backend_config])
        .setup(|app| {
            let port = free_port();
            let token = uuid::Uuid::new_v4().simple().to_string();
            let child = spawn_engine(app.handle(), port, &token);
            app.manage(Engine { port, token, child: Mutex::new(child) });
            Ok(())
        })
        .build(tauri::generate_context!())
        .expect("error while building Dabitur")
        .run(|app, event| {
            if let RunEvent::Exit = event {
                stop_engine(app);
            }
        });
}
