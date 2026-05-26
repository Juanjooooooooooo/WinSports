import { render, screen } from "@testing-library/react";
import { describe, it, expect } from "vitest";
import RetentionFunnel from "./RetentionFunnel";

describe("RetentionFunnel", () => {
  it("muestra 'Cargando...' mientras data es null", () => {
    render(<RetentionFunnel data={null} />);
    expect(screen.getByText("Cargando...")).toBeInTheDocument();
  });

  it("renderiza las 5 etapas con valor y porcentaje relativo al total", () => {
    const data = {
      total: 1000,
      firstquartile: 800,
      midpoint: 600,
      thirdquartile: 400,
      complete: 200,
    };
    render(<RetentionFunnel data={data} />);

    expect(screen.getByText("Inicio (START)")).toBeInTheDocument();
    expect(screen.getByText("25% — Primer cuartil")).toBeInTheDocument();
    expect(screen.getByText("50% — Mitad")).toBeInTheDocument();
    expect(screen.getByText("75% — Tercer cuartil")).toBeInTheDocument();
    expect(screen.getByText("100% — Completo")).toBeInTheDocument();

    // value (pct%) — el total marca el 100%
    expect(screen.getByText(`${(1000).toLocaleString()} (100.0%)`)).toBeInTheDocument();
    expect(screen.getByText(`${(800).toLocaleString()} (80.0%)`)).toBeInTheDocument();
    expect(screen.getByText(`${(200).toLocaleString()} (20.0%)`)).toBeInTheDocument();
  });
});
