use std::fs;
use std::path::Path;

fn main() {
  // Ensure placeholder icon so tauri::generate_context!() doesn't panic.
  let icon_path = Path::new("src-tauri/icons/icon.png");
  if !icon_path.exists() {
    if let Some(parent) = icon_path.parent() { fs::create_dir_all(parent).ok(); }
    // 1x1 transparent PNG
    let png_bytes = base64::decode("iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR4nGNgYAAAAAMAASsJTYQAAAAASUVORK5CYII=").unwrap();
    fs::write(icon_path, png_bytes).expect("write placeholder icon");
  }
  tauri_build::build();
}
