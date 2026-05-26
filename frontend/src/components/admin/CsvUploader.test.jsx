import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, it, expect, vi } from "vitest";
import CsvUploader from "./CsvUploader";

describe("CsvUploader", () => {
  it("deshabilita el botón hasta que se elige un archivo", () => {
    render(<CsvUploader />);
    expect(screen.getByRole("button", { name: "Subir y procesar" })).toBeDisabled();
  });

  it("sube el archivo, muestra el resumen y avisa al padre", async () => {
    const result = {
      filename: "nuevos.csv",
      inserted: 48,
      rows_skipped: 2,
      rows_total: 50,
      batch_errors: 0,
      events_total: 98,
      sessions_built: 20,
      content_stats_built: 8,
    };
    vi.stubGlobal(
      "fetch",
      vi.fn(() => Promise.resolve({ ok: true, json: () => Promise.resolve(result) }))
    );
    const onUploaded = vi.fn();
    const user = userEvent.setup();
    render(<CsvUploader onUploaded={onUploaded} />);

    const file = new File(["Date,SubscriberID\n"], "nuevos.csv", { type: "text/csv" });
    await user.upload(screen.getByLabelText("Archivo CSV"), file);

    const btn = screen.getByRole("button", { name: "Subir y procesar" });
    expect(btn).toBeEnabled();
    await user.click(btn);

    expect(await screen.findByText(/procesado/)).toBeInTheDocument();
    expect(globalThis.fetch).toHaveBeenCalledWith(
      "/api/admin/upload-csv",
      expect.objectContaining({ method: "POST" })
    );
    expect(onUploaded).toHaveBeenCalled();
  });
});
