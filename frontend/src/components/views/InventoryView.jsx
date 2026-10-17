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
                <div style={{ fontWeight: 700, color: '#14213D' }}>Warehouse B (Detroit Distribution)</div>
                <div style={{ fontSize: '0.74rem', color: '#64748B' }}>DTW-MI-02 &bull; Total Stock: 150u</div>
              </td>
              <td style={{ fontWeight: 600 }}>Warehouse A (Chicago)</td>
              <td>282 miles</td>
              <td><strong>1.5 Days</strong> (Dedicated Freight)</td>
              <td>$8/unit + $130 base</td>
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
                <div style={{ fontWeight: 700, color: '#14213D' }}>Warehouse C (Columbus Depot)</div>
                <div style={{ fontSize: '0.74rem', color: '#64748B' }}>CMH-OH-03 &bull; Total Stock: 80u</div>
              </td>
              <td style={{ fontWeight: 600 }}>Warehouse A (Chicago)</td>
              <td>355 miles</td>
              <td><strong>2.0 Days</strong> (Standard Ground)</td>
              <td>$12/unit + $200 base</td>
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
                <div style={{ fontWeight: 700, color: '#14213D' }}>Apex Global Logistics (Port Newark)</div>
                <div style={{ fontSize: '0.74rem', color: '#64748B' }}>Supplier Direct &bull; EWR-NJ</div>
              </td>
              <td style={{ fontWeight: 600 }}>Warehouse A (Chicago)</td>
              <td>790 miles</td>
              <td><strong>1.5 Days</strong> (Expedited Air Cargo)</td>
              <td>$1,350 flat expedite fee</td>
              <td>
                <span style={{ color: '#64748B', fontWeight: 700 }}>50 units</span> (Complete Batch)
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
