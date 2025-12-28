import React, { useRef } from 'react';

interface SidebarProps {
  width: number;
  collapsed: boolean;
  onToggle: () => void;
  onResize: (w: number) => void;
  vaultSelected: boolean;
}

export const Sidebar: React.FC<SidebarProps> = ({ width, collapsed, onToggle, onResize, vaultSelected }) => {
  const ref = useRef<HTMLDivElement>(null);

  // basic drag resize
  function onMouseDown(e: React.MouseEvent) {
    if (collapsed) return;
    const startX = e.clientX;
    const startWidth = width;
    function onMove(ev: MouseEvent) {
      const delta = ev.clientX - startX;
      const next = Math.min(600, Math.max(200, startWidth + delta));
      onResize(next);
    }
    function onUp() {
      window.removeEventListener('mousemove', onMove);
      window.removeEventListener('mouseup', onUp);
    }
    window.addEventListener('mousemove', onMove);
    window.addEventListener('mouseup', onUp);
  }

  return (
    <div
      ref={ref}
      className={`relative h-full bg-surfaceAlt border-r border-border transition-all duration-150 flex flex-col ${collapsed ? 'w-10' : ''}`}
      style={!collapsed ? { width } : undefined}
    >
      <div className="flex items-center justify-between px-2 py-2 text-xs border-b border-border">
        <span className="font-semibold">{collapsed ? '⟫' : 'Sidebar'}</span>
        <button onClick={onToggle} className="px-1 py-0.5 rounded bg-surface border border-border text-[10px]">{collapsed ? 'Open' : 'Close'}</button>
      </div>
      {!collapsed && (
        <div className="p-2 flex-1 overflow-auto text-[11px] space-y-2">
          {!vaultSelected && <div className="text-slate-400">Select a vault to load tree...</div>}
          {vaultSelected && <div className="text-slate-300">(Vault tree placeholder)</div>}
          <div className="pt-2 border-t border-border">Tabs:<br/>Setup | Files | Threads</div>
        </div>
      )}
      {!collapsed && <div onMouseDown={onMouseDown} className="absolute top-0 right-0 w-1 cursor-col-resize h-full select-none" />}
    </div>
  );
};
