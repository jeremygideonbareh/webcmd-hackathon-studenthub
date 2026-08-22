import { describe, it, expect } from "vitest";
import { calculateRisk } from "./math";

describe("calculateRisk — attendance calculus (matches attendance_calculus.py)", () => {
  it("WARNING for 42/52 (80.77%) → must_attend 15", () => {
    const r = calculateRisk(42, 52, 0.85);
    expect(r.current_pct).toBe(80.77);
    expect(r.risk_level).toBe("WARNING");
    expect(r.classes_can_skip).toBe(0);
    expect(r.classes_must_attend).toBe(15);
  });

  it("SAFE for 48/50 (96%) → can_skip 6", () => {
    const r = calculateRisk(48, 50, 0.85);
    expect(r.risk_level).toBe("SAFE");
    expect(r.classes_can_skip).toBe(6);
    expect(r.classes_must_attend).toBe(0);
  });

  it("DANGER for 38/50 (76%) → must_attend 30", () => {
    const r = calculateRisk(38, 50, 0.85);
    expect(r.risk_level).toBe("DANGER");
    expect(r.classes_must_attend).toBe(30);
    expect(r.classes_can_skip).toBe(0);
  });

  it("SAFE for 45/50 (90%) → can_skip 2 (90% is >= 90 boundary)", () => {
    const r = calculateRisk(45, 50, 0.85);
    expect(r.risk_level).toBe("SAFE");
    expect(r.classes_can_skip).toBe(2);
  });

  it("handles total=0 gracefully", () => {
    const r = calculateRisk(0, 0, 0.85);
    expect(r.current_pct).toBe(0);
    expect(r.risk_level).toBe("DANGER");
  });

  it("respects a custom threshold", () => {
    // 90/100 with threshold 0.8 → can_skip = floor((90 - 80)/0.8) = 12
    const r = calculateRisk(90, 100, 0.8);
    expect(r.risk_level).toBe("SAFE");
    expect(r.classes_can_skip).toBe(12);
  });
});
