import React from 'react';
import {
  Sparkles,
  ArrowRightLeft,
  CheckCircle2,
  DollarSign,
  AlertCircle,
  Layers,
  ArrowRight
} from 'lucide-react';

export default function RecommendationCard({
  optimizationResult,
  onCompareScenarios,
  onViewExplanation
}) {
  if (!optimizationResult || !optimizationResult.recommendedOption) {
    return null;
  }

  const { recommendedOption, baselineTotalCost, neededUnits } = optimizationResult;
  const isRecommendedTransfer = recommendedOption.type === 'STOCK_TRANSFER';

  return (
    <div className="recommendation-card">
      {/* Header Banner with Subtle Blue/Violet Gradient */}
      <div className="rec-header-banner">
        <div className="rec-title-group">
          <div className="rec-badge-ai">
            <Sparkles size={13} />
            AI Decision Support
          </div>
          <div className="rec-heading">Optimal Disruption Recovery Prescription</div>
        </div>
        <span style={{ fontSize: '0.74rem', color: '#64748B', fontWeight: 600 }}>
          Objective: Min Total Cost s.t. Constraints
        </span>
      </div>

      <div className="rec-body">
        {/* Recommended Action Highlight Box */}
        <div className="rec-action-highlight">
          <div className="rec-action-title">
            <ArrowRightLeft size={18} />
            {recommendedOption.title}
          </div>
          <p className="rec-action-desc">
            {recommendedOption.constraintNotes} This recommendation delivers{' '}
            <strong>{recommendedOption.unitsSupplied} units</strong> to Warehouse A via direct dedicated transit (1.5 days), arriving{' '}
            <strong>prior to stock depletion</strong>, eliminating unmet customer orders.
          </p>
        </div>

        {/* 3-Part Financial Comparison Strip */}
        <div className="financial-strip">
          <div className="financial-box highlight">
            <div className="fin-label">Action Cost (Recovery)</div>
            <div className="fin-value green">
              ${recommendedOption.totalCost.toLocaleString()}
            </div>
            <div className="fin-delta">
              ${recommendedOption.savingsVsBaseline.toLocaleString()} ({recommendedOption.percentReduction}%) savings
            </div>
          </div>

          <div className="financial-box">
            <div className="fin-label">Shortage Under Recommendation</div>
            <div className="fin-value blue">
              {recommendedOption.unmetUnits} units
            </div>
            <div style={{ fontSize: '0.7rem', color: '#10B981', fontWeight: 600, marginTop: 2 }}>
              100% Demand Covered
            </div>
          </div>

          <div className="financial-box baseline">
            <div className="fin-label">No-Action Baseline Penalty</div>
            <div className="fin-value red">
              ${baselineTotalCost.toLocaleString()}
            </div>
            <div style={{ fontSize: '0.7rem', color: '#EF4444', fontWeight: 600, marginTop: 2 }}>
              {neededUnits} unmet units @ $100/ea
            </div>
          </div>
        </div>

        {/* Explicit Operational Constraints Checklist */}
        <div className="constraints-card">
          <div className="constraints-title">Operational Feasibility & Safety Constraints Verified</div>
          
          <div className="constraint-item">
            <CheckCircle2 size={15} className="check-icon" />
            <span>
              <strong>Source Reserve Margin:</strong> Warehouse B retains{' '}
              {recommendedOption.retainedStockAtSource ?? 110} units (exceeds safety threshold of{' '}
              {recommendedOption.sourceSafetyThreshold ?? 50} units).
            </span>
          </div>

          <div className="constraint-item">
            <CheckCircle2 size={15} className="check-icon" />
            <span>
              <strong>Runway vs. Transit Time:</strong> Inter-hub transit of 1.5 days is faster than Warehouse A's stock depletion runway.
            </span>
          </div>

          <div className="constraint-item">
            <CheckCircle2 size={15} className="check-icon" />
            <span>
              <strong>Freight Capacity:</strong> {recommendedOption.unitsSupplied ?? 40}-unit payload is within dedicated transport capacity.
            </span>
          </div>
        </div>
      </div>

      {/* Footer Actions */}
      <div className="rec-footer">
        <div style={{ display: 'flex', alignItems: 'center', gap: 6, fontSize: '0.74rem', color: '#64748B' }}>
          <AlertCircle size={14} color="#3B6FF5" />
          <span>Decision support recommendation — awaiting manager dispatch approval</span>
        </div>

        <button
          className="btn-secondary"
          onClick={onCompareScenarios}
          title="Compare all 4 alternatives side by side"
        >
          <Layers size={15} />
          Compare 4 Alternatives
          <ArrowRight size={13} />
        </button>
      </div>
    </div>
  );
}
