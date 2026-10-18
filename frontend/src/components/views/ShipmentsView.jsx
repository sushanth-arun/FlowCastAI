import React, { useState } from 'react';
import ShipmentTable from '../ShipmentTable';
import ShipmentDetailModal from '../ShipmentDetailModal';
import { Truck, Server, Radio, ShieldCheck } from 'lucide-react';

export default function ShipmentsView({
  shipments,
  allShipments = [],
  selectedShipmentId,
  onSelectShipment,
  searchQuery,
  onNavigateToDecisions
}) {
  const [modalShipment, setModalShipment] = useState(null);

  const fullFleet = allShipments.length > 0 ? allShipments : shipments;
  const delayedCount = fullFleet.filter(s => s.riskLevel?.toUpperCase() === 'HIGH').length;
  const onTimeCount = fullFleet.length - delayedCount;

  return (
    <div>
      <div className="page-header">
        <div>
          <h1 className="page-title">Inbound Shipments & AI Delay Predictions</h1>
          <p className="page-subtitle">
            Continuous real-time tracking and delay probability estimation across all inbound supply routes
          </p>
        </div>
      </div>

      {/* Network Surveillance Status Bar */}
      <div
        style={{
          background: '#FFFFFF',
          borderRadius: 10,
          padding: '14px 20px',
          border: '1px solid #E2E8F0',
          marginBottom: 20,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          flexWrap: 'wrap',
          gap: 12
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: 20 }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
            <span
              className="status-dot"
              style={{ background: '#10B981', boxShadow: '0 0 8px rgba(16, 185, 129, 0.6)' }}
            />
            <span style={{ fontSize: '0.84rem', fontWeight: 700, color: '#1E293B' }}>
              Active Route Surveillance
            </span>
          </div>

          <div style={{ fontSize: '0.78rem', color: '#64748B', display: 'flex', alignItems: 'center', gap: 16 }}>
            <span>Total Fleet: <strong style={{ color: '#1E293B' }}>{fullFleet.length} Active</strong></span>
            <span>Priority Monitored: <strong style={{ color: '#2563EB' }}>{shipments.length} Routes</strong></span>
            <span>Critical Delays: <strong style={{ color: '#EF4444' }}>{delayedCount}</strong></span>
            <span>Fleet On-Time: <strong style={{ color: '#10B981' }}>{((onTimeCount / fullFleet.length) * 100).toFixed(1)}%</strong></span>
          </div>
        </div>

        <div
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: 8,
            fontSize: '0.74rem',
            color: '#64748B',
            background: '#F8FAFD',
            padding: '5px 12px',
            borderRadius: 6,
            border: '1px solid #E2E8F0'
          }}
        >
          <Server size={13} color="#3B6FF5" />
          <span>Click <strong>"Analyze"</strong> on any shipment to open instant AI diagnostic popup</span>
        </div>
      </div>

      {/* Shipment Table with Dual-View Toggle & In-Table Search */}
      <ShipmentTable
        priorityShipments={shipments}
        allShipments={fullFleet}
        selectedShipmentId={selectedShipmentId}
        onSelectShipment={onSelectShipment}
        onAnalyzeShipment={(shp) => {
          if (onSelectShipment) onSelectShipment(shp.id);
          setModalShipment(shp);
        }}
        searchQuery={searchQuery}
      />

      {/* Instant Shipment Diagnostic Modal Popup */}
      <ShipmentDetailModal
        isOpen={!!modalShipment}
        onClose={() => setModalShipment(null)}
        shipment={modalShipment}
        onNavigateToDecisions={onNavigateToDecisions}
      />
    </div>
  );
}
