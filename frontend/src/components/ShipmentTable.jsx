import React, { useState } from 'react';
import {
  AlertTriangle,
  CheckCircle,
  Clock,
  ExternalLink,
  ChevronRight,
  Filter
} from 'lucide-react';

export default function ShipmentTable({ shipments, selectedShipmentId, onSelectShipment, searchQuery }) {
  const [riskFilter, setRiskFilter] = useState('ALL');

  // Filter shipments by search query and risk filter
  const filtered = shipments.filter((shp) => {
    const matchesFilter =
      riskFilter === 'ALL' || shp.riskLevel.toUpperCase() === riskFilter;

    const query = searchQuery.toLowerCase().trim();
    const matchesSearch =
      !query ||
      shp.id.toLowerCase().includes(query) ||
      shp.sku.toLowerCase().includes(query) ||
      shp.productName.toLowerCase().includes(query) ||
      shp.destinationName.toLowerCase().includes(query);

    return matchesFilter && matchesSearch;
  });

  // Calculate dynamic counts based on actual incoming shipments
  const highCount = shipments.filter(s => s.riskLevel?.toUpperCase() === 'HIGH').length;
  const mediumCount = shipments.filter(s => s.riskLevel?.toUpperCase() === 'MEDIUM').length;
  const lowCount = shipments.filter(s => s.riskLevel?.toUpperCase() === 'LOW').length;

  return (
    <div className="card-container" style={{ marginTop: '28px' }}>
      <div className="table-controls-bar">
        <div>
          <div className="card-heading">Active Inbound Shipments & Delay Risk Predictions</div>
          <div className="card-subheading">
            Trained delay risk inference for incoming component shipments
          </div>
        </div>

        {/* Filter Pills */}
        <div className="filter-pills">
          <button
            className={`filter-pill ${riskFilter === 'ALL' ? 'active' : ''}`}
            onClick={() => setRiskFilter('ALL')}
          >
            All ({shipments.length})
          </button>
          <button
            className={`filter-pill ${riskFilter === 'HIGH' ? 'active' : ''}`}
            onClick={() => setRiskFilter('HIGH')}
          >
            High Risk ({highCount})
          </button>
          <button
            className={`filter-pill ${riskFilter === 'MEDIUM' ? 'active' : ''}`}
            onClick={() => setRiskFilter('MEDIUM')}
          >
            Medium ({mediumCount})
          </button>
          <button
            className={`filter-pill ${riskFilter === 'LOW' ? 'active' : ''}`}
            onClick={() => setRiskFilter('LOW')}
          >
            Low Risk ({lowCount})
          </button>
        </div>
      </div>

      <div style={{ overflowX: 'auto' }}>
        <table className="shipments-table">
          <thead>
            <tr>
              <th>Shipment ID</th>
              <th>Product / SKU</th>
              <th>Destination Hub</th>
              <th>Scheduled Arrival</th>
              <th>Risk Level</th>
              <th>Predicted Delay</th>
              <th>Carrier Status</th>
              <th>Action</th>
            </tr>
          </thead>
          <tbody>
            {filtered.map((shp) => {
              const isSelected = shp.id === selectedShipmentId;
              const badgeClass =
                shp.riskLevel === 'High'
                  ? 'red'
                  : shp.riskLevel === 'Medium'
                  ? 'amber'
                  : 'green';

              return (
                <tr
                  key={shp.id}
                  className={isSelected ? 'selected' : ''}
                  onClick={() => onSelectShipment(shp.id)}
                  style={{ cursor: 'pointer' }}
                >
                  <td className="shipment-id-cell">
                    {shp.id}
                    {shp.isFocalScenario && (
                      <span
                        style={{
                          marginLeft: 6,
                          fontSize: '0.65rem',
                          background: '#EFF6FF',
                          color: '#2563EB',
                          padding: '1px 5px',
                          borderRadius: 3,
                          fontWeight: 700
                        }}
                      >
                        FOCUS
                      </span>
                    )}
                  </td>
                  <td>
                    <div style={{ fontWeight: 600 }}>{shp.productName}</div>
                    <div style={{ fontSize: '0.74rem', color: '#64748B', fontFamily: 'var(--font-mono)' }}>
                      {shp.sku} &bull; {shp.quantity} units
                    </div>
                  </td>
                  <td>
                    <div style={{ fontWeight: 500 }}>{shp.destinationName}</div>
                    <div style={{ fontSize: '0.72rem', color: '#94A3B8' }}>{shp.origin.split(' (')[0]}</div>
                  </td>
                  <td>
                    <div style={{ fontWeight: 500 }}>{shp.scheduledArrival}</div>
                    <div style={{ fontSize: '0.72rem', color: '#94A3B8' }}>{shp.transportMode}</div>
                  </td>
                  <td>
                    <span className={`risk-badge ${badgeClass}`}>
                      {shp.riskLevel === 'High' ? (
                        <AlertTriangle size={11} />
                      ) : (
                        <CheckCircle size={11} />
                      )}
                      {shp.riskLevel} ({Math.round(shp.delayProbability * 100)}%)
                    </span>
                  </td>
                  <td>
                    <div style={{ fontWeight: 700, color: shp.predictedDelayDays >= 3 ? '#DC2626' : '#14213D' }}>
                      +{shp.predictedDelayDays} Days
                    </div>
                    <div style={{ fontSize: '0.7rem', color: '#718096' }}>
                      Model confidence: 91%
                    </div>
                  </td>
                  <td>
                    <div style={{ fontSize: '0.78rem', color: '#334155', fontWeight: 500 }}>
                      {shp.status}
                    </div>
                  </td>
                  <td>
                    <button
                      className="btn-secondary"
                      style={{ padding: '4px 10px', fontSize: '0.75rem' }}
                      onClick={(e) => {
                        e.stopPropagation();
                        onSelectShipment(shp.id);
                      }}
                    >
                      {isSelected ? 'Active Focus' : 'Analyze'}
                      <ChevronRight size={13} />
                    </button>
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </div>
  );
}
