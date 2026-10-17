import React from 'react';
import { Package, AlertTriangle, Warehouse, DollarSign } from 'lucide-react';

export default function KpiCards({
  kpis = {},
  shipments = [],
  warehouses = [],
  optimizationResult = null,
  focalShortageCost = 4000
}) {
  const totalShipments = shipments.length > 0 ? shipments.length : (kpis.totalShipments || 4);
  const atRiskShipments = shipments.length > 0
    ? shipments.filter((s) => s.riskLevel === 'High' || s.riskLevel === 'Medium').length
    : (kpis.atRiskShipments || 1);
  const criticalHubs = warehouses.length > 0
    ? warehouses.filter((w) => w.status === 'critical').length
    : (kpis.criticalLowStockItems || 1);
  const criticalHubName = warehouses.find((w) => w.status === 'critical')?.name || 'Warehouse A (Chennai Hub)';
  const costAtRisk = optimizationResult?.baselineTotalCost || kpis.estimatedPotentialCostImpact || focalShortageCost || 4000;
  const savings = optimizationResult?.recommendedOption?.savingsVsBaseline || 3550;

  const cards = [
    {
      id: 'total',
      label: 'Total Active Shipments',
      value: totalShipments,
      subtext: `Monitored across ${warehouses.length || 3} fulfillment hubs`,
      color: 'blue',
      icon: Package
    },
    {
      id: 'at-risk',
      label: 'Disrupted / At-Risk Shipments',
      value: atRiskShipments,
      subtext: `${atRiskShipments} critical delay (SHP-CH-01 Port Congestion)`,
      color: 'red',
      icon: AlertTriangle
    },
    {
      id: 'low-stock',
      label: 'Critical Low-Stock Hubs',
      value: `${criticalHubs} Hub`,
      subtext: `${criticalHubName} below safety threshold`,
      color: 'amber',
      icon: Warehouse
    },
    {
      id: 'cost-impact',
      label: 'Estimated Cost at Risk',
      value: `$${costAtRisk.toLocaleString()}`,
      subtext: `$${savings.toLocaleString()} net savings via AI transfer`,
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
