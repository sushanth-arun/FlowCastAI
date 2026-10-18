import React from 'react';
import { Warehouse, ArrowRight, ShieldCheck, AlertTriangle, Truck } from 'lucide-react';
import InventoryImpactCard from '../InventoryImpactCard';

export default function InventoryView({ warehouses, optimizationResult }) {
  return (
    <div>
      <div className="page-header">
        <div>
          <h1 className="page-title">Multi-Warehouse Inventory & Safety Buffers</h1>
          <p className="page-subtitle">
            Inventory balance sheets, safety thresholds, and inter-hub transfer logistics network
          </p>
        </div>
      </div>

      {/* Main Inventory Impact Card with SVG Curve */}
      <InventoryImpactCard
        warehouses={warehouses}
        optimizationResult={optimizationResult}
      />

      {/* Inter-Warehouse Transfer Matrix Table */}
      <div className="card-container" style={{ marginTop: '28px' }}>
        <div className="card-heading" style={{ marginBottom: 16 }}>
          Inter-Hub Transfer Logistics & Feasibility Matrix
        </div>

        <table className="shipments-table">
          <thead>
            <tr>
              <th>Source Facility</th>
              <th>Destination</th>
              <th>Distance</th>
              <th>Transit Time</th>
              <th>Transfer Cost Rate</th>
              <th>Available Usable Surplus</th>
              <th>Feasibility Status</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td>
                <div style={{ fontWeight: 700, color: '#14213D' }}>Warehouse B (Bengaluru Hub)</div>
                <div style={{ fontSize: '0.74rem', color: '#64748B' }}>Hosur Gateway &bull; Total Stock: 150u</div>
              </td>
              <td style={{ fontWeight: 600 }}>Warehouse A (Chennai Hub)</td>
              <td>350 km</td>
              <td><strong>1.5 Days</strong> (Dedicated Freight)</td>
              <td>$8/unit + $130 base ($450 total)</td>
              <td>
                <span style={{ color: '#059669', fontWeight: 700 }}>+100 units</span> (retains 50u safety)
              </td>
              <td>
                <span className="risk-badge green">
                  <ShieldCheck size={12} />
                  Fully Feasible (Optimal)
                </span>
              </td>
            </tr>

            <tr>
              <td>
                <div style={{ fontWeight: 700, color: '#14213D' }}>Warehouse C (Hyderabad Hub)</div>
                <div style={{ fontSize: '0.74rem', color: '#64748B' }}>Shamshabad Depot &bull; Total Stock: 80u</div>
              </td>
              <td style={{ fontWeight: 600 }}>Warehouse A (Chennai Hub)</td>
              <td>625 km</td>
              <td><strong>2.0 Days</strong> (Standard Express)</td>
              <td>$12/unit + $200 base ($620 total)</td>
              <td>
                <span style={{ color: '#2563EB', fontWeight: 700 }}>+35 units</span> (retains 45u safety)
              </td>
              <td>
                <span className="risk-badge amber">
                  <AlertTriangle size={12} />
                  Partial Only (35u max)
                </span>
              </td>
            </tr>

            <tr>
              <td>
                <div style={{ fontWeight: 700, color: '#14213D' }}>Apex Air Logistics (Chennai Airport)</div>
                <div style={{ fontSize: '0.74rem', color: '#64748B' }}>Supplier Direct &bull; MAA Air Cargo</div>
              </td>
              <td style={{ fontWeight: 600 }}>Warehouse A (Chennai Hub)</td>
              <td>45 km</td>
              <td><strong>1.0 Day</strong> (Expedited Air Freight)</td>
              <td>$1,350 flat expedite fee</td>
              <td>
                <span style={{ color: '#64748B', fontWeight: 700 }}>40 units</span> (Complete Batch)
              </td>
              <td>
                <span className="risk-badge" style={{ background: '#F1F5F9', color: '#64748B' }}>
                  Feasible (High Cost)
                </span>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  );
}
