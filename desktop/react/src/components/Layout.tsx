import React, { useState } from 'react';
import { Sidebar } from './Sidebar';
import { ChatPanel } from './ChatPanel';

interface LayoutProps {
  vaultSelected: boolean;
}

export const Layout: React.FC<LayoutProps> = ({ vaultSelected }) => {
  const [sidebarWidth, setSidebarWidth] = useState(320);
  const [collapsed, setCollapsed] = useState(false);

  return (
    <div className="flex flex-1 h-[calc(100vh-56px)]">
      <Sidebar
        width={sidebarWidth}
        collapsed={collapsed}
        onToggle={() => setCollapsed(c => !c)}
        onResize={setSidebarWidth}
        vaultSelected={vaultSelected}
      />
      <ChatPanel />
    </div>
  );
};
