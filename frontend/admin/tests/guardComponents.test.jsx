import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import LockBanner from '../src/components/guard/LockBanner';
import DayRow from '../src/components/guard/DayRow';

describe('LockBanner', () => {
  it('should render locked message', () => {
    render(<LockBanner status="locked" />);
    expect(screen.getByText(/נעול|לא נפתח/)).toBeInTheDocument();
  });

  it('should render published message', () => {
    render(<LockBanner status="published" />);
    expect(screen.getByText(/פורסם/)).toBeInTheDocument();
  });

  it('should render no-week message when status is null', () => {
    render(<LockBanner status={null} />);
    expect(screen.getByText(/אין שבוע/)).toBeInTheDocument();
  });
});

describe('DayRow', () => {
  const baseDay = {
    day_index: 0,
    available: true,
    shift_type: null,
    from_hour: '',
    to_hour: '',
    blocked: false,
  };

  it('should render day name', () => {
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
    expect(screen.getByText('יום ראשון')).toBeInTheDocument();
  });

  it('should show available toggle button', () => {
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
    expect(screen.getByText('זמין')).toBeInTheDocument();
  });

  it('should call onToggleAvailable when clicked', () => {
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
    fireEvent.click(screen.getByText('זמין'));
    expect(onToggle).toHaveBeenCalledWith(0);
  });

  it('should show blocked badge when day is blocked', () => {
    render(
      <DayRow
        day={{ ...baseDay, blocked: true }}
        events={[]}
        disabled={false}
        onToggleAvailable={vi.fn()}
        onSetShiftType={vi.fn()}
        onSetHours={vi.fn()}
        onToggleEvent={vi.fn()}
      />,
    );
    expect(screen.getByText('חסום')).toBeInTheDocument();
  });

  it('should show shift type buttons when available', () => {
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
    expect(screen.getByText('בוקר')).toBeInTheDocument();
    expect(screen.getByText('צהריים')).toBeInTheDocument();
    expect(screen.getByText('לילה')).toBeInTheDocument();
  });

  it('should show event buttons', () => {
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
    expect(screen.getByText('חופשה')).toBeInTheDocument();
    expect(screen.getByText('מילואים')).toBeInTheDocument();
    expect(screen.getByText('רענון נשק')).toBeInTheDocument();
  });

  it('should disable all buttons when disabled=true', () => {
    render(
      <DayRow
        day={baseDay}
        events={[]}
        disabled={true}
        onToggleAvailable={vi.fn()}
        onSetShiftType={vi.fn()}
        onSetHours={vi.fn()}
        onToggleEvent={vi.fn()}
      />,
    );
    const buttons = screen.getAllByRole('button');
    buttons.forEach((btn) => {
      expect(btn).toBeDisabled();
    });
  });
});