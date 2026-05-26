import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, it, expect, vi } from "vitest";
import DocumentTable from "./DocumentTable";

const noop = () => {};

function renderTable(data, overrides = {}) {
  return render(
    <DocumentTable
      collections={["events", "sessions", "content_stats"]}
      collection="events"
      onCollectionChange={noop}
      data={data}
      page={1}
      pageSize={25}
      onPageChange={noop}
      onSave={vi.fn()}
      onDelete={vi.fn()}
      {...overrides}
    />
  );
}

describe("DocumentTable", () => {
  it("muestra 'Cargando...' mientras data es null", () => {
    renderTable(null);
    expect(screen.getByText("Cargando...")).toBeInTheDocument();
  });

  it("muestra 'Sin documentos' cuando la lista está vacía", () => {
    renderTable({ total: 0, documents: [] });
    expect(screen.getByText("Sin documentos")).toBeInTheDocument();
  });

  it("renderiza filas y entra en modo edición al hacer clic en Editar", async () => {
    const user = userEvent.setup();
    renderTable({ total: 1, documents: [{ _id: "a1", title: "Liga", duration: 120 }] });

    expect(screen.getByText("Liga")).toBeInTheDocument();

    await user.click(screen.getByRole("button", { name: "Editar" }));
    expect(screen.getByRole("button", { name: "Guardar" })).toBeInTheDocument();
    // Los campos escalares se vuelven inputs editables (excepto _id)
    expect(screen.getByLabelText("title")).toHaveValue("Liga");
  });

  it("llama onSave solo con los campos modificados, preservando tipos", async () => {
    const onSave = vi.fn().mockResolvedValue();
    const user = userEvent.setup();
    renderTable(
      { total: 1, documents: [{ _id: "a1", title: "Liga", duration: 120 }] },
      { onSave }
    );

    await user.click(screen.getByRole("button", { name: "Editar" }));
    const input = screen.getByLabelText("duration");
    await user.clear(input);
    await user.type(input, "200");
    await user.click(screen.getByRole("button", { name: "Guardar" }));

    expect(onSave).toHaveBeenCalledWith("a1", { duration: 200 });
  });
});
