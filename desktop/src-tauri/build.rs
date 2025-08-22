use std::fs;
use std::path::Path;
use base64::Engine; // for Engine::decode
use base64::engine::general_purpose::STANDARD;

fn main() {
  // Ensure placeholder icon so tauri::generate_context!() doesn't panic.
  // Tauri generate_context!() looks for icons at <crate_root>/icons/* by default.
  // Previously we wrote to src-tauri/icons/, which didn't satisfy the macro and caused a panic.
  let icon_path = Path::new("icons/icon.png");
  if !icon_path.exists() {
    if let Some(parent) = icon_path.parent() { fs::create_dir_all(parent).ok(); }
    // 1x1 transparent PNG
  let png_bytes = STANDARD.decode("iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR4nGNgYAAAAAMAASsJTYQAAAAASUVORK5CYII=").unwrap();
    fs::write(icon_path, png_bytes).expect("write placeholder icon");
  }
  tauri_build::build();
}
