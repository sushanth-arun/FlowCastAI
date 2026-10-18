import React from 'react';
import { Search, Bell, Database, UserCheck } from 'lucide-react';

export default function Topbar({
  activeTab,
  searchQuery,
  setSearchQuery,
  isBackendLive,
  onNotificationClick
}) {
  const pageTitles = {
    overview: 'Supply Chain Risk & Recovery Overview',
    shipments: 'Inbound Shipments & Delay Predictions',
    inventory: 'Multi-Warehouse Inventory & Safety Thresholds',
    recommendations: 'AI Prescriptive Recommendations Engine',
    reports: 'Datathon Project Architecture & ROI Report'
  };

  return (
    <header className="topbar">
      {/* Left: Breadcrumbs & Search */}
      <div className="topbar-left">
        <div className="breadcrumb-label">
          FlowCast AI <span style={{ margin: '0 6px', color: '#CBD5E1' }}>/</span> 
          <strong style={{ color: '#14213D' }}>{pageTitles[activeTab] || 'Overview'}</strong>
        </div>

        <div className="search-box">
          <Search size={16} color="#94A3B8" />
          <input
            type="text"
            className="search-input"
            placeholder="Search shipments, SKUs (e.g., PRD-101), or hubs..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
          />
        </div>
      </div>

      {/* Right: API Mode Badge, Notification, Profile */}
      <div className="topbar-right">
        <div
          className={`api-mode-pill ${isBackendLive ? 'live' : ''}`}
          style={isBackendLive ? { background: '#ECFDF5', color: '#059669', borderColor: '#A7F3D0' } : {}}
          title={isBackendLive ? "Connected to live FastAPI ONNX gateway on port 8000" : "Running local deterministic model"}
        >
          <Database size={13} color={isBackendLive ? "#10B981" : "#3B6FF5"} />
          {isBackendLive ? 'Live ONNX Gateway (Connected)' : 'Simulated Data (Backend Ready)'}
        </div>

        <button 
          className="topbar-action-btn" 
          title="Critical Alerts"
          onClick={onNotificationClick}
        >
          <Bell size={18} />
          <span className="badge-counter">2</span>
        </button>

        <div className="user-profile-btn">
          <div className="user-avatar">Z3</div>
          <span className="user-name">Team FlowCast</span>
        </div>
      </div>
    </header>
  );
}
