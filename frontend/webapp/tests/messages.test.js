import { describe, it, expect } from "vitest";
import { messages, DAY_NAMES, SHIFT_LABELS, EVENT_LABELS } from "../src/utils/messages.js";

describe("messages", () => {
  it("exports messages object with required keys", () => {
    expect(messages.LABEL_LOADING).toBeDefined();
    expect(messages.LABEL_SUBMIT).toBeDefined();
    expect(messages.LABEL_NOTES).toBeDefined();
    expect(messages.LABEL_AVAILABLE).toBeDefined();
    expect(messages.LABEL_UNAVAILABLE).toBeDefined();
    expect(messages.LABEL_BLOCKED).toBeDefined();
    expect(messages.SUCCESS_SUBMITTED).toBeDefined();
  });

  it("exports DAY_NAMES with 7 entries", () => {
    const keys = Object.keys(DAY_NAMES);
    expect(keys.length).toBe(7);
  });

  it("exports SHIFT_LABELS", () => {
    expect(Object.keys(SHIFT_LABELS).length).toBeGreaterThanOrEqual(3);
  });

  it("exports EVENT_LABELS", () => {
    expect(Object.keys(EVENT_LABELS).length).toBeGreaterThanOrEqual(1);
  });

  it("all values are non-empty Hebrew strings", () => {
    const allValues = [
      ...Object.values(messages),
      ...Object.values(DAY_NAMES),
      ...Object.values(SHIFT_LABELS),
      ...Object.values(EVENT_LABELS),
    ];
    for (const v of allValues) {
      expect(typeof v).toBe("string");
      expect(v.length).toBeGreaterThan(0);
    }
  });
});