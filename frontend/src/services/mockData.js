/**
 * FlowCast AI — Operational Data & Scenario Simulation Engine
 * IBM Z Datathon 2026 | Real-Time AI for Critical Decisions
 * 
 * Demonstrates the 3-warehouse supply chain disruption scenario:
 * - Warehouse A (Chicago): 20 units (Critical Shortage due to delayed shipment SHP-8821)
 * - Warehouse B (Detroit): 150 units (Surplus: 100 units above safety threshold)
 * - Warehouse C (Columbus): 80 units (Surplus: 35 units above safety threshold)
 */

export const INITIAL_WAREHOUSES = [
  {
    id: 'WH-A',
    code: 'ORD-CHI-01',
    name: 'Warehouse A (Chicago Hub)',
    location: 'Chicago, IL',
    role: 'Assembly & Fulfillment Center',
    currentStock: 20,
    safetyStock: 30,
    maxCapacity: 250,
    dailyDemand: 10,
    status: 'critical',
    statusLabel: 'Critical Shortage Risk',
    color: '#EF4444',
    incomingShipmentId: 'SHP-8821',
    coordinates: { lat: 41.8781, lng: -87.6298 }
  },
  {
    id: 'WH-B',
    code: 'DTW-MI-02',
    name: 'Warehouse B (Detroit Distribution)',
    location: 'Detroit, MI',
    role: 'Regional Component Reserve Hub',
    currentStock: 150,
    safetyStock: 50,
    maxCapacity: 300,
    dailyDemand: 6,
    status: 'surplus',
    statusLabel: 'Significant Surplus (+100 usable)',
    color: '#10B981',
    transitDaysToA: 1.5,
    transferUnitCost: 8,
    transferFixedCost: 130,
    distanceMiles: 282,
    coordinates: { lat: 42.3314, lng: -83.0458 }
  },
  {
    id: 'WH-C',
    code: 'CMH-OH-03',
    name: 'Warehouse C (Columbus Depot)',
    location: 'Columbus, OH',
    role: 'Secondary Distribution Center',
    currentStock: 80,
    safetyStock: 45,
    maxCapacity: 200,
    dailyDemand: 5,
    status: 'moderate',
    statusLabel: 'Moderate Surplus (+35 usable)',
    color: '#3B6FF5',
    transitDaysToA: 2.0,
    transferUnitCost: 12,
    transferFixedCost: 200,
    distanceMiles: 355,
    coordinates: { lat: 39.9612, lng: -82.9988 }
  }
];

export const INITIAL_SHIPMENTS = [
  {
    id: 'SHP-8821',
    sku: 'FLW-9402',
    productName: 'Automotive ECU Controller Module',
    destinationWarehouseId: 'WH-A',
    destinationName: 'Warehouse A (Chicago Hub)',
    origin: 'Apex Global Logistics (Port of Newark, NJ)',
    quantity: 50,
    scheduledArrival: 'Oct 20, 2026',
    predictedDelayDays: 4.0,
    delayProbability: 0.88,
    riskLevel: 'High',
    riskBadgeColor: 'red',
    status: 'Delayed (Port Congestion)',
    isFocalScenario: true,
    transportMode: 'Standard Intermodal Freight',
    estimatedCarrierSlaPenalty: '$4,000 (at $100/unit unmet)'
  },
  {
    id: 'SHP-7940',
    sku: 'FLW-3108',
    productName: 'Precision Stepper Motor 24V',
    destinationWarehouseId: 'WH-B',
    destinationName: 'Warehouse B (Detroit Distribution)',
    origin: 'Nordic Sensor Dynamics (Chicago, IL)',
    quantity: 120,
    scheduledArrival: 'Oct 21, 2026',
    predictedDelayDays: 0.5,
    delayProbability: 0.21,
    riskLevel: 'Low',
    riskBadgeColor: 'green',
    status: 'On Schedule (In Transit)',
    isFocalScenario: false,
    transportMode: 'Dedicated Truckload (FTL)'
  },
  {
    id: 'SHP-9104',
    sku: 'FLW-5520',
    productName: 'Thermal Management Heatsink Fin 4U',
    destinationWarehouseId: 'WH-A',
    destinationName: 'Warehouse A (Chicago Hub)',
    origin: 'Pacific Alloy Machining (Long Beach, CA)',
    quantity: 80,
    scheduledArrival: 'Oct 23, 2026',
    predictedDelayDays: 2.5,
    delayProbability: 0.65,
    riskLevel: 'Medium',
    riskBadgeColor: 'amber',
    status: 'Customs Clearance Delay',
    isFocalScenario: false,
    transportMode: 'Rail Intermodal'
  },
  {
    id: 'SHP-6512',
    sku: 'FLW-1049',
    productName: 'Optoelectronic Coupler IC Array',
    destinationWarehouseId: 'WH-C',
    destinationName: 'Warehouse C (Columbus Depot)',
    origin: 'East Coast Semiconductor (Boston, MA)',
    quantity: 200,
    scheduledArrival: 'Oct 24, 2026',
    predictedDelayDays: 0.3,
    delayProbability: 0.14,
    riskLevel: 'Low',
    riskBadgeColor: 'green',
    status: 'Dispatched from Hub',
    isFocalScenario: false,
    transportMode: 'Priority Ground'
  },
  {
    id: 'SHP-8319',
    sku: 'FLW-8812',
    productName: 'Power Isolation Transformer 500W',
    destinationWarehouseId: 'WH-B',
    destinationName: 'Warehouse B (Detroit Distribution)',
    origin: 'Midwest Forge & Coil (Cleveland, OH)',
    quantity: 45,
    scheduledArrival: 'Oct 22, 2026',
    predictedDelayDays: 3.2,
    delayProbability: 0.74,
    riskLevel: 'High',
    riskBadgeColor: 'red',
    status: 'Carrier Capacity Delay',
    isFocalScenario: false,
    transportMode: 'Less-than-Truckload (LTL)'
  }
];

