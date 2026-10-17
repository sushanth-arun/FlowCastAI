/**
 * FlowCast AI — Operational Data & Scenario Simulation Engine
 * IBM Z Datathon 2026 | Real-Time AI for Critical Decisions
 * 
 * 3-Warehouse Supply Chain Disruption Scenario:
 * - Warehouse A (Chennai): 160 units (Critical Shortage due to delayed shipment SHP-CH-01)
 * - Warehouse B (Bengaluru): 680 units (Surplus: +530 units above safety threshold)
 * - Warehouse C (Hyderabad): 450 units (Surplus: +250 units above safety threshold)
 */

export const INITIAL_WAREHOUSES = [
  {
    id: 'WH-A',
    code: 'MAA-CHE-01',
    name: 'Warehouse A (Chennai Hub)',
    location: 'Chennai, Tamil Nadu',
    role: 'Fulfillment & Critical Target',
    currentStock: 160,
    safetyStock: 150,
    maxCapacity: 500,
    dailyDemand: 20,
    status: 'critical',
    statusLabel: 'Critical Shortage Risk',
    color: '#EF4444',
    incomingShipmentId: 'SHP-CH-01',
    coordinates: { lat: 13.0827, lng: 80.2707 }
  },
  {
    id: 'WH-B',
    code: 'BLR-KA-02',
    name: 'Warehouse B (Bengaluru Hub)',
    location: 'Bengaluru, Karnataka',
    role: 'Regional Component Reserve Hub',
    currentStock: 680,
    safetyStock: 150,
    maxCapacity: 600,
    dailyDemand: 15,
    status: 'surplus',
    statusLabel: 'Significant Surplus (+530 usable)',
    color: '#10B981',
    transitDaysToA: 1.5,
    transferUnitCost: 8,
    transferFixedCost: 130,
    distanceMiles: 215,
    coordinates: { lat: 12.9716, lng: 77.5946 }
  },
  {
    id: 'WH-C',
    code: 'HYD-TS-03',
    name: 'Warehouse C (Hyderabad Hub)',
    location: 'Hyderabad, Telangana',
    role: 'Secondary Distribution Depot',
    currentStock: 450,
    safetyStock: 200,
    maxCapacity: 450,
    dailyDemand: 12,
    status: 'moderate',
    statusLabel: 'Moderate Surplus (+250 usable)',
    color: '#3B6FF5',
    transitDaysToA: 2.0,
    transferUnitCost: 12,
    transferFixedCost: 200,
    distanceMiles: 390,
    coordinates: { lat: 17.3850, lng: 78.4867 }
  }
];

export const INITIAL_SHIPMENTS = [
  {
    id: 'SHP-CH-01',
    sku: 'PRD-101',
    productName: 'IoT Telemetry Sensor Nodes',
    destinationWarehouseId: 'WH-A',
    destinationName: 'Warehouse A (Chennai Hub)',
    origin: 'Port of Chennai',
    quantity: 180,
    scheduledArrival: 'Delayed (+3 Days)',
    predictedDelayDays: 3.0,
    delayProbability: 0.88,
    riskLevel: 'High',
    riskBadgeColor: 'red',
    status: 'Delayed (Port Congestion)',
    isFocalScenario: true,
    transportMode: 'Intermodal Freight',
    estimatedCarrierSlaPenalty: '$26,400 (at $120/unit unmet)'
  },
  {
    id: 'SHP-CH-02',
    sku: 'PRD-102',
    productName: 'Smart Cardio Monitor Units',
    destinationWarehouseId: 'WH-A',
    destinationName: 'Warehouse A (Chennai Hub)',
    origin: 'Sri City Hub',
    quantity: 80,
    scheduledArrival: 'Tomorrow, 10:00',
    predictedDelayDays: 0.4,
    delayProbability: 0.15,
    riskLevel: 'Low',
    riskBadgeColor: 'green',
    status: 'On Schedule',
    isFocalScenario: false,
    transportMode: 'Intermodal Freight'
  },
  {
    id: 'SHP-BLR-01',
    sku: 'PRD-101',
    productName: 'IoT Telemetry Sensor Nodes',
    destinationWarehouseId: 'WH-B',
    destinationName: 'Warehouse B (Bengaluru Hub)',
    origin: 'Hosur Gateway',
    quantity: 150,
    scheduledArrival: 'Today, 21:00',
    predictedDelayDays: 0.4,
    delayProbability: 0.18,
    riskLevel: 'Low',
    riskBadgeColor: 'green',
    status: 'On Schedule',
    isFocalScenario: false,
    transportMode: 'Dedicated Truckload'
  },
  {
    id: 'SHP-HYD-01',
    sku: 'PRD-101',
    productName: 'IoT Telemetry Sensor Nodes',
    destinationWarehouseId: 'WH-C',
    destinationName: 'Warehouse C (Hyderabad Hub)',
    origin: 'Shamshabad Cargo Terminal',
    quantity: 100,
    scheduledArrival: 'Tomorrow, 08:00',
    predictedDelayDays: 0.4,
    delayProbability: 0.14,
    riskLevel: 'Low',
    riskBadgeColor: 'green',
    status: 'On Schedule',
    isFocalScenario: false,
    transportMode: 'Dedicated Truckload'
  }
];

