import { BrowserRouter as Router, Routes, Route, NavLink } from 'react-router-dom'
import Upload from './pages/Upload'
import Dashboard from './pages/Dashboard'
import ClauseDetail from './pages/ClauseDetail'

function App() {
  return (
    <Router>
      <a className="skip-link" href="#main-content">
        Skip to content
      </a>
      <div className="app-container">
        {/* Navigation */}
        <nav className="navbar">
          <NavLink to="/" className="navbar-brand">
            <span className="navbar-logo">🛡️</span>
            <div>
              <div className="navbar-title">LexGuard</div>
              <div className="navbar-subtitle">AI Contract Intelligence</div>
            </div>
          </NavLink>
          <div className="navbar-nav">
            <NavLink
              to="/"
              className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}
              end
            >
              Upload
            </NavLink>
            <NavLink
              to="/dashboard"
              className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}
            >
              Dashboard
            </NavLink>
          </div>
        </nav>

        {/* Routes */}
        <main id="main-content" tabIndex={-1}>
          <Routes>
            <Route path="/" element={<Upload />} />
            <Route path="/dashboard" element={<Dashboard />} />
            <Route path="/clause/:clauseId" element={<ClauseDetail />} />
          </Routes>
        </main>
      </div>
    </Router>
  )
}

export default App
