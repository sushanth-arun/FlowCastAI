"""
FlowCast AI - 3-Warehouse Supply Chain Decision Support System Dashboard.
Served at GET / by FastAPI Orchestrator.
Supports:
- Interconnected 3-Warehouse Network: Chennai (WH-A), Bengaluru (WH-B), Hyderabad (WH-C).
- Multi-warehouse selector (All Warehouses, Chennai, Bengaluru, Hyderabad).
- 4 Simulation Scenarios (Normal, Chennai Disruption, Multi-Warehouse Risk, Insufficient Inventory).
- Dynamic Network KPIs, Warehouse Inventory Monitoring, and Inbound Shipment Disruption Tracking.
- Multi-Warehouse Recovery Solver & Side-by-side Baseline vs. Recovery Financial Impact Comparison.
- Preserved Module 1, Module 2, and Module 3 ML telemetry test panels.
"""

DASHBOARD_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>FlowCast AI - 3-Warehouse Supply Chain Decision Support System</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Outfit:wght@400;600;700;800&display=swap" rel="stylesheet">
  <style>
    :root {
      --bg-primary: #0a0e17;
      --bg-card: rgba(18, 24, 38, 0.85);
      --bg-input: #121826;
      --border-color: rgba(255, 255, 255, 0.08);
      --border-focus: #38bdf8;
      --accent-cyan: #06b6d4;
      --accent-indigo: #6366f1;
      --accent-emerald: #10b981;
      --accent-amber: #f59e0b;
      --accent-rose: #f43f5e;
      --text-main: #f1f5f9;
      --text-muted: #94a3b8;
    }

    * { box-sizing: border-box; margin: 0; padding: 0; }
    body {
      font-family: 'Inter', -apple-system, sans-serif;
      background: var(--bg-primary);
      color: var(--text-main);
      min-height: 100vh;
      display: flex;
      flex-direction: column;
      background-image: 
        radial-gradient(circle at 15% 10%, rgba(99, 102, 241, 0.12) 0%, transparent 40%),
        radial-gradient(circle at 85% 90%, rgba(6, 182, 212, 0.12) 0%, transparent 40%);
    }

    /* Header */
    header {
      background: rgba(15, 23, 42, 0.85);
      backdrop-filter: blur(14px);
      border-bottom: 1px solid var(--border-color);
      padding: 1.1rem 2rem;
      display: flex;
      align-items: center;
      justify-content: space-between;
      position: sticky;
      top: 0;
      z-index: 50;
    }

    .brand-group {
      display: flex;
      align-items: center;
      gap: 1rem;
    }

    .logo-badge {
      background: linear-gradient(135deg, #06b6d4, #6366f1);
      width: 42px;
      height: 42px;
      border-radius: 10px;
      display: flex;
      align-items: center;
      justify-content: center;
      font-family: 'Outfit', sans-serif;
      font-weight: 800;
      font-size: 1.2rem;
      color: #fff;
      box-shadow: 0 4px 14px rgba(6, 182, 212, 0.35);
    }

    .brand-title {
      font-family: 'Outfit', sans-serif;
      font-weight: 700;
      font-size: 1.35rem;
      letter-spacing: -0.02em;
      background: linear-gradient(to right, #fff, #94a3b8);
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
    }

    .brand-sub {
      font-size: 0.76rem;
      color: var(--text-muted);
      text-transform: uppercase;
      letter-spacing: 0.08em;
    }

    .nav-links {
      display: flex;
      gap: 0.8rem;
      align-items: center;
    }

    .badge-status {
      display: inline-flex;
      align-items: center;
      gap: 0.4rem;
      background: rgba(16, 185, 129, 0.12);
      border: 1px solid rgba(16, 185, 129, 0.3);
      color: #34d399;
      font-size: 0.8rem;
      font-weight: 500;
      padding: 0.35rem 0.8rem;
      border-radius: 9999px;
    }

    .badge-status::before {
      content: '';
      width: 7px;
      height: 7px;
      background: #10b981;
      border-radius: 50%;
      box-shadow: 0 0 8px #10b981;
    }

    .btn-link {
      background: rgba(255, 255, 255, 0.05);
      border: 1px solid var(--border-color);
      color: var(--text-main);
      padding: 0.4rem 0.9rem;
      border-radius: 8px;
      font-size: 0.85rem;
      text-decoration: none;
      transition: all 0.2s;
    }
    .btn-link:hover {
      background: rgba(255, 255, 255, 0.12);
      border-color: rgba(255, 255, 255, 0.2);
    }

    /* Main Container */
    main {
      flex: 1;
      max-width: 1400px;
      margin: 0 auto;
      padding: 1.8rem;
      width: 100%;
    }

    /* Navigation Tabs */
    .tab-bar {
      display: flex;
      gap: 0.6rem;
      border-bottom: 1px solid var(--border-color);
      margin-bottom: 1.8rem;
      padding-bottom: 0.5rem;
      overflow-x: auto;
    }

    .tab-btn {
      background: none;
      border: none;
      color: var(--text-muted);
      font-family: 'Inter', sans-serif;
      font-size: 0.92rem;
      font-weight: 600;
      padding: 0.6rem 1.1rem;
      border-radius: 8px;
      cursor: pointer;
      transition: all 0.2s;
      white-space: nowrap;
      display: flex;
      align-items: center;
      gap: 0.5rem;
    }

    .tab-btn:hover {
      color: var(--text-main);
      background: rgba(255, 255, 255, 0.04);
    }

    .tab-btn.active {
      color: #38bdf8;
      background: rgba(56, 189, 248, 0.1);
      border-bottom: 2px solid #38bdf8;
    }

    /* View Panels */
    .view-panel {
      display: none;
      animation: fadeIn 0.3s ease-in-out;
    }
    .view-panel.active {
      display: block;
    }

    @keyframes fadeIn {
      from { opacity: 0; transform: translateY(6px); }
      to { opacity: 1; transform: translateY(0); }
    }

    /* Control Toolbar (Warehouse & Scenario Selectors) */
    .control-toolbar {
      background: var(--bg-card);
      border: 1px solid var(--border-color);
      border-radius: 14px;
      padding: 1.2rem 1.6rem;
      margin-bottom: 1.8rem;
      display: flex;
      flex-wrap: wrap;
      justify-content: space-between;
      align-items: center;
      gap: 1.2rem;
      box-shadow: 0 4px 20px rgba(0, 0, 0, 0.2);
    }

    .control-group {
      display: flex;
      align-items: center;
      gap: 0.8rem;
    }

    .control-label {
      font-size: 0.85rem;
      font-weight: 600;
      color: var(--text-muted);
      text-transform: uppercase;
      letter-spacing: 0.05em;
    }

    .btn-filter-pill {
      background: rgba(255, 255, 255, 0.05);
      border: 1px solid var(--border-color);
      color: var(--text-muted);
      font-size: 0.85rem;
      font-weight: 500;
      padding: 0.45rem 0.95rem;
      border-radius: 9999px;
      cursor: pointer;
      transition: all 0.2s;
    }
    .btn-filter-pill:hover {
      background: rgba(255, 255, 255, 0.1);
      color: #fff;
    }
    .btn-filter-pill.active {
      background: rgba(56, 189, 248, 0.15);
      color: #38bdf8;
      border-color: #38bdf8;
      font-weight: 600;
    }

    .select-ctrl {
      background: var(--bg-input);
      border: 1px solid var(--border-color);
      color: var(--text-main);
      padding: 0.5rem 0.9rem;
      border-radius: 8px;
      font-size: 0.88rem;
      outline: none;
      cursor: pointer;
    }
    .select-ctrl:focus {
      border-color: var(--border-focus);
    }

    /* KPI Grid */
    .kpi-grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(210px, 1fr));
      gap: 1.2rem;
      margin-bottom: 2rem;
    }

    .kpi-card {
      background: var(--bg-card);
      border: 1px solid var(--border-color);
      border-radius: 14px;
      padding: 1.3rem;
      display: flex;
      flex-direction: column;
      gap: 0.4rem;
      box-shadow: 0 4px 18px rgba(0, 0, 0, 0.15);
      position: relative;
      overflow: hidden;
    }

    .kpi-card::before {
      content: '';
      position: absolute;
      top: 0; left: 0; right: 0;
      height: 3px;
      background: linear-gradient(90deg, #06b6d4, #6366f1);
    }

    .kpi-title {
      font-size: 0.78rem;
      color: var(--text-muted);
      text-transform: uppercase;
      letter-spacing: 0.05em;
      font-weight: 600;
    }

    .kpi-value {
      font-family: 'Outfit', sans-serif;
      font-size: 1.7rem;
      font-weight: 700;
      color: #fff;
    }

    .kpi-sub {
      font-size: 0.78rem;
      color: var(--text-muted);
    }

    /* Section Cards */
    .section-card {
      background: var(--bg-card);
      border: 1px solid var(--border-color);
      border-radius: 16px;
      padding: 1.8rem;
      margin-bottom: 2rem;
      box-shadow: 0 8px 24px rgba(0, 0, 0, 0.2);
    }

    .section-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 1.3rem;
      flex-wrap: wrap;
      gap: 0.8rem;
    }

    .section-title {
      font-family: 'Outfit', sans-serif;
      font-size: 1.25rem;
      font-weight: 700;
      color: #fff;
      display: flex;
      align-items: center;
      gap: 0.6rem;
    }

    /* Tables */
    .table-container {
      width: 100%;
      overflow-x: auto;
    }

    table {
      width: 100%;
      border-collapse: collapse;
      font-size: 0.88rem;
      text-align: left;
    }

    th {
      background: rgba(255, 255, 255, 0.03);
      color: var(--text-muted);
      font-weight: 600;
      padding: 0.85rem 1rem;
      border-bottom: 1px solid var(--border-color);
      white-space: nowrap;
      text-transform: uppercase;
      font-size: 0.75rem;
      letter-spacing: 0.05em;
    }

    td {
      padding: 0.9rem 1rem;
      border-bottom: 1px solid rgba(255, 255, 255, 0.04);
      color: var(--text-main);
      white-space: nowrap;
    }

    tr:hover td {
      background: rgba(255, 255, 255, 0.02);
    }

    /* Status Badges */
    .badge-pill {
      font-size: 0.75rem;
      font-weight: 700;
      padding: 0.28rem 0.65rem;
      border-radius: 6px;
      letter-spacing: 0.04em;
      display: inline-block;
    }

    .status-healthy { background: rgba(16, 185, 129, 0.15); color: #34d399; border: 1px solid rgba(16, 185, 129, 0.3); }
    .status-low-stock { background: rgba(245, 158, 11, 0.15); color: #fbbf24; border: 1px solid rgba(245, 158, 11, 0.3); }
    .status-at-risk { background: rgba(249, 115, 22, 0.15); color: #fb923c; border: 1px solid rgba(249, 115, 22, 0.3); }
    .status-stockout { background: rgba(244, 63, 94, 0.15); color: #f43f5e; border: 1px solid rgba(244, 63, 94, 0.3); }

    /* Recovery Recommendation Banner */
    .recommendation-banner {
      background: linear-gradient(135deg, rgba(99, 102, 241, 0.12), rgba(6, 182, 212, 0.12));
      border: 1px solid rgba(56, 189, 248, 0.35);
      border-radius: 14px;
      padding: 1.6rem;
      margin-bottom: 1.6rem;
      display: flex;
      flex-direction: column;
      gap: 0.8rem;
      position: relative;
    }

    .banner-top {
      display: flex;
      justify-content: space-between;
      align-items: center;
      flex-wrap: wrap;
      gap: 0.8rem;
    }

    .headline-text {
      font-family: 'Outfit', sans-serif;
      font-size: 1.2rem;
      font-weight: 700;
      color: #fff;
    }

    .explanation-text {
      font-size: 0.9rem;
      color: #cbd5e1;
      line-height: 1.5;
    }

    /* Comparison Grid */
    .comparison-grid {
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 1.4rem;
      margin-top: 1rem;
    }

    @media (max-width: 900px) {
      .comparison-grid { grid-template-columns: 1fr; }
    }

    .comp-box {
      background: rgba(0, 0, 0, 0.25);
      border: 1px solid var(--border-color);
      border-radius: 12px;
      padding: 1.2rem;
    }

    .comp-box.baseline {
      border-left: 4px solid #f43f5e;
    }

    .comp-box.recommended {
      border-left: 4px solid #10b981;
    }

    .comp-title {
      font-size: 0.8rem;
      text-transform: uppercase;
      letter-spacing: 0.05em;
      font-weight: 700;
      margin-bottom: 0.8rem;
    }
    .comp-box.baseline .comp-title { color: #f43f5e; }
    .comp-box.recommended .comp-title { color: #10b981; }

    .comp-row {
      display: flex;
      justify-content: space-between;
      padding: 0.45rem 0;
      font-size: 0.85rem;
      border-bottom: 1px solid rgba(255, 255, 255, 0.04);
    }
    .comp-row:last-child { border-bottom: none; }
    .comp-val-bold { font-weight: 700; color: #fff; }

    /* Module 1/2/3 Split Panels (Preserved) */
    .module-split {
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 2rem;
    }
    @media (max-width: 960px) {
      .module-split { grid-template-columns: 1fr; }
    }

    .form-grid {
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 1rem;
    }
    .full-width { grid-column: span 2; }

    .field-group {
      display: flex;
      flex-direction: column;
      gap: 0.35rem;
    }
    .field-group label {
      font-size: 0.8rem;
      font-weight: 500;
      color: var(--text-muted);
    }

    .input-ctrl {
      background: var(--bg-input);
      border: 1px solid var(--border-color);
      color: var(--text-main);
      padding: 0.65rem 0.85rem;
      border-radius: 8px;
      font-size: 0.9rem;
      outline: none;
    }
    .input-ctrl:focus {
      border-color: var(--border-focus);
    }

    .btn-submit {
      width: 100%;
      margin-top: 1.4rem;
      background: linear-gradient(135deg, #06b6d4, #6366f1);
      border: none;
      color: #fff;
      font-weight: 600;
      font-size: 0.95rem;
      padding: 0.85rem;
      border-radius: 10px;
      cursor: pointer;
      display: flex;
      align-items: center;
      justify-content: center;
      gap: 0.5rem;
      transition: all 0.2s;
    }
    .btn-submit:hover { opacity: 0.92; transform: translateY(-1px); }

    .json-box {
      background: #060911;
      border: 1px solid var(--border-color);
      border-radius: 10px;
      padding: 1rem;
      font-family: 'SFMono-Regular', Consolas, monospace;
      font-size: 0.8rem;
      color: #93c5fd;
      max-height: 240px;
      overflow-y: auto;
      white-space: pre-wrap;
    }

    /* Footer */
    footer {
      border-top: 1px solid var(--border-color);
      padding: 1.5rem;
      text-align: center;
      font-size: 0.85rem;
      color: var(--text-muted);
      background: rgba(10, 14, 23, 0.85);
    }
  </style>
</head>
<body>

  <header>
    <div class="brand-group">
      <div class="logo-badge">FC</div>
      <div>
        <div class="brand-title">FlowCast AI &bull; IBM Z Datathon 2026</div>
        <div class="brand-sub">Multi-Warehouse Decision Support & Inventory Recovery System</div>
      </div>
    </div>
    <div class="nav-links">
      <span class="badge-status">3 Warehouses Interconnected</span>
      <a href="/docs" target="_blank" class="btn-link">Swagger /docs</a>
      <a href="/healthz" target="_blank" class="btn-link">GET /healthz</a>
    </div>
  </header>

  <main>
    <!-- Navigation Tabs -->
    <div class="tab-bar">
      <button class="tab-btn active" onclick="switchNavTab('network')">
        <span>🌐</span> 3-Warehouse Control Center & Recovery Engine
      </button>
      <button class="tab-btn" onclick="switchNavTab('m1')">
        <span>⚙️</span> Module 1: Telemetry Asset Health
      </button>
      <button class="tab-btn" onclick="switchNavTab('m2')">
        <span>🚚</span> Module 2: Logistics Delays (DataCo ML)
      </button>
      <button class="tab-btn" onclick="switchNavTab('m3')">
        <span>📦</span> Module 3: Inventory Demand (DataCo ML)
      </button>
    </div>

    <!-- ============================================================== -->
    <!-- PRIMARY 3-WAREHOUSE NETWORK VIEW -->
    <!-- ============================================================== -->
    <div id="panel-network" class="view-panel active">

      <!-- Control Toolbar: Warehouse Selector + Scenario Simulation -->
      <div class="control-toolbar">
        <div class="control-group">
          <span class="control-label">Warehouse Focus:</span>
          <button class="btn-filter-pill active" onclick="selectWarehouse('ALL', this)">All Warehouses (Network)</button>
          <button class="btn-filter-pill" onclick="selectWarehouse('WH-A', this)">Chennai (WH-A)</button>
          <button class="btn-filter-pill" onclick="selectWarehouse('WH-B', this)">Bengaluru (WH-B)</button>
          <button class="btn-filter-pill" onclick="selectWarehouse('WH-C', this)">Hyderabad (WH-C)</button>
        </div>

        <div class="control-group">
          <span class="control-label">Simulate Scenario:</span>
          <select id="scenario_select" class="select-ctrl" onchange="onScenarioChange()">
            <option value="scenario_1">Scenario 1: Normal Operations (Balanced Network)</option>
            <option value="scenario_2" selected>Scenario 2: Chennai Shipment Disruption (Inbound Delayed)</option>
            <option value="scenario_3">Scenario 3: Multiple Warehouses at Risk (Simultaneous Deficits)</option>
            <option value="scenario_4">Scenario 4: Insufficient Network Inventory (System-Wide Deficit)</option>
          </select>
        </div>
      </div>

      <!-- Network Overview KPI Grid -->
      <div class="kpi-grid">
        <div class="kpi-card">
          <div class="kpi-title">Total Network Inventory</div>
          <div id="kpi_total_inv" class="kpi-value">-- units</div>
          <div id="kpi_demand_sub" class="kpi-sub">Total Demand: -- units</div>
        </div>
        <div class="kpi-card">
          <div class="kpi-title">Warehouses At Risk</div>
          <div id="kpi_wh_risk" class="kpi-value" style="color: #fbbf24">--</div>
          <div class="kpi-sub">Out of 3 interconnected hubs</div>
        </div>
        <div class="kpi-card">
          <div class="kpi-title">Delayed Inbound Shipments</div>
          <div id="kpi_delayed_ships" class="kpi-value" style="color: #f43f5e">--</div>
          <div class="kpi-sub">Elevated arrival disruption risk</div>
        </div>
        <div class="kpi-card">
          <div class="kpi-title">Products Facing Shortage</div>
          <div id="kpi_shortage_products" class="kpi-value" style="color: #fb923c">--</div>
          <div class="kpi-sub">Stockout / safety stock deficit</div>
        </div>
        <div class="kpi-card">
          <div class="kpi-title">Unmet Demand (Avoided)</div>
          <div id="kpi_shortage_avoided" class="kpi-value" style="color: #34d399">-- units</div>
          <div id="kpi_baseline_unmet" class="kpi-sub">Baseline Deficit: -- units</div>
        </div>
        <div class="kpi-card">
          <div class="kpi-title">Estimated Net Savings</div>
          <div id="kpi_net_savings" class="kpi-value" style="color: #38bdf8">$ --</div>
          <div class="kpi-sub">After freight recovery costs</div>
        </div>
      </div>

      <!-- Multi-Warehouse Recovery Recommendation Engine -->
      <div class="section-card">
        <div class="section-header">
          <div class="section-title">
            <span>⚡</span> FlowCast Recovery Recommendation Engine
          </div>
          <span id="rec_status_badge" class="badge-pill status-healthy">ANALYZING</span>
        </div>

        <div id="rec_banner" class="recommendation-banner">
          <div class="banner-top">
            <div id="rec_headline" class="headline-text">Calculating optimal recovery plan...</div>
            <span id="rec_action_pill" class="badge-pill status-healthy">RECOMMENDATION</span>
          </div>
          <div id="rec_explanation" class="explanation-text">...</div>
        </div>

        <!-- Baseline vs. Recovery Financial Comparison Matrix -->
        <div class="comparison-grid">
          <div class="comp-box baseline">
            <div class="comp-title">Baseline: No Recovery Action</div>
            <div class="comp-row">
              <span>Projected Unmet Units:</span>
              <span id="comp_base_unmet" class="comp-val-bold">-- units</span>
            </div>
            <div class="comp-row">
              <span>Shortage Penalty Rate:</span>
              <span>$120.00 / unmet unit</span>
            </div>
            <div class="comp-row">
              <span>Total Disruption Penalty:</span>
              <span id="comp_base_penalty" class="comp-val-bold">$ --</span>
            </div>
            <div class="comp-row">
              <span>Recovery Transport Cost:</span>
              <span>$0.00</span>
            </div>
            <div class="comp-row">
              <span>Total Baseline Cost:</span>
              <span id="comp_base_total" class="comp-val-bold" style="color: #f43f5e">$ --</span>
            </div>
          </div>

          <div class="comp-box recommended">
            <div class="comp-title">FlowCast Recommended Recovery Action</div>
            <div class="comp-row">
              <span>Shortage Units Avoided:</span>
              <span id="comp_units_avoided" class="comp-val-bold" style="color: #34d399">-- units</span>
            </div>
            <div class="comp-row">
              <span>Remaining Unmet Demand:</span>
              <span id="comp_rec_unmet">-- units</span>
            </div>
            <div class="comp-row">
              <span>Estimated Logistics / Transfer Cost:</span>
              <span id="comp_rec_cost">--</span>
            </div>
            <div class="comp-row">
              <span>Post-Recovery Total Cost:</span>
              <span id="comp_rec_total">--</span>
            </div>
            <div class="comp-row">
              <span>Net Financial Savings:</span>
              <span id="comp_rec_savings" class="comp-val-bold" style="color: #38bdf8; font-size: 1.05rem">$ --</span>
            </div>
          </div>
        </div>

        <!-- Feasible Recovery Options Table -->
        <div style="margin-top: 1.6rem">
          <div style="font-weight: 600; font-size: 0.95rem; margin-bottom: 0.8rem; color: #cbd5e1">
            Evaluated Recovery Options Comparison
          </div>
          <div class="table-container">
            <table>
              <thead>
                <tr>
                  <th>Option ID</th>
                  <th>Action Type</th>
                  <th>Source Hub</th>
                  <th>Destination Hub</th>
                  <th>Product</th>
                  <th>Transfer Qty</th>
                  <th>Transit Window</th>
                  <th>Recovery Cost</th>
                  <th>Remaining Shortage</th>
                  <th>Net Savings</th>
                </tr>
              </thead>
              <tbody id="recovery_options_tbody">
                <!-- Dynamically populated -->
              </tbody>
            </table>
          </div>
        </div>
      </div>

      <!-- Warehouse Inventory Monitoring -->
      <div class="section-card">
        <div class="section-header">
          <div class="section-title">
            <span>📦</span> Warehouse Inventory Health & Stock Balances
          </div>
          <div style="font-size: 0.82rem; color: var(--text-muted)">
            Real-time multi-echelon stock levels & projected deficits
          </div>
        </div>
        <div class="table-container">
          <table>
            <thead>
              <tr>
                <th>Warehouse</th>
                <th>Product ID & Name</th>
                <th>Category</th>
                <th>Current Stock</th>
                <th>Daily Demand</th>
                <th>Safety Stock</th>
                <th>Inbound Shipment</th>
                <th>Projected End Stock</th>
                <th>Transferable Surplus</th>
                <th>Status</th>
              </tr>
            </thead>
            <tbody id="inventory_tbody">
              <!-- Dynamically populated -->
            </tbody>
          </table>
        </div>
      </div>

      <!-- Inbound Shipment Disruption Monitoring -->
      <div class="section-card">
        <div class="section-header">
          <div class="section-title">
            <span>🚚</span> Inbound Replenishment & Shipment Disruption Monitoring
          </div>
          <div style="font-size: 0.82rem; color: var(--text-muted)">
            Telemetry & DataCo ML Delay Risk Indicators (Simulated Demo Stream)
          </div>
        </div>
        <div class="table-container">
          <table>
            <thead>
              <tr>
                <th>Shipment ID</th>
                <th>Destination Hub</th>
                <th>Origin Terminal</th>
                <th>Product</th>
                <th>Quantity</th>
                <th>ETA / Status</th>
                <th>Delay Risk Score</th>
                <th>Impact on Stock</th>
                <th>Severity</th>
              </tr>
            </thead>
            <tbody id="shipments_tbody">
              <!-- Dynamically populated -->
            </tbody>
          </table>
        </div>
      </div>

    </div>

    <!-- ============================================================== -->
    <!-- PRESERVED MODULE 1 PANEL (Telemetry Asset Health) -->
    <!-- ============================================================== -->
    <div id="panel-m1" class="view-panel">
      <div class="module-split">
        <div class="section-card">
          <div class="section-header">
            <div class="section-title">IoT Telemetry & Operational Parameters</div>
          </div>
          <form id="form-m1" onsubmit="event.preventDefault(); submitModule1();">
            <div class="form-grid">
              <div class="field-group">
                <label>Asset ID</label>
                <input id="m1_asset_id" class="input-ctrl" value="A0001" required>
              </div>
              <div class="field-group">
                <label>Facility Location</label>
                <input id="m1_location" class="input-ctrl" value="Lake Davidland" required>
              </div>
              <div class="field-group">
                <label>Temperature (°C)</label>
                <input id="m1_temp" type="number" step="0.01" class="input-ctrl" value="32.34" required>
              </div>
              <div class="field-group">
                <label>Vibration Metric</label>
                <input id="m1_vib" type="number" step="0.01" class="input-ctrl" value="3.99" required>
              </div>
              <div class="field-group">
                <label>Condition Score (0-100)</label>
                <input id="m1_cond" type="number" step="0.1" class="input-ctrl" value="67.39" required>
              </div>
              <div class="field-group">
                <label>Resource Utilization (%)</label>
                <input id="m1_util" type="number" step="0.1" class="input-ctrl" value="87.04" required>
              </div>
              <div class="field-group">
                <label>Delivery Efficiency (%)</label>
                <input id="m1_eff" type="number" step="0.1" class="input-ctrl" value="79.99" required>
              </div>
              <div class="field-group">
                <label>Downtime Hours</label>
                <input id="m1_down" type="number" step="0.1" class="input-ctrl" value="3.22" required>
              </div>
              <div class="field-group">
                <label>Inventory Level</label>
                <select id="m1_inv" class="input-ctrl">
                  <option value="Low">Low</option>
                  <option value="Medium" selected>Medium</option>
                  <option value="High">High</option>
                </select>
              </div>
              <div class="field-group">
                <label>Logistics Cost ($)</label>
                <input id="m1_cost" type="number" step="0.1" class="input-ctrl" value="5148.45" required>
              </div>
              <div class="field-group">
                <label>Last Maintenance</label>
                <input id="m1_maint" class="input-ctrl" value="28-09-2023" required>
              </div>
              <div class="field-group">
                <label>Timestamp</label>
                <input id="m1_ts" class="input-ctrl" value="13-09-2024 19:31" required>
              </div>
            </div>
            <button type="submit" class="btn-submit">
              <span>⚡</span> Run Module 1 ONNX Inference
            </button>
          </form>
        </div>

        <div class="section-card">
          <div class="section-header">
            <div class="section-title">ONNX Inference Output</div>
            <span id="m1_status_pill" class="badge-pill status-healthy">READY</span>
          </div>
          <div style="display: flex; flex-direction: column; gap: 1rem">
            <div class="kpi-card" style="padding: 1rem">
              <div class="kpi-title">Predicted Efficiency Class</div>
              <div id="m1_pred_name" class="kpi-value" style="font-size: 1.3rem">Optimal Efficiency</div>
              <div id="m1_conf_val" class="kpi-sub">Confidence: 98.6%</div>
            </div>
            <div>
              <div class="kpi-title" style="margin-bottom: 0.5rem">Raw Response Payload</div>
              <div id="m1_json_box" class="json-box">Run inference to view payload...</div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- ============================================================== -->
    <!-- PRESERVED MODULE 2 PANEL (Logistics Delays) -->
    <!-- ============================================================== -->
    <div id="panel-m2" class="view-panel">
      <div class="module-split">
        <div class="section-card">
          <div class="section-header">
            <div class="section-title">Logistics & Order Shipping Attributes</div>
          </div>
          <form id="form-m2" onsubmit="event.preventDefault(); submitModule2();">
            <div class="form-grid">
              <div class="field-group">
                <label>Shipping Mode</label>
                <select id="m2_mode" class="input-ctrl">
                  <option value="Standard Class" selected>Standard Class</option>
                  <option value="First Class">First Class</option>
                  <option value="Second Class">Second Class</option>
                  <option value="Same Day">Same Day</option>
                </select>
              </div>
              <div class="field-group">
                <label>Destination Market</label>
                <select id="m2_market" class="input-ctrl">
                  <option value="LATAM" selected>LATAM</option>
                  <option value="Pacific Asia">Pacific Asia</option>
                  <option value="USCA">USCA</option>
                  <option value="Africa">Africa</option>
                  <option value="Europe">Europe</option>
                </select>
              </div>
              <div class="field-group">
                <label>Order Region</label>
                <input id="m2_region" class="input-ctrl" value="South America" required>
              </div>
              <div class="field-group">
                <label>Order Item Quantity</label>
                <input id="m2_qty" type="number" step="1" class="input-ctrl" value="2" required>
              </div>
              <div class="field-group full-width">
                <label>Sales Volume ($)</label>
                <input id="m2_sales" type="number" step="0.1" class="input-ctrl" value="250.0" required>
              </div>
            </div>
            <button type="submit" class="btn-submit">
              <span>🚚</span> Run Module 2 ONNX Inference
            </button>
          </form>
        </div>

        <div class="section-card">
          <div class="section-header">
            <div class="section-title">Delay Risk Classification</div>
            <span id="m2_status_pill" class="badge-pill status-healthy">READY</span>
          </div>
          <div style="display: flex; flex-direction: column; gap: 1rem">
            <div class="kpi-card" style="padding: 1rem">
              <div class="kpi-title">Delay Prediction</div>
              <div id="m2_pred_name" class="kpi-value" style="font-size: 1.3rem">ON_TIME</div>
              <div id="m2_conf_val" class="kpi-sub">Delay Probability: 30.2%</div>
            </div>
            <div>
              <div class="kpi-title" style="margin-bottom: 0.5rem">Raw Response Payload</div>
              <div id="m2_json_box" class="json-box">Run inference to view payload...</div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- ============================================================== -->
    <!-- PRESERVED MODULE 3 PANEL (Inventory Demand) -->
    <!-- ============================================================== -->
    <div id="panel-m3" class="view-panel">
      <div class="module-split">
        <div class="section-card">
          <div class="section-header">
            <div class="section-title">Product Catalog & Demand Profiling</div>
          </div>
          <form id="form-m3" onsubmit="event.preventDefault(); submitModule3();">
            <div class="form-grid">
              <div class="field-group">
                <label>Department Name</label>
                <select id="m3_dept" class="input-ctrl">
                  <option value="Fitness" selected>Fitness</option>
                  <option value="Apparel">Apparel</option>
                  <option value="Golf">Golf</option>
                  <option value="Footwear">Footwear</option>
                  <option value="Outdoors">Outdoors</option>
                </select>
              </div>
              <div class="field-group">
                <label>Category Name</label>
                <input id="m3_cat" class="input-ctrl" value="Cardio Equipment" required>
              </div>
              <div class="field-group">
                <label>Product Price ($)</label>
                <input id="m3_price" type="number" step="0.01" class="input-ctrl" value="129.99" required>
              </div>
              <div class="field-group">
                <label>Discount Rate (0.0 - 1.0)</label>
                <input id="m3_disc" type="number" step="0.01" class="input-ctrl" value="0.10" required>
              </div>
            </div>
            <button type="submit" class="btn-submit">
              <span>📦</span> Run Module 3 ONNX Inference
            </button>
          </form>
        </div>

        <div class="section-card">
          <div class="section-header">
            <div class="section-title">Stockout & Demand Projection</div>
            <span id="m3_status_pill" class="badge-pill status-healthy">READY</span>
          </div>
          <div style="display: flex; flex-direction: column; gap: 1rem">
            <div class="kpi-card" style="padding: 1rem">
              <div class="kpi-title">Stockout Status</div>
              <div id="m3_pred_name" class="kpi-value" style="font-size: 1.3rem">IN_STOCK_STABLE</div>
              <div id="m3_demand_val" class="kpi-sub">Estimated Demand: 1.0 units</div>
            </div>
            <div>
              <div class="kpi-title" style="margin-bottom: 0.5rem">Raw Response Payload</div>
              <div id="m3_json_box" class="json-box">Run inference to view payload...</div>
            </div>
          </div>
        </div>
      </div>
    </div>

  </main>

  <footer>
    FlowCast AI &bull; IBM Z Datathon 2026 &bull; Multi-Warehouse Decision Support &bull; Powered by ONNX Runtime & FastAPI
  </footer>

  <script>
    let activeWarehouseFilter = 'ALL';

    function switchNavTab(tabId) {
      document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
      document.querySelectorAll('.view-panel').forEach(p => p.classList.remove('active'));
      event.currentTarget.classList.add('active');
      document.getElementById('panel-' + tabId).classList.add('active');
    }

    function selectWarehouse(whId, btnEl) {
      document.querySelectorAll('.btn-filter-pill').forEach(b => b.classList.remove('active'));
      btnEl.classList.add('active');
      activeWarehouseFilter = whId;
      fetchNetworkState();
    }

    function onScenarioChange() {
      fetchNetworkState();
    }

    async function fetchNetworkState() {
      const scenario = document.getElementById('scenario_select').value;
      const url = `/api/v1/network/state?scenario=${scenario}&warehouse=${activeWarehouseFilter}`;

      try {
        const res = await fetch(url);
        const data = await res.json();
        renderDashboard(data);
      } catch (err) {
        console.error('Failed to fetch network state:', err);
      }
    }

    function renderDashboard(data) {
      const summary = data.network_summary;
      const rec = data.recovery_evaluation.recommendation;
      const comp = data.recovery_evaluation.comparison;
      const options = data.recovery_evaluation.options || [];

      // 1. Render KPIs
      document.getElementById('kpi_total_inv').innerText = summary.total_inventory_units.toLocaleString() + ' units';
      document.getElementById('kpi_demand_sub').innerText = 'Total Expected Demand: ' + summary.total_expected_demand.toLocaleString() + ' units';
      document.getElementById('kpi_wh_risk').innerText = summary.warehouses_at_risk + ' / 3 Hubs';
      document.getElementById('kpi_delayed_ships').innerText = summary.shipments_delayed_count;
      document.getElementById('kpi_shortage_products').innerText = summary.products_facing_shortage_count + ' Products';
      document.getElementById('kpi_shortage_avoided').innerText = comp.shortage_units_avoided + ' units';
      document.getElementById('kpi_baseline_unmet').innerText = 'Baseline Deficit: ' + comp.baseline_unmet_units + ' units';
      document.getElementById('kpi_net_savings').innerText = '$' + comp.estimated_net_savings.toLocaleString();

      // 2. Render Recommendation Banner
      const statusBadge = document.getElementById('rec_status_badge');
      const actionPill = document.getElementById('rec_action_pill');
      const recHeadline = document.getElementById('rec_headline');
      const recExpl = document.getElementById('rec_explanation');

      if (!rec || rec.status === 'NO_RECOVERY_NEEDED') {
        statusBadge.className = 'badge-pill status-healthy';
        statusBadge.innerText = 'HEALTHY NETWORK';
        actionPill.className = 'badge-pill status-healthy';
        actionPill.innerText = 'NO ACTION NEEDED';
        recHeadline.innerText = 'Network Inventory Operating at Optimal Balance';
        recExpl.innerText = 'All three warehouses (Chennai, Bengaluru, Hyderabad) maintain healthy stocks exceeding demand and required safety thresholds. No inter-warehouse transfer or expedited shipping required.';
      } else if (rec.status === 'UNAVOIDABLE_SHORTAGE') {
        statusBadge.className = 'badge-pill status-stockout';
        statusBadge.innerText = 'CRITICAL DEFICIT';
        actionPill.className = 'badge-pill status-stockout';
        actionPill.innerText = 'INSUFFICIENT SURPLUS';
        recHeadline.innerText = rec.headline;
        recExpl.innerText = rec.explanation;
      } else {
        statusBadge.className = 'badge-pill status-at-risk';
        statusBadge.innerText = 'RECOVERY ACTIVE';
        actionPill.className = 'badge-pill status-healthy';
        actionPill.innerText = rec.action_type.replace(/_/g, ' ');
        recHeadline.innerText = rec.headline;
        recExpl.innerText = rec.explanation;
      }

      // 3. Render Financial Comparison Matrix
      document.getElementById('comp_base_unmet').innerText = comp.baseline_unmet_units + ' units';
      document.getElementById('comp_base_penalty').innerText = '$' + comp.baseline_shortage_penalty.toLocaleString();
      document.getElementById('comp_base_total').innerText = '$' + comp.baseline_shortage_penalty.toLocaleString();

      document.getElementById('comp_units_avoided').innerText = comp.shortage_units_avoided + ' units';
      document.getElementById('comp_rec_unmet').innerText = comp.recovery_unmet_units + ' units';
      document.getElementById('comp_rec_cost').innerText = '$' + comp.estimated_recovery_cost.toLocaleString();
      document.getElementById('comp_rec_total').innerText = '$' + comp.post_recovery_total_cost.toLocaleString();
      document.getElementById('comp_rec_savings').innerText = '$' + comp.estimated_net_savings.toLocaleString();

      // 4. Render Evaluated Options Table
      const optTbody = document.getElementById('recovery_options_tbody');
      optTbody.innerHTML = '';
      if (options.length === 0) {
        optTbody.innerHTML = '<tr><td colspan="10" style="text-align: center; color: var(--text-muted)">No shortages detected in the network.</td></tr>';
      } else {
        options.forEach(opt => {
          const tr = document.createElement('tr');
          const isRec = rec && rec.actions && rec.actions.some(a => a.option_id === opt.option_id);
          if (isRec) tr.style.background = 'rgba(56, 189, 248, 0.08)';

          tr.innerHTML = `
            <td><code>${opt.option_id}</code> ${isRec ? '<span class="badge-pill status-healthy" style="font-size: 0.65rem">OPTIMAL</span>' : ''}</td>
            <td><strong>${opt.type.replace(/_/g, ' ')}</strong></td>
            <td>${opt.source_city}</td>
            <td>${opt.destination_city}</td>
            <td>${opt.product_name}</td>
            <td><strong>${opt.transfer_quantity}</strong></td>
            <td>${opt.transit_hours > 0 ? opt.transit_hours + ' hrs' : 'N/A'}</td>
            <td>$${opt.transport_cost.toFixed(2)}</td>
            <td>${opt.remaining_shortage} units</td>
            <td style="color: ${opt.net_savings > 0 ? '#34d399' : '#94a3b8'}; font-weight: 600">$${opt.net_savings.toFixed(2)}</td>
          `;
          optTbody.appendChild(tr);
        });
      }

      // 5. Render Inventory Table
      const invTbody = document.getElementById('inventory_tbody');
      invTbody.innerHTML = '';
      data.warehouses.forEach(wh => {
        wh.inventory.forEach(item => {
          const tr = document.createElement('tr');
          let statusClass = 'status-healthy';
          if (item.status === 'Projected Stockout') statusClass = 'status-stockout';
          else if (item.status === 'At Risk') statusClass = 'status-at-risk';
          else if (item.status === 'Low Stock') statusClass = 'status-low-stock';

          tr.innerHTML = `
            <td><strong>${wh.city}</strong> <span style="font-size: 0.75rem; color: var(--text-muted)">(${wh.id})</span></td>
            <td>${item.product_name} <br><span style="font-size: 0.75rem; color: var(--text-muted)">${item.product_id}</span></td>
            <td>${item.category}</td>
            <td><strong>${item.current_stock}</strong></td>
            <td>${item.expected_demand}</td>
            <td>${item.min_safety_stock}</td>
            <td>${item.incoming_replenishment} ${item.shipment_delayed ? '<span style="color: #f43f5e">(Delayed)</span>' : '<span style="color: #34d399">(On Time)</span>'}</td>
            <td style="font-weight: 700; color: ${item.projected_ending_stock < item.min_safety_stock ? '#f43f5e' : '#f1f5f9'}">${item.projected_ending_stock}</td>
            <td style="color: ${item.available_transferable_stock > 0 ? '#38bdf8' : '#94a3b8'}">${item.available_transferable_stock} units</td>
            <td><span class="badge-pill ${statusClass}">${item.status.toUpperCase()}</span></td>
          `;
          invTbody.appendChild(tr);
        });
      });

      // 6. Render Shipments Table
      const shpTbody = document.getElementById('shipments_tbody');
      shpTbody.innerHTML = '';
      data.warehouses.forEach(wh => {
        wh.inbound_shipments.forEach(shp => {
          const tr = document.createElement('tr');
          let sevClass = 'status-healthy';
          if (shp.delay_severity === 'HIGH') sevClass = 'status-stockout';
          else if (shp.delay_severity === 'MODERATE') sevClass = 'status-at-risk';

          tr.innerHTML = `
            <td><code>${shp.shipment_id}</code></td>
            <td>${wh.city} (${wh.id})</td>
            <td>${shp.origin_hub}</td>
            <td>${shp.product_name}</td>
            <td><strong>${shp.quantity} units</strong></td>
            <td>${shp.expected_arrival}</td>
            <td>${(shp.delay_risk_score * 100).toFixed(0)}% <span style="font-size: 0.7rem; color: var(--text-muted)">[DataCo ML]</span></td>
            <td>${shp.is_delayed ? '<span style="color: #f43f5e">Depletes Safety Stock</span>' : '<span style="color: #34d399">On Schedule</span>'}</td>
            <td><span class="badge-pill ${sevClass}">${shp.delay_severity} RISK</span></td>
          `;
          shpTbody.appendChild(tr);
        });
      });
    }

    // Module 1 Post Handler
    async function submitModule1() {
      const payload = {
        Asset_ID: document.getElementById('m1_asset_id').value,
        Location: document.getElementById('m1_location').value,
        Temperature: parseFloat(document.getElementById('m1_temp').value),
        Vibration: parseFloat(document.getElementById('m1_vib').value),
        Last_Maintenance: document.getElementById('m1_maint').value,
        Condition_Score: parseFloat(document.getElementById('m1_cond').value),
        Resource_Utilization: parseFloat(document.getElementById('m1_util').value),
        Delivery_Efficiency: parseFloat(document.getElementById('m1_eff').value),
        Downtime_Hours: parseFloat(document.getElementById('m1_down').value),
        Inventory_Level: document.getElementById('m1_inv').value,
        Logistics_Cost: parseFloat(document.getElementById('m1_cost').value),
        Timestamp: document.getElementById('m1_ts').value
      };

      try {
        const res = await fetch('/api/v1/health', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(payload)
        });
        const data = await res.json();
        document.getElementById('m1_json_box').innerText = JSON.stringify(data, null, 2);
        document.getElementById('m1_pred_name').innerText = data.classification_name;
        document.getElementById('m1_conf_val').innerText = 'Confidence: ' + (data.confidence * 100).toFixed(1) + '%';
        const pill = document.getElementById('m1_status_pill');
        pill.className = 'badge-pill ' + (data.flag_failure_risk ? 'status-stockout' : 'status-healthy');
        pill.innerText = data.risk_severity + ' RISK';
      } catch (err) {
        document.getElementById('m1_json_box').innerText = 'Error: ' + err.message;
      }
    }

    // Module 2 Post Handler
    async function submitModule2() {
      const payload = {
        Shipping_Mode: document.getElementById('m2_mode').value,
        Market: document.getElementById('m2_market').value,
        Order_Region: document.getElementById('m2_region').value,
        Order_Item_Quantity: parseFloat(document.getElementById('m2_qty').value),
        Sales: parseFloat(document.getElementById('m2_sales').value)
      };

      try {
        const res = await fetch('/api/v1/delays', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(payload)
        });
        const data = await res.json();
        document.getElementById('m2_json_box').innerText = JSON.stringify(data, null, 2);
        document.getElementById('m2_pred_name').innerText = data.delay_prediction_label;
        document.getElementById('m2_conf_val').innerText = 'Delay Probability: ' + (data.probabilities.late_risk_prob * 100).toFixed(1) + '%';
        const pill = document.getElementById('m2_status_pill');
        pill.className = 'badge-pill ' + (data.late_delivery_risk === 1 ? 'status-stockout' : 'status-healthy');
        pill.innerText = data.delay_severity + ' DELAY RISK';
      } catch (err) {
        document.getElementById('m2_json_box').innerText = 'Error: ' + err.message;
      }
    }

    // Module 3 Post Handler
    async function submitModule3() {
      const payload = {
        Department_Name: document.getElementById('m3_dept').value,
        Category_Name: document.getElementById('m3_cat').value,
        Product_Price: parseFloat(document.getElementById('m3_price').value),
        Order_Item_Discount_Rate: parseFloat(document.getElementById('m3_disc').value)
      };

      try {
        const res = await fetch('/api/v1/stockout', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(payload)
        });
        const data = await res.json();
        document.getElementById('m3_json_box').innerText = JSON.stringify(data, null, 2);
        document.getElementById('m3_pred_name').innerText = data.stockout_risk_status;
        document.getElementById('m3_demand_val').innerText = 'Estimated Demand: ' + data.estimated_demand_quantity.toFixed(1) + ' units';
        const pill = document.getElementById('m3_status_pill');
        pill.className = 'badge-pill ' + (data.stockout_risk_label === 1 ? 'status-stockout' : 'status-healthy');
        pill.innerText = data.stockout_risk_status;
      } catch (err) {
        document.getElementById('m3_json_box').innerText = 'Error: ' + err.message;
      }
    }

    // Initial load
    window.addEventListener('DOMContentLoaded', () => {
      fetchNetworkState();
    });
  </script>
</body>
</html>
"""
