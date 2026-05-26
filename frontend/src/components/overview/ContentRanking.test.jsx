import { render, screen } from "@testing-library/react";
import { describe, it, expect } from "vitest";
import ContentRanking from "./ContentRanking";

describe("ContentRanking", () => {
  it("muestra 'Cargando...' mientras data es null", () => {
    render(<ContentRanking data={null} />);
    expect(screen.getByText("Cargando...")).toBeInTheDocument();
  });

  it("muestra 'Sin datos' cuando la lista está vacía", () => {
    render(<ContentRanking data={[]} />);
    expect(screen.getByText("Sin datos")).toBeInTheDocument();
  });

  it("renderiza el ranking con título, posición y reproducciones formateadas", () => {
    const data = [
      { title: "Liga BetPlay", total_plays: 1200 },
      { title: "Champions", total_plays: 800 },
    ];
    render(<ContentRanking data={data} />);

    expect(screen.getByText("Liga BetPlay")).toBeInTheDocument();
    expect(screen.getByText("Champions")).toBeInTheDocument();
    // Posiciones del ranking
    expect(screen.getByText("1.")).toBeInTheDocument();
    expect(screen.getByText("2.")).toBeInTheDocument();
    // toLocaleString con miles
    expect(screen.getByText((1200).toLocaleString())).toBeInTheDocument();
  });
});
