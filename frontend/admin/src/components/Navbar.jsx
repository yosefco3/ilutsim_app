import { NavLink, useNavigate } from 'react-router-dom';
import { adminLogout, isLoggedIn } from '../api/adminApiClient';
import messages from '../utils/messages';

export default function Navbar() {
  const navigate = useNavigate();
  const authenticated = isLoggedIn();

  const handleLogout = () => {
    adminLogout();
    navigate('/login');
  };

  if (!authenticated) {
    return (
      <nav className="navbar">
        <div className="navbar-brand">{messages.app.title}</div>
        <div className="navbar-links">
          <NavLink to="/login">{messages.nav.login}</NavLink>
        </div>
      </nav>
    );
  }

  return (
    <nav className="navbar">
      <div className="navbar-brand">{messages.app.title}</div>
      <div className="navbar-links">
        <NavLink to="/guards">{messages.nav.guards}</NavLink>
        <NavLink to="/weeks">{messages.nav.weeks}</NavLink>
        <NavLink to="/submissions">{messages.nav.submissions}</NavLink>
        <NavLink to="/import">{messages.nav.import}</NavLink>
        <NavLink to="/export">{messages.nav.export}</NavLink>
        <NavLink to="/settings">{messages.nav.settings}</NavLink>
        <span className="navbar-group-sep" aria-hidden="true">|</span>
        <span className="navbar-group-label">{messages.nav.builderGroup}</span>
        <NavLink to="/builder/profiles">{messages.nav.profiles}</NavLink>
        <button className="btn btn-secondary btn-sm" onClick={handleLogout}>
          {messages.nav.logout}
        </button>
      </div>
    </nav>
  );
}
