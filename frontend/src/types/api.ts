/** TypeScript types matching backend Pydantic schemas — per PRD §05 */

export interface Asset {
  id: string;
  tenant_id: string;
  name: string;
  therapeutic_area: string | null;
  modality: string | null;
  indication: string | null;
  us_list_price: number | null;
  us_net_share: number | null;
  launch_year: number | null;
  peak_year: number | null;
  loe_year: number | null;
  cogs_percent: number;
  discount_rate: number;
  us_patient_population: number | null;
  ex_us_patient_population: number | null;
  peak_capture_rate: number;
  part_b_share: number;
  ramp_years: number;
  is_sample: boolean;
  sample_origin: string | null;
  created_at: string;
  updated_at: string;
  archived_at: string | null;
}

export interface AssetCreate {
  name: string;
  therapeutic_area?: string | null;
  modality?: string | null;
  indication?: string | null;
  us_list_price?: number | null;
  us_net_share?: number | null;
  launch_year?: number | null;
  peak_year?: number | null;
  loe_year?: number | null;
  cogs_percent?: number | null;
  discount_rate?: number | null;
  us_patient_population?: number | null;
  ex_us_patient_population?: number | null;
  peak_capture_rate?: number | null;
  part_b_share?: number | null;
  ramp_years?: number | null;
}

export type AssetUpdate = Partial<AssetCreate> & {
  expected_updated_at?: string | null;
  force_override?: boolean;
};

export interface CountryData {
  id: string;
  country_code: string;
  list_price: number | null;
  net_price: number | null;
  volume: number | null;
  launched: boolean;
  launch_year: number | null;
  withdrawn: boolean;
  g2n_ratio: number | null;
  g2n_time_series: Record<string, number> | null;
  updated_at: string;
}

export interface GenerousConfig {
  active: boolean;
  year: number | null;
  medicaid_share: number;
}

export interface GuardConfig {
  active: boolean;
  year: number | null;
  submit_method_ii: boolean;
  phase_in: number | null;
}

export interface GlobeConfig {
  active: boolean;
  year: number | null;
  submit_method_ii: boolean;
  phase_in: number | null;
}

export interface RegulationsConfig {
  generous: GenerousConfig;
  guard: GuardConfig;
  globe: GlobeConfig;
}

export interface LeversConfig {
  withdrawals: string[];
  price_floors: Record<string, number>;
  delayed_launches: Record<string, number>;
  de_opt_in: boolean;
  gr_clawback_stress: boolean;
}

export interface MonteCarloResult {
  samples_n: number;
  mean: number;
  p05: number;
  p50: number;
  p95: number;
  range: number;
  sigma_input: number;
}

export interface Scenario {
  id: string;
  tenant_id: string;
  asset_id: string;
  name: string;
  description: string | null;
  is_baseline: boolean;
  regulations: RegulationsConfig;
  levers: LeversConfig;
  cascade_config: Record<string, unknown>;
  created_at: string;
  updated_at: string;
  archived_at: string | null;
}

export interface YearlyBreakdown {
  year: number;
  us_revenue: number;
  ex_us_revenue: number;
  total_net: number;
  discounted: number;
}

export interface SimulationResult {
  simulation_id: string;
  engine_version: string;
  computed_at: string;
  npv: number;
  peak_revenue: number | null;
  method_i_value: number | null;
  method_i_anchor: string | null;
  method_ii_value: number | null;
  applicable_benchmark: number | null;
  per_unit_rebate: number | null;
  effective_us_net: number | null;
  cascade_iterations: number | null;
  cascade_converged: boolean | null;
  final_prices: Record<string, number>;
  yearly_breakdown: YearlyBreakdown[];
  monte_carlo_result: unknown | null;
}

export interface SimulateResponse {
  simulation_id: string;
  engine_version: string;
  computed_at: string;
  computed_in_ms: number;
  results: SimulationResult;
}

export interface Page<T> {
  items: T[];
  next_cursor: string | null;
}

export interface AnchorCountry {
  country: string;
  country_name: string;
  nominal: number;
  ppp: number;
  adjusted: number;
}

export interface AnchorAnalysis {
  model: string;
  anchor: AnchorCountry;
  second: AnchorCountry | null;
  benchmark: number;
  anchor_gap: number;
  anchor_gap_pct: number;
  is_non_obvious_anchor: boolean;
  nominal_lowest: AnchorCountry | null;
  ringfence_recommendation: string;
  all_ranked: AnchorCountry[];
}

export interface CountryDataInput {
  list_price?: number | null;
  net_price?: number | null;
  volume?: number | null;
  launched?: boolean;
  launch_year?: number | null;
  withdrawn?: boolean;
  g2n_ratio?: number | null;
  g2n_time_series?: Record<string, number> | null;
  expected_updated_at?: string | null;
  force_override?: boolean;
}

export interface ScenarioCreate {
  name: string;
  description?: string;
  is_baseline?: boolean;
  regulations?: Partial<RegulationsConfig>;
  levers?: Partial<LeversConfig>;
  cascade_config?: Record<string, unknown>;
  country_data?: Array<CountryDataInput & { country_code: string }>;
}

export type ScenarioUpdate = Partial<ScenarioCreate> & {
  expected_updated_at?: string | null;
  force_override?: boolean;
};

export interface ScenarioDuplicate {
  new_name: string;
}

export interface AssetDuplicate {
  new_name: string;
}

export interface OptimizerRecommendation {
  type: string;
  title: string;
  target: string;
  rationale: string;
  estimated_impact: number | null;
  confidence: "high" | "medium" | "low";
  action: string | null;
}

export interface OptimizerResult {
  scenario_id: string;
  recommendations: OptimizerRecommendation[];
}

export interface ScenarioCompareItem {
  scenario_id: string;
  scenario_name: string;
  simulation: SimulationResult | null;
}

export interface ScenarioCompareResult {
  items: ScenarioCompareItem[];
}

export interface MarketImpact {
  country: string;
  country_name: string;
  before: number;
  after: number;
  delta: number;
  delta_pct: number;
}

export interface DECascadeResult {
  opt_in_rebate_pct: number;
  de_price_before: number;
  de_price_after: number;
  de_disclosed_delta: number;
  market_impacts: MarketImpact[];
  referencing_markets_count: number;
  actually_impacted_count: number;
  cascade_iterations: number;
}
