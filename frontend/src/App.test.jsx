import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, it, expect, beforeEach, vi } from "vitest";
import App from "./App";

// Endpoints cuyo body completo se asigna al estado (page hace `.then(setX)`).
// Para mantenerlos en estado "cargando" sin reventar, su json() resuelve a null;
// el resto desestructura `d.campo`, así que con {} basta (d.campo → undefined).
// Con todo en loading, no se montan recharts ni el mapa de Leaflet.
const WHOLE_BODY_ENDPOINTS = [
  "rebuffering-rate",
  "startup-time",
  "content-completion-ranking",
  "user-profiles",
  "retention-funnel",
];

beforeEach(() => {
  vi.stubGlobal(
    "fetch",
    vi.fn((url) => {
      const body = WHOLE_BODY_ENDPOINTS.some((e) => url.includes(e)) ? null : {};
      return Promise.resolve({ json: () => Promise.resolve(body) });
    })
  );
});

describe("App (navegación)", () => {
  it("arranca en Overview", () => {
    render(<App />);
    expect(screen.getByRole("heading", { name: "Overview" })).toBeInTheDocument();
  });

  it("cambia a QoE al hacer clic en su botón del sidebar", async () => {
    const user = userEvent.setup();
    render(<App />);

    await user.click(screen.getByRole("button", { name: "QoE" }));
    expect(screen.getByRole("heading", { name: "QoE" })).toBeInTheDocument();
  });

  it("muestra 'en construcción' para páginas no implementadas", async () => {
    const user = userEvent.setup();
    render(<App />);

    await user.click(screen.getByRole("button", { name: "Alertas" }));
    expect(screen.getByText(/en construcción/i)).toBeInTheDocument();
  });
});
