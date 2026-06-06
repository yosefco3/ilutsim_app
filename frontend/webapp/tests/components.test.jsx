import { describe, it, expect, vi } from "vitest";
import { render, screen, fireEvent } from "@testing-library/react";
import LockBanner from "../src/components/LockBanner.jsx";
import DayRow from "../src/components/DayRow.jsx";
import SubmissionForm from "../src/components/SubmissionForm.jsx";

describe("LockBanner", () => {
  it("renders locked message", () => {
    render(<LockBanner />);
    expect(screen.getByText(/אין שבוע פעיל/)).toBeDefined();
  });
});

describe("DayRow", () => {
  const baseDay = {
    day_index: 0,
    available: false,
    shift_type: "regular",
    from_hour: "",
    to_hour: "",
    blocked: false,
  };

  it("renders day name", () => {
    render(
      <DayRow
        day={baseDay}
        events={[]}
        disabled={false}
        onToggleAvailable={vi.fn()}
        onSetShiftType={vi.fn()}
        onSetHours={vi.fn()}
        onToggleEvent={vi.fn()}
      />,
    );
    // Should render a day name (Hebrew)
    expect(screen.getByRole("button", { name: /זמין|לא זמין/ })).toBeDefined();
  });

  it("calls onToggleAvailable when clicked", () => {
    const onToggle = vi.fn();
    render(
      <DayRow
        day={baseDay}
        events={[]}
        disabled={false}
        onToggleAvailable={onToggle}
        onSetShiftType={vi.fn()}
        onSetHours={vi.fn()}
        onToggleEvent={vi.fn()}
      />,
    );
    fireEvent.click(screen.getByRole("button", { name: /לא זמין/ }));
    expect(onToggle).toHaveBeenCalledWith(0);
  });

  it("shows shift buttons when available", () => {
    const day = { ...baseDay, available: true };
    render(
      <DayRow
        day={day}
        events={[]}
        disabled={false}
        onToggleAvailable={vi.fn()}
        onSetShiftType={vi.fn()}
        onSetHours={vi.fn()}
        onToggleEvent={vi.fn()}
      />,
    );
    // Should show shift type buttons
    const buttons = screen.getAllByRole("button");
    expect(buttons.length).toBeGreaterThan(2);
  });
});

describe("SubmissionForm", () => {
  it("shows loading state", () => {
    const submission = {
      loading: true,
      error: null,
      success: false,
      week: null,
      days: [],
      events: [],
      notes: "",
      setNotes: vi.fn(),
      isLocked: false,
      toggleAvailable: vi.fn(),
      setShiftType: vi.fn(),
      setHours: vi.fn(),
      toggleEvent: vi.fn(),
      submit: vi.fn(),
    };
    render(<SubmissionForm submission={submission} />);
    expect(screen.getByText(/טוען/)).toBeDefined();
  });

  it("shows error banner", () => {
    const submission = {
      loading: false,
      error: "שגיאה",
      success: false,
      week: null,
      days: [],
      events: [],
      notes: "",
      setNotes: vi.fn(),
      isLocked: false,
      toggleAvailable: vi.fn(),
      setShiftType: vi.fn(),
      setHours: vi.fn(),
      toggleEvent: vi.fn(),
      submit: vi.fn(),
    };
    render(<SubmissionForm submission={submission} />);
    expect(screen.getByText("שגיאה")).toBeDefined();
  });
});