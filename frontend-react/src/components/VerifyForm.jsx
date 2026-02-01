import React, { useState } from 'react';
import { verifyOwnership } from '../services/api';

export default function VerifyForm(){
  const [imageId, setImageId] = useState('');
  const [userAddress, setUserAddress] = useState('');
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);

  async function onSubmit(e){
    e.preventDefault();
    if(!imageId || !userAddress) return setResult({type:'error', message:'Fill all fields'});
    setLoading(true); setResult({type:'info', message:'Verifying...'});
    try{
      const data = await verifyOwnership(imageId, userAddress);
      setResult({type:'success', message: data.isOwner ? 'Ownership verified' : 'Not owner', data});
    }catch(err){
      setResult({type:'error', message: err.message || String(err)});
    }finally{ setLoading(false); }
  }

  return (
    <div className="card">
      <h2>✅ Verify Image Ownership</h2>
      <form onSubmit={onSubmit}>
        <div className="form-group">
          <label>Image ID:</label>
          <input type="text" value={imageId} onChange={e=>setImageId(e.target.value)} />
        </div>
        <div className="form-group">
          <label>Ethereum Address:</label>
          <input type="text" value={userAddress} onChange={e=>setUserAddress(e.target.value)} />
        </div>
        <button className="btn btn-info" type="submit" disabled={loading}>{loading? '🔄 Verifying...' : '🔍 Verify Ownership'}</button>
      </form>

      <div className="result-container">
        {result && <div className={`result ${result.type}`}><div className="result-data">{result.message}</div></div>}
      </div>
    </div>
  );
}
