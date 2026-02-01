import React, { useState } from 'react';
import { hideData, downloadImage } from '../services/api';

export default function HideForm() {
  const [file, setFile] = useState(null);
  const [secret, setSecret] = useState('');
  const [password, setPassword] = useState('');
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);

  function onFileChange(e){
    const f = e.target.files[0];
    if (!f) { setFile(null); return; }
    // Basic client-side validations
    const maxSize = 16 * 1024 * 1024; // 16MB
    const allowedTypes = ['image/png','image/jpeg','image/jpg','image/bmp','image/tiff','image/gif','image/webp'];
    if (f.size > maxSize) {
      setResult({ type:'error', message: 'File too large (max 16MB)' });
      setFile(null);
      return;
    }
    if (f.type && !allowedTypes.includes(f.type.toLowerCase())) {
      setResult({ type:'error', message: 'Unsupported file type' });
      setFile(null);
      return;
    }
    setResult(null);
    setFile(f);
  }

  async function onSubmit(e){
    e.preventDefault();
    if(!file || !secret) return setResult({ type:'error', message:'Please select image and enter secret' });
    setLoading(true); setResult({ type:'info', message:'Processing...' });
    try{
      const data = await hideData(file, secret, password);
      setResult({ type:'success', message: `Image ID: ${data.imageId}\nIPFS: ${data.ipfsHash}`, data });
    }catch(err){
      setResult({ type:'error', message: err.message || String(err) });
    }finally{ setLoading(false); }
  }

  async function handleDownload(imageId){
    try{
      const blob = await downloadImage(imageId);
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `steganographic_${imageId}.png`;
      document.body.appendChild(a);
      a.click();
      a.remove();
      window.URL.revokeObjectURL(url);
    }catch(err){
      setResult({ type:'error', message: err.message || 'Download failed' });
    }
  }

  return (
    <div className="card hide-card">
      <h2>🖼️ Hide Secret Data in Image</h2>
      <form onSubmit={onSubmit} encType="multipart/form-data">
        <div className="form-group">
          <label>Select Image:</label>
          <input type="file" accept="image/*" onChange={onFileChange} />
          {file && <div className="file-info">Selected file: <strong>{file.name}</strong> — {(file.size/1024).toFixed(1)} KB</div>}
        </div>
        <div className="form-group">
          <label>Secret Data:</label>
          <textarea rows={4} value={secret} onChange={e=>setSecret(e.target.value)} />
        </div>
        <div className="form-group">
          <label>Password (optional):</label>
          <input type="password" value={password} onChange={e=>setPassword(e.target.value)} />
        </div>

        <div className="form-actions">
          <button className="btn btn-primary" type="submit" disabled={loading}>{loading? 'Processing...' : '🔒 Hide Data & Store on Blockchain'}</button>
        </div>
      </form>

      <div className="result-container">
        {result && (
          result.type === 'success' && result.data ? (
            <div className="success-box">
              <strong>✅ DATA SUCCESSFULLY HIDDEN & STORED</strong>
              <div className="info-list">
                <ul>
                  <li><strong>Image ID:</strong> {result.data.imageId}</li>
                  <li><strong>IPFS Hash:</strong> <a href={`https://ipfs.io/ipfs/${result.data.ipfsHash}`} target="_blank" rel="noopener noreferrer">{result.data.ipfsHash}</a></li>
                  <li><strong>Metadata Hash:</strong> {result.data.metadataHash}</li>
                  <li><strong>Transaction:</strong> {result.data.transactionHash} (block {result.data.blockNumber})</li>
                </ul>
                <div style={{marginTop:8}}>
                  <ol>
                    <li>Click the Download button below to save the steganographic image.</li>
                    <li>Send the Image ID to the intended receiver so they can use the Extract page.</li>
                    <li>You can verify ownership using the Verify tab.</li>
                  </ol>
                </div>
                <div className="success-actions">
                  <button className="btn btn-success" onClick={()=>handleDownload(result.data.imageId)}>📥 Download Steganographic Image</button>
                </div>
              </div>
            </div>
          ) : (
            <div className={`result ${result.type}`}><div className="result-data">{result.message}</div></div>
          )
        )}
      </div>
    </div>
  );
}
