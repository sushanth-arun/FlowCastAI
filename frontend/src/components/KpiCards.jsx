import React from 'react';
import { Package, AlertTriangle, Warehouse, ShieldCheck } from 'lucide-react';

export default function KpiCards({
  kpis = {},
  shipments = [],
  warehouses = [],
  optimizationResult = null
}) {
  const totalShipments = kpis.totalShipments || 148;
  const atRiskShipments = shipments.length > 0
    ? shipments.filter((s) => s.riskLevel === 'High' || s.riskLevel === 'Medium').length
    : (kpis.atRiskShipments || 1);
  const criticalHubs = warehouses.length > 0
    ? warehouses.filter((w) => w.status === 'critical').length
    : (kpis.criticalLowStockItems || 1);
  const criticalHubName = warehouses.find((w) => w.status === 'critical')?.name || 'Warehouse A (Chennai Hub)';

  const cards = [
    {
      id: 'total',
      label: 'Total Active Shipments',
      value: totalShipments,
      subtext: '34 currently in transit across network',
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
      id: 'on-time-rate',
      label: 'Fleet On-Time Delivery Rate',
      value: '97.3%',
      subtext: '1 priority route off-schedule (SHP-CH-01)',
      color: 'violet',
      icon: ShieldCheck
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
