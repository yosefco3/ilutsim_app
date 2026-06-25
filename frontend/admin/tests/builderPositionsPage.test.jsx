import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';

vi.mock('../src/api/builderApiClient', () => ({
  listProfiles: vi.fn(),
  listPositions: vi.fn(),
  createPosition: vi.fn(),
  updatePosition: vi.fn(),
  deletePosition: vi.fn(),
  listAttributes: vi.fn(),
  createAttribute: vi.fn(),
  deleteAttribute: vi.fn(),
}));
const toast = { success: vi.fn(), error: vi.fn() };
vi.mock('../src/components/Toast', () => ({ useToast: () => toast }));

import {
  listProfiles,
  listPositions,
  createPosition,
  deletePosition,
  listAttributes,
} from '../src/api/builderApiClient';
import PositionsPage from '../src/pages/builder/PositionsPage';

const PROFILE = { id: 'p1', name: 'שגרה', is_default: true };
const ATTR = { id: 'a1', key: 'armed', label: 'חמוש', display_order: 0 };
const POSITION = {
  id: 'pos1',
  profile_id: 'p1',
  name: 'ארנונה',
  day_schedules: { 0: { start: '07:30', end: '15:00' } },
  required_attributes: ['armed'],
  display_order: 1,
};

function renderPage() {
  return render(
    <MemoryRouter>
      <PositionsPage />
    </MemoryRouter>,
  );
}

beforeEach(() => {
  vi.clearAllMocks();
  listProfiles.mockResolvedValue([PROFILE]);
  listAttributes.mockResolvedValue([ATTR]);
  listPositions.mockResolvedValue([POSITION]);
});

describe('PositionsPage', () => {
  it('loads the profile selector and lists positions', async () => {
    renderPage();
    expect(await screen.findByText('ארנונה')).toBeInTheDocument();
    expect(screen.getByText('חמוש')).toBeInTheDocument(); // requirement tag
  });

  it('creates a position with day schedule and requirement', async () => {
    createPosition.mockResolvedValue({ ...POSITION, id: 'pos2' });
    renderPage();
    await screen.findByText('ארנונה');

    fireEvent.click(screen.getByText('עמדה חדשה'));
    fireEvent.change(screen.getByLabelText('שם העמדה'), { target: { value: 'קומה 6' } });
    fireEvent.click(screen.getByLabelText('ראשון')); // activate Sunday
    fireEvent.click(screen.getByLabelText('חמוש')); // requirement (in editor)
    fireEvent.click(screen.getByText('שמור'));

    await waitFor(() => expect(createPosition).toHaveBeenCalled());
    const [profileArg, body] = createPosition.mock.calls[0];
    expect(profileArg).toBe('p1');
    expect(body.name).toBe('קומה 6');
    expect(body.day_schedules['0']).toEqual({ start: '07:00', end: '15:00' });
    expect(body.required_attributes).toEqual(['armed']);
  });

  it('blocks save when no day is active', async () => {
    renderPage();
    await screen.findByText('ארנונה');

    fireEvent.click(screen.getByText('עמדה חדשה'));
    fireEvent.change(screen.getByLabelText('שם העמדה'), { target: { value: 'בלי ימים' } });
    fireEvent.click(screen.getByText('שמור'));

    await waitFor(() => expect(toast.error).toHaveBeenCalled());
    expect(createPosition).not.toHaveBeenCalled();
  });

  it('deletes a position after confirmation', async () => {
    deletePosition.mockResolvedValue(null);
    renderPage();
    await screen.findByText('ארנונה');

    fireEvent.click(screen.getByText('מחק')); // opens confirm
    const buttons = screen.getAllByText('מחק');
    fireEvent.click(buttons[buttons.length - 1]);

    await waitFor(() => expect(deletePosition).toHaveBeenCalledWith('pos1'));
  });
});
