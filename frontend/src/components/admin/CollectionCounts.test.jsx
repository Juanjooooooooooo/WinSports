import { render, screen } from "@testing-library/react";
import { describe, it, expect } from "vitest";
import CollectionCounts from "./CollectionCounts";

describe("CollectionCounts", () => {
  it("muestra '—' en cada tarjeta mientras data es null", () => {
    render(<CollectionCounts data={null} />);
    expect(screen.getByText("Total documentos")).toBeInTheDocument();
    expect(screen.getByText("Eventos (raw)")).toBeInTheDocument();
    // KPICard renderiza '—' cuando value es null (una por tarjeta)
    expect(screen.getAllByText("—").length).toBeGreaterThanOrEqual(4);
  });

  it("renderiza el total y los conteos por colección", () => {
    const data = {
      total: 66,
      collections: [
        { name: "events", count: 50 },
        { name: "sessions", count: 12 },
        { name: "content_stats", count: 4 },
      ],
    };
    render(<CollectionCounts data={data} />);
    expect(screen.getByText("66")).toBeInTheDocument();
    expect(screen.getByText("50")).toBeInTheDocument();
    expect(screen.getByText("12")).toBeInTheDocument();
    expect(screen.getByText("4")).toBeInTheDocument();
  });
});
