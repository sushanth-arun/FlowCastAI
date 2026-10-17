import React from 'react';
import {
  LayoutDashboard,
  Truck,
  Warehouse,
  Sparkles,
  FileText,
  Server,
  ShieldCheck
} from 'lucide-react';

export default function Sidebar({ activeTab, setActiveTab, atRiskCount = 6 }) {
  const navItems = [
    { id: 'overview', label: 'Overview', icon: LayoutDashboard },
    { id: 'shipments', label: 'Shipments', icon: Truck, badge: atRiskCount },
    { id: 'inventory', label: 'Inventory & Hubs', icon: Warehouse },
    { id: 'recommendations', label: 'AI Decisions', icon: Sparkles },
    { id: 'reports', label: 'Executive Report', icon: FileText }
  ];

  return (
    <aside className="sidebar">
      {/* Brand Header */}
      <div className="sidebar-header">
        <div className="logo-badge">
          <Sparkles size={22} />
        </div>
        <div className="logo-text-group">
          <div className="logo-title">
            FlowCast AI
            <span className="logo-tag">IBM Z</span>
          </div>
          <div className="logo-subtitle">Supply Chain Intelligence</div>
        </div>
      </div>

      {/* Navigation */}
      <nav className="sidebar-nav">
        <div className="nav-section-label">Command Center</div>
        {navItems.map((item) => {
          const Icon = item.icon;
          const isActive = activeTab === item.id;
          return (
            <button
              key={item.id}
              onClick={() => setActiveTab(item.id)}
              className={`nav-item ${isActive ? 'active' : ''}`}
            >
              <Icon size={18} className="nav-icon" />
              <span>{item.label}</span>
              {item.badge ? (
                <span className="nav-badge">{item.badge}</span>
              ) : null}
            </button>
          );
        })}
      </nav>

      {/* LinuxONE Verification Footer */}
      <div className="sidebar-footer">
        <div className="linuxone-card">
          <div className="linuxone-header">
            <div className="linuxone-title">
              <Server size={14} color="#60A5FA" />
              Target: IBM LinuxONE
            </div>
            <span className="status-dot" title="Environment verified" />
          </div>
          <div className="linuxone-desc">
            Verified s390x package compatibility for scikit-learn & Python 3.11.
          </div>
          <div className="linuxone-tag">
            <ShieldCheck size={11} style={{ display: 'inline', marginRight: 4, verticalAlign: 'text-bottom' }} />
            s390x Certified Stack
          </div>
        </div>
      </div>
    </aside>
  );
}