export const INITIAL_KPIS = {
  totalShipments: 4,
  activeInTransit: 4,
  atRiskShipments: 1,
  highRiskShipments: 1,
  criticalLowStockItems: 1,
  estimatedPotentialCostImpact: 26400,
  immediateFocalImpact: 26400
};

/**
 * Mathematical Optimization & Decision Support Engine
 * Solves constrained recovery options for Warehouse A disruption.
 * 
 * Objective: Minimize Total Cost = Action Cost + (Unmet Demand * Penalty Rate)
 * Subject to:
 * 1. Source Warehouse Inventory >= Safety Stock Threshold
 * 2. Transfer Arrival Time <= Days until Unmet Demand
 * 3. Transfer Quantity <= Source Surplus
 */
export function calculateOptimization(params = {}) {
  const {
    delayDays = 3.0,
    dailyDemand = 20,
    whBTransferUnitCost = 8,
    whCTransferUnitCost = 12,
    shortagePenaltyPerUnit = 120,
    expediteAirCost = 8100,
    whACurrentStock = 160,
    whBSurplusTotal = 680,
    whBSafetyStock = 150,
    whCSurplusTotal = 450,
    whCSafetyStock = 200
  } = params;

  // Warehouse A stock runway
  const runwayDays = Number((whACurrentStock / dailyDemand).toFixed(1));
  
  // Total arrival horizon with delay
  const normalArrivalDays = 1.0;
  const actualArrivalDays = Number((normalArrivalDays + delayDays).toFixed(1));
  
  // Total demand required until shipment arrives
  const totalDemandUntilArrival = Math.round(actualArrivalDays * dailyDemand);
  
  // Shortage without any recovery intervention
  const unconstrainedShortage = Math.max(0, totalDemandUntilArrival - whACurrentStock);
  const neededUnits = Math.min(unconstrainedShortage, 220); // target shortage is up to 220 units

  // 1. Baseline Option (No Action)
  const baselineUnmetUnits = neededUnits;
  const baselinePenaltyCost = baselineUnmetUnits * shortagePenaltyPerUnit;
  const baselineTotalCost = baselinePenaltyCost;

  // 2. Warehouse B Transfer Evaluation (Bengaluru)
  const whBUsableSurplus = Math.max(0, whBSurplusTotal - whBSafetyStock);
  const whBTransferUnits = Math.min(neededUnits, whBUsableSurplus);
  const whBTransitDays = 1.5;
  const whBActionCost = whBTransferUnits > 0 ? (whBTransferUnits * whBTransferUnitCost) + 130 : 0;
  const whBUnmetUnits = Math.max(0, neededUnits - whBTransferUnits);
  const whBPenaltyCost = whBUnmetUnits * shortagePenaltyPerUnit;
  const whBTotalCost = whBActionCost + whBPenaltyCost;
  const whBFeasible = whBTransferUnits === neededUnits && whBTransitDays <= (runwayDays + 1.0);

  // 3. Warehouse C Transfer Evaluation (Hyderabad)
  const whCUsableSurplus = Math.max(0, whCSurplusTotal - whCSafetyStock);
  const whCTransferUnits = Math.min(neededUnits, whCUsableSurplus);
  const whCTransitDays = 2.0;
  const whCActionCost = whCTransferUnits > 0 ? (whCTransferUnits * whCTransferUnitCost) + 200 : 0;
  const whCUnmetUnits = Math.max(0, neededUnits - whCTransferUnits);
  const whCPenaltyCost = whCUnmetUnits * shortagePenaltyPerUnit;
  const whCTotalCost = whCActionCost + whCPenaltyCost;
  const whCFeasible = whCTransferUnits >= neededUnits && whCTransitDays <= (runwayDays + 0.5);

  // 4. Expedited Supplier Air Freight
  const airTransitDays = 1.0;
  const airActionCost = expediteAirCost;
  const airUnmetUnits = 0;
  const airTotalCost = airActionCost;
  const airFeasible = true;

  // Compile option list
  const options = [
    {
      id: 'opt-b',
      title: 'Inter-Warehouse Transfer from Bengaluru Hub (WH-B)',
      type: 'STOCK_TRANSFER',
      sourceWarehouse: 'Warehouse B (Bengaluru Hub)',
      sourceCode: 'WH-B',
      unitsSupplied: whBTransferUnits,
      transitTimeDays: whBTransitDays,
      actionCost: whBActionCost,
      unmetUnits: whBUnmetUnits,
      penaltyCost: whBPenaltyCost,
      totalCost: whBTotalCost,
      savingsVsBaseline: Math.max(0, baselineTotalCost - whBTotalCost),
      percentReduction: baselineTotalCost > 0 ? Number(((baselineTotalCost - whBTotalCost) / baselineTotalCost * 100).toFixed(1)) : 0,
      isFeasible: whBFeasible,
      retainedStockAtSource: whBSurplusTotal - whBTransferUnits,
      sourceSafetyThreshold: whBSafetyStock,
      constraintNotes: `Transfers ${whBTransferUnits} units. Source retains ${whBSurplusTotal - whBTransferUnits} units (> ${whBSafetyStock} safety stock). Transit time 1.5d arrives before stockout.`,
      urgencyBadge: 'Optimal Cost & Speed'
    },
    {
      id: 'opt-c',
      title: 'Inter-Warehouse Transfer from Hyderabad Hub (WH-C)',
      type: 'STOCK_TRANSFER',
      sourceWarehouse: 'Warehouse C (Hyderabad Hub)',
      sourceCode: 'WH-C',
      unitsSupplied: whCTransferUnits,
      transitTimeDays: whCTransitDays,
      actionCost: whCActionCost,
      unmetUnits: whCUnmetUnits,
      penaltyCost: whCPenaltyCost,
      totalCost: whCTotalCost,
      savingsVsBaseline: Math.max(0, baselineTotalCost - whCTotalCost),
      percentReduction: baselineTotalCost > 0 ? Number(((baselineTotalCost - whCTotalCost) / baselineTotalCost * 100).toFixed(1)) : 0,
      isFeasible: whCFeasible,
      retainedStockAtSource: whCSurplusTotal - whCTransferUnits,
      sourceSafetyThreshold: whCSafetyStock,
      constraintNotes: `Hyderabad retains ${whCSurplusTotal - whCTransferUnits} units to preserve safety stock. Transfers ${whCTransferUnits} units.`,
      urgencyBadge: whCUnmetUnits > 0 ? 'Partial Recovery Only' : 'Feasible'
    },
    {
      id: 'opt-air',
      title: 'Expedited Direct Air Freight from Port of Chennai',
      type: 'EXPEDITED_FREIGHT',
      sourceWarehouse: 'Port of Chennai Cargo Terminal',
      sourceCode: 'SUPPLIER-AIR',
      unitsSupplied: neededUnits,
      transitTimeDays: airTransitDays,
      actionCost: airActionCost,
      unmetUnits: 0,
      penaltyCost: 0,
      totalCost: airTotalCost,
      savingsVsBaseline: Math.max(0, baselineTotalCost - airTotalCost),
      percentReduction: baselineTotalCost > 0 ? Number(((baselineTotalCost - airTotalCost) / baselineTotalCost * 100).toFixed(1)) : 0,
      isFeasible: airFeasible,
      retainedStockAtSource: 'N/A',
      sourceSafetyThreshold: 'N/A',
      constraintNotes: 'Cuts shipment lead time to 1.0 day via priority dedicated air courier. Prevents shortage but incurs premium freight surcharge.',
      urgencyBadge: 'High Cost Alternative'
    },
    {
      id: 'opt-baseline',
      title: 'No Action (Baseline — Accept Delay & Stockout)',
      type: 'NO_ACTION',
      sourceWarehouse: 'None',
      sourceCode: 'NONE',
      unitsSupplied: 0,
      transitTimeDays: actualArrivalDays,
      actionCost: 0,
      unmetUnits: baselineUnmetUnits,
      penaltyCost: baselinePenaltyCost,
      totalCost: baselineTotalCost,
      savingsVsBaseline: 0,
      percentReduction: 0,
      isFeasible: true,
      retainedStockAtSource: 'N/A',
      sourceSafetyThreshold: 'N/A',
      constraintNotes: `Stock runs out after ${runwayDays} days. Customer demand for ${baselineUnmetUnits} units goes completely unmet.`,
      urgencyBadge: 'Default Inaction'
    }
  ];

  // Pick the winner: lowest total cost among fully feasible options, or lowest cost overall
  const feasibleOptions = options.filter(o => o.id !== 'opt-baseline' && o.unmetUnits === 0 && o.isFeasible);
  const recommendedOption = feasibleOptions.length > 0
    ? feasibleOptions.sort((a, b) => a.totalCost - b.totalCost)[0]
    : options.sort((a, b) => a.totalCost - b.totalCost)[0];

  // Daily inventory trajectory for chart (Days 0 to 7)
  const trajectory = [];
  let simStockBaseline = whACurrentStock;
  let simStockRecommended = whACurrentStock;

  for (let d = 0; d <= 7; d++) {
    // Baseline trajectory
    const dayDemand = d === 0 ? 0 : dailyDemand;
    simStockBaseline = Math.max(0, simStockBaseline - dayDemand);
    if (d === Math.round(actualArrivalDays)) {
      simStockBaseline += 50; // delayed shipment arrives
    }

    // Recommended trajectory (receives transfer on day 2 or 1.5)
    simStockRecommended = Math.max(0, simStockRecommended - dayDemand);
    if (d === 2) {
      simStockRecommended += recommendedOption.unitsSupplied; // transfer arrived
    }
    if (d === Math.round(actualArrivalDays)) {
      simStockRecommended += 50; // original shipment arrives
    }

    trajectory.push({
      day: `Day ${d}`,
      dayNum: d,
      baselineStock: simStockBaseline,
      recommendedStock: simStockRecommended,
      safetyStockThreshold: 30,
      demandRate: dailyDemand
    });
  }

  return {
    runwayDays,
    actualArrivalDays,
    unconstrainedShortage,
    neededUnits,
    baselineTotalCost,
    recommendedOption,
    options,
    trajectory,
    inputParams: {
      delayDays,
      dailyDemand,
      whBTransferUnitCost,
      shortagePenaltyPerUnit,
      expediteAirCost
    }
  };
}
