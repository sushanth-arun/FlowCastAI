"""
FlowCast AI - 3-Warehouse Inventory Network & Recovery Optimization Engine.

Implements:
1. Three-Warehouse Simulated Inventory Network:
   - WH-A: Chennai (Tamil Nadu Hub)
   - WH-B: Bengaluru (Karnataka Hub)
   - WH-C: Hyderabad (Telangana Hub)
2. Explicit inventory calculations:
   - Current Inventory, Expected Demand, Safety Stock, Incoming Replenishments.
   - Projected Stockout / Shortage determination with delay impacts.
3. Multi-Warehouse Recovery Solver:
   - Evaluates transferable stock: max(0, Current Stock - Demand - Safety Stock).
   - Strict constraint: Source warehouse MUST retain minimum safety stock.
   - Compares: Inter-warehouse transfers, expedited replenishment, or no action.
   - No double allocation of surplus stock across competing shortages.
   - Consistent baseline vs. recovery financial impact (Shortage penalty avoided, recovery cost, net savings).
4. Four Scenarios:
   - Scenario 1: Normal Operations (Balanced network)
   - Scenario 2: Chennai Shipment Disruption (Inbound delay at WH-A, surplus in WH-B)
   - Scenario 3: Multiple Warehouses at Risk (Simultaneous shortages in WH-A & WH-C, fair surplus allocation)
   - Scenario 4: Insufficient Network Inventory (System-wide stockout, evaluate expediting / unavoidable shortage)
"""

from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, asdict
import copy


@dataclass
class ProductInventory:
    product_id: str
    product_name: str
    category: str
    current_stock: int
    expected_demand: int
    min_safety_stock: int
    incoming_replenishment: int
    shipment_delayed: bool = False
    unit_cost: float = 120.0  # Shortage penalty per unit


@dataclass
class InboundShipment:
    shipment_id: str
    destination_wh: str
    origin_hub: str
    product_id: str
    product_name: str
    quantity: int
    expected_arrival: str
    delay_risk_score: float  # 0.0 - 1.0 (DataCo ML Model / Telemetry)
    delay_severity: str      # LOW, MODERATE, HIGH
    is_delayed: bool
    expedited_available: bool = True
    expedited_cost_per_unit: float = 45.0


@dataclass
class Warehouse:
    id: str
    name: str
    city: str
    state: str
    capacity_sqft: int
    inventory: List[ProductInventory]
    inbound_shipments: List[InboundShipment]


# Inter-warehouse logistics matrix (Transit time in hours, freight cost per unit)
TRANSIT_MATRIX = {
    ("WH-A", "WH-B"): {"distance_km": 350, "transit_hours": 8, "cost_per_unit": 14.50},
    ("WH-B", "WH-A"): {"distance_km": 350, "transit_hours": 8, "cost_per_unit": 14.50},
    ("WH-A", "WH-C"): {"distance_km": 630, "transit_hours": 14, "cost_per_unit": 22.00},
    ("WH-C", "WH-A"): {"distance_km": 630, "transit_hours": 14, "cost_per_unit": 22.00},
    ("WH-B", "WH-C"): {"distance_km": 570, "transit_hours": 12, "cost_per_unit": 19.50},
    ("WH-C", "WH-B"): {"distance_km": 570, "transit_hours": 12, "cost_per_unit": 19.50},
}


