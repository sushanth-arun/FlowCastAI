import React, { useState, useEffect } from 'react';
import Sidebar from './components/Sidebar';
import Topbar from './components/Topbar';
import KpiCards from './components/KpiCards';
import RecommendationCard from './components/RecommendationCard';
import InventoryImpactCard from './components/InventoryImpactCard';
import ShipmentTable from './components/ShipmentTable';
import WhatIfSimulator from './components/WhatIfSimulator';
import ScenarioModal from './components/ScenarioModal';

// Dedicated Tab Views
import ShipmentsView from './components/views/ShipmentsView';
import InventoryView from './components/views/InventoryView';
import DecisionsView from './components/views/DecisionsView';
import ReportsView from './components/views/ReportsView';

// API & Simulation Engine
import {
  checkBackendHealth,
  getOverviewKPIs,
  getShipments,
  getWarehouses,
  runScenarioSimulation
} from './services/api';

export default function App() {
  const [activeTab, setActiveTab] = useState('overview');
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedShipmentId, setSelectedShipmentId] = useState('SHP-8821');
  const [isScenarioModalOpen, setIsScenarioModalOpen] = useState(false);

  // Core Data State
  const [kpis, setKpis] = useState({});
  const [shipments, setShipments] = useState([]);
  const [warehouses, setWarehouses] = useState([]);
  const [optimizationResult, setOptimizationResult] = useState(null);
  const [isSimulating, setIsSimulating] = useState(false);
  const [isBackendLive, setIsBackendLive] = useState(false);

  // Initial load
  useEffect(() => {
    async function initData() {
      const [liveStatus, loadedKpis, loadedShipments, loadedWarehouses, initialOpt] = await Promise.all([
        checkBackendHealth(),
        getOverviewKPIs(),
        getShipments(),
        getWarehouses(),
        runScenarioSimulation()
      ]);

      setIsBackendLive(liveStatus);
      setKpis(loadedKpis);
      setShipments(loadedShipments);
      setWarehouses(loadedWarehouses);
      setOptimizationResult(initialOpt);
    }

    initData();
  }, []);

  // Handler for running simulation
  const handleRunSimulation = async (params) => {
    setIsSimulating(true);
    try {
      const [result] = await Promise.all([
        runScenarioSimulation(params),
        new Promise((resolve) => setTimeout(resolve, 280))
      ]);
      setOptimizationResult(result);
    } catch (err) {
      console.error('Simulation error:', err);
    } finally {
      setIsSimulating(false);
    }
  };

  // Handler for selecting shipment
  const handleSelectShipment = (id) => {
    setSelectedShipmentId(id);
    // If selecting focal shipment SHP-8821, reset or align scenario
    if (id === 'SHP-8821') {
      handleRunSimulation({
        delayDays: 4.0,
        dailyDemand: 10,
        whBTransferUnitCost: 8,
        shortagePenaltyPerUnit: 100
      });
    }
  };

  return (
    <div className="app-layout">
      {/* 1. Left Dark Navy Sidebar */}
      <Sidebar
        activeTab={activeTab}
        setActiveTab={setActiveTab}
        atRiskCount={kpis.atRiskShipments || 6}
      />

      {/* 2. Main Wrapper */}
      <div className="main-wrapper">
        {/* Top Navigation */}
        <Topbar
          activeTab={activeTab}
          searchQuery={searchQuery}
          setSearchQuery={setSearchQuery}
          isBackendLive={isBackendLive}
          onNotificationClick={() => {
            setActiveTab('shipments');
            setSelectedShipmentId('SHP-8821');
          }}
        />

        {/* 3. Page Workspace */}
        <main className="workspace">
          {activeTab === 'overview' && (
            <div>
              {/* Main Heading */}
              <div className="page-header">
                <div>
                  <h1 className="page-title">FlowCast AI — Supply Chain Overview</h1>
                  <p className="page-subtitle">
                    Predict disruptions. Understand inventory impact. Recommend recovery actions.
                  </p>
                </div>
              </div>

              {/* Section 1: 4 Summary KPI Cards */}
              <KpiCards
                kpis={kpis}
                focalShortageCost={optimizationResult?.baselineTotalCost || 4000}
              />

              {/* Decision Workspace: Recommendation + Inventory Impact */}
              <div className="decision-grid">
                {/* Section 4: AI Recovery Recommendation */}
                <RecommendationCard
                  optimizationResult={optimizationResult}
                  onCompareScenarios={() => setIsScenarioModalOpen(true)}
                />

                {/* Section 3: Inventory Impact & 3-Warehouse Balances */}
                <InventoryImpactCard
                  warehouses={warehouses}
                  optimizationResult={optimizationResult}
                />
              </div>

              {/* Section 2: Shipment Risk Overview Table */}
              <ShipmentTable
                shipments={shipments}
                selectedShipmentId={selectedShipmentId}
                onSelectShipment={handleSelectShipment}
                searchQuery={searchQuery}
              />

              {/* Section 5: What-If Interactive Simulator */}
              <WhatIfSimulator
                currentParams={optimizationResult?.inputParams}
                onRunSimulation={handleRunSimulation}
                isSimulating={isSimulating}
                optimizationResult={optimizationResult}
              />
            </div>
          )}

          {activeTab === 'shipments' && (
            <ShipmentsView
              shipments={shipments}
              selectedShipmentId={selectedShipmentId}
              onSelectShipment={handleSelectShipment}
              searchQuery={searchQuery}
            />
          )}

          {activeTab === 'inventory' && (
            <InventoryView
              warehouses={warehouses}
              optimizationResult={optimizationResult}
            />
          )}

          {activeTab === 'recommendations' && (
            <DecisionsView
              optimizationResult={optimizationResult}
              onCompareScenarios={() => setIsScenarioModalOpen(true)}
              onRunSimulation={handleRunSimulation}
              isSimulating={isSimulating}
            />
          )}

          {activeTab === 'reports' && (
            <ReportsView
              optimizationResult={optimizationResult}
            />
          )}
        </main>
      </div>

      {/* Scenario Comparison Modal */}
      <ScenarioModal
        isOpen={isScenarioModalOpen}
        onClose={() => setIsScenarioModalOpen(false)}
        options={optimizationResult?.options}
        recommendedId={optimizationResult?.recommendedOption?.id}
      />
    </div>
  );
}
