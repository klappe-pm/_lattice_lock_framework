import { Outlet, NavLink, useLocation } from 'react-router-dom';
import { useUIStore } from '../../store';
import './AppShell.css';

// Icons as simple SVGs for Material Design style
const DashboardIcon = () => (
  <svg xmlns="http://www.w3.org/2000/svg" height="24" viewBox="0 -960 960 960" width="24" fill="currentColor">
    <path d="M520-600v-240h320v240H520ZM120-440v-400h320v400H120Zm400 320v-400h320v400H520Zm-400 0v-240h320v240H120Zm80-400h160v-240H200v240Zm400 320h160v-240H600v240Zm0-480h160v-80H600v80ZM200-200h160v-80H200v80Zm160-320Zm240-160Zm0 240ZM360-280Z"/>
  </svg>
);

const ModelsIcon = () => (
  <svg xmlns="http://www.w3.org/2000/svg" height="24" viewBox="0 -960 960 960" width="24" fill="currentColor">
    <path d="M480-400q-50 0-85-35t-35-85q0-50 35-85t85-35q50 0 85 35t35 85q0 50-35 85t-85 35Zm0-80q17 0 28.5-11.5T520-520q0-17-11.5-28.5T480-560q-17 0-28.5 11.5T440-520q0 17 11.5 28.5T480-480ZM160-120v-160q0-33 23.5-56.5T240-360h80q20 0 37 8t29 22q32 36 78 53t96 17q50 0 96-17t78-53q12-14 29-22t37-8h80q33 0 56.5 23.5T960-280v160H640v-80q-38 22-78.5 31T480-160q-41 0-81.5-9T320-200v80H160Zm80-80h80v-41l6-4 18-9q32-16 68-21t68-5q32 0 68 5t68 21l18 9 6 4v41h80v-80q-44-36-100-58t-120-22q-64 0-120 22t-100 58v80Zm240-200Z"/>
  </svg>
);

const ExecuteIcon = () => (
  <svg xmlns="http://www.w3.org/2000/svg" height="24" viewBox="0 -960 960 960" width="24" fill="currentColor">
    <path d="M320-200v-560l440 280-440 280Zm80-280Zm0 134 210-134-210-134v268Z"/>
  </svg>
);

const HistoryIcon = () => (
  <svg xmlns="http://www.w3.org/2000/svg" height="24" viewBox="0 -960 960 960" width="24" fill="currentColor">
    <path d="M480-120q-138 0-240.5-91.5T122-440h82q14 104 92.5 172T480-200q117 0 198.5-81.5T760-480q0-117-81.5-198.5T480-760q-69 0-129 32t-101 88h110v80H120v-240h80v94q51-64 124.5-99T480-840q75 0 140.5 28.5t114 77q48.5 48.5 77 114T840-480q0 75-28.5 140.5t-77 114q-48.5 48.5-114 77T480-120Zm112-192L440-464v-216h80v184l128 128-56 56Z"/>
  </svg>
);

const SettingsIcon = () => (
  <svg xmlns="http://www.w3.org/2000/svg" height="24" viewBox="0 -960 960 960" width="24" fill="currentColor">
    <path d="m370-80-16-128q-13-5-24.5-12T307-235l-119 50L78-375l103-78q-1-7-1-13.5v-27q0-6.5 1-13.5L78-585l110-190 119 50q11-8 23-15t24-12l16-128h220l16 128q13 5 24.5 12t22.5 15l119-50 110 190-103 78q1 7 1 13.5v27q0 6.5-2 13.5l103 78-110 190-118-50q-11 8-23 15t-24 12L590-80H370Zm70-80h79l14-106q31-8 57.5-23.5T639-327l99 41 39-68-86-65q5-14 7-29.5t2-31.5q0-16-2-31.5t-7-29.5l86-65-39-68-99 42q-22-23-48.5-38.5T533-694l-13-106h-79l-14 106q-31 8-57.5 23.5T321-beckoned633l-99-41-39 68 86 64q-5 15-7 30t-2 32q0 16 2 31t7 30l-86 65 39 68 99-42q22 23 48.5 38.5T427-266l13 106Zm42-180q58 0 99-41t41-99q0-58-41-99t-99-41q-59 0-99.5 41T342-480q0 58 40.5 99t99.5 41Zm-2-140Z"/>
  </svg>
);

const MenuIcon = () => (
  <svg xmlns="http://www.w3.org/2000/svg" height="24" viewBox="0 -960 960 960" width="24" fill="currentColor">
    <path d="M120-240v-80h720v80H120Zm0-200v-80h720v80H120Zm0-200v-80h720v80H120Z"/>
  </svg>
);

const navItems = [
  { path: '/', label: 'Dashboard', icon: DashboardIcon },
  { path: '/models', label: 'Models', icon: ModelsIcon },
  { path: '/execute', label: 'Execute', icon: ExecuteIcon },
  { path: '/history', label: 'History', icon: HistoryIcon },
];

export default function AppShell() {
  const location = useLocation();
  const { isSidebarCollapsed, toggleSidebar } = useUIStore();

  const getPageTitle = () => {
    const currentItem = navItems.find((item) => item.path === location.pathname);
    return currentItem?.label || 'Lattice Lock';
  };

  return (
    <div className={`app-shell ${isSidebarCollapsed ? 'collapsed' : ''}`}>
      {/* Navigation Rail */}
      <nav className="navigation-rail">
        <div className="nav-header">
          <button className="btn btn-icon" onClick={toggleSidebar} title="Toggle menu">
            <MenuIcon />
          </button>
        </div>

        <div className="nav-items">
          {navItems.map(({ path, label, icon: Icon }) => (
            <NavLink
              key={path}
              to={path}
              className={({ isActive }) =>
                `nav-item ${isActive ? 'active' : ''}`
              }
              title={label}
            >
              <div className="nav-icon">
                <Icon />
              </div>
              <span className="nav-label">{label}</span>
            </NavLink>
          ))}
        </div>

        <div className="nav-footer">
          <NavLink to="/settings" className="nav-item" title="Settings">
            <div className="nav-icon">
              <SettingsIcon />
            </div>
            <span className="nav-label">Settings</span>
          </NavLink>
        </div>
      </nav>

      {/* Main Content Area */}
      <div className="main-container">
        {/* Top App Bar */}
        <header className="top-app-bar">
          <h1 className="page-title">{getPageTitle()}</h1>
          <div className="app-bar-actions">
            <div className="connection-status status-indicator status-online">
              <span className="status-dot"></span>
              <span>Connected</span>
            </div>
          </div>
        </header>

        {/* Page Content */}
        <main className="page-content">
          <Outlet />
        </main>
      </div>
    </div>
  );
}
