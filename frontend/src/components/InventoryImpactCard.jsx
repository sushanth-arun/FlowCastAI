import React, { useState } from 'react';
import { Warehouse, TrendingDown, Clock, AlertTriangle, CheckCircle } from 'lucide-react';

export default function InventoryImpactCard({ warehouses, optimizationResult }) {
  const [hoveredPoint, setHoveredPoint] = useState(null);

  if (!optimizationResult) return null;

  const { runwayDays, actualArrivalDays, neededUnits, trajectory } = optimizationResult;

  // Chart coordinate mapping
  const chartWidth = 560;
  const chartHeight = 180;
  const padLeft = 40;
  const padRight = 20;
  const padTop = 20;
  const padBottom = 28;

  const innerWidth = chartWidth - padLeft - padRight;
  const innerHeight = chartHeight - padTop - padBottom;

  const maxVal = 90; // scale y-axis up to 90 units
  const minVal = 0;

  const getX = (dNum) => padLeft + (dNum / 7) * innerWidth;
  const getY = (val) => padTop + innerHeight - (Math.min(maxVal, Math.max(0, val)) / maxVal) * innerHeight;

  // Safety stock y
  const safetyY = getY(30);

  // Generate SVG path for Baseline
  const baselinePath = trajectory.map((pt, i) => `${i === 0 ? 'M' : 'L'} ${getX(pt.dayNum)} ${getY(pt.baselineStock)}`).join(' ');

  // Generate SVG path for Recommended
  const recommendedPath = trajectory.map((pt, i) => `${i === 0 ? 'M' : 'L'} ${getX(pt.dayNum)} ${getY(pt.recommendedStock)}`).join(' ');

  // Fill area under baseline curve to show shortage area
  const stockoutFillPath = `M ${getX(2)} ${getY(0)} L ${getX(Math.min(6, Math.round(actualArrivalDays)))} ${getY(0)} L ${getX(Math.min(6, Math.round(actualArrivalDays)))} ${getY(30)} L ${getX(2)} ${getY(30)} Z`;

  return (
    <div className="card-container" style={{ minWidth: 0, overflow: 'hidden' }}>
      <div className="card-header-row" style={{ flexWrap: 'wrap', gap: 10, alignItems: 'flex-start' }}>
        <div style={{ minWidth: 0, flex: 1 }}>
          <div className="card-heading">Warehouse Inventory & Shortage Projection</div>
          <div className="card-subheading" style={{ whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>
            Live multi-warehouse balance sheet for SKU PRD-101 (IoT Telemetry Sensor Nodes)
          </div>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: 6, flexShrink: 0 }}>
          <span style={{ fontSize: '0.72rem', fontWeight: 600, color: '#EF4444', background: '#FEF2F2', padding: '3px 7px', borderRadius: 4, border: '1px solid #FCA5A5', whiteSpace: 'nowrap' }}>
            <TrendingDown size={11} style={{ display: 'inline', marginRight: 3, verticalAlign: 'middle' }} />
            Runway: {runwayDays} Days
          </span>
          <span style={{ fontSize: '0.72rem', fontWeight: 600, color: '#718096', background: '#EDF2F7', padding: '3px 7px', borderRadius: 4, whiteSpace: 'nowrap' }}>
            <Clock size={11} style={{ display: 'inline', marginRight: 3, verticalAlign: 'middle' }} />
            Delay: +{actualArrivalDays - 2}d
          </span>
        </div>
      </div>

      {/* 3 Warehouses Mini Status Cards */}
      <div className="warehouses-row">
        {warehouses.map((wh) => {
          const isA = wh.id === 'WH-A';
          const isB = wh.id === 'WH-B';
          const isC = wh.id === 'WH-C';

          return (
            <div
              key={wh.id}
              className={`wh-mini-card ${isA ? 'active-target' : isB ? 'active-source' : ''}`}
            >
              <div className="wh-header-block" style={{ marginBottom: 4 }}>
                <div style={{ fontSize: '0.84rem', fontWeight: 800, color: '#14213D', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>
                  {wh.name.split(' (')[0]}
                </div>
                <div style={{ marginTop: 3 }}>
                  <span className={`wh-tag ${isA ? 'red' : isB ? 'green' : 'blue'}`}>
                    {isA ? 'Target Deficit' : isB ? 'Optimal Source' : 'Secondary Hub'}
                  </span>
                </div>
              </div>
              <div className="wh-stock-metric">
                {wh.currentStock} <span style={{ fontSize: '0.8rem', fontWeight: 500, color: '#64748B' }}>units</span>
              </div>
              <div className="wh-stock-sub" style={{ whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>
                {isA ? (
                  <span style={{ color: '#DC2626', fontWeight: 600 }}>Safety: {wh.safetyStock} (-{neededUnits} Deficit)</span>
                ) : isB ? (
                  <span style={{ color: '#059669', fontWeight: 600 }}>Surplus: +100 units</span>
                ) : (
                  <span style={{ color: '#2563EB', fontWeight: 600 }}>Surplus: +35 units</span>
                )}
              </div>
            </div>
          );
        })}
      </div>

      {/* SVG Interactive Trajectory Chart */}
      <div className="chart-wrapper" style={{ width: '100%', maxWidth: '100%', overflow: 'hidden' }}>
        <svg
          viewBox={`0 0 ${chartWidth} ${chartHeight}`}
          preserveAspectRatio="xMidYMid meet"
          style={{ width: '100%', height: 'auto', display: 'block', maxWidth: '100%' }}
        >
          <defs>
            <linearGradient id="recGrad" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stopColor="#3B6FF5" stopOpacity="0.25" />
              <stop offset="100%" stopColor="#3B6FF5" stopOpacity="0.0" />
            </linearGradient>
            <linearGradient id="shortageGrad" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stopColor="#EF4444" stopOpacity="0.18" />
              <stop offset="100%" stopColor="#EF4444" stopOpacity="0.04" />
            </linearGradient>
          </defs>

          {/* Grid lines */}
          {[0, 30, 60, 90].map((v) => (
            <g key={v}>
              <line
                x1={padLeft}
                y1={getY(v)}
                x2={chartWidth - padRight}
                y2={getY(v)}
                stroke="#E2E8F0"
                strokeDasharray={v === 30 ? "4 4" : "none"}
                strokeWidth={v === 30 ? "1.5" : "1"}
              />
              <text
                x={padLeft - 8}
                y={getY(v) + 4}
                textAnchor="end"
                fontSize="10"
                fill={v === 30 ? "#F59E0B" : "#94A3B8"}
                fontWeight={v === 30 ? "600" : "400"}
              >
                {v}
              </text>
            </g>
          ))}

          {/* Stockout Zone highlight */}
          <path d={stockoutFillPath} fill="url(#shortageGrad)" />

          {/* Safety threshold label */}
          <text
            x={chartWidth - padRight - 5}
            y={safetyY - 5}
            textAnchor="end"
            fontSize="9"
            fill="#D97706"
            fontWeight="600"
          >
            Safety Threshold (30u)
          </text>

          {/* Baseline path (Red) */}
          <path
            d={baselinePath}
            fill="none"
            stroke="#EF4444"
            strokeWidth="2.5"
            strokeDasharray="5 3"
          />

          {/* Recommended path (Electric Blue) */}
          <path
            d={recommendedPath}
            fill="none"
            stroke="#3B6FF5"
            strokeWidth="3"
          />

          {/* Data Points */}
          {trajectory.map((pt) => (
            <g key={pt.dayNum}>
              {/* Recommended dot */}
              <circle
                cx={getX(pt.dayNum)}
                cy={getY(pt.recommendedStock)}
                r={hoveredPoint === pt.dayNum ? "6" : "4"}
                fill="#3B6FF5"
                stroke="#FFFFFF"
                strokeWidth="2"
                style={{ cursor: 'pointer', transition: 'r 0.15s ease' }}
                onMouseEnter={() => setHoveredPoint(pt.dayNum)}
                onMouseLeave={() => setHoveredPoint(null)}
              />
              {/* Baseline dot */}
              <circle
                cx={getX(pt.dayNum)}
                cy={getY(pt.baselineStock)}
                r="3"
                fill="#EF4444"
                stroke="#FFFFFF"
                strokeWidth="1.5"
              />

              {/* Day Labels on X Axis */}
              <text
                x={getX(pt.dayNum)}
                y={chartHeight - 6}
                textAnchor="middle"
                fontSize="10"
                fill="#64748B"
                fontWeight="500"
              >
                {pt.day.replace('Day ', 'D')}
              </text>
            </g>
          ))}
        </svg>
      </div>

      {/* Chart Legend */}
      <div className="chart-legend">
        <div className="legend-item">
          <div className="legend-color blue" />
          <span>Recommended Transfer from B (Restores Stock at Day 2)</span>
        </div>
        <div className="legend-item">
          <div className="legend-color red" style={{ borderTop: '2px dashed #EF4444' }} />
          <span>No-Action Baseline (Stockout from Day 2 to {Math.round(actualArrivalDays)})</span>
        </div>
        <div className="legend-item">
          <div className="legend-color" style={{ background: '#F59E0B', height: 2 }} />
          <span>Min Safety Target (30 units)</span>
        </div>
      </div>
    </div>
  );
}
