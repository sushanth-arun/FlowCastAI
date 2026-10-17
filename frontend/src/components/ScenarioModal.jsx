import React from 'react';
import { X, CheckCircle2, AlertTriangle, ShieldAlert, Award } from 'lucide-react';

export default function ScenarioModal({ isOpen, onClose, options, recommendedId }) {
  if (!isOpen || !options) return null;

  return (
    <div className="modal-backdrop" onClick={onClose}>
      <div className="modal-dialog" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <div>
            <div className="modal-title">Operational Recovery Alternatives Comparison Matrix</div>
            <div style={{ fontSize: '0.78rem', color: '#64748B', marginTop: 2 }}>
              Constrained optimization evaluation for Warehouse A (SKU FLW-9402)
            </div>
          </div>
          <button className="modal-close-btn" onClick={onClose} title="Close">
            <X size={20} />
          </button>
        </div>

        <div className="modal-content-area">
          <table className="comparison-table">
            <thead>
              <tr>
                <th>Recovery Option</th>
                <th>Source Hub</th>
                <th>Units Provided</th>
                <th>Lead Time</th>
                <th>Action Cost</th>
                <th>Unmet Shortage</th>
                <th>Total Cost</th>
                <th>Status / Verdict</th>
              </tr>
            </thead>
            <tbody>
              {options.map((opt) => {
                const isWinner = opt.id === recommendedId;

                return (
                  <tr key={opt.id} className={isWinner ? 'winner' : ''}>
                    <td>
                      <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
                        {isWinner && <Award size={16} color="#3B6FF5" />}
                        <div>
                          <div style={{ fontWeight: 700, color: isWinner ? '#3B6FF5' : '#14213D' }}>
                            {opt.title}
                          </div>
                          <div style={{ fontSize: '0.72rem', color: '#64748B', marginTop: 2 }}>
                            {opt.constraintNotes}
                          </div>
                        </div>
                      </div>
                    </td>
                    <td style={{ fontFamily: 'var(--font-mono)', fontSize: '0.78rem' }}>
                      {opt.sourceCode}
                    </td>
                    <td style={{ fontWeight: 600 }}>
                      {opt.unitsSupplied} units
                    </td>
                    <td>
                      {opt.transitTimeDays} days
                    </td>
                    <td style={{ fontWeight: 600 }}>
                      ${opt.actionCost.toLocaleString()}
                    </td>
                    <td>
                      {opt.unmetUnits > 0 ? (
                        <span style={{ color: '#EF4444', fontWeight: 700 }}>
                          {opt.unmetUnits} units (${opt.penaltyCost})
                        </span>
                      ) : (
                        <span style={{ color: '#10B981', fontWeight: 600 }}>
                          0 (Covered)
                        </span>
                      )}
                    </td>
                    <td>
                      <div style={{ fontWeight: 800, fontSize: '0.92rem', color: isWinner ? '#059669' : opt.id === 'opt-baseline' ? '#DC2626' : '#14213D' }}>
                        ${opt.totalCost.toLocaleString()}
                      </div>
                      {isWinner && (
                        <div style={{ fontSize: '0.68rem', color: '#059669', fontWeight: 700 }}>
                          Lowest Total Cost
                        </div>
                      )}
                    </td>
                    <td>
                      {isWinner ? (
                        <span className="risk-badge green">
                          <CheckCircle2 size={12} />
                          Recommended
                        </span>
                      ) : opt.unmetUnits > 0 && opt.id !== 'opt-baseline' ? (
                        <span className="risk-badge amber">
                          <AlertTriangle size={12} />
                          Partial Capacity
                        </span>
                      ) : opt.id === 'opt-baseline' ? (
                        <span className="risk-badge red">
                          <ShieldAlert size={12} />
                          High Penalty
                        </span>
                      ) : (
                        <span className="risk-badge" style={{ background: '#F1F5F9', color: '#64748B', border: '1px solid #CBD5E1' }}>
                          Sub-Optimal Cost
                        </span>
                      )}
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>

          <div style={{ marginTop: '20px', padding: '12px 16px', background: '#F8FAFD', borderRadius: '8px', border: '1px solid #E2E8F0', display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
            <div style={{ fontSize: '0.78rem', color: '#475569' }}>
              <strong>Mathematical Formulation:</strong> Objective solves min(Action_Cost + &Sigma; Unmet &times; Penalty_Rate) subject to Source_Stock - &Delta;Stock &ge; Safety_Threshold.
            </div>
            <button className="btn-primary" onClick={onClose}>
              Done Viewing
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
