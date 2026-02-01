import React, { useState } from 'react';
import { getUserImages } from '../services/api';

export default function Analytics({ health }){
  const [address, setAddress] = useState('');
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(false);

  async function fetchUser(){
    if(!address) return setData({error:'Enter address'});
    setLoading(true); setData(null);
    try{
      const res = await getUserImages(address);
      setData(res);
    }catch(err){ setData({error: err.message || String(err)}); }
    setLoading(false);
  }

  return (
    <div className="card">
      <h2>📊 System Analytics</h2>
      <div className="analytics-section">
        <h3>System Health</h3>
        <div id="systemHealth">
          <div className="analytics-grid">
            <div className="analytics-item"><div className="number">{health.ipfs==='connected'?'✅':'❌'}</div><div className="label">IPFS Status</div></div>
            <div className="analytics-item"><div className="number">{health.blockchain==='connected'?'✅':'❌'}</div><div className="label">Blockchain Status</div></div>
            <div className="analytics-item"><div className="number">{health.status}</div><div className="label">Overall</div></div>
            <div className="analytics-item"><div className="number">{new Date(health.timestamp).toLocaleTimeString()}</div><div className="label">Last Check</div></div>
          </div>
        </div>
      </div>

      <div className="analytics-section">
        <h3>User Images</h3>
        <div className="form-group">
          <input placeholder="0x..." value={address} onChange={e=>setAddress(e.target.value)} />
          <button className="btn btn-info" onClick={fetchUser} disabled={loading}>{loading? 'Loading...':'📈 Get User Analytics'}</button>
        </div>
        {data && (
          data.error ? <div className="result error">{data.error}</div> : (
            <div className="result success">
              <div className="result-data">
                <p><strong>Total Images:</strong> {data.imageCount}</p>
                <ul>{(data.imageIds||[]).map(id=> <li key={id}>{id}</li>)}</ul>
              </div>
            </div>
          )
        )}
      </div>
    </div>
  );
}
