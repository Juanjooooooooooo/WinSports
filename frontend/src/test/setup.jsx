// Setup global de Vitest: matchers de jest-dom, limpieza del DOM entre tests,
// y stubs para las dependencias que no funcionan en jsdom (react-leaflet) o que
// salen a la red (fetch).
import "@testing-library/jest-dom/vitest";
import { cleanup } from "@testing-library/react";
import { afterEach, beforeEach, vi } from "vitest";

// react-leaflet monta un mapa real (canvas/DOM de Leaflet) que jsdom no soporta.
// Lo reemplazamos por divs simples para que las páginas que incluyen <UsersMap/>
// se rendericen sin reventar. Los tests de UI de verdad van contra los
// componentes presentacionales, no contra el mapa.
vi.mock("react-leaflet", () => ({
  MapContainer: ({ children }) => <div data-testid="map">{children}</div>,
  TileLayer: () => null,
  CircleMarker: ({ children }) => <div data-testid="marker">{children}</div>,
  Tooltip: ({ children }) => <div>{children}</div>,
}));

// fetch por defecto: respuesta vacía. Cada test puede sobreescribirlo con su
// propio mock vía vi.stubGlobal si necesita datos concretos.
beforeEach(() => {
  vi.stubGlobal(
    "fetch",
    vi.fn(() => Promise.resolve({ json: () => Promise.resolve({}) }))
  );
});

afterEach(() => {
  cleanup();
  vi.unstubAllGlobals();
  vi.clearAllMocks();
});
