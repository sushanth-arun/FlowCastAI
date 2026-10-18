import React, { useState, useEffect } from 'react';
import {
  AlertTriangle,
  CheckCircle,
  Clock,
  ChevronRight,
  ChevronLeft,
  Search,
  X,
  Star,
  Globe,
  Filter
} from 'lucide-react';

export default function ShipmentTable({
  priorityShipments = [],
  allShipments = [],
  shipments = [],
  selectedShipmentId,
  onSelectShipment,
  searchQuery = '',
  onAnalyzeShipment
}) {
  const [viewMode, setViewMode] = useState('priority'); // 'priority' | 'all'
  const [riskFilter, setRiskFilter] = useState('ALL');
  const [tableSearch, setTableSearch] = useState('');
  const [currentPage, setCurrentPage] = useState(1);
  const pageSize = 10;

  // Determine active dataset
  const priorityList = priorityShipments.length > 0 ? priorityShipments : shipments;
  const fullFleetList = allShipments.length > 0 ? allShipments : (priorityShipments.length > 0 ? priorityShipments : shipments);
  const activeDataset = viewMode === 'priority' ? priorityList : fullFleetList;

  // Reset page whenever viewMode, riskFilter, or search changes
  useEffect(() => {
    setCurrentPage(1);
  }, [viewMode, riskFilter, tableSearch, searchQuery]);

  // Combined search term
  const effectiveQuery = (tableSearch || searchQuery || '').toLowerCase().trim();

  // Filter dataset
  const filtered = activeDataset.filter((shp) => {
    const matchesRisk =
      riskFilter === 'ALL' || shp.riskLevel?.toUpperCase() === riskFilter;

    if (!effectiveQuery) return matchesRisk;

    const matchesSearch =
      (shp.id && shp.id.toLowerCase().includes(effectiveQuery)) ||
      (shp.sku && shp.sku.toLowerCase().includes(effectiveQuery)) ||
      (shp.productName && shp.productName.toLowerCase().includes(effectiveQuery)) ||
      (shp.destinationName && shp.destinationName.toLowerCase().includes(effectiveQuery)) ||
      (shp.origin && shp.origin.toLowerCase().includes(effectiveQuery)) ||
      (shp.status && shp.status.toLowerCase().includes(effectiveQuery));

    return matchesRisk && matchesSearch;
  });

  // Dynamic counts for active view
  const allCount = activeDataset.length;
  const highCount = activeDataset.filter((s) => s.riskLevel?.toUpperCase() === 'HIGH').length;
  const mediumCount = activeDataset.filter((s) => s.riskLevel?.toUpperCase() === 'MEDIUM').length;
  const lowCount = activeDataset.filter((s) => s.riskLevel?.toUpperCase() === 'LOW').length;

  // Pagination calculations
  const totalPages = Math.max(1, Math.ceil(filtered.length / pageSize));
  const validCurrentPage = Math.min(currentPage, totalPages);
  const startIndex = (validCurrentPage - 1) * pageSize;
  const displayedShipments =
    viewMode === 'all'
      ? filtered.slice(startIndex, startIndex + pageSize)
      : filtered;

  return (
    <div className="card-container" style={{ marginTop: '20px' }}>
      {/* Top Header Row with Segmented View Toggle */}
      <div
        style={{
          display: 'flex',
          alignItems: 'flex-start',
          justifyContent: 'space-between',
          flexWrap: 'wrap',
          gap: 16,
          marginBottom: 16,
          paddingBottom: 16,
          borderBottom: '1px solid #E2E8F0'
        }}
      >
        <div>
          <div className="card-heading" style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
            {viewMode === 'priority' ? (
              <>
                <Star size={18} color="#2563EB" />
                Priority Monitored Inbound Shipments & Delay Predictions
              </>
            ) : (
              <>
                <Globe size={18} color="#3B6FF5" />
                Complete Network Inbound Fleet ({fullFleetList.length} Active Shipments)
              </>
            )}
          </div>
          <div className="card-subheading">
            {viewMode === 'priority'
              ? `Curated AI delay risk inference for 4 priority supply routes feeding Chennai, Bengaluru & Hyderabad manufacturing hubs`
              : `Real-time telematics surveillance across all ${fullFleetList.length} active inbound corridors in India's logistics network`}
          </div>
        </div>

        {/* Segmented Dual-View Toggle Switch */}
        <div className="view-toggle-wrap">
          <button
            type="button"
            className={`view-toggle-btn ${viewMode === 'priority' ? 'active' : ''}`}
            onClick={() => {
              setViewMode('priority');
              setRiskFilter('ALL');
            }}
          >
            <Star size={13} color={viewMode === 'priority' ? '#2563EB' : '#64748B'} />
            Priority Watchlist ({priorityList.length})
          </button>

          <button
            type="button"
            className={`view-toggle-btn ${viewMode === 'all' ? 'active' : ''}`}
            onClick={() => {
              setViewMode('all');
              setRiskFilter('ALL');
            }}
          >
            <Globe size={13} color={viewMode === 'all' ? '#3B6FF5' : '#64748B'} />
            All Network Fleet ({fullFleetList.length})
          </button>
        </div>
      </div>

      {/* Second Row: In-Table Search & Risk Filter Pills */}
      <div className="table-controls-bar" style={{ flexWrap: 'wrap', gap: 12 }}>
        {/* In-Table Search Input (Shown in both or especially full view) */}
        <div className="table-search-input-wrap">
          <Search
            size={15}
            color="#94A3B8"
            style={{ position: 'absolute', left: 10, pointerEvents: 'none' }}
          />
          <input
            type="text"
            className="table-search-input"
            placeholder={
              viewMode === 'priority'
                ? 'Filter priority routes...'
                : `Search all ${fullFleetList.length} shipments by ID, SKU, Hub, Carrier...`
            }
            value={tableSearch}
            onChange={(e) => setTableSearch(e.target.value)}
          />
          {tableSearch && (
            <button
              type="button"
              onClick={() => setTableSearch('')}
              style={{
                position: 'absolute',
                right: 8,
                background: 'none',
                border: 'none',
                cursor: 'pointer',
                color: '#94A3B8',
                display: 'flex',
                alignItems: 'center'
              }}
              title="Clear search"
            >
              <X size={14} />
            </button>
          )}
        </div>

        {/* Risk Level Filter Pills */}
        <div className="filter-pills">
          <button
            type="button"
            className={`filter-pill ${riskFilter === 'ALL' ? 'active' : ''}`}
            onClick={() => setRiskFilter('ALL')}
          >
            All ({allCount})
          </button>
          <button
            type="button"
            className={`filter-pill ${riskFilter === 'HIGH' ? 'active' : ''}`}
            onClick={() => setRiskFilter('HIGH')}
          >
            High Risk ({highCount})
          </button>
          {mediumCount > 0 && (
            <button
              type="button"
              className={`filter-pill ${riskFilter === 'MEDIUM' ? 'active' : ''}`}
              onClick={() => setRiskFilter('MEDIUM')}
            >
              Medium ({mediumCount})
            </button>
          )}
          <button
            type="button"
            className={`filter-pill ${riskFilter === 'LOW' ? 'active' : ''}`}
            onClick={() => setRiskFilter('LOW')}
          >
            Low Risk ({lowCount})
          </button>
        </div>
      </div>

      {/* Shipment Table Grid */}
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
            {displayedShipments.length > 0 ? (
              displayedShipments.map((shp) => {
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
                    onClick={() => {
                      if (onAnalyzeShipment) onAnalyzeShipment(shp);
                      else onSelectShipment(shp.id);
                    }}
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
                      <div style={{ fontWeight: 700, color: shp.predictedDelayDays >= 3 ? '#DC2626' : shp.predictedDelayDays >= 1 ? '#D97706' : '#14213D' }}>
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
                        style={{ padding: '5px 12px', fontSize: '0.75rem', display: 'flex', alignItems: 'center', gap: 4 }}
                        onClick={(e) => {
                          e.stopPropagation();
                          if (onAnalyzeShipment) {
                            onAnalyzeShipment(shp);
                          } else {
                            onSelectShipment(shp.id);
                          }
                        }}
                        title="Open instant AI diagnostic popup"
                      >
                        Analyze
                        <ChevronRight size={13} />
                      </button>
                    </td>
                  </tr>
                );
              })
            ) : (
              <tr>
                <td colSpan="8" style={{ textAlign: 'center', padding: '36px 20px', color: '#64748B' }}>
                  <div style={{ fontSize: '0.9rem', fontWeight: 600, color: '#1E293B' }}>
                    No shipments found matching "{effectiveQuery}"
                  </div>
                  <div style={{ fontSize: '0.78rem', marginTop: 4 }}>
                    Try searching for another Shipment ID, SKU (e.g. <code>PRD-101</code>), or destination hub.
                  </div>
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>

      {/* Pagination Footer Controls (Active on 'all' view or when multiple pages exist) */}
      {viewMode === 'all' && (
        <div className="pagination-bar">
          <div>
            Showing <strong style={{ color: '#1E293B' }}>{filtered.length === 0 ? 0 : startIndex + 1}</strong> to{' '}
            <strong style={{ color: '#1E293B' }}>{Math.min(startIndex + pageSize, filtered.length)}</strong> of{' '}
            <strong style={{ color: '#1E293B' }}>{filtered.length}</strong> shipments
            {filtered.length < fullFleetList.length && (
              <span style={{ color: '#94A3B8', marginLeft: 6 }}>
                (filtered from {fullFleetList.length} total)
              </span>
            )}
          </div>

          <div className="pagination-controls">
            <button
              type="button"
              className="pagination-btn"
              disabled={validCurrentPage <= 1}
              onClick={() => setCurrentPage((p) => Math.max(1, p - 1))}
            >
              <ChevronLeft size={14} />
              Previous
            </button>

            <span style={{ fontSize: '0.78rem', color: '#475569', fontWeight: 600 }}>
              Page {validCurrentPage} of {totalPages}
            </span>

            <button
              type="button"
              className="pagination-btn"
              disabled={validCurrentPage >= totalPages}
              onClick={() => setCurrentPage((p) => Math.min(totalPages, p + 1))}
            >
              Next
              <ChevronRight size={14} />
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
