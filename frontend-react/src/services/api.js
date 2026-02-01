const API_BASE = process.env.REACT_APP_API_BASE || '';

async function request(path, opts = {}){
  const res = await fetch(API_BASE + path, opts);
  if(!res.ok){
    const err = await res.json().catch(()=>({error:res.statusText}));
    throw new Error(err.error || err.message || res.statusText);
  }
  return res.json();
}

export async function getHealth(){
  return request('/api/health');
}

export async function hideData(file, secretData, password){
  const fd = new FormData();
  fd.append('image', file);
  fd.append('secretData', secretData);
  fd.append('password', password || '');
  const res = await fetch(API_BASE + '/api/hide', { method: 'POST', body: fd });
  if(!res.ok){ const err = await res.json().catch(()=>null); throw new Error((err && err.error) || res.statusText); }
  return res.json();
}

export async function extractData(imageId, password){
  return request('/api/extract', { method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({imageId, password}) });
}

export async function extractFromFile(file, password){
  const fd = new FormData();
  fd.append('stegoImage', file);
  fd.append('password', password || '');
  const res = await fetch(API_BASE + '/api/extract', { method: 'POST', body: fd });
  if(!res.ok){ const err = await res.json().catch(()=>null); throw new Error((err && err.error) || res.statusText); }
  return res.json();
}

export async function verifyOwnership(imageId, userAddress){
  return request('/api/verify', { method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({imageId, userAddress}) });
}

export async function getUserImages(address){
  return request(`/api/user-images/${address}`);
}

export async function downloadImage(imageId){
  const res = await fetch(API_BASE + `/api/download/${imageId}`);
  if(!res.ok){
    const err = await res.json().catch(()=>null);
    throw new Error((err && err.error) || res.statusText || 'Download failed');
  }
  const blob = await res.blob();
  return blob;
}
