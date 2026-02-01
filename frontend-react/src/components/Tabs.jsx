import React from 'react';

export default function Tabs({ current, setCurrent }) {
  return (
    <div className="tabs">
      <button className={`tab-button ${current==='hide' ? 'active':''}`} onClick={()=>setCurrent('hide')}>Hide Data</button>
      <button className={`tab-button ${current==='extract' ? 'active':''}`} onClick={()=>setCurrent('extract')}>Extract Data</button>
      <button className={`tab-button ${current==='verify' ? 'active':''}`} onClick={()=>setCurrent('verify')}>Verify Image</button>
      <button className={`tab-button ${current==='analytics' ? 'active':''}`} onClick={()=>setCurrent('analytics')}>Analytics</button>
    </div>
  );
}
