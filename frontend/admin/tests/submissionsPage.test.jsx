import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';

vi.mock('../src/hooks/useWeeks', () => ({ useWeeks: vi.fn() }));
vi.mock('../src/hooks/useSubmissions', () => ({ useSubmissions: vi.fn() }));
vi.mock('../src/components/Toast', () => ({ useToast: () => vi.fn() }));
vi.mock('../src/api/adminApiClient', () => ({
  sendWeekReminders: vi.fn(),
  fetchConstraintRules: vi.fn().mockResolvedValue(null),
}));

import { useWeeks } from '../src/hooks/useWeeks';
import { useSubmissions } from '../src/hooks/useSubmissions';
import SubmissionsPage from '../src/pages/SubmissionsPage';
import messages from '../src/utils/messages';

const submissions = [
  { user_id: 'g1', full_name: 'בובי ביטון', submitted_at: '2026-06-13T15:20:12' },
];

function setup(weekStatus) {
  const week = { id: 1, status: weekStatus, week_label: 'שבוע 24', start_date: '2026-06-14' };
  useWeeks.mockReturnValue({ weeks: [week], loading: false });
  useSubmissions.mockReturnValue({
    submissions,
    detailedData: { submitted: [], pending: [] },
    loading: false,
  });
  render(
    <MemoryRouter>
      <SubmissionsPage />
    </MemoryRouter>,
  );
}

describe('SubmissionsPage — admin fill-constraints gating by week status', () => {
  beforeEach(() => {
    useWeeks.mockReset();
    useSubmissions.mockReset();
  });

  // The week selector auto-defaults only to an 'open' week, so for non-open
  // statuses we pick the week explicitly via the <select>.
  function selectWeek() {
    fireEvent.change(screen.getByRole('combobox'), { target: { value: '1' } });
  }

  it('shows the fill-constraints button when the week is locked (admin may still edit)', () => {
    setup('locked');
    selectWeek();
    expect(
      screen.getByRole('button', { name: messages.guards.fillConstraints }),
    ).toBeInTheDocument();
  });

  it('shows the fill-constraints button when the week is open', () => {
    setup('open');
    // 'open' auto-selects, no manual pick needed.
    expect(
      screen.getByRole('button', { name: messages.guards.fillConstraints }),
    ).toBeInTheDocument();
  });

  it('hides the fill-constraints button only once the week is published', () => {
    setup('published');
    selectWeek();
    expect(
      screen.queryByRole('button', { name: messages.guards.fillConstraints }),
    ).not.toBeInTheDocument();
  });
});
