import { useState, useEffect, useRef } from 'react';
import { Activity, Shield, AlertTriangle, CheckCircle } from 'lucide-react';

function App() {
  const [connected, setConnected] = useState(false);
  const [projects, setProjects] = useState([]);
  const ws = useRef(null);

  useEffect(() => {
    // Connect to WebSocket
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const host = window.location.host || 'localhost:8080';
    // Use the dev server proxy if on localhost:5173, else use relative
    const wsUrl = import.meta.env.DEV 
      ? `ws://localhost:8080/dashboard/live` 
      : `${protocol}//${host}/dashboard/live`;

    const connect = () => {
      ws.current = new WebSocket(wsUrl);
      
      ws.current.onopen = () => {
        console.log('Connected');
        setConnected(true);
      };
      
      ws.current.onclose = () => {
        console.log('Disconnected');
        setConnected(false);
        setTimeout(connect, 3000);
      };

      ws.current.onmessage = (event) => {
        if (event.data === 'ping') { ws.current.send('pong'); return; }
        if (event.data === 'pong') return;
        
        try {
          const msg = JSON.parse(event.data);
          if (msg.type === 'projects_update') {
            setProjects(msg.data);
          }
        } catch (e) {
          console.error(e);
        }
      };
    };

    connect();

    return () => {
      if (ws.current) ws.current.close();
    };
  }, []);

  return (
    <div className="min-h-screen p-8">
      <header className="mb-8 flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-slate-900">Lattice Lock</h1>
          <p className="text-slate-500">System Governance Dashboard</p>
        </div>
        <div className={`px-3 py-1 rounded-full text-sm font-medium ${connected ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700'}`}>
          {connected ? 'Connected' : 'Disconnected'}
        </div>
      </header>

      <main className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {/* Placeholder for project cards */}
        {projects.length === 0 ? (
           <div className="col-span-full text-center py-12 text-slate-400 bg-white rounded-lg border border-slate-200 border-dashed">
             Waiting for project data...
           </div>
        ) : (
          projects.map(p => (
            <div key={p.id} className="bg-white p-6 rounded-lg shadow-sm border border-slate-200">
              <div className="flex justify-between items-start mb-4">
                <h3 className="font-semibold text-lg">{p.name}</h3>
                <span className={`px-2 py-0.5 rounded text-xs uppercase ${
                  p.status === 'healthy' ? 'bg-green-100 text-green-700' : 
                  p.status === 'error' ? 'bg-red-100 text-red-700' : 'bg-yellow-100 text-yellow-700'
                }`}>
                  {p.status}
                </span>
              </div>
              <div className="text-sm text-slate-600 space-y-2">
                 <div className="flex justify-between">
                   <span>Health Score</span>
                   <span className="font-medium">{p.health_score}%</span>
                 </div>
                 <div className="flex justify-between">
                   <span>Validations</span>
                   <span className="font-medium">{p.validation_count}</span>
                 </div>
              </div>
            </div>
          ))
        )}
      </main>
    </div>
  )
}

export default App
