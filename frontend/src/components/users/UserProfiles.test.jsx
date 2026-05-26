import { render, screen } from "@testing-library/react";
import { describe, it, expect } from "vitest";
import UserProfiles from "./UserProfiles";

describe("UserProfiles", () => {
  it("muestra 'Cargando...' mientras data es null", () => {
    render(<UserProfiles data={null} />);
    expect(screen.getByText("Cargando...")).toBeInTheDocument();
  });

  it("renderiza los tres perfiles con conteos y porcentaje sobre el total", () => {
    const data = {
      total_users: 100,
      profiles: [
        { profile: "Heavy", count: 20, avg_events: 75.0, range: "≥ 50 eventos" },
        { profile: "Mid", count: 30, avg_events: 25.0, range: "10–49 eventos" },
        { profile: "Vague", count: 50, avg_events: 4.0, range: "< 10 eventos" },
      ],
    };
    render(<UserProfiles data={data} />);

    expect(screen.getByText("Heavy user")).toBeInTheDocument();
    expect(screen.getByText("Mid user")).toBeInTheDocument();
    expect(screen.getByText("Vague user")).toBeInTheDocument();

    // Conteos
    expect(screen.getByText("20")).toBeInTheDocument();
    expect(screen.getByText("30")).toBeInTheDocument();
    expect(screen.getByText("50")).toBeInTheDocument();

    // Porcentajes (count / total_users)
    expect(screen.getByText("20% de usuarios")).toBeInTheDocument();
    expect(screen.getByText("50% de usuarios")).toBeInTheDocument();

    // Header con total
    expect(
      screen.getByText("100 usuarios · clasificados por nº de eventos")
    ).toBeInTheDocument();
  });
});
