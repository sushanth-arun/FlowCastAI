import React, { useState, useEffect } from 'react';
import { Sliders, RefreshCw, Zap, AlertCircle } from 'lucide-react';

export default function WhatIfSimulator({
  currentParams,
  onRunSimulation,
  isSimulating,
  optimizationResult
}) {
  const [params, setParams] = useState({
    delayDays: currentParams?.delayDays || 4.0,
    dailyDemand: currentParams?.dailyDemand || 10,
    whBTransferUnitCost: currentParams?.whBTransferUnitCost || 8,
    shortagePenaltyPerUnit: currentParams?.shortagePenaltyPerUnit || 100
  });

  // Keep local params in sync if external scenario changes
  useEffect(() => {
    if (currentParams) {
      setParams({
        delayDays: currentParams.delayDays ?? 4.0,
        dailyDemand: currentParams.dailyDemand ?? 10,
        whBTransferUnitCost: currentParams.whBTransferUnitCost ?? 8,
        shortagePenaltyPerUnit: currentParams.shortagePenaltyPerUnit ?? 100
      });
    }
  }, [currentParams]);

  const handleChange = (field, value) => {
    setParams((prev) => ({
      ...prev,
      [field]: Number(value)
    }));
  };

  const handleReset = () => {
    const defaults = {
      delayDays: 4.0,
      dailyDemand: 10,
      whBTransferUnitCost: 8,
      shortagePenaltyPerUnit: 100
    };
    setParams(defaults);
    onRunSimulation(defaults);
  };

  const handleSubmit = (e) => {
    if (e && e.preventDefault) e.preventDefault();
    onRunSimulation(params);
  };

  const rec = optimizationResult?.recommendedOption;
  const baselineCost = optimizationResult?.baselineTotalCost || 4000;

  // Check if current slider values differ from evaluated simulation
  const hasPendingChanges =
    currentParams &&
    (params.delayDays !== currentParams.delayDays ||
      params.dailyDemand !== currentParams.dailyDemand ||
      params.whBTransferUnitCost !== currentParams.whBTransferUnitCost ||
      params.shortagePenaltyPerUnit !== currentParams.shortagePenaltyPerUnit);

  return (
    <div className="simulator-card">
      <div className="sim-header">
        <div>
          <div className="card-heading" style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
            <Sliders size={20} color="#3B6FF5" />
            Interactive "What-If" Disruption Stress Simulator
          </div>
          <div className="card-subheading">
            Adjust operational variables below, then click "Run Simulation" to recalculate the optimal recovery strategy
          </div>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
          {hasPendingChanges && (
            <span style={{ fontSize: '0.74rem', color: '#D97706', fontWeight: 600, display: 'flex', alignItems: 'center', gap: 4 }}>
              <AlertCircle size={13} />
              Unapplied changes
            </span>
          )}

          <button
            type="button"
            className="btn-secondary"
            onClick={handleReset}
            disabled={isSimulating}
            title="Reset to default baseline scenario"
          >
            <RefreshCw size={14} />
            Reset Defaults
          </button>

          <button
            type="button"
            className="btn-primary"
            onClick={handleSubmit}
            disabled={isSimulating}
            style={hasPendingChanges ? { boxShadow: '0 0 14px rgba(59, 111, 245, 0.45)' } : {}}
          >
            <Zap size={14} />
            {isSimulating ? 'Computing Optimal...' : 'Run Simulation'}
          </button>
        </div>
      </div>

      <form onSubmit={handleSubmit}>
        <div className="sim-controls-grid">
          {/* Control 1: Shipment Delay Days */}
          <div className="control-group">
            <div className="control-label-row">
              <span>Predicted Delay Duration</span>
              <span className="control-val">+{params.delayDays} Days</span>
            </div>
            <input
              type="range"
              min="1"
              max="10"
              step="0.5"
              value={params.delayDays}
              onChange={(e) => handleChange('delayDays', e.target.value)}
              className="slider-input"
            />
            <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.68rem', color: '#94A3B8' }}>
              <span>1 Day (Minor)</span>
              <span>10 Days (Severe)</span>
            </div>
          </div>

          {/* Control 2: Daily Demand Surge */}
          <div className="control-group">
            <div className="control-label-row">
              <span>Warehouse A Demand Rate</span>
              <span className="control-val">{params.dailyDemand} Units / Day</span>
            </div>
            <input
              type="range"
              min="5"
              max="25"
              step="1"
              value={params.dailyDemand}
              onChange={(e) => handleChange('dailyDemand', e.target.value)}
              className="slider-input"
            />
            <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.68rem', color: '#94A3B8' }}>
              <span>5u/d (Low)</span>
              <span>25u/d (High Surge)</span>
            </div>
          </div>

          {/* Control 3: Transfer Unit Cost */}
          <div className="control-group">
            <div className="control-label-row">
              <span>Warehouse B Unit Transfer Cost</span>
              <span className="control-val">${params.whBTransferUnitCost} / Unit</span>
            </div>
            <input
              type="range"
              min="4"
              max="25"
              step="1"
              value={params.whBTransferUnitCost}
              onChange={(e) => handleChange('whBTransferUnitCost', e.target.value)}
              className="slider-input"
            />
            <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.68rem', color: '#94A3B8' }}>
              <span>$4 (Discount)</span>
              <span>$25 (Surge Freight)</span>
            </div>
          </div>

          {/* Control 4: Stockout Penalty Rate */}
          <div className="control-group">
            <div className="control-label-row">
              <span>Unmet Stockout Penalty SLA</span>
              <span className="control-val">${params.shortagePenaltyPerUnit} / Unmet Unit</span>
            </div>
            <input
              type="range"
              min="40"
              max="250"
              step="10"
              value={params.shortagePenaltyPerUnit}
              onChange={(e) => handleChange('shortagePenaltyPerUnit', e.target.value)}
              className="slider-input"
            />
            <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.68rem', color: '#94A3B8' }}>
              <span>$40 (Standard)</span>
              <span>$250 (Critical OEM Contract)</span>
            </div>
          </div>
        </div>
      </form>

      {/* Dynamic Simulation Result Strip */}
      {rec && (
        <div className="sim-result-strip">
          <div className="sim-summary-text">
            <span>Simulated Outcome: </span>
            <strong>{rec.title}</strong>{' '}
            <span>| Total Action Cost: <strong>${rec.totalCost.toLocaleString()}</strong></span>{' '}
            <span>vs Inaction Baseline: <strong style={{ color: '#EF4444' }}>${baselineCost.toLocaleString()}</strong></span>
          </div>

          <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
            <span style={{ fontSize: '0.78rem', color: '#10B981', fontWeight: 700, background: '#ECFDF5', padding: '4px 10px', borderRadius: 6, border: '1px solid #A7F3D0' }}>
              +${rec.savingsVsBaseline.toLocaleString()} Net Preserved Profit ({rec.percentReduction}%)
            </span>
          </div>
        </div>
      )}
    </div>
  );
}
