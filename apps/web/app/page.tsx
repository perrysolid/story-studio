'use client';
import { useState } from 'react';

export default function Home() {
  const [prompt, setPrompt] = useState('');
  const [job, setJob] = useState<string | null>(null);
  const [status, setStatus] = useState<string>('idle');
  const [videoPath, setVideoPath] = useState<string | null>(null);

  const API_BASE = process.env.NEXT_PUBLIC_API_BASE || 'http://localhost:8000';

  async function createJob() {
    setStatus('creating');
    const res = await fetch(`${API_BASE}/generate`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ prompt })
    });
    const data = await res.json();
    setJob(data.job_id);
    pollStatus(data.job_id);
  }

  async function pollStatus(id: string) {
    setStatus('running');
    const iv = setInterval(async () => {
      const r = await fetch(`${API_BASE}/status/${id}`);
      const d = await r.json();
      if (d.status === 'done') {
        clearInterval(iv);
        setStatus('done');
        const rr = await fetch(`${API_BASE}/result/${id}`);
        const dd = await rr.json();
        setVideoPath(dd.video_path);
      }
    }, 2000);
  }

  return (
    <main className="max-w-2xl mx-auto p-6 space-y-4">
      <h1 className="text-2xl font-bold">Story Studio</h1>
      <textarea
        value={prompt} onChange={e=>setPrompt(e.target.value)}
        placeholder="Write a touching story about..." rows={6}
        style={{width:'100%', padding:'12px', borderRadius: 8, border: '1px solid #ccc'}}
      />
      <button onClick={createJob} style={{padding:'10px 16px', borderRadius:8, background:'#000', color:'#fff'}}>Create</button>
      <div>Status: {status}</div>
      {videoPath && (
        <video src={videoPath} controls style={{width:'100%', borderRadius:12}}/>
      )}
    </main>
  );
}
