import React, { useState } from 'react';
import { extractData, extractFromFile } from '../services/api';

export default function ExtractForm(){
  const [mode, setMode] = useState('upload'); // 'upload' or 'image'
  const [imageId, setImageId] = useState('');
  const [file, setFile] = useState(null);
  const [password, setPassword] = useState('');
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);

  function onFileChange(e){
    const f = e.target.files[0];
    if(!f){ setFile(null); return; }
    const maxSize = 16 * 1024 * 1024;
    const allowedTypes = ['image/png','image/jpeg','image/jpg','image/bmp','image/tiff','image/gif','image/webp'];
    if(f.size > maxSize){ setResult({type:'error', message:'File too large (max 16MB)'}); setFile(null); return; }
    if(f.type && !allowedTypes.includes(f.type.toLowerCase())){ setResult({type:'error', message:'Unsupported file type'}); setFile(null); return; }
    setResult(null);
    setFile(f);
    setImageId('');
  }

  async function onSubmit(e){
    e.preventDefault();

    if(mode === 'upload'){
      if(!file) return setResult({type:'error', message:'Please upload a stego image to extract from'});
      setLoading(true); setResult({type:'info', message:'Extracting from uploaded image...'});
      try{
        const data = await extractFromFile(file, password);
        setResult({type:'success', message: data.data, data});
      }catch(err){
        setResult({type:'error', message: err.message || String(err)});
      }finally{ setLoading(false); }
      return;
    }

    // image id mode
    if(!imageId) return setResult({type:'error', message:'Image ID required'});
    setLoading(true); setResult({type:'info', message:'Retrieving...'});
    try{
      const data = await extractData(imageId, password);
      setResult({type:'success', message: data.data, data});
    }catch(err){
      setResult({type:'error', message: err.message || String(err)});
    }finally{ setLoading(false); }
  }

  return (
    <div className="card extract-card">
      <h2>🔓 Extract Secret Data</h2>
      <form onSubmit={onSubmit} encType="multipart/form-data">
        <div className="form-group extract-mode-toggle">
          <label>Choose Extraction Method:</label>
          <div className="mode-options">
            <label className={`option ${mode==='upload'?'active':''}`}> 
              <input type="radio" name="extractMode" value="upload" checked={mode==='upload'} onChange={()=>setMode('upload')} />
              <span className="opt-label">Uploaded</span>
              <span className="opt-sub">Upload image</span>
            </label>
            <label className={`option ${mode==='image'?'active':''}`}>
              <input type="radio" name="extractMode" value="image" checked={mode==='image'} onChange={()=>setMode('image')} />
              <span className="opt-label">Use Image</span>
              <span className="opt-sub">Image ID</span>
            </label>
          </div>
        </div>

        {mode === 'image' && (
          <div className="form-group">
            <label>Image ID:</label>
            <input type="text" value={imageId} onChange={e=>setImageId(e.target.value)} placeholder="IMG-..." />
          </div>
        )}

        {mode === 'upload' && (
          <div className="form-group">
            <label>Upload Steganographic Image:</label>
            <input type="file" accept="image/*" onChange={onFileChange} />
            {file && <div className="small">Selected file: {file.name}</div>}
          </div>
        )}

        <div className="form-group">
          <label>Password (if encrypted):</label>
          <input type="password" value={password} onChange={e=>setPassword(e.target.value)} />
        </div>

        <div className="form-actions">
          <button className="btn btn-secondary" type="submit" disabled={loading}>{loading? '🔄 Extracting...' : '🔓 Extract Data'}</button>
        </div>
      </form>

      <div className="result-container">
        {result && result.type === 'success' ? (
          <div className="extract-success-box">
            <div className="success-header">✅ SECRET DATA SUCCESSFULLY RETRIEVED</div>
            <div className="secret-label">YOUR SECRET MESSAGE</div>
            <div className="secret-value">{typeof result.message === 'string' ? result.message : JSON.stringify(result.message)}</div>
            <div className="extract-note">Extraction complete: The hidden data was securely embedded in the image.</div>
            {result.data && result.data.imageId && (
              <div className="success-actions"><button className="btn btn-success" onClick={()=>{
                // download via API
                import('../services/api').then(m=>m.downloadImage(result.data.imageId).then(blob=>{
                  const url = window.URL.createObjectURL(blob);
                  const a = document.createElement('a'); a.href = url; a.download = `steganographic_${result.data.imageId}.png`; document.body.appendChild(a); a.click(); a.remove(); window.URL.revokeObjectURL(url);
                })).catch(()=>{});
              }}>📥 Download extracted image</button></div>
            )}
          </div>
        ) : (
          result && <div className={`result ${result.type}`}><div className="result-data">{result.message}</div></div>
        )}
      </div>
    </div>
  );
}
