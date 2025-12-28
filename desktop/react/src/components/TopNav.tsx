import React from 'react';

interface TopNavProps {
  onSelectVault: () => void;
}

export const TopNav: React.FC<TopNavProps> = ({ onSelectVault }) => {
  return (
    <header className="flex items-center gap-2 px-3 py-2 bg-surfaceAlt border-b border-border text-sm select-none">
      <div className="flex items-center gap-2 font-semibold">
        <img src="/logo.svg" className="h-7 rounded shadow" />
        <span>VaultWarrior</span>
      </div>
      <button onClick={onSelectVault} className="px-2 py-1 bg-surface rounded border border-border hover:bg-surface/70">Select Vault</button>
      <button className="px-2 py-1 bg-surface rounded border border-border hover:bg-surface/70">Reindex</button>
      <button className="px-2 py-1 bg-surface rounded border border-border hover:bg-surface/70">Open Vault</button>
      <button className="px-2 py-1 bg-surface rounded border border-border hover:bg-surface/70">Logs</button>
      <button className="px-2 py-1 bg-surface rounded border border-border hover:bg-surface/70">Restart</button>
      <div className="ml-auto flex items-center gap-2">
        <button className="px-2 py-1 text-xs bg-surface rounded border border-border hover:bg-surface/70">Diagnostics</button>
        <button className="px-2 py-1 text-xs bg-surface rounded border border-border hover:bg-surface/70">Theme</button>
      </div>
    </header>
  );
};
