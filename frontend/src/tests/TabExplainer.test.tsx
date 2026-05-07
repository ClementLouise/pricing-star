import { fireEvent, render, screen } from "@testing-library/react";
import { beforeEach, describe, expect, it } from "vitest";

import { TabExplainer } from "@/components/TabExplainer";

const base = {
  tabId: "test-tab",
  whatItDoes: "Ce tab fait X.",
  whenToUse: "Utiliser quand Y.",
};

const withWatchOut = { ...base, watchOutFor: "Attention à Z." };

describe("TabExplainer", () => {
  beforeEach(() => {
    localStorage.clear();
  });

  it("renders collapsed by default when already discovered", () => {
    localStorage.setItem("pricingstar.explainer.discovered", "true");
    render(<TabExplainer {...base} />);
    expect(screen.getByRole("button")).toHaveAttribute("aria-expanded", "false");
    expect(screen.getByText("Voir l'explication")).toBeInTheDocument();
  });

  it("auto-expands on first visit (discovered not set)", () => {
    render(<TabExplainer {...base} />);
    expect(screen.getByRole("button")).toHaveAttribute("aria-expanded", "true");
    expect(screen.getByText("Masquer")).toBeInTheDocument();
  });

  it("click toggles collapsed → expanded", () => {
    localStorage.setItem("pricingstar.explainer.discovered", "true");
    render(<TabExplainer {...base} />);
    fireEvent.click(screen.getByRole("button"));
    expect(screen.getByRole("button")).toHaveAttribute("aria-expanded", "true");
    expect(screen.getByText("Masquer")).toBeInTheDocument();
  });

  it("click toggles expanded → collapsed", () => {
    render(<TabExplainer {...base} />);
    // starts expanded (not discovered)
    fireEvent.click(screen.getByRole("button"));
    expect(screen.getByRole("button")).toHaveAttribute("aria-expanded", "false");
    expect(screen.getByText("Voir l'explication")).toBeInTheDocument();
  });

  it("persists state to localStorage across remounts", () => {
    localStorage.setItem("pricingstar.explainer.discovered", "true");
    const { unmount } = render(<TabExplainer {...base} />);
    fireEvent.click(screen.getByRole("button")); // expand
    unmount();
    render(<TabExplainer {...base} />);
    expect(screen.getByRole("button")).toHaveAttribute("aria-expanded", "true");
    expect(localStorage.getItem("pricingstar.explainer.test-tab")).toBe("expanded");
  });

  it("collapse persists to localStorage across remounts", () => {
    localStorage.setItem("pricingstar.explainer.discovered", "true");
    const { unmount } = render(<TabExplainer {...base} />);
    unmount(); // already collapsed
    render(<TabExplainer {...base} />);
    expect(screen.getByRole("button")).toHaveAttribute("aria-expanded", "false");
  });

  it("sets discovered flag on first toggle", () => {
    render(<TabExplainer {...base} />); // auto-expanded
    expect(localStorage.getItem("pricingstar.explainer.discovered")).toBeNull();
    fireEvent.click(screen.getByRole("button")); // collapse → sets flag
    expect(localStorage.getItem("pricingstar.explainer.discovered")).toBe("true");
  });

  it("new tab defaults collapsed once discovered=true", () => {
    localStorage.setItem("pricingstar.explainer.discovered", "true");
    render(<TabExplainer tabId="brand-new-tab" whatItDoes="X" whenToUse="Y" />);
    expect(screen.getByRole("button")).toHaveAttribute("aria-expanded", "false");
  });

  it("shows 2 columns when watchOutFor is absent", () => {
    localStorage.setItem("pricingstar.explainer.discovered", "true");
    render(<TabExplainer {...base} />);
    fireEvent.click(screen.getByRole("button")); // expand
    expect(screen.getByText("À QUOI ÇA SERT")).toBeInTheDocument();
    expect(screen.getByText("QUAND L'UTILISER")).toBeInTheDocument();
    expect(screen.queryByText("ATTENTION")).not.toBeInTheDocument();
  });

  it("shows 3 columns when watchOutFor is provided", () => {
    localStorage.setItem("pricingstar.explainer.discovered", "true");
    render(<TabExplainer {...withWatchOut} />);
    fireEvent.click(screen.getByRole("button")); // expand
    expect(screen.getByText("À QUOI ÇA SERT")).toBeInTheDocument();
    expect(screen.getByText("QUAND L'UTILISER")).toBeInTheDocument();
    expect(screen.getByText("ATTENTION")).toBeInTheDocument();
    expect(screen.getByText("Attention à Z.")).toBeInTheDocument();
  });

  it("Enter key toggles the explainer", () => {
    localStorage.setItem("pricingstar.explainer.discovered", "true");
    render(<TabExplainer {...base} />);
    fireEvent.keyDown(screen.getByRole("button"), { key: "Enter" });
    expect(screen.getByRole("button")).toHaveAttribute("aria-expanded", "true");
  });

  it("Space key toggles the explainer", () => {
    localStorage.setItem("pricingstar.explainer.discovered", "true");
    render(<TabExplainer {...base} />);
    fireEvent.keyDown(screen.getByRole("button"), { key: " " });
    expect(screen.getByRole("button")).toHaveAttribute("aria-expanded", "true");
  });

  it("aria-expanded reflects state through multiple toggles", () => {
    localStorage.setItem("pricingstar.explainer.discovered", "true");
    render(<TabExplainer {...base} />);
    const btn = screen.getByRole("button");
    expect(btn).toHaveAttribute("aria-expanded", "false");
    fireEvent.click(btn);
    expect(btn).toHaveAttribute("aria-expanded", "true");
    fireEvent.click(btn);
    expect(btn).toHaveAttribute("aria-expanded", "false");
  });
});
