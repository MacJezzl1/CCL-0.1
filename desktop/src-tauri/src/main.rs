#![cfg_attr(feature = "custom-protocol", deny(dead_code))]

use tauri::{CustomProtocol, Manager, Runtime, WindowEvent};
use tauri::{
    api::process::restart,
    event::{Event, EventHandler},
    window::WindowBuilder,
};
use serde_json::json;

fn main() {
    // Initialize app
    let app = tauri::Builder::default()
        .invoke_handler(tauri::generate_handler![
            get_system_info,
            open_external_link,
            save_file,
            read_file,
            list_directory,
        ])
        .setup(|app| {
            #[cfg(debug_assertions)]
            {
                let window = app.get_window("main").unwrap();
                window.open_dev_tools();
            }
            Ok(())
        })
        .build(tauri::generate_context!())
        .expect("error while building tauri application");

    // Run the app
    app.run(|_app_handle, event| match event {
        // Handle window events
        Event::WindowEvent { label, event, .. } => match event {
            WindowEvent::Resized(_) => {
                println!("Window {} resized", label);
            }
            WindowEvent::Moved(_) => {
                println!("Window {} moved", label);
            }
            _ => {}
        },
        _ => {}
    });
}

// ===== System Info =====
#[tauri::command]
fn get_system_info() -> Result<String, String> {
    let info = json!({
        "os": std::env::consts::OS,
        "arch": std::env::consts::ARCH,
        "version": env!("CARGO_PKG_VERSION"),
        "cpuCores": num_cpus::get(),
    });
    
    Ok(info.to_string())
}

// ===== Open External Link =====
#[tauri::command]
fn open_external_link(url: String) -> Result<(), String> {
    open::that(url).map_err(|e| e.to_string())?;
    Ok(())
}

// ===== Save File =====
#[tauri::command]
fn save_file(path: String, content: String) -> Result<(), String> {
    std::fs::write(&path, content).map_err(|e| e.to_string())?;
    Ok(())
}

// ===== Read File =====
#[tauri::command]
fn read_file(path: String) -> Result<String, String> {
    std::fs::read_to_string(&path).map_err(|e| e.to_string())
}

// ===== List Directory =====
#[tauri::command]
fn list_directory(path: String) -> Result<Vec<String>, String> {
    let mut files = Vec::new();
    
    if let Ok(entries) = std::fs::read_dir(&path) {
        for entry in entries {
            if let Ok(entry) = entry {
                if let Some(name) = entry.file_name().to_str() {
                    files.push(name.to_string());
                }
            }
        }
    }
    
    Ok(files)
}
