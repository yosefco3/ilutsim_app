import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';

// Control auth state per-test
const isLoggedIn = vi.fn();
vi.mock('../src/api/adminApiClient', () => ({
  isLoggedIn: () => isLoggedIn(),
  adminLogout: vi.fn(),
}));

import Navbar from '../src/components/Navbar';
import messages from '../src/utils/messages';

function renderNavbar() {
  render(
    <MemoryRouter>
      <Navbar />
    </MemoryRouter>,
  );
}

describe('Navbar links', () => {
  beforeEach(() => {
    isLoggedIn.mockReset();
  });

  it('shows the submissions link when authenticated', () => {
    isLoggedIn.mockReturnValue(true);
    renderNavbar();
    const link = screen.getByRole('link', { name: messages.nav.submissions });
    expect(link).toHaveAttribute('href', '/submissions');
  });

  it('shows events and export links when authenticated', () => {
    isLoggedIn.mockReturnValue(true);
    renderNavbar();
    expect(screen.getByRole('link', { name: messages.nav.events })).toHaveAttribute('href', '/events');
    expect(screen.getByRole('link', { name: messages.nav.export })).toHaveAttribute('href', '/export');
  });

  it('hides app links when not authenticated', () => {
    isLoggedIn.mockReturnValue(false);
    renderNavbar();
    expect(screen.queryByRole('link', { name: messages.nav.submissions })).toBeNull();
    expect(screen.getByRole('link', { name: messages.nav.login })).toBeInTheDocument();
  });
});
