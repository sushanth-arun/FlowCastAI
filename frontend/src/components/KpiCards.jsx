import React from 'react';
import { Package, AlertTriangle, Warehouse, DollarSign } from 'lucide-react';

export default function KpiCards({ kpis, focalShortageCost = 4000 }) {
  const cards = [
    {
      id: 'total',
      label: 'Total Active Shipments',
      value: kpis.totalShipments || 148,
      subtext: '34 currently in transit across 3 hubs',
      color: 'blue',
      icon: Package
    },
    {
      id: 'at-risk',
      label: 'Disrupted / At-Risk Shipments',
      value: kpis.atRiskShipments || 6,
      subtext: '2 high-risk delays (including SHP-8821)',
      color: 'red',
      icon: AlertTriangle
    },
    {
      id: 'low-stock',
      label: 'Critical Low-Stock Hubs',
      value: `${kpis.criticalLowStockItems || 1} Hub`,
      subtext: 'Warehouse A (ORD-CHI) below safety threshold',
      color: 'amber',
      icon: Warehouse
    },
    {
      id: 'cost-impact',
      label: 'Estimated Cost at Risk',
      value: `$${(kpis.estimatedPotentialCostImpact || 18400).toLocaleString()}`,
      subtext: `$${focalShortageCost.toLocaleString()} immediate focus on Warehouse A`,
      color: 'violet',
      icon: DollarSign
    }
  ];

  return (
    <div className="kpi-grid">
      {cards.map((card) => {
        const Icon = card.icon;
        return (
          <div key={card.id} className={`kpi-card ${card.color}`}>
            <div className="kpi-header">
              <span className="kpi-label">{card.label}</span>
              <div className={`kpi-icon-wrap ${card.color}`}>
                <Icon size={18} />
              </div>
            </div>
            <div className="kpi-value">{card.value}</div>
            <div className="kpi-subtext">
              <span>{card.subtext}</span>
            </div>
          </div>
        );
      })}
    </div>
  );
}
