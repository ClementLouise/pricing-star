import { create } from "zustand";

import type { Asset, Scenario, SimulationResult } from "@/types/api";

interface AppState {
  // Active context
  activeAsset: Asset | null;
  activeScenario: Scenario | null;
  latestSimulation: SimulationResult | null;
  activeTab: string;

  // Actions
  setActiveAsset: (asset: Asset | null) => void;
  setActiveScenario: (scenario: Scenario | null) => void;
  setLatestSimulation: (result: SimulationResult | null) => void;
  setActiveTab: (tab: string) => void;
}

export const useAppStore = create<AppState>((set) => ({
  activeAsset: null,
  activeScenario: null,
  latestSimulation: null,
  activeTab: "asset",

  setActiveAsset: (asset) => set({ activeAsset: asset }),
  setActiveScenario: (scenario) => set({ activeScenario: scenario }),
  setLatestSimulation: (result) => set({ latestSimulation: result }),
  setActiveTab: (tab) => set({ activeTab: tab }),
}));
