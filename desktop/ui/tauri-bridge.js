// Minimal dynamic loader to access Tauri APIs without bundler.
// Tries dynamic import of @tauri-apps/api; if it fails, leaves existing globals untouched.
(function(){
  const g = window;
  if(g.__TAURI__ && (g.__TAURI__.invoke || g.__TAURI__.core?.invoke)) return; // already available
  import('@tauri-apps/api/core').then(core => {
    import('@tauri-apps/api/dialog').then(dialog => {
      g.__TAURI__ = g.__TAURI__ || {};
      if(!g.__TAURI__.invoke) g.__TAURI__.invoke = core.invoke;
      if(!g.__TAURI__.dialog) g.__TAURI__.dialog = {};
      if(!g.__TAURI__.dialog.open) g.__TAURI__.dialog.open = dialog.open;
      console.log('Tauri bridge: API modules loaded');
    }).catch(e => console.warn('Tauri bridge failed to load dialog module', e));
  }).catch(e => console.warn('Tauri bridge failed to load core module', e));
})();
