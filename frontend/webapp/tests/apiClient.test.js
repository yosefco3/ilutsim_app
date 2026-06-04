import { describe, it, expect, vi, beforeEach } from "vitest";
import { api } from "../src/api/apiClient.js";

describe("apiClient", () => {
  beforeEach(() => {
    globalThis.fetch = vi.fn();
  });

  it("api has get, post, put methods", () => {
    expect(typeof api.get).toBe("function");
    expect(typeof api.post).toBe("function");
    expect(typeof api.put).toBe("function");
  });

  it("api.get calls fetch with correct method", async () => {
    globalThis.fetch.mockResolvedValue({
      ok: true,
      json: () => Promise.resolve({ data: 1 }),
    });
    const result = await api.get("/test");
    expect(globalThis.fetch).toHaveBeenCalled();
    const [url, opts] = globalThis.fetch.mock.calls[0];
    expect(url).toContain("/test");
    expect(opts.method).toBe("GET");
  });

  it("api.post sends JSON body", async () => {
    globalThis.fetch.mockResolvedValue({
      ok: true,
      json: () => Promise.resolve({ ok: true }),
    });
    await api.post("/submit", { foo: "bar" });
    const [, opts] = globalThis.fetch.mock.calls[0];
    expect(opts.method).toBe("POST");
    expect(opts.body).toBe(JSON.stringify({ foo: "bar" }));
    expect(opts.headers["Content-Type"]).toBe("application/json");
  });
});