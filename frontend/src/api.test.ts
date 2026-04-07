import { describe, it, expect, vi, afterEach } from "vitest";
import { api, baseline } from "./api";
afterEach(() => vi.unstubAllGlobals());
describe("API boundary", () => {
  it("reports structured processing failures", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue({
        ok: false,
        json: async () => ({ error: { message: "CRC failed" } }),
      }),
    );
    await expect(api("/transmissions")).rejects.toThrow("CRC failed");
  });
  it("identifies offline backends", async () => {
    vi.stubGlobal("fetch", vi.fn().mockRejectedValue(new TypeError("network")));
    await expect(api("/health")).rejects.toThrow("Backend is offline");
  });
  it("preserves real responses", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue({
        ok: true,
        json: async () => ({ status: "ok", simulation_mode: true }),
      }),
    );
    await expect(api("/health")).resolves.toEqual({
      status: "ok",
      simulation_mode: true,
    });
  });
  it("defines a reproducible baseline", () => {
    expect(baseline.seed).toBe(42);
    expect(baseline.repetition).toBe(1);
    expect(baseline.snr_db).toBe(12);
  });
});