export const INITIAL_KPIS = {
  totalShipments: 148,
  activeInTransit: 34,
  atRiskShipments: 6,
  highRiskShipments: 2,
  criticalLowStockItems: 1,
  estimatedPotentialCostImpact: 18400,
  immediateFocalImpact: 4000
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
    delayDays = 4.0,
    dailyDemand = 10,
    whBTransferUnitCost = 8,
    whCTransferUnitCost = 12,
    shortagePenaltyPerUnit = 100,
    expediteAirCost = 1350,
    whACurrentStock = 20,
    whBSurplusTotal = 150,
    whBSafetyStock = 50,
    whCSurplusTotal = 80,
    whCSafetyStock = 45
  } = params;

  // Warehouse A stock runway
  const runwayDays = Number((whACurrentStock / dailyDemand).toFixed(1));
  
  // Total arrival horizon with delay
  const normalArrivalDays = 2.0;
  const actualArrivalDays = Number((normalArrivalDays + delayDays).toFixed(1));
  
  // Total demand required until shipment arrives
  const totalDemandUntilArrival = Math.round(actualArrivalDays * dailyDemand);
  
  // Shortage without any recovery intervention
  const unconstrainedShortage = Math.max(0, totalDemandUntilArrival - whACurrentStock);
  const neededUnits = Math.min(unconstrainedShortage, 50); // incoming shipment volume is 50

  // 1. Baseline Option (No Action)
  const baselineUnmetUnits = neededUnits;
  const baselinePenaltyCost = baselineUnmetUnits * shortagePenaltyPerUnit;
  const baselineTotalCost = baselinePenaltyCost;

  // 2. Warehouse B Transfer Evaluation
  const whBUsableSurplus = Math.max(0, whBSurplusTotal - whBSafetyStock);
  const whBTransferUnits = Math.min(neededUnits, whBUsableSurplus);
  const whBTransitDays = 1.5;
  const whBActionCost = whBTransferUnits > 0 ? (whBTransferUnits * whBTransferUnitCost) + 130 : 0;
  const whBUnmetUnits = Math.max(0, neededUnits - whBTransferUnits);
  const whBPenaltyCost = whBUnmetUnits * shortagePenaltyPerUnit;
  const whBTotalCost = whBActionCost + whBPenaltyCost;
  const whBFeasible = whBTransferUnits === neededUnits && whBTransitDays <= (runwayDays + 0.5);

  // 3. Warehouse C Transfer Evaluation
  const whCUsableSurplus = Math.max(0, whCSurplusTotal - whCSafetyStock);
  const whCTransferUnits = Math.min(neededUnits, whCUsableSurplus);
  const whCTransitDays = 2.0;
  const whCActionCost = whCTransferUnits > 0 ? (whCTransferUnits * whCTransferUnitCost) + 200 : 0;
  const whCUnmetUnits = Math.max(0, neededUnits - whCTransferUnits);
  const whCPenaltyCost = whCUnmetUnits * shortagePenaltyPerUnit;
  const whCTotalCost = whCActionCost + whCPenaltyCost;
  const whCFeasible = whCTransferUnits >= neededUnits && whCTransitDays <= runwayDays;

  // 4. Expedited Supplier Air Freight
  const airTransitDays = 1.5;
  const airActionCost = expediteAirCost;
  const airUnmetUnits = 0;
  const airTotalCost = airActionCost;
  const airFeasible = true;

  // Compile option list
  const options = [
    {
      id: 'opt-b',
      title: 'Inter-Warehouse Transfer from Warehouse B (Detroit)',
      type: 'STOCK_TRANSFER',
      sourceWarehouse: 'Warehouse B (Detroit Distribution)',
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
      title: 'Inter-Warehouse Transfer from Warehouse C (Columbus)',
      type: 'STOCK_TRANSFER',
      sourceWarehouse: 'Warehouse C (Columbus Depot)',
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
      constraintNotes: `C capped at +${whCUsableSurplus} usable units to preserve ${whCSafetyStock} safety stock. Leaves ${whCUnmetUnits} units unmet.`,
      urgencyBadge: whCUnmetUnits > 0 ? 'Partial Recovery Only' : 'Feasible'
    },
    {
      id: 'opt-air',
      title: 'Expedited Direct Air Freight from Supplier',
      type: 'EXPEDITED_FREIGHT',
      sourceWarehouse: 'Apex Global Logistics (Port of Newark)',
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
      constraintNotes: 'Cuts shipment lead time to 1.5 days. Prevents all shortage but carries high air courier surcharge.',
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
