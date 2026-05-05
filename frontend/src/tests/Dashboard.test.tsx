import { render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

import Dashboard from "@/pages/Dashboard";

vi.mock("@auth0/auth0-react", () => ({
  useAuth0: () => ({
    user: {
      name: "Sarah Chen",
      "https://pricingstar.io/tenant_id": "abc-123",
      "https://pricingstar.io/tenant_tier": "trial",
    },
    logout: vi.fn(),
  }),
}));

describe("Dashboard", () => {
  it("shows the user name and tenant context", () => {
    render(<Dashboard />);
    expect(screen.getByText(/Hello, Sarah Chen/)).toBeInTheDocument();
    expect(screen.getByText("abc-123")).toBeInTheDocument();
    expect(screen.getByText("trial")).toBeInTheDocument();
  });
});
