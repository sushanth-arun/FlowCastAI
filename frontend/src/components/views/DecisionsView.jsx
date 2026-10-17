import React from 'react';
import RecommendationCard from '../RecommendationCard';
import WhatIfSimulator from '../WhatIfSimulator';
import { Sparkles, Code, CheckCircle2, DollarSign } from 'lucide-react';

export default function DecisionsView({
  optimizationResult,
  onCompareScenarios,
  onRunSimulation,
  isSimulating
}) {
  return (
    <div>
      <div className="page-header">
        <div>
          <h1 className="page-title">AI Prescriptive Decision Engine</h1>
          <p className="page-subtitle">
            Constrained mathematical optimization minimizing supply chain disruption costs
          </p>
        </div>
      </div>

      {/* Main Recommendation Hero */}
      <RecommendationCard
        optimizationResult={optimizationResult}
        onCompareScenarios={onCompareScenarios}
      />

      {/* Mathematical Objective & Formulation Section */}
      <div className="card-container" style={{ marginTop: '28px', background: '#FAFCFF', border: '1px solid #D6E4FF' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 12 }}>
          <Code size={18} color="#3B6FF5" />
          <div className="card-heading">Optimization Formulation & Operational Constraints</div>
        </div>

        <div style={{ display: 'grid', gridTemplateColumns: '1.2fr 0.8fr', gap: 20 }}>
          <div style={{ background: '#FFFFFF', padding: '16px', borderRadius: '10px', border: '1px solid #E2E8F0' }}>
            <div style={{ fontSize: '0.78rem', fontWeight: 700, color: '#3B6FF5', textTransform: 'uppercase', marginBottom: 8 }}>
              Objective Function (Cost Minimization)
            </div>
            <div style={{ fontFamily: 'var(--font-mono)', fontSize: '0.86rem', color: '#14213D', background: '#F8FAFD', padding: '12px', borderRadius: '6px', border: '1px solid #E2E8F0', lineHeight: 1.6 }}>
              min Total_Cost = Action_Cost(x) + [Unmet_Demand(x) &times; Penalty_Rate]
            </div>
            <div style={{ fontSize: '0.76rem', color: '#64748B', marginTop: 8 }}>
              Where <code>Action_Cost</code> includes per-unit haulage fees and fixed dispatch costs; <code>Penalty_Rate</code> reflects customer contract SLA penalties ($100/unmet unit).
            </div>
          </div>

          <div style={{ background: '#FFFFFF', padding: '16px', borderRadius: '10px', border: '1px solid #E2E8F0' }}>
            <div style={{ fontSize: '0.78rem', fontWeight: 700, color: '#10B981', textTransform: 'uppercase', marginBottom: 8 }}>
              Hard Constraints Verified
            </div>
            <ul style={{ listStyle: 'none', display: 'flex', flexDirection: 'column', gap: 8, fontSize: '0.78rem', color: '#334155' }}>
              <li style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
                <CheckCircle2 size={14} color="#10B981" />
                <span><strong>Safety Threshold:</strong> Stock<sub>source</sub> - &Delta;S &ge; Safety<sub>min</sub></span>
              </li>
              <li style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
                <CheckCircle2 size={14} color="#10B981" />
                <span><strong>Timing Feasibility:</strong> Transit_Days &le; Stockout_Runway<sub>A</sub></span>
              </li>
              <li style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
                <CheckCircle2 size={14} color="#10B981" />
                <span><strong>Carrier Limit:</strong> &Delta;S &le; Max_LTL_Capacity (100u)</span>
              </li>
            </ul>
          </div>
        </div>
      </div>

      {/* Simulator */}
      <WhatIfSimulator
        currentParams={optimizationResult?.inputParams}
        onRunSimulation={onRunSimulation}
        isSimulating={isSimulating}
        optimizationResult={optimizationResult}
      />
    </div>
  );
}
