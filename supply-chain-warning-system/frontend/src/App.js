
import React, { useState, useEffect, useCallback } from 'react';
import axios from 'axios';
import Dashboard from './components/Dashboard';
import ShipmentForm from './components/ShipmentForm';
import AlertBox from './components/AlertBox';

const API = process.env.REACT_APP_API_URL || 'http://localhost:8080';
const mono = "'IBM Plex Mono', monospace";

export default function App() {
  const [tab, setTab] = useState('dashboard');
  const [alerts, setAlerts] = useState([]);
  const [refreshKey, setRefreshKey] = useState(0);
  const [sidebarOpen, setSidebarOpen] = useState(true);

  const loadAlerts = useCallback(async () => {
    try {
      const res = await axios.get(`${API}/api/shipments/alerts`);
      setAlerts(res.data);
    } catch (e) {
      // backend may not be up yet
    }
  }, []);

  useEffect(() => {
    loadAlerts();
    const iv = setInterval(loadAlerts, 15000);
    return () => clearInterval(iv);
  }, [loadAlerts]);

  const handleShipmentCreated = () => {
    setRefreshKey(k => k + 1);
    loadAlerts();
    setTab('dashboard');
  };

  const criticalCount = alerts.filter(a => a.alertTriggered && a.riskLevel === 'CRITICAL').length;

  return (
    <div style={{
      minHeight: '100vh',
      background: '#050505',
      color: '#DDD',
      fontFamily: mono,
      display: 'flex',
    }}>
      {/* Sidebar */}
      <div style={{
        width: sidebarOpen ? 220 : 52,
        background: '#080808',
        borderRight: '1px solid #111',
        display: 'flex',
        flexDirection: 'column',
        transition: 'width 0.2s ease',
        overflow: 'hidden',
        flexShrink: 0,
      }}>
        {/* Logo */}
        <div style={{
          padding: '20px 16px',
          borderBottom: '1px solid #111',
          display: 'flex', alignItems: 'center', gap: 12,
          whiteSpace: 'nowrap',
        }}>
          <div style={{
            width: 20, height: 20, flexShrink: 0,
            background: '#0A84FF',
            clipPath: 'polygon(50% 0%, 100% 100%, 0% 100%)',
          }} />
          {sidebarOpen && (
            <span style={{ fontSize: 10, letterSpacing: 3, color: '#555', fontWeight: 700 }}>
              SCWS
            </span>
          )}
        </div>

        {/* Nav items */}
        <nav style={{ flex: 1, padding: '12px 0' }}>
          {[
            { id: 'dashboard', label: 'DASHBOARD', icon: '▦' },
            { id: 'new', label: 'NEW SHIPMENT', icon: '+' },
            { id: 'alerts', label: `ALERTS${criticalCount > 0 ? ` (${criticalCount})` : ''}`, icon: '!' },
          ].map(item => (
            <button
              key={item.id}
              onClick={() => setTab(item.id)}
              style={{
                display: 'flex', alignItems: 'center', gap: 12,
                width: '100%', background: 'none',
                border: 'none', borderLeft: `2px solid ${tab === item.id ? '#0A84FF' : 'transparent'}`,
                color: tab === item.id ? '#DDD' : '#444',
                padding: '12px 16px',
                cursor: 'pointer', fontSize: 10, letterSpacing: 2,
                fontFamily: mono, fontWeight: tab === item.id ? 700 : 400,
                transition: 'all 0.15s',
                whiteSpace: 'nowrap',
              }}
            >
              <span style={{ fontSize: 14, width: 20, textAlign: 'center', flexShrink: 0 }}>
                {item.icon}
              </span>
              {sidebarOpen && item.label}
            </button>
          ))}
        </nav>

        {/* Toggle */}
        <button
          onClick={() => setSidebarOpen(o => !o)}
          style={{
            background: 'none', border: 'none', borderTop: '1px solid #111',
            color: '#333', padding: '14px 16px', cursor: 'pointer',
            fontFamily: mono, fontSize: 12,
            display: 'flex', alignItems: 'center', justifyContent: sidebarOpen ? 'flex-end' : 'center',
          }}
        >
          {sidebarOpen ? '◂' : '▸'}
        </button>
      </div>

      {/* Main */}
      <div style={{ flex: 1, display: 'flex', flexDirection: 'column', minWidth: 0 }}>
        {/* Topbar */}
        <div style={{
          height: 52, borderBottom: '1px solid #111',
          display: 'flex', alignItems: 'center', justifyContent: 'space-between',
          padding: '0 24px', background: '#080808', flexShrink: 0,
        }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
            <div style={{ width: 6, height: 6, background: '#00C853', borderRadius: '50%' }} />
            <span style={{ fontSize: 10, letterSpacing: 3, color: '#333' }}>
              SUPPLY CHAIN WARNING SYSTEM
            </span>
          </div>
          <div style={{ display: 'flex', gap: 20, alignItems: 'center' }}>
            {criticalCount > 0 && (
              <span style={{
                background: '#FF1A1A', color: '#000',
                fontSize: 10, fontWeight: 700, padding: '3px 10px', letterSpacing: 1,
                animation: 'blink 1s step-end infinite',
              }}>
                {criticalCount} CRITICAL
              </span>
            )}
            <span style={{ fontSize: 10, color: '#222' }}>
              {new Date().toISOString().slice(0, 19).replace('T', ' ')} UTC
            </span>
          </div>
        </div>

        {/* Content */}
        <div style={{ flex: 1, overflow: 'auto', padding: 24 }}>
          {tab === 'dashboard' && (
            <>
              {alerts.filter(a => a.alertTriggered).length > 0 && (
                <div style={{ marginBottom: 20 }}>
                  <AlertBox alerts={alerts} />
                </div>
              )}
              <Dashboard refreshKey={refreshKey} />
            </>
          )}

          {tab === 'new' && (
            <div style={{ maxWidth: 760 }}>
              <div style={{
                fontSize: 10, letterSpacing: 4, color: '#333', marginBottom: 24,
                paddingBottom: 16, borderBottom: '1px solid #111'
              }}>
                NEW SHIPMENT REGISTRATION
              </div>
              <ShipmentForm onShipmentCreated={handleShipmentCreated} />
            </div>
          )}

          {tab === 'alerts' && (
            <div style={{ maxWidth: 760 }}>
              <div style={{
                fontSize: 10, letterSpacing: 4, color: '#333', marginBottom: 24,
                paddingBottom: 16, borderBottom: '1px solid #111'
              }}>
                ALERT MANAGEMENT CENTER
              </div>
              <AlertBox alerts={alerts} />
            </div>
          )}
        </div>
      </div>

      <style>{`
        @import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;600;700&display=swap');
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body { background: #050505; }
        ::-webkit-scrollbar { width: 4px; height: 4px; }
        ::-webkit-scrollbar-track { background: #080808; }
        ::-webkit-scrollbar-thumb { background: #1A1A1A; }
        @keyframes alertPulse {
          0%, 100% { opacity: 1; }
          50% { opacity: 0.6; }
        }
        @keyframes blink {
          0%, 100% { opacity: 1; }
          50% { opacity: 0; }
        }
        input:focus, select:focus {
          border-color: #0A84FF !important;
          outline: none;
        }
        button:hover { opacity: 0.8; }
      `}</style>
    </div>
  );
}
