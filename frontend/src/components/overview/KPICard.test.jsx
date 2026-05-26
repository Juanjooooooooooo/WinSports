import { render, screen } from "@testing-library/react";
import { describe, it, expect } from "vitest";
import KPICard from "./KPICard";

describe("KPICard", () => {
  it("muestra el guion largo cuando value es null", () => {
    render(<KPICard title="Total Reproducciones" value={null} />);
    expect(screen.getByText("Total Reproducciones")).toBeInTheDocument();
    expect(screen.getByText("—")).toBeInTheDocument();
  });

  it("renderiza el value y el subtitle cuando vienen", () => {
    render(
      <KPICard title="Usuarios Únicos" value="1,234" subtitle="suscriptores distintos" />
    );
    expect(screen.getByText("1,234")).toBeInTheDocument();
    expect(screen.getByText("suscriptores distintos")).toBeInTheDocument();
  });

  it("oculta el subtitle cuando no se pasa", () => {
    render(<KPICard title="Dispositivo Líder" value="WEB" />);
    expect(screen.queryByText("suscriptores distintos")).not.toBeInTheDocument();
  });
});
