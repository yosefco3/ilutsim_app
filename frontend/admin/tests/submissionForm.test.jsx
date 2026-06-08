import { describe, it, expect, vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import SubmissionForm from '../src/components/guard/SubmissionForm';

// Mock hooks
vi.mock('../src/hooks/useTelegram', () => ({
  useTelegram: () => ({
    initData: 'test-init-data',
    isDevMode: true,
    user: { id: 'dev-user', first_name: 'Dev' },
    mainButton: { show: vi.fn(), hide: vi.fn(), onClick: vi.fn() },
    close: vi.fn(),
  }),
}));

vi.mock('../src/hooks/useSubmission', () => ({
  useSubmission: vi.fn(),
}));

import { useSubmission } from '../src/hooks/useSubmission';

describe('SubmissionForm', () => {
  it('should show loading state', () => {
    useSubmission.mockReturnValue({
      loading: true,
      days: [],
      canSubmit: false,
      isLocked: false,
      weekStatus: null,
      week: null,
      error: null,
      success: false,
      notes: '',
      events: [],
      toggleAvailable: vi.fn(),
      setShiftType: vi.fn(),
      setHours: vi.fn(),
      toggleEvent: vi.fn(),
      setNotes: vi.fn(),
      submit: vi.fn(),
    });

    render(<SubmissionForm />);
    expect(screen.getByText(/טוען/)).toBeInTheDocument();
  });

  it('should show lock banner when week is locked', () => {
    useSubmission.mockReturnValue({
      loading: false,
      days: [],
      canSubmit: false,
      isLocked: true,
      weekStatus: 'locked',
      week: { week_id: 'w1', week_label: 'שבוע 1', status: 'locked' },
      error: null,
      success: false,
      notes: '',
      events: [],
      toggleAvailable: vi.fn(),
      setShiftType: vi.fn(),
      setHours: vi.fn(),
      toggleEvent: vi.fn(),
      setNotes: vi.fn(),
      submit: vi.fn(),
    });

    render(<SubmissionForm />);
    expect(screen.getByText(/לא נפתח|נעול/)).toBeInTheDocument();
  });

  it('should show form with days when week is open', () => {
    useSubmission.mockReturnValue({
      loading: false,
      days: [
        { day_index: 0, available: true, shift_type: null, from_hour: '', to_hour: '', blocked: false },
        { day_index: 1, available: false, shift_type: null, from_hour: '', to_hour: '', blocked: false },
      ],
      canSubmit: true,
      isLocked: false,
      weekStatus: 'open',
      week: { week_id: 'w1', week_label: 'שבוע 1', status: 'open' },
      error: null,
      success: false,
      notes: '',
      events: [],
      toggleAvailable: vi.fn(),
      setShiftType: vi.fn(),
      setHours: vi.fn(),
      toggleEvent: vi.fn(),
      setNotes: vi.fn(),
      submit: vi.fn(),
    });

    render(<SubmissionForm />);
    expect(screen.getByText('יום ראשון')).toBeInTheDocument();
    expect(screen.getByText('יום שני')).toBeInTheDocument();
    expect(screen.getByText(/שבוע 1/)).toBeInTheDocument();
  });

  it('should show success message after submission', () => {
    useSubmission.mockReturnValue({
      loading: false,
      days: [],
      canSubmit: false,
      isLocked: false,
      weekStatus: 'open',
      week: { week_id: 'w1', week_label: 'שבוע 1', status: 'open' },
      error: null,
      success: true,
      notes: '',
      events: [],
      toggleAvailable: vi.fn(),
      setShiftType: vi.fn(),
      setHours: vi.fn(),
      toggleEvent: vi.fn(),
      setNotes: vi.fn(),
      submit: vi.fn(),
    });

    render(<SubmissionForm />);
    expect(screen.getByText(/נשלח|הוגש/)).toBeInTheDocument();
  });

  it('should show error message on error', () => {
    useSubmission.mockReturnValue({
      loading: false,
      days: [],
      canSubmit: true,
      isLocked: false,
      weekStatus: 'open',
      week: { week_id: 'w1', week_label: 'שבוע 1', status: 'open' },
      error: 'שגיאת תקשורת',
      success: false,
      notes: '',
      events: [],
      toggleAvailable: vi.fn(),
      setShiftType: vi.fn(),
      setHours: vi.fn(),
      toggleEvent: vi.fn(),
      setNotes: vi.fn(),
      submit: vi.fn(),
    });

    render(<SubmissionForm />);
    expect(screen.getByText(/שגיאת תקשורת/)).toBeInTheDocument();
  });

  it('should wrap content in guard-layout div', () => {
    useSubmission.mockReturnValue({
      loading: true, days: [], canSubmit: false, isLocked: false,
      weekStatus: null, week: null, error: null, success: false, notes: '',
      events: [],
      toggleAvailable: vi.fn(), setShiftType: vi.fn(), setHours: vi.fn(),
      toggleEvent: vi.fn(), setNotes: vi.fn(), submit: vi.fn(),
    });

    const { container } = render(<SubmissionForm />);
    expect(container.querySelector('.guard-layout')).toBeInTheDocument();
  });
});