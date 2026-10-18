import React, { useState, useRef, useEffect } from 'react';
import { Warehouse, TrendingDown, Clock, AlertTriangle, CheckCircle } from 'lucide-react';

export default function InventoryImpactCard({ warehouses, optimizationResult }) {
  const [hoveredPoint, setHoveredPoint] = useState(null);
  const wrapperRef = useRef(null);
  const [chartWidth, setChartWidth] = useState(700);

  // Measure container width dynamically to keep 1:1 scale on both half-width (Overview) and full-width (Inventory) views
  useEffect(() => {
    if (!wrapperRef.current) return;
    const updateWidth = () => {
      if (wrapperRef.current) {
        const w = wrapperRef.current.clientWidth;
        if (w > 0) setChartWidth(w);
      }
    };
    updateWidth();

    const ro = new ResizeObserver((entries) => {
      for (const entry of entries) {
        if (entry.contentRect.width > 0) {
          setChartWidth(Math.round(entry.contentRect.width));
        }
      }
    });

    ro.observe(wrapperRef.current);
    return () => ro.disconnect();
  }, []);

  if (!optimizationResult) return null;

  const { runwayDays, actualArrivalDays, neededUnits, trajectory } = optimizationResult;

  // Chart coordinate mapping - dynamic responsive width with fixed sleek 190px height
  const chartHeight = 190;
  const padLeft = 38;
  const padRight = 18;
  const padTop = 16;
  const padBottom = 26;

  const innerWidth = Math.max(200, chartWidth - padLeft - padRight);
  const innerHeight = chartHeight - padTop - padBottom; // 148px

  // Scale y-axis up to 70 units so trajectory (peaks at 60) fills the vertical canvas cleanly
  const maxVal = 70;

  const getX = (dNum) => padLeft + (dNum / 7) * innerWidth;
  const getY = (val) => padTop + innerHeight - (Math.min(maxVal, Math.max(0, val)) / maxVal) * innerHeight;

  // Safety stock threshold y-coordinate
  const safetyY = getY(30);

  // Generate SVG path for Baseline
  const baselinePath = trajectory.map((pt, i) => `${i === 0 ? 'M' : 'L'} ${getX(pt.dayNum)} ${getY(pt.baselineStock)}`).join(' ');

  // Generate SVG path for Recommended
  const recommendedPath = trajectory.map((pt, i) => `${i === 0 ? 'M' : 'L'} ${getX(pt.dayNum)} ${getY(pt.recommendedStock)}`).join(' ');

  // Area under recommended curve
  const recAreaPath = `${recommendedPath} L ${getX(7)} ${getY(0)} L ${getX(0)} ${getY(0)} Z`;

  // Fill area under baseline curve to show shortage area
  const stockoutFillPath = `M ${getX(2)} ${getY(0)} L ${getX(Math.min(6, Math.round(actualArrivalDays)))} ${getY(0)} L ${getX(Math.min(6, Math.round(actualArrivalDays)))} ${getY(30)} L ${getX(2)} ${getY(30)} Z`;

  return (
    <div className="card-container" style={{ minWidth: 0, display: 'flex', flexDirection: 'column' }}>
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

      {/* SVG Interactive Trajectory Chart with True 1:1 Aspect Ratio */}
      <div
        ref={wrapperRef}
        className="chart-wrapper"
        style={{ width: '100%', height: chartHeight, position: 'relative' }}
      >
        <svg
          viewBox={`0 0 ${chartWidth} ${chartHeight}`}
          preserveAspectRatio="none"
          style={{ width: '100%', height: '100%', display: 'block' }}
        >
          <defs>
            <linearGradient id="recGrad" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stopColor="#3B6FF5" stopOpacity="0.16" />
              <stop offset="100%" stopColor="#3B6FF5" stopOpacity="0.0" />
            </linearGradient>
            <linearGradient id="shortageGrad" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stopColor="#EF4444" stopOpacity="0.14" />
              <stop offset="100%" stopColor="#EF4444" stopOpacity="0.03" />
            </linearGradient>
          </defs>

          {/* Grid lines: 0, 20, 40, 60 */}
          {[0, 20, 40, 60].map((v) => (
            <g key={v}>
              <line
                x1={padLeft}
                y1={getY(v)}
                x2={chartWidth - padRight}
                y2={getY(v)}
                stroke={v === 0 ? "#CBD5E1" : "#E2E8F0"}
                strokeWidth={v === 0 ? "1.5" : "1"}
              />
              <text
                x={padLeft - 6}
                y={getY(v) + 3.5}
                textAnchor="end"
                fontSize="10"
                fill="#64748B"
                fontWeight="500"
              >
                {v}
              </text>
            </g>
          ))}

          {/* Stockout Zone highlight */}
          <path d={stockoutFillPath} fill="url(#shortageGrad)" />
          <text
            x={(getX(2) + getX(Math.min(6, Math.round(actualArrivalDays)))) / 2}
            y={(getY(0) + getY(30)) / 2 + 3}
            textAnchor="middle"
            fontSize="9"
            fill="#DC2626"
            fontWeight="700"
            letterSpacing="0.04em"
            opacity="0.85"
          >
            CRITICAL STOCKOUT WINDOW (DAYS 2–6)
          </text>

          {/* Safety threshold line */}
          <line
            x1={padLeft}
            y1={safetyY}
            x2={chartWidth - padRight}
            y2={safetyY}
            stroke="#F59E0B"
            strokeDasharray="4 4"
            strokeWidth="1.5"
          />

          {/* Safety threshold label with badge */}
          <rect
            x={chartWidth - padRight - 124}
            y={safetyY - 14}
            width="124"
            height="13"
            rx="3"
            fill="#FFFBEB"
            stroke="#FDE68A"
            strokeWidth="0.8"
          />
          <text
            x={chartWidth - padRight - 5}
            y={safetyY - 4}
            textAnchor="end"
            fontSize="9"
            fill="#B45309"
            fontWeight="700"
          >
            Safety Threshold (30u)
          </text>

          {/* Area fill under recommended line */}
          <path d={recAreaPath} fill="url(#recGrad)" />

          {/* Baseline path (Red Dashed) */}
          <path
            d={baselinePath}
            fill="none"
            stroke="#EF4444"
            strokeWidth="2.2"
            strokeDasharray="5 3"
          />

          {/* Recommended path (Electric Blue) */}
          <path
            d={recommendedPath}
            fill="none"
            stroke="#2563EB"
            strokeWidth="2.8"
          />

          {/* Data Points */}
          {trajectory.map((pt) => {
            const isHovered = hoveredPoint?.dayNum === pt.dayNum;
            return (
              <g key={pt.dayNum}>
                {/* Recommended dot */}
                <circle
                  cx={getX(pt.dayNum)}
                  cy={getY(pt.recommendedStock)}
                  r={isHovered ? "5.5" : "4"}
                  fill="#2563EB"
                  stroke="#FFFFFF"
                  strokeWidth="2"
                  style={{ cursor: 'pointer', transition: 'r 0.15s ease' }}
                  onMouseEnter={() => setHoveredPoint(pt)}
                  onMouseLeave={() => setHoveredPoint(null)}
                />

                {/* Baseline dot */}
                <circle
                  cx={getX(pt.dayNum)}
                  cy={getY(pt.baselineStock)}
                  r="3"
                  fill="#EF4444"
                  stroke="#FFFFFF"
                  strokeWidth="1.2"
                  style={{ cursor: 'pointer' }}
                  onMouseEnter={() => setHoveredPoint(pt)}
                  onMouseLeave={() => setHoveredPoint(null)}
                />

                {/* Day Labels on X Axis */}
                <text
                  x={getX(pt.dayNum)}
                  y={chartHeight - 8}
                  textAnchor="middle"
                  fontSize="10"
                  fill="#475569"
                  fontWeight="600"
                >
                  {pt.day.replace('Day ', 'D')}
                </text>
              </g>
            );
          })}

          {/* Interactive Tooltip Card on Hover */}
          {hoveredPoint && (
            <g transform={`translate(${Math.min(chartWidth - 145, Math.max(padLeft, getX(hoveredPoint.dayNum) - 65))}, ${Math.max(10, getY(hoveredPoint.recommendedStock) - 45)})`}>
              <rect
                width="130"
                height="38"
                rx="6"
                fill="#0F172A"
                opacity="0.94"
                stroke="#334155"
                strokeWidth="1"
              />
              <text x="8" y="14" fontSize="9" fill="#94A3B8" fontWeight="600">
                {hoveredPoint.day} Projection
              </text>
              <text x="8" y="28" fontSize="10" fill="#60A5FA" fontWeight="700">
                Rec: {hoveredPoint.recommendedStock}u
              </text>
              <text x="68" y="28" fontSize="10" fill="#F87171" fontWeight="700">
                Base: {hoveredPoint.baselineStock}u
              </text>
            </g>
          )}
        </svg>
      </div>

      {/* Chart Legend */}
      <div className="chart-legend" style={{ marginTop: 'auto' }}>
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
