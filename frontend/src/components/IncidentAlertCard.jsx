import React from 'react';
import {
  AlertTriangle,
  Clock,
  Truck,
  MapPin,
  Sparkles,
  ArrowRight,
  Layers,
  ShieldAlert,
  CheckCircle2
} from 'lucide-react';

export default function IncidentAlertCard({
  shipment = null,
  optimizationResult = null,
  onNavigateToDecisions,
  onNavigateToShipments,
  onCompareScenarios
}) {
  const fShipment = shipment || {
    id: 'SHP-CH-01',
    sku: 'PRD-101',
    productName: 'IoT Telemetry Sensor Nodes',
    quantity: 180,
    origin: 'Port of Chennai',
    destinationName: 'Warehouse A (Chennai Hub)',
    scheduledArrival: 'Delayed (+4 Days)',
    predictedDelayDays: 4.0,
    delayProbability: 0.88,
    riskLevel: 'High',
    status: 'Delayed (Port Congestion)',
    transportMode: 'Intermodal Freight'
  };

  const rec = optimizationResult?.recommendedOption || {
    title: 'Inter-Warehouse Transfer from Bengaluru Hub (WH-B)',
    unitsSupplied: 40,
    totalCost: 450,
    savingsVsBaseline: 3550,
    percentReduction: 88.8
  };

  const baselineCost = optimizationResult?.baselineTotalCost || 4000;
  const runway = optimizationResult?.runwayDays || 2.0;

  return (
    <div className="card-container" style={{ display: 'flex', flexDirection: 'column', height: '100%', border: '1px solid #FECACA', background: '#FFFAFA' }}>
      {/* Incident Header */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', paddingBottom: 14, borderBottom: '1px solid #FEE2E2', marginBottom: 14 }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
          <div style={{ width: 36, height: 36, borderRadius: 8, background: '#FEE2E2', display: 'flex', alignItems: 'center', justifyContent: 'center', color: '#DC2626' }}>
            <AlertTriangle size={20} />
          </div>
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
              <span style={{ fontSize: '0.98rem', fontWeight: 800, color: '#991B1B' }}>
                Active Disruption Incident Alert
              </span>
              <span className="risk-badge red" style={{ fontSize: '0.68rem', padding: '2px 7px' }}>
                Level 1 Critical
              </span>
            </div>
            <div style={{ fontSize: '0.76rem', color: '#7F1D1D', marginTop: 2 }}>
              Trained Delay Risk Inference (DataCo Model Confidence: {Math.round(fShipment.delayProbability * 100)}%)
            </div>
          </div>
        </div>

        <button
          onClick={onNavigateToShipments}
          className="btn-secondary"
          style={{ fontSize: '0.74rem', padding: '5px 10px', height: 'auto', background: '#FFFFFF', borderColor: '#FECACA', color: '#991B1B' }}
          title="Inspect full carrier tracking"
        >
          View Carrier Feed
          <ArrowRight size={13} style={{ marginLeft: 4 }} />
        </button>
      </div>

      {/* Disruption Incident Metadata Grid */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: 10, marginBottom: 16 }}>
        <div style={{ background: '#FFFFFF', padding: '12px 14px', borderRadius: 8, border: '1px solid #FEE2E2' }}>
          <div style={{ fontSize: '0.7rem', color: '#64748B', fontWeight: 600, textTransform: 'uppercase' }}>
            Delayed Inbound Shipment
          </div>
          <div style={{ fontSize: '0.92rem', fontWeight: 800, color: '#14213D', marginTop: 4 }}>
            {fShipment.id} &bull; {fShipment.quantity} units
          </div>
          <div style={{ fontSize: '0.74rem', color: '#475569', marginTop: 2 }}>
            {fShipment.productName} ({fShipment.sku})
          </div>
        </div>

        <div style={{ background: '#FFFFFF', padding: '12px 14px', borderRadius: 8, border: '1px solid #FEE2E2' }}>
          <div style={{ fontSize: '0.7rem', color: '#64748B', fontWeight: 600, textTransform: 'uppercase' }}>
            Root Cause & Delay
          </div>
          <div style={{ fontSize: '0.92rem', fontWeight: 800, color: '#DC2626', marginTop: 4, display: 'flex', alignItems: 'center', gap: 6 }}>
            <Clock size={15} />
            +{fShipment.predictedDelayDays} Days ({fShipment.status})
          </div>
          <div style={{ fontSize: '0.74rem', color: '#475569', marginTop: 2 }}>
            Route: {fShipment.origin} &rarr; {fShipment.destinationName.split(' (')[0]}
          </div>
        </div>
      </div>

      {/* Downstream Consequence Alert Banner */}
      <div style={{ background: '#FFF1F2', padding: '10px 14px', borderRadius: 8, border: '1px solid #FECDD3', display: 'flex', alignItems: 'center', gap: 10, marginBottom: 16 }}>
        <ShieldAlert size={18} color="#E11D48" style={{ flexShrink: 0 }} />
        <div style={{ fontSize: '0.78rem', color: '#9F1239', lineHeight: 1.4 }}>
          <strong>Critical Inventory Horizon:</strong> Warehouse A has only <strong>{runway} days of stock runway</strong>. Delay will cause a <strong>40-unit stockout</strong> costing <strong>${baselineCost.toLocaleString()}</strong> in customer SLA penalties.
        </div>
      </div>

      {/* AI Prescriptive Recovery Solution Box */}
      <div style={{ background: '#F0F9FF', padding: '14px 16px', borderRadius: 10, border: '1px solid #BAE6FD', marginTop: 'auto' }}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 8 }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 6, fontSize: '0.78rem', fontWeight: 700, color: '#0284C7' }}>
            <Sparkles size={14} />
            AI Decision Support Prescription
          </div>
          <span style={{ fontSize: '0.72rem', color: '#059669', fontWeight: 700, background: '#DCFCE7', padding: '2px 8px', borderRadius: 4, border: '1px solid #BBF7D0' }}>
            +${rec.savingsVsBaseline.toLocaleString()} ({rec.percentReduction}%) Saved
          </span>
        </div>

        <div style={{ fontSize: '0.92rem', fontWeight: 800, color: '#0F172A', marginBottom: 6 }}>
          {rec.title}
        </div>
        <p style={{ fontSize: '0.76rem', color: '#475569', margin: '0 0 12px 0', lineHeight: 1.5 }}>
          Transfers <strong>{rec.unitsSupplied} units</strong> via dedicated intermodal route (1.5d transit). Arrives prior to Warehouse A depletion, eliminating customer stockout orders at an action cost of only <strong>${rec.totalCost.toLocaleString()}</strong>.
        </p>

        {/* Action Buttons */}
        <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
          <button
            onClick={onNavigateToDecisions}
            className="btn-primary"
            style={{ fontSize: '0.78rem', padding: '8px 14px', flex: 1, justifyContent: 'center' }}
          >
            Review AI Prescriptive Decision
            <ArrowRight size={14} style={{ marginLeft: 6 }} />
          </button>

          <button
            onClick={onCompareScenarios}
            className="btn-secondary"
            style={{ fontSize: '0.78rem', padding: '8px 12px', background: '#FFFFFF', borderColor: '#BAE6FD', color: '#0369A1' }}
            title="Compare all 4 alternatives side by side"
          >
            <Layers size={14} style={{ marginRight: 4 }} />
            Compare 4 Alternatives
          </button>
        </div>
      </div>
    </div>
  );
}
