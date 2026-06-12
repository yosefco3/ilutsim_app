import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import { MemoryRouter, Routes, Route } from 'react-router-dom';

// Mock the data hook so we can drive each render state.
vi.mock('../src/hooks/useSubmissions', () => ({
  useSubmissions: vi.fn(),
}));

import { useSubmissions } from '../src/hooks/useSubmissions';
import SubmissionDetailPage from '../src/pages/SubmissionDetailPage';

function renderPage(weekId = 'week-1') {
  return render(
    <MemoryRouter initialEntries={[`/submissions/${weekId}`]}>
      <Routes>
        <Route path="/submissions/:weekId" element={<SubmissionDetailPage />} />
      </Routes>
    </MemoryRouter>,
  );
}

const detailedData = {
  week_label: '08/06/2026 - 14/06/2026',
  submitted: [
    {
      user_id: 'u1',
      full_name: 'דנה לוי',
      submitted_at: '2026-06-08T10:00:00Z',
      general_notes: 'הערה כללית',
      days: [
        {
          shift_windows: [
            { shift_type: 'morning', start_time: '07:00', end_time: '16:00' },
          ],
        },
      ],
    },
  ],
  missing: [
    { user_id: 'u2', full_name: 'יוסי כהן', phone_number: '0500000000' },
  ],
};

describe('SubmissionDetailPage', () => {
  beforeEach(() => {
    useSubmissions.mockReset();
  });

  it('renders loading state', () => {
    useSubmissions.mockReturnValue({ loading: true, error: null, detailedData: null });
    renderPage();
    expect(screen.getByText('טוען...')).toBeInTheDocument();
  });

  it('renders error state', () => {
    useSubmissions.mockReturnValue({ loading: false, error: 'boom', detailedData: null });
    renderPage();
    expect(screen.getByText(/שגיאה/)).toBeInTheDocument();
  });

  it('renders submitted and missing tables', () => {
    useSubmissions.mockReturnValue({ loading: false, error: null, detailedData });
    renderPage();
    expect(screen.getByText(/פירוט אילוצים/)).toBeInTheDocument();
    expect(screen.getByText('דנה לוי')).toBeInTheDocument();
    expect(screen.getByText('יוסי כהן')).toBeInTheDocument();
  });

  it('expandable detail shows shift information', () => {
    useSubmissions.mockReturnValue({ loading: false, error: null, detailedData });
    renderPage();
    // Shift hours hidden until expanded
    expect(screen.queryByText(/07:00 - 16:00/)).not.toBeInTheDocument();
    fireEvent.click(screen.getByText('הצג'));
    expect(screen.getByText(/07:00 - 16:00/)).toBeInTheDocument();
    expect(screen.getByText(/הערה כללית/)).toBeInTheDocument();
  });

  it('back link navigates to /submissions', () => {
    useSubmissions.mockReturnValue({ loading: false, error: null, detailedData });
    renderPage();
    const back = screen.getByText(/חזרה לרשימת השבועות/);
    expect(back.closest('a')).toHaveAttribute('href', '/submissions');
  });
});