class FlowCastNetworkEngine:
    """
    Centralized data-access and recovery engine for the 3-Warehouse Supply Chain.
    """

    @staticmethod
    def get_base_scenario(scenario_id: str = "scenario_1") -> List[Warehouse]:
        """
        Build reproducible warehouse states for the 4 key MVP scenarios.
        """
        # Products modeled
        p_sensors = ("PRD-101", "IoT Telemetry Sensor Nodes", "Industrial Electronics")
        p_cardio = ("PRD-102", "Smart Cardio Monitor Units", "Medical Fitness")
        p_bearings = ("PRD-103", "Precision Motor Bearings", "Mechanical Assets")

        if scenario_id == "scenario_1":
            # SCENARIO 1: Normal Operations (All warehouses healthy)
            wh_a = Warehouse(
                id="WH-A", name="Warehouse A", city="Chennai", state="Tamil Nadu", capacity_sqft=120000,
                inventory=[
                    ProductInventory(p_sensors[0], p_sensors[1], p_sensors[2], current_stock=450, expected_demand=200, min_safety_stock=150, incoming_replenishment=100, shipment_delayed=False),
                    ProductInventory(p_cardio[0], p_cardio[1], p_cardio[2], current_stock=320, expected_demand=180, min_safety_stock=100, incoming_replenishment=80, shipment_delayed=False),
                    ProductInventory(p_bearings[0], p_bearings[1], p_bearings[2], current_stock=600, expected_demand=300, min_safety_stock=200, incoming_replenishment=150, shipment_delayed=False),
                ],
                inbound_shipments=[
                    InboundShipment("SHP-CH-01", "WH-A", "Port of Chennai", p_sensors[0], p_sensors[1], 100, "Today, 18:00", 0.12, "LOW", False),
                    InboundShipment("SHP-CH-02", "WH-A", "Sri City Hub", p_cardio[0], p_cardio[1], 80, "Tomorrow, 10:00", 0.18, "LOW", False),
                ]
            )
            wh_b = Warehouse(
                id="WH-B", name="Warehouse B", city="Bengaluru", state="Karnataka", capacity_sqft=150000,
                inventory=[
                    ProductInventory(p_sensors[0], p_sensors[1], p_sensors[2], current_stock=520, expected_demand=220, min_safety_stock=180, incoming_replenishment=120, shipment_delayed=False),
                    ProductInventory(p_cardio[0], p_cardio[1], p_cardio[2], current_stock=410, expected_demand=190, min_safety_stock=120, incoming_replenishment=100, shipment_delayed=False),
                    ProductInventory(p_bearings[0], p_bearings[1], p_bearings[2], current_stock=750, expected_demand=350, min_safety_stock=250, incoming_replenishment=200, shipment_delayed=False),
                ],
                inbound_shipments=[
                    InboundShipment("SHP-BLR-01", "WH-B", "Hosur Gateway", p_sensors[0], p_sensors[1], 120, "Today, 21:00", 0.15, "LOW", False),
                ]
            )
            wh_c = Warehouse(
                id="WH-C", name="Warehouse C", city="Hyderabad", state="Telangana", capacity_sqft=135000,
                inventory=[
                    ProductInventory(p_sensors[0], p_sensors[1], p_sensors[2], current_stock=480, expected_demand=210, min_safety_stock=160, incoming_replenishment=110, shipment_delayed=False),
                    ProductInventory(p_cardio[0], p_cardio[1], p_cardio[2], current_stock=360, expected_demand=170, min_safety_stock=110, incoming_replenishment=90, shipment_delayed=False),
                    ProductInventory(p_bearings[0], p_bearings[1], p_bearings[2], current_stock=680, expected_demand=320, min_safety_stock=220, incoming_replenishment=180, shipment_delayed=False),
                ],
                inbound_shipments=[
                    InboundShipment("SHP-HYD-01", "WH-C", "Shamshabad Cargo Terminal", p_sensors[0], p_sensors[1], 110, "Tomorrow, 08:00", 0.14, "LOW", False),
                ]
            )
            return [wh_a, wh_b, wh_c]

        elif scenario_id == "scenario_2":
            # SCENARIO 2: Chennai Shipment Disruption (WH-A faces shortage; WH-B has surplus)
            wh_a = Warehouse(
                id="WH-A", name="Warehouse A", city="Chennai", state="Tamil Nadu", capacity_sqft=120000,
                inventory=[
                    # Sensor inventory depleted: demand=380, stock=160, incoming=180 delayed -> Projected deficit = -220
                    ProductInventory(p_sensors[0], p_sensors[1], p_sensors[2], current_stock=160, expected_demand=380, min_safety_stock=150, incoming_replenishment=180, shipment_delayed=True),
                    ProductInventory(p_cardio[0], p_cardio[1], p_cardio[2], current_stock=320, expected_demand=180, min_safety_stock=100, incoming_replenishment=80, shipment_delayed=False),
                    ProductInventory(p_bearings[0], p_bearings[1], p_bearings[2], current_stock=580, expected_demand=280, min_safety_stock=200, incoming_replenishment=120, shipment_delayed=False),
                ],
                inbound_shipments=[
                    InboundShipment("SHP-CH-01", "WH-A", "Port of Chennai", p_sensors[0], p_sensors[1], 180, "Delayed (+3 Days)", 0.88, "HIGH", True),
                    InboundShipment("SHP-CH-02", "WH-A", "Sri City Hub", p_cardio[0], p_cardio[1], 80, "Tomorrow, 10:00", 0.15, "LOW", False),
                ]
            )
            wh_b = Warehouse(
                id="WH-B", name="Warehouse B", city="Bengaluru", state="Karnataka", capacity_sqft=150000,
                inventory=[
                    # Has ample surplus: 680 - 200 demand - 180 safety = 300 transferable units
                    ProductInventory(p_sensors[0], p_sensors[1], p_sensors[2], current_stock=680, expected_demand=200, min_safety_stock=180, incoming_replenishment=150, shipment_delayed=False),
                    ProductInventory(p_cardio[0], p_cardio[1], p_cardio[2], current_stock=390, expected_demand=170, min_safety_stock=120, incoming_replenishment=90, shipment_delayed=False),
                    ProductInventory(p_bearings[0], p_bearings[1], p_bearings[2], current_stock=700, expected_demand=320, min_safety_stock=220, incoming_replenishment=160, shipment_delayed=False),
                ],
                inbound_shipments=[
                    InboundShipment("SHP-BLR-01", "WH-B", "Hosur Gateway", p_sensors[0], p_sensors[1], 150, "Today, 21:00", 0.18, "LOW", False),
                ]
            )
            wh_c = Warehouse(
                id="WH-C", name="Warehouse C", city="Hyderabad", state="Telangana", capacity_sqft=135000,
                inventory=[
                    # Moderate surplus: 450 - 210 demand - 160 safety = 80 transferable units
                    ProductInventory(p_sensors[0], p_sensors[1], p_sensors[2], current_stock=450, expected_demand=210, min_safety_stock=160, incoming_replenishment=100, shipment_delayed=False),
                    ProductInventory(p_cardio[0], p_cardio[1], p_cardio[2], current_stock=350, expected_demand=160, min_safety_stock=110, incoming_replenishment=80, shipment_delayed=False),
                    ProductInventory(p_bearings[0], p_bearings[1], p_bearings[2], current_stock=650, expected_demand=300, min_safety_stock=200, incoming_replenishment=150, shipment_delayed=False),
                ],
                inbound_shipments=[
                    InboundShipment("SHP-HYD-01", "WH-C", "Shamshabad Cargo Terminal", p_sensors[0], p_sensors[1], 100, "Tomorrow, 14:00 (+1.5 Days)", 0.58, "MODERATE", False),
                ]
            )
            return [wh_a, wh_b, wh_c]

        elif scenario_id == "scenario_3":
            # SCENARIO 3: Multiple Warehouses at Risk (WH-A and WH-C face simultaneous sensor shortages)
            wh_a = Warehouse(
                id="WH-A", name="Warehouse A", city="Chennai", state="Tamil Nadu", capacity_sqft=120000,
                inventory=[
                    # Shortage of 160 units
                    ProductInventory(p_sensors[0], p_sensors[1], p_sensors[2], current_stock=180, expected_demand=340, min_safety_stock=150, incoming_replenishment=150, shipment_delayed=True),
                    ProductInventory(p_cardio[0], p_cardio[1], p_cardio[2], current_stock=310, expected_demand=180, min_safety_stock=100, incoming_replenishment=80, shipment_delayed=False),
                    ProductInventory(p_bearings[0], p_bearings[1], p_bearings[2], current_stock=590, expected_demand=290, min_safety_stock=200, incoming_replenishment=130, shipment_delayed=False),
                ],
                inbound_shipments=[
                    InboundShipment("SHP-CH-01", "WH-A", "Port of Chennai", p_sensors[0], p_sensors[1], 150, "Delayed (+4 Days)", 0.92, "HIGH", True),
                ]
            )
            wh_b = Warehouse(
                id="WH-B", name="Warehouse B", city="Bengaluru", state="Karnataka", capacity_sqft=150000,
                inventory=[
                    # Bengaluru has 250 units surplus: 630 - 200 demand - 180 safety = 250
                    ProductInventory(p_sensors[0], p_sensors[1], p_sensors[2], current_stock=630, expected_demand=200, min_safety_stock=180, incoming_replenishment=120, shipment_delayed=False),
                    ProductInventory(p_cardio[0], p_cardio[1], p_cardio[2], current_stock=380, expected_demand=180, min_safety_stock=120, incoming_replenishment=90, shipment_delayed=False),
                    ProductInventory(p_bearings[0], p_bearings[1], p_bearings[2], current_stock=710, expected_demand=310, min_safety_stock=220, incoming_replenishment=170, shipment_delayed=False),
                ],
                inbound_shipments=[
                    InboundShipment("SHP-BLR-01", "WH-B", "Hosur Gateway", p_sensors[0], p_sensors[1], 120, "Today, 21:00", 0.19, "LOW", False),
                ]
            )
            wh_c = Warehouse(
                id="WH-C", name="Warehouse C", city="Hyderabad", state="Telangana", capacity_sqft=135000,
                inventory=[
                    # Also facing shortage: 170 stock - 310 demand = -140 deficit
                    ProductInventory(p_sensors[0], p_sensors[1], p_sensors[2], current_stock=170, expected_demand=310, min_safety_stock=160, incoming_replenishment=140, shipment_delayed=True),
                    ProductInventory(p_cardio[0], p_cardio[1], p_cardio[2], current_stock=340, expected_demand=170, min_safety_stock=110, incoming_replenishment=80, shipment_delayed=False),
                    ProductInventory(p_bearings[0], p_bearings[1], p_bearings[2], current_stock=640, expected_demand=300, min_safety_stock=200, incoming_replenishment=140, shipment_delayed=False),
                ],
                inbound_shipments=[
                    InboundShipment("SHP-HYD-01", "WH-C", "Shamshabad Cargo Terminal", p_sensors[0], p_sensors[1], 140, "Delayed (+2 Days)", 0.85, "HIGH", True),
                ]
            )
            return [wh_a, wh_b, wh_c]

        else:
            # SCENARIO 4: Insufficient Network Inventory (System-wide stockout)
            wh_a = Warehouse(
                id="WH-A", name="Warehouse A", city="Chennai", state="Tamil Nadu", capacity_sqft=120000,
                inventory=[
                    ProductInventory(p_sensors[0], p_sensors[1], p_sensors[2], current_stock=120, expected_demand=390, min_safety_stock=150, incoming_replenishment=150, shipment_delayed=True),
                    ProductInventory(p_cardio[0], p_cardio[1], p_cardio[2], current_stock=290, expected_demand=200, min_safety_stock=100, incoming_replenishment=70, shipment_delayed=False),
                    ProductInventory(p_bearings[0], p_bearings[1], p_bearings[2], current_stock=550, expected_demand=310, min_safety_stock=200, incoming_replenishment=110, shipment_delayed=False),
                ],
                inbound_shipments=[
                    InboundShipment("SHP-CH-01", "WH-A", "Port of Chennai", p_sensors[0], p_sensors[1], 150, "Delayed (+5 Days)", 0.94, "HIGH", True),
                ]
            )
            wh_b = Warehouse(
                id="WH-B", name="Warehouse B", city="Bengaluru", state="Karnataka", capacity_sqft=150000,
                inventory=[
                    # No surplus: 320 stock - 220 demand - 180 safety = -80 (0 transferable)
                    ProductInventory(p_sensors[0], p_sensors[1], p_sensors[2], current_stock=320, expected_demand=220, min_safety_stock=180, incoming_replenishment=90, shipment_delayed=False),
                    ProductInventory(p_cardio[0], p_cardio[1], p_cardio[2], current_stock=360, expected_demand=190, min_safety_stock=120, incoming_replenishment=80, shipment_delayed=False),
                    ProductInventory(p_bearings[0], p_bearings[1], p_bearings[2], current_stock=680, expected_demand=330, min_safety_stock=220, incoming_replenishment=150, shipment_delayed=False),
                ],
                inbound_shipments=[
                    InboundShipment("SHP-BLR-01", "WH-B", "Hosur Gateway", p_sensors[0], p_sensors[1], 90, "Tomorrow, 14:00", 0.22, "LOW", False),
                ]
            )
            wh_c = Warehouse(
                id="WH-C", name="Warehouse C", city="Hyderabad", state="Telangana", capacity_sqft=135000,
                inventory=[
                    # No surplus: 290 stock - 210 demand - 160 safety = -80 (0 transferable)
                    ProductInventory(p_sensors[0], p_sensors[1], p_sensors[2], current_stock=290, expected_demand=210, min_safety_stock=160, incoming_replenishment=80, shipment_delayed=False),
                    ProductInventory(p_cardio[0], p_cardio[1], p_cardio[2], current_stock=330, expected_demand=180, min_safety_stock=110, incoming_replenishment=70, shipment_delayed=False),
                    ProductInventory(p_bearings[0], p_bearings[1], p_bearings[2], current_stock=620, expected_demand=320, min_safety_stock=200, incoming_replenishment=130, shipment_delayed=False),
                ],
                inbound_shipments=[
                    InboundShipment("SHP-HYD-01", "WH-C", "Shamshabad Cargo Terminal", p_sensors[0], p_sensors[1], 80, "Tomorrow, 11:00", 0.25, "LOW", False),
                ]
            )
            return [wh_a, wh_b, wh_c]

    @staticmethod
    def calculate_inventory_status(item: ProductInventory) -> Tuple[int, int, str]:
        """
        Calculate projected ending stock, shortage, and health status.

        Rules:
            effective_replenishment = 0 if shipment_delayed else incoming_replenishment
            projected_end_stock = current_stock + effective_replenishment - expected_demand
            shortage = max(0, -projected_end_stock)
            safety_deficit = max(0, min_safety_stock - projected_end_stock)
        """
        replenish = 0 if item.shipment_delayed else item.incoming_replenishment
        projected_end = item.current_stock + replenish - item.expected_demand

        shortage = max(0, -projected_end)

        if projected_end <= 0:
            status = "Projected Stockout"  # Red
        elif projected_end < item.min_safety_stock:
            status = "At Risk"             # Orange
        elif projected_end < item.min_safety_stock * 1.25:
            status = "Low Stock"           # Yellow
        else:
            status = "Healthy"             # Green

        return projected_end, shortage, status

    @classmethod
    def evaluate_recovery(cls, warehouses: List[Warehouse]) -> Dict[str, Any]:
        """
        Evaluate and solve multi-warehouse recovery optimization across the network.
        Guarantees:
            1. Source warehouse always retains its min_safety_stock.
            2. Available surplus is strictly tracked so competing shortages cannot double-count surplus.
            3. Ranks feasible options: Inter-warehouse transfer, expedited shipping, or no action.
        """
        # Step 1: Detect all shortages across all warehouses
        shortages: List[Dict[str, Any]] = []
        for wh in warehouses:
            for item in wh.inventory:
                proj_end, shortage_qty, status = cls.calculate_inventory_status(item)
                if shortage_qty > 0 or proj_end < item.min_safety_stock:
                    target_shortage = shortage_qty if shortage_qty > 0 else (item.min_safety_stock - proj_end)
                    shortages.append({
                        "warehouse_id": wh.id,
                        "warehouse_name": wh.name,
                        "city": wh.city,
                        "product_id": item.product_id,
                        "product_name": item.product_name,
                        "current_stock": item.current_stock,
                        "expected_demand": item.expected_demand,
                        "min_safety_stock": item.min_safety_stock,
                        "shortage_qty": target_shortage,
                        "status": status,
                        "unit_penalty": item.unit_cost
                    })

        if not shortages:
            return {
                "requires_recovery": False,
                "message": "Network inventory healthy across all warehouses. No recovery action needed.",
                "shortages_detected": [],
                "options": [],
                "recommendation": None,
                "comparison": None
            }

        # Step 2: Track transferable surplus per warehouse & product (strictly preventing double allocation)
        available_surplus: Dict[Tuple[str, str], int] = {}
        for wh in warehouses:
            for item in wh.inventory:
                surplus = max(0, item.current_stock - item.expected_demand - item.min_safety_stock)
                available_surplus[(wh.id, item.product_id)] = surplus

        options: List[Dict[str, Any]] = []
        allocated_transfers: List[Dict[str, Any]] = []

        total_unmet_baseline = sum(s["shortage_qty"] for s in shortages)
        total_baseline_penalty = sum(s["shortage_qty"] * s["unit_penalty"] for s in shortages)

        # Step 3: Find recovery options for each shortage
        for sht in shortages:
            dest_id = sht["warehouse_id"]
            p_id = sht["product_id"]
            qty_needed = sht["shortage_qty"]

            # Option A & B: Transfer from peer warehouses
            for peer in warehouses:
                if peer.id == dest_id:
                    continue
                surplus = available_surplus.get((peer.id, p_id), 0)
                transit_info = TRANSIT_MATRIX.get((peer.id, dest_id), {"transit_hours": 10, "cost_per_unit": 18.0})

                if surplus > 0:
                    transfer_qty = min(qty_needed, surplus)
                    trans_cost = transfer_qty * transit_info["cost_per_unit"]
                    unmet_remaining = qty_needed - transfer_qty
                    penalty_rem = unmet_remaining * sht["unit_penalty"]
                    total_cost = trans_cost + penalty_rem
                    penalty_saved = (qty_needed - unmet_remaining) * sht["unit_penalty"]
                    net_benefit = penalty_saved - trans_cost

                    options.append({
                        "option_id": f"TRANSFER_{peer.id}_TO_{dest_id}_{p_id}",
                        "type": "INTER_WAREHOUSE_TRANSFER",
                        "source_wh_id": peer.id,
                        "source_city": peer.city,
                        "destination_wh_id": dest_id,
                        "destination_city": sht["city"],
                        "product_id": p_id,
                        "product_name": sht["product_name"],
                        "transfer_quantity": transfer_qty,
                        "surplus_available": surplus,
                        "transit_hours": transit_info["transit_hours"],
                        "transport_cost": round(trans_cost, 2),
                        "shortage_resolved": transfer_qty,
                        "remaining_shortage": unmet_remaining,
                        "total_cost": round(total_cost, 2),
                        "penalty_saved": round(penalty_saved, 2),
                        "net_savings": round(net_benefit, 2),
                        "is_feasible": True,
                        "description": f"Transfer {transfer_qty} units from {peer.city} ({peer.id}) to {sht['city']} ({dest_id}) via road logistics."
                    })

            # Option C: Expedite inbound shipment if delayed
            for wh in warehouses:
                if wh.id == dest_id:
                    for shp in wh.inbound_shipments:
                        if shp.product_id == p_id and shp.is_delayed and shp.expedited_available:
                            exp_qty = min(qty_needed, shp.quantity)
                            exp_cost = exp_qty * shp.expedited_cost_per_unit
                            unmet_rem = qty_needed - exp_qty
                            total_cost = exp_cost + (unmet_rem * sht["unit_penalty"])
                            penalty_saved = exp_qty * sht["unit_penalty"]
                            net_benefit = penalty_saved - exp_cost

                            options.append({
                                "option_id": f"EXPEDITE_{shp.shipment_id}_{dest_id}",
                                "type": "EXPEDITE_INBOUND_SHIPMENT",
                                "source_wh_id": shp.origin_hub,
                                "source_city": shp.origin_hub,
                                "destination_wh_id": dest_id,
                                "destination_city": sht["city"],
                                "product_id": p_id,
                                "product_name": sht["product_name"],
                                "transfer_quantity": exp_qty,
                                "surplus_available": shp.quantity,
                                "transit_hours": 6,
                                "transport_cost": round(exp_cost, 2),
                                "shortage_resolved": exp_qty,
                                "remaining_shortage": unmet_rem,
                                "total_cost": round(total_cost, 2),
                                "penalty_saved": round(penalty_saved, 2),
                                "net_savings": round(net_benefit, 2),
                                "is_feasible": True,
                                "description": f"Expedite incoming shipment {shp.shipment_id} via dedicated air express."
                            })

            # Option D: No Action (baseline reference)
            options.append({
                "option_id": f"NO_ACTION_{dest_id}_{p_id}",
                "type": "NO_ACTION",
                "source_wh_id": "NONE",
                "source_city": "None",
                "destination_wh_id": dest_id,
                "destination_city": sht["city"],
                "product_id": p_id,
                "product_name": sht["product_name"],
                "transfer_quantity": 0,
                "surplus_available": 0,
                "transit_hours": 0,
                "transport_cost": 0.0,
                "shortage_resolved": 0,
                "remaining_shortage": qty_needed,
                "total_cost": round(qty_needed * sht["unit_penalty"], 2),
                "penalty_saved": 0.0,
                "net_savings": 0.0,
                "is_feasible": True,
                "description": f"Take no action; absorb {qty_needed} units unmet demand and disruption penalty."
            })

        # Step 4: Pick optimal plan (Maximum Shortage Avoided, then Minimum Total Cost)
        active_options = [o for o in options if o["type"] != "NO_ACTION"]
        active_options.sort(key=lambda o: (-o["shortage_resolved"], o["total_cost"]))

        best_actions = []
        surplus_pool = copy.deepcopy(available_surplus)
        total_resolved = 0
        total_recovery_cost = 0.0

        for opt in active_options:
            if opt["type"] == "INTER_WAREHOUSE_TRANSFER":
                key = (opt["source_wh_id"], opt["product_id"])
                avail = surplus_pool.get(key, 0)
                if avail >= opt["transfer_quantity"] and opt["transfer_quantity"] > 0:
                    surplus_pool[key] -= opt["transfer_quantity"]
                    best_actions.append(opt)
                    total_resolved += opt["transfer_quantity"]
                    total_recovery_cost += opt["transport_cost"]
            elif opt["type"] == "EXPEDITE_INBOUND_SHIPMENT":
                best_actions.append(opt)
                total_resolved += opt["transfer_quantity"]
                total_recovery_cost += opt["transport_cost"]

        unmet_after = max(0, total_unmet_baseline - total_resolved)
        total_cost_after = total_recovery_cost + (unmet_after * 120.0)
        net_savings = total_baseline_penalty - total_cost_after

        if not best_actions:
            # Network has zero surplus and no expeditable shipments
            recommendation = {
                "status": "UNAVOIDABLE_SHORTAGE",
                "action_type": "NO_RECOVERY_FEASIBLE",
                "headline": "Insufficient Network Surplus: All warehouses operating at or below safety stock threshold.",
                "explanation": "Neither Warehouse B nor Warehouse C holds surplus above their mandatory safety thresholds. Transferring inventory would trigger secondary stockouts.",
                "actions": [],
                "unmet_units": total_unmet_baseline
            }
        else:
            first_action = best_actions[0]
            recommendation = {
                "status": "OPTIMAL_RECOVERY_FOUND",
                "action_type": first_action["type"],
                "headline": f"Execute Inter-Warehouse Logistics Transfer from {first_action['source_city']} to {first_action['destination_city']}"
                if first_action["type"] == "INTER_WAREHOUSE_TRANSFER" else
                f"Expedite Inbound Replenishment to {first_action['destination_city']}",
                "explanation": (
                    f"Transferring {first_action['transfer_quantity']} units of {first_action['product_name']} "
                    f"from {first_action['source_city']} ({first_action['source_wh_id']}) resolves the projected deficit. "
                    f"{first_action['source_city']} retains its mandatory safety stock. Transit window: {first_action['transit_hours']} hrs."
                ),
                "actions": best_actions,
                "unmet_units": unmet_after
            }

        comparison = {
            "baseline_unmet_units": int(total_unmet_baseline),
            "recovery_unmet_units": int(unmet_after),
            "shortage_units_avoided": int(total_resolved),
            "estimated_recovery_cost": round(total_recovery_cost, 2),
            "baseline_shortage_penalty": round(total_baseline_penalty, 2),
            "post_recovery_shortage_penalty": round(unmet_after * 120.0, 2),
            "post_recovery_total_cost": round(total_cost_after, 2),
            "estimated_net_savings": round(net_savings, 2)
        }

        return {
            "requires_recovery": True,
            "shortages_detected": shortages,
            "options": options,
            "recommendation": recommendation,
            "comparison": comparison
        }

    @classmethod
    def get_network_state(
        cls,
        scenario_id: str = "scenario_1",
        selected_wh_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Assemble the full unified network state for the frontend dashboard.
        """
        warehouses = cls.get_base_scenario(scenario_id)
        recovery_eval = cls.evaluate_recovery(warehouses)

        # Aggregate network-level metrics dynamically
        total_network_inventory = 0
        total_network_demand = 0
        total_safety_stock = 0
        total_delayed_shipments = 0
        warehouses_at_risk_count = 0
        products_facing_shortage_set = set()

        wh_payloads: List[Dict[str, Any]] = []

        for wh in warehouses:
            wh_inventory_items = []
            wh_has_risk = False

            for item in wh.inventory:
                proj_end, shortage, status = cls.calculate_inventory_status(item)
                total_network_inventory += item.current_stock
                total_network_demand += item.expected_demand
                total_safety_stock += item.min_safety_stock

                if status in ["At Risk", "Projected Stockout"]:
                    wh_has_risk = True
                    products_facing_shortage_set.add(item.product_id)

                surplus_avail = max(0, item.current_stock - item.expected_demand - item.min_safety_stock)

                wh_inventory_items.append({
                    "product_id": item.product_id,
                    "product_name": item.product_name,
                    "category": item.category,
                    "current_stock": item.current_stock,
                    "expected_demand": item.expected_demand,
                    "min_safety_stock": item.min_safety_stock,
                    "incoming_replenishment": item.incoming_replenishment,
                    "shipment_delayed": item.shipment_delayed,
                    "projected_ending_stock": proj_end,
                    "projected_shortage": shortage,
                    "available_transferable_stock": surplus_avail,
                    "status": status,
                    "status_color": "red" if status == "Projected Stockout" else (
                        "orange" if status == "At Risk" else (
                            "yellow" if status == "Low Stock" else "green"
                        )
                    )
                })

            for shp in wh.inbound_shipments:
                if shp.is_delayed:
                    total_delayed_shipments += 1

            if wh_has_risk:
                warehouses_at_risk_count += 1

            wh_payloads.append({
                "id": wh.id,
                "name": wh.name,
                "city": wh.city,
                "state": wh.state,
                "capacity_sqft": wh.capacity_sqft,
                "has_risk": wh_has_risk,
                "inventory": wh_inventory_items,
                "inbound_shipments": [asdict(s) for s in wh.inbound_shipments]
            })

        # Filter by selected warehouse if specified (and not 'ALL')
        active_wh_data = wh_payloads
        if selected_wh_id and selected_wh_id.upper() != "ALL":
            active_wh_data = [w for w in wh_payloads if w["id"] == selected_wh_id.upper()]

        comparison = recovery_eval.get("comparison") or {
            "baseline_unmet_units": 0,
            "recovery_unmet_units": 0,
            "shortage_units_avoided": 0,
            "estimated_recovery_cost": 0.0,
            "baseline_shortage_penalty": 0.0,
            "post_recovery_shortage_penalty": 0.0,
            "post_recovery_total_cost": 0.0,
            "estimated_net_savings": 0.0
        }

        network_summary = {
            "scenario_id": scenario_id,
            "selected_filter": selected_wh_id or "ALL",
            "total_inventory_units": int(total_network_inventory),
            "total_expected_demand": int(total_network_demand),
            "warehouses_at_risk": int(warehouses_at_risk_count),
            "shipments_delayed_count": int(total_delayed_shipments),
            "products_facing_shortage_count": len(products_facing_shortage_set),
            "projected_unmet_demand_baseline": comparison["baseline_unmet_units"],
            "projected_unmet_demand_after_recovery": comparison["recovery_unmet_units"],
            "total_estimated_recovery_cost": comparison["estimated_recovery_cost"],
            "estimated_net_savings": comparison["estimated_net_savings"]
        }

        return {
            "network_summary": network_summary,
            "warehouses": active_wh_data,
            "all_warehouses_metadata": [{"id": w["id"], "name": w["name"], "city": w["city"]} for w in wh_payloads],
            "recovery_evaluation": recovery_eval
        }
