import React, { useEffect, useState } from 'react';
import Header from './components/Header';
import Tabs from './components/Tabs';
import HideForm from './components/HideForm';
import ExtractForm from './components/ExtractForm';
import VerifyForm from './components/VerifyForm';
import Analytics from './components/Analytics';
import { getHealth } from './services/api';
import './App.css';

function App() {
  const [currentTab, setCurrentTab] = useState('hide');
  const [health, setHealth] = useState({ ipfs: 'checking', blockchain: 'checking', status: 'checking', timestamp: Date.now() });

  useEffect(() => {
    checkSystemHealth();
    const id = setInterval(checkSystemHealth, 15000);
    return () => clearInterval(id);
  }, []);

  async function checkSystemHealth() {
    try {
      const data = await getHealth();
      setHealth(data);
    } catch (e) {
      setHealth({ ipfs: 'disconnected', blockchain: 'disconnected', status: 'unhealthy', timestamp: Date.now() });
    }
  }

  return (
    <div className="container">
      <Header health={health} />
      <Tabs current={currentTab} setCurrent={setCurrentTab} />

      <div className={`tab-content ${currentTab === 'hide' ? 'active' : ''}`}>
        <HideForm />
      </div>

      <div className={`tab-content ${currentTab === 'extract' ? 'active' : ''}`}>
        <ExtractForm />
      </div>

      <div className={`tab-content ${currentTab === 'verify' ? 'active' : ''}`}>
        <VerifyForm />
      </div>

      <div className={`tab-content ${currentTab === 'analytics' ? 'active' : ''}`}>
        <Analytics health={health} />
      </div>

      <footer>
        <p>🐍 Python Backend • ⛓️ Ethereum Sepolia • 🌐 IPFS • 🔒 AES Encryption</p>
        <p>Built for educational purposes</p>
      </footer>
    </div>
  );
}

export default App;
