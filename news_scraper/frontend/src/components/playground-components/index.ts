import { EventImpactTimeline } from './EventImpactTimeline';
import { NewsSentimentStream } from './NewsSentimentStream';
import { ExposureWheel } from './ExposureWheel';
import { RadarChart } from './RadarChart';
import { ScenarioComparison } from './ScenarioComparison';

// --- New imports based on schemas ---
import { AlertsInsights } from './AlertsInsights';
import { HoldingsDashboard } from './HoldingsDashboard';
import { RateYieldDashboard } from './RateYieldDashboard';
import { AIInsightCard } from './AIInsightCard';
import { CorrelationMatrixFXCom } from './CorrelationMatrixFXCom';
import { PolicyDifferentialDashboard } from './PolicyDifferentialDashboard';
import { SentimentVolatilityChart } from './SentimentVolatilityChart';
import { CorrelationMatrix } from './CorrelationMatrix';
import { OptimizationHeatmap } from './OptimizationHeatmap';
import { TopMovers } from './TopMovers';
import { AttributionBySector } from './AttributionBySector';
import { RiskSensitivityTable } from './risk-sensitivity';
import { RiskMap } from './risk-map';
import { LiquidationCostTable } from './liquidation-cost-table';
import { ComplianceStatusTable } from './compilance-status';
import { CreditSpreadsChart } from './credit-spreads-chart';
import { ALMMatrixTable } from './alm-matrix-table';
import { CashFlowForecastChart } from './cash-flow-forecast-chart';
import { LiquidityBufferGauge } from './liquidity-buffer-gauge';
import { CapitalEfficiencyChart } from './capital-efficiency-chart';
import { OptimizationCard } from './optimization-card';
import { StressTestResults } from './stress-test-results';
import { ComparisonView } from './comparison-view';
import { RiskAllocationChart } from './risk-allocation-chart';
import { AdjustWeightSlider } from './adjust-weight-slider';
import { ScenarioAdjustmentSlider } from './scenario-adjustment-slider';
import { LiquidityProfileChart } from './liquidity-profile-chart';
import { AllocationVsPolicyTable } from './allocation-vs-policy-table';
import { TradeLog } from './TradeLogPage';


// ---------------- FINAL REGISTRY ----------------
export const ComponentMap: Record<string, React.FC<any>> = {
  
  // Version A components
  AlertsInsights,
  AlertInsights: AlertsInsights, // Alias for schema compatibility
  EventImpactTimeline,
  ExposureWheel,
  HoldingsDashboard,

  // Version B components
  NewsSentimentStream,
  RateYieldDashboard,
  AIInsightCard,
  AiInsightCard: AIInsightCard, // Alias for schema compatibility
  CorrelationMatrixFXCom,

  // Version C components
  PolicyDifferentialDashboard,
  SentimentVolatilityChart,
  CorrelationMatrix,
  OptimizationHeatmap,
  OptimizationHeatMap: OptimizationHeatmap, // Alias for schema compatibility
  TopMovers,
  AttributionBySector,

  // Version D components
  RiskSensitivityTable,
  RiskMap,
  LiquidationCostTable,
  ComplianceStatusTable,
  CreditSpreadsChart,
  ALMMatrixTable,
  LiquidityProfileChart,
  AllocationVsPolicyTable,

  // Version E components
  CashFlowForecastChart,
  LiquidityBufferGauge,
  CapitalEfficiencyChart,
  OptimizationCard,
  StressTestResults,
  ComparisonView,
  RiskAllocationChart,
  AdjustWeightSlider,
  ScenarioAdjustmentSlider,

  // Existing
  RadarChart,
  ScenarioComparison,
  TradeLog,
  TradeLogPage: TradeLog // Alias for schema compatibility
};
