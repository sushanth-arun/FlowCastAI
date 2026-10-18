import React, { useEffect } from 'react';
import {
  X,
  Truck,
  MapPin,
  Clock,
  AlertTriangle,
  CheckCircle,
  ShieldAlert,
  Sparkles,
  ArrowRight,
  Server,
  DollarSign
} from 'lucide-react';

export default function ShipmentDetailModal({
  isOpen,
  onClose,
  shipment,
  onNavigateToDecisions
}) {
  useEffect(() => {
    const handleKeyDown = (e) => {
      if (e.key === 'Escape' && isOpen) {
        onClose();
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [isOpen, onClose]);

  if (!isOpen || !shipment) return null;

  const isHighRisk = shipment.riskLevel?.toUpperCase() === 'HIGH';
  const isMedRisk = shipment.riskLevel?.toUpperCase() === 'MEDIUM';
  const isLowRisk = !isHighRisk && !isMedRisk;

  return (
    <div className="modal-backdrop" onClick={onClose}>
      <div className="modal-dialog" onClick={(e) => e.stopPropagation()} style={{ maxWidth: 860 }}>
        {/* Modal Header */}
        <div className="modal-header">
          <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
            <div
              style={{
                width: 40,
                height: 40,
                borderRadius: 10,
                background: isHighRisk ? '#FEE2E2' : '#EFF6FF',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                color: isHighRisk ? '#DC2626' : '#2563EB'
              }}
            >
              <Truck size={22} />
            </div>
            <div>
              <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
                <span className="modal-title" style={{ fontSize: '1.2rem' }}>
                  {shipment.id} — {shipment.productName}
                </span>
                <span
                  className={`risk-badge ${isHighRisk ? 'red' : isMedRisk ? 'amber' : 'green'}`}
                  style={{ fontSize: '0.72rem', padding: '3px 9px' }}
                >
                  {isHighRisk ? <AlertTriangle size={12} /> : <CheckCircle size={12} />}
                  {shipment.riskLevel} Risk ({Math.round(shipment.delayProbability * 100)}% Probability)
                </span>
              </div>
              <div style={{ fontSize: '0.78rem', color: '#64748B', marginTop: 2 }}>
                SKU: <strong>{shipment.sku}</strong> &bull; Batch Quantity: <strong>{shipment.quantity} units</strong> &bull; Mode: <strong>{shipment.transportMode}</strong>
              </div>
            </div>
          </div>

          <button className="modal-close-btn" onClick={onClose} title="Close (Esc)">
            <X size={18} />
          </button>
        </div>

        {/* Modal Content */}
        <div className="modal-content-area">
          {/* 4 Diagnostic Parameter Tiles */}
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: 12, marginBottom: 18 }}>
            <div style={{ background: '#F8FAFD', padding: '14px', borderRadius: 8, border: '1px solid #E2E8F0' }}>
              <div style={{ fontSize: '0.7rem', color: '#64748B', fontWeight: 700, textTransform: 'uppercase' }}>
                ORIGIN CARRIER
              </div>
              <div style={{ fontSize: '0.88rem', fontWeight: 800, color: '#14213D', marginTop: 4 }}>
                {shipment.origin}
              </div>
              <div style={{ fontSize: '0.72rem', color: '#64748B', marginTop: 2 }}>
                {shipment.transportMode}
              </div>
            </div>

            <div style={{ background: '#F8FAFD', padding: '14px', borderRadius: 8, border: '1px solid #E2E8F0' }}>
              <div style={{ fontSize: '0.7rem', color: '#64748B', fontWeight: 700, textTransform: 'uppercase' }}>
                DESTINATION HUB
              </div>
              <div style={{ fontSize: '0.88rem', fontWeight: 800, color: '#14213D', marginTop: 4 }}>
                {shipment.destinationName}
              </div>
              <div style={{ fontSize: '0.72rem', color: '#64748B', marginTop: 2 }}>
                Production Line Demand
              </div>
            </div>

            <div style={{ background: '#F8FAFD', padding: '14px', borderRadius: 8, border: '1px solid #E2E8F0' }}>
              <div style={{ fontSize: '0.7rem', color: '#64748B', fontWeight: 700, textTransform: 'uppercase' }}>
                PREDICTED DELAY
              </div>
              <div style={{ fontSize: '1rem', fontWeight: 800, color: shipment.predictedDelayDays >= 3 ? '#DC2626' : '#2563EB', marginTop: 4 }}>
                +{shipment.predictedDelayDays} Days
              </div>
              <div style={{ fontSize: '0.72rem', color: '#64748B', marginTop: 2 }}>
                Model Confidence: 91%
              </div>
            </div>

            <div style={{ background: '#F8FAFD', padding: '14px', borderRadius: 8, border: '1px solid #E2E8F0' }}>
              <div style={{ fontSize: '0.7rem', color: '#64748B', fontWeight: 700, textTransform: 'uppercase' }}>
                CARRIER STATUS & SLA
              </div>
              <div style={{ fontSize: '0.86rem', fontWeight: 700, color: '#1E293B', marginTop: 4 }}>
                {shipment.status}
              </div>
              <div style={{ fontSize: '0.72rem', color: isHighRisk ? '#DC2626' : '#059669', fontWeight: 600, marginTop: 2 }}>
                {shipment.estimatedCarrierSlaPenalty || (isHighRisk ? '$4,000 SLA Penalty' : 'SLA Target Met')}
              </div>
            </div>
          </div>

          {/* Machine Learning Model Inference Context Card */}
          <div style={{ background: '#FFFFFF', padding: '16px', borderRadius: 10, border: '1px solid #E2E8F0', marginBottom: 18 }}>
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 10 }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: 6, fontSize: '0.82rem', fontWeight: 700, color: '#1E293B' }}>
                <Server size={15} color="#3B6FF5" />
                IBM LinuxONE Real-Time ONNX Inference Evaluation
              </div>
              <span style={{ fontSize: '0.72rem', color: '#3B6FF5', background: '#EFF6FF', padding: '2px 8px', borderRadius: 4, fontWeight: 600 }}>
                Model Latency: 0.013 ms (67,000 req/s)
              </span>
            </div>

            <p style={{ fontSize: '0.78rem', color: '#475569', lineHeight: 1.5, margin: 0 }}>
              Evaluated via DataCo trained Logistics & Delay Risk Model (Module 2 ONNX) hosted natively on s390x. 
              {isHighRisk ? (
                <> Predicted port congestion along the <strong>{shipment.origin}</strong> corridor exceeds safe arrival buffer. Without operational intervention, this delay will trigger stock depletion at <strong>{shipment.destinationName}</strong>.</>
              ) : (
                <> Carrier velocity and telemetry telemetry signals indicate this route is operating within the 95% confidence interval for on-schedule fulfillment.</>
              )}
            </p>
          </div>

          {/* Prescriptive Action Recommendation Callout (If High Risk) */}
          {isHighRisk ? (
            <div style={{ background: '#F0F9FF', padding: '16px', borderRadius: 10, border: '1px solid #BAE6FD', display: 'flex', alignItems: 'center', justifyContent: 'space-between', gap: 16 }}>
              <div>
                <div style={{ display: 'flex', alignItems: 'center', gap: 6, fontSize: '0.82rem', fontWeight: 700, color: '#0369A1', marginBottom: 4 }}>
                  <Sparkles size={15} />
                  AI Prescriptive Recovery Solution Available
                </div>
                <div style={{ fontSize: '0.78rem', color: '#334155', lineHeight: 1.4 }}>
                  Inter-Warehouse Transfer from <strong>Bengaluru Hub (WH-B)</strong> can deliver 40 units in 1.5 days, preventing customer stockout and avoiding <strong>$4,000</strong> in contractual penalties.
                </div>
              </div>

              {onNavigateToDecisions && (
                <button
                  onClick={() => {
                    onClose();
                    onNavigateToDecisions();
                  }}
                  className="btn-primary"
                  style={{ fontSize: '0.78rem', padding: '9px 14px', whiteSpace: 'nowrap', display: 'flex', alignItems: 'center', gap: 6, flexShrink: 0 }}
                >
                  View AI Decision Plan
                  <ArrowRight size={14} />
                </button>
              )}
            </div>
          ) : (
            <div style={{ background: '#ECFDF5', padding: '14px 16px', borderRadius: 10, border: '1px solid #A7F3D0', display: 'flex', alignItems: 'center', gap: 10 }}>
              <CheckCircle size={18} color="#059669" style={{ flexShrink: 0 }} />
              <div style={{ fontSize: '0.78rem', color: '#065F46', lineHeight: 1.4 }}>
                <strong>No Recovery Action Required:</strong> This shipment is on schedule. Warehouse stock levels remain safely above threshold buffers.
              </div>
            </div>
          )}
        </div>

        {/* Modal Sticky Footer */}
        <div className="modal-footer">
          <div style={{ fontSize: '0.74rem', color: '#64748B', display: 'flex', alignItems: 'center', gap: 6 }}>
            <span>Telemetry Source: GPS Route Tracking & Carrier EDI 214 Feed</span>
          </div>

          <button className="btn-primary" onClick={onClose} style={{ minWidth: 120 }}>
            Done Viewing
          </button>
        </div>
      </div>
    </div>
  );
}
