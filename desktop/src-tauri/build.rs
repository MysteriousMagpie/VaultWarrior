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
  // Attempt to auto-generate icon variants via Python script if available (best-effort, ignore errors)
  if std::process::Command::new("python")
      .args(["scripts/gen_icons.py"]) // executed from workspace root when cargo runs build script? current dir is crate root
      .status()
      .map(|s| s.success())
      .unwrap_or(false) {
    println!("cargo:warning=Icon generation script executed successfully");
  } else {
    println!("cargo:warning=Icon generation skipped or failed (non-fatal)");
  }
  tauri_build::build();
}
