import { render, screen } from "@testing-library/react";
import { describe, it, expect } from "vitest";
import RebufferingRate from "./RebufferingRate";

describe("RebufferingRate", () => {
  it("muestra 'Cargando...' mientras data es null", () => {
    render(<RebufferingRate data={null} />);
    expect(screen.getByText("Cargando...")).toBeInTheDocument();
  });

  it("renderiza los dos gauges (eventos y sesiones) con sus porcentajes y detalles", () => {
    const data = {
      event_rate: 3.5,
      rebuffer_events: 350,
      total_events: 10000,
      session_rate: 12.0,
      rebuffer_sessions: 60,
      total_sessions: 500,
    };
    render(<RebufferingRate data={data} />);

    expect(screen.getByText("Por eventos")).toBeInTheDocument();
    expect(screen.getByText("Por sesiones")).toBeInTheDocument();
    expect(screen.getByText("3.5%")).toBeInTheDocument();
    expect(screen.getByText("12%")).toBeInTheDocument();
    expect(
      screen.getByText(
        `${(350).toLocaleString()} / ${(10000).toLocaleString()} eventos`
      )
    ).toBeInTheDocument();
    expect(
      screen.getByText(`${(60).toLocaleString()} / ${(500).toLocaleString()} sesiones`)
    ).toBeInTheDocument();
  });
});
