import React, { useState } from 'react';
import { TopNav } from './TopNav';
import { Layout } from './Layout';

export const App: React.FC = () => {
  const [vaultSelected, setVaultSelected] = useState(false);
  return (
    <div className="h-full flex flex-col">
      <TopNav onSelectVault={() => setVaultSelected(true)} />
      <Layout vaultSelected={vaultSelected} />
    </div>
  );
};
