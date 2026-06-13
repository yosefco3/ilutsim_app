import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';

// Mock the weeks hook and the API client so we control both.
vi.mock('../src/hooks/useWeeks', () => ({
  useWeeks: vi.fn(),
}));
vi.mock('../src/api/adminApiClient', () => ({
  exportExcel: vi.fn(),
}));

import { useWeeks } from '../src/hooks/useWeeks';
import { exportExcel } from '../src/api/adminApiClient';
import ExportPage from '../src/pages/ExportPage';

function renderPage() {
  return render(
    <MemoryRouter>
      <ExportPage />
    </MemoryRouter>,
  );
}

describe('ExportPage', () => {
  beforeEach(() => {
    useWeeks.mockReset();
    exportExcel.mockReset();
    useWeeks.mockReturnValue({
      weeks: [{ id: 'week-1', week_label: '08/06/2026 - 14/06/2026' }],
      loading: false,
    });
    // jsdom lacks URL.createObjectURL / revokeObjectURL
    global.URL.createObjectURL = vi.fn(() => 'blob:mock');
    global.URL.revokeObjectURL = vi.fn();
  });

  it('renders the download button with real (non-undefined) label', () => {
    renderPage();
    const btn = screen.getByRole('button');
    expect(btn.textContent).toBe('הורד קובץ Excel');
    expect(btn.textContent).not.toMatch(/undefined/);
  });

  it('disables the button until a week is selected', () => {
    renderPage();
    expect(screen.getByRole('button')).toBeDisabled();
  });

  it('defaults the selector to the relevant (open) week and enables export', async () => {
    useWeeks.mockReturnValue({
      weeks: [
        { id: 'week-1', week_label: 'שבוע ישן', status: 'published' },
        { id: 'week-2', week_label: 'שבוע רלוונטי', status: 'open' },
      ],
      loading: false,
    });
    renderPage();

    await waitFor(() =>
      expect(screen.getByRole('combobox')).toHaveValue('week-2'),
    );
    expect(screen.getByRole('button')).toBeEnabled();
  });

  it('calls exportExcel with the selected week id on click', async () => {
    exportExcel.mockResolvedValue(new Blob(['xlsx']));
    renderPage();

    fireEvent.change(screen.getByRole('combobox'), { target: { value: 'week-1' } });
    fireEvent.click(screen.getByRole('button'));

    await waitFor(() => expect(exportExcel).toHaveBeenCalledWith('week-1'));
  });
});
