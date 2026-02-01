import React from 'react';

export default function Header({ health }) {
  return (
    <header>
      <h1>🔐 Blockchain Image Steganography</h1>
      <p>Hide secret data in images using Python backend, store on IPFS, and verify on Ethereum blockchain</p>
      <div className="status-bar">
        <span id="ipfs-status" className={`status-indicator ${health.ipfs==='connected'? 'connected': health.ipfs==='disconnected'? 'disconnected':'checking'}`}>
          {health.ipfs==='connected' ? '✅ IPFS Connected' : health.ipfs==='disconnected' ? '❌ IPFS Disconnected' : '🔄 Checking IPFS...'}
        </span>
        <span id="blockchain-status" className={`status-indicator ${health.blockchain==='connected'? 'connected': health.blockchain==='disconnected'? 'disconnected':'checking'}`}>
          {health.blockchain==='connected' ? '✅ Blockchain Connected' : health.blockchain==='disconnected' ? '❌ Blockchain Disconnected' : '🔄 Checking Blockchain...'}
        </span>
      </div>
    </header>
  );
}
