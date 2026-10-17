import React from 'react';
import ShipmentTable from '../ShipmentTable';
import { Truck, MapPin, Clock, ArrowRight, ShieldAlert } from 'lucide-react';

export default function ShipmentsView({ shipments, selectedShipmentId, onSelectShipment, searchQuery }) {
  const selectedShipment = shipments.find(s => s.id === selectedShipmentId) || shipments[0];

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

      {/* Selected Shipment Detail Card */}
      {selectedShipment && (
        <div className="card-container" style={{ marginBottom: '24px', background: '#FAFCFF', border: '1px solid #D6E4FF' }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 14 }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
              <div style={{ width: 36, height: 36, borderRadius: 8, background: '#EFF6FF', display: 'flex', alignItems: 'center', justifyContent: 'center', color: '#2563EB' }}>
                <Truck size={20} />
              </div>
              <div>
                <div style={{ fontSize: '1.1rem', fontWeight: 700, color: '#14213D' }}>
                  {selectedShipment.id} — {selectedShipment.productName}
                </div>
                <div style={{ fontSize: '0.78rem', color: '#64748B' }}>
                  SKU: {selectedShipment.sku} &bull; Batch Quantity: {selectedShipment.quantity} units
                </div>
              </div>
            </div>

            <span className={`risk-badge ${selectedShipment.riskLevel === 'High' ? 'red' : selectedShipment.riskLevel === 'Medium' ? 'amber' : 'green'}`}>
              Delay Probability: {Math.round(selectedShipment.delayProbability * 100)}% ({selectedShipment.riskLevel} Risk)
            </span>
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: 16, background: '#FFFFFF', padding: '16px', borderRadius: '10px', border: '1px solid #E2E8F0' }}>
            <div>
              <div style={{ fontSize: '0.72rem', color: '#64748B', fontWeight: 600 }}>ORIGIN CARRIER</div>
              <div style={{ fontSize: '0.85rem', fontWeight: 700, color: '#14213D', marginTop: 4 }}>{selectedShipment.origin}</div>
              <div style={{ fontSize: '0.72rem', color: '#94A3B8' }}>{selectedShipment.transportMode}</div>
            </div>
            <div>
              <div style={{ fontSize: '0.72rem', color: '#64748B', fontWeight: 600 }}>DESTINATION HUB</div>
              <div style={{ fontSize: '0.85rem', fontWeight: 700, color: '#14213D', marginTop: 4 }}>{selectedShipment.destinationName}</div>
              <div style={{ fontSize: '0.72rem', color: '#94A3B8' }}>Assembly Line 2 Demand</div>
            </div>
            <div>
              <div style={{ fontSize: '0.72rem', color: '#64748B', fontWeight: 600 }}>PREDICTED DELAY</div>
              <div style={{ fontSize: '0.95rem', fontWeight: 800, color: selectedShipment.predictedDelayDays >= 3 ? '#DC2626' : '#2563EB', marginTop: 4 }}>
                +{selectedShipment.predictedDelayDays} Days
              </div>
              <div style={{ fontSize: '0.72rem', color: '#94A3B8' }}>ETA: Oct 24, 2026 (Revised)</div>
            </div>
            <div>
              <div style={{ fontSize: '0.72rem', color: '#64748B', fontWeight: 600 }}>DISRUPTION CAUSE</div>
              <div style={{ fontSize: '0.85rem', fontWeight: 700, color: '#334155', marginTop: 4 }}>{selectedShipment.status}</div>
              <div style={{ fontSize: '0.72rem', color: '#DC2626', fontWeight: 600 }}>{selectedShipment.estimatedCarrierSlaPenalty || 'SLA OK'}</div>
            </div>
          </div>
        </div>
      )}

      {/* Shipment Table */}
      <ShipmentTable
        shipments={shipments}
        selectedShipmentId={selectedShipmentId}
        onSelectShipment={onSelectShipment}
        searchQuery={searchQuery}
      />
    </div>
  );
}
