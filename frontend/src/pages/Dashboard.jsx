/**
 * Dashboard Page — Main analysis results view.
 * Shows risk gauge, severity breakdown, executive summary, and clause cards.
 */

import { useState, useEffect, useMemo } from 'react'
import { useNavigate } from 'react-router-dom'
import { motion } from 'framer-motion'
import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip, BarChart, Bar, XAxis, YAxis } from 'recharts'
import RiskMeter from '../components/RiskMeter'
import ClauseCard from '../components/ClauseCard'
import ExportButton from '../components/ExportButton'

const SEVERITY_COLORS = {
  CRITICAL: '#ef233c',
  HIGH: '#ff6b35',
  MEDIUM: '#f7b32b',
  LOW: '#2ec4b6',
  NONE: '#6c757d',
}

const SEVERITY_ORDER = ['CRITICAL', 'HIGH', 'MEDIUM', 'LOW', 'NONE']

export default function Dashboard() {
  const [report, setReport] = useState(null)
  const [filter, setFilter] = useState('ALL')
  const navigate = useNavigate()

  useEffect(() => {
    const stored = sessionStorage.getItem('lexguard_report')
    if (stored) {
      try { setReport(JSON.parse(stored)) } catch { navigate('/') }
    } else { navigate('/') }
  }, [navigate])

  const filteredClauses = useMemo(() => {
    if (!report?.analyzed_clauses) return []
    if (filter === 'ALL') return report.analyzed_clauses
    return report.analyzed_clauses.filter((c) => c.max_severity === filter)
  }, [report, filter])

  const pieData = useMemo(() => {
    if (!report?.score?.breakdown) return []
    const b = report.score.breakdown
    return SEVERITY_ORDER.filter((s) => (b[s] || 0) > 0).map((s) => ({ name: s, value: b[s], color: SEVERITY_COLORS[s] }))
  }, [report])

  const categoryData = useMemo(() => {
    if (!report?.category_breakdown) return []
    return Object.entries(report.category_breakdown).map(([name, value]) => ({
      name: name.charAt(0) + name.slice(1).toLowerCase(), count: value,
    }))
  }, [report])

  if (!report) return <div className="loading-container"><div className="spinner" /><p className="loading-text">Loading...</p></div>

  const { score, executive_summary, filename, flagged_clauses, total_clauses } = report
  const tooltipStyle = { background: 'rgba(15,15,30,0.95)', border: '1px solid rgba(255,255,255,0.1)', borderRadius: '8px', fontSize: '0.8rem', color: '#e8e8f0' }

  return (
    <div className="animate-fade-in">
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '32px', flexWrap: 'wrap', gap: '16px' }}>
        <div>
          <h1 style={{ marginBottom: '6px' }}>Analysis Report</h1>
          <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem' }}>📄 {filename}</p>
        </div>
        <div style={{ display: 'flex', gap: '8px' }}>
          <ExportButton reportId={report.report_id} />
          <button className="btn btn-ghost" onClick={() => navigate('/')}>＋ New Analysis</button>
        </div>
      </div>

      <div className="score-section">
        <RiskMeter score={score?.overall_score || 0} grade={score?.grade || 'N/A'} />
        <div className="score-stats">
          <div className="stat-card"><div className="stat-value">{total_clauses}</div><div className="stat-label">Total Clauses</div></div>
          <div className="stat-card"><div className="stat-value" style={{ color: 'var(--severity-critical)' }}>{flagged_clauses}</div><div className="stat-label">Flagged</div></div>
          <div className="stat-card"><div className="stat-value" style={{ color: 'var(--severity-critical)' }}>{score?.breakdown?.CRITICAL || 0}</div><div className="stat-label">Critical</div></div>
          <div className="stat-card"><div className="stat-value" style={{ color: 'var(--severity-high)' }}>{score?.breakdown?.HIGH || 0}</div><div className="stat-label">High Risk</div></div>
        </div>
      </div>

      {pieData.length > 0 && (
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '24px', marginBottom: '40px' }}>
          <motion.div className="glass-card" initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.2 }}>
            <h3 style={{ fontSize: '0.85rem', color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.1em', marginBottom: '16px' }}>Severity Distribution</h3>
            <ResponsiveContainer width="100%" height={200}>
              <PieChart><Pie data={pieData} cx="50%" cy="50%" innerRadius={50} outerRadius={80} paddingAngle={4} dataKey="value">
                {pieData.map((e, i) => <Cell key={i} fill={e.color} stroke="transparent" />)}
              </Pie><Tooltip contentStyle={tooltipStyle} /></PieChart>
            </ResponsiveContainer>
            <div style={{ display: 'flex', gap: '12px', justifyContent: 'center', flexWrap: 'wrap' }}>
              {pieData.map((d) => <div key={d.name} style={{ display: 'flex', alignItems: 'center', gap: '6px', fontSize: '0.75rem' }}><div style={{ width: 8, height: 8, borderRadius: '50%', background: d.color }} /><span style={{ color: 'var(--text-secondary)' }}>{d.name}: {d.value}</span></div>)}
            </div>
          </motion.div>
          {categoryData.length > 0 && (
            <motion.div className="glass-card" initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.3 }}>
              <h3 style={{ fontSize: '0.85rem', color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.1em', marginBottom: '16px' }}>Risk Categories</h3>
              <ResponsiveContainer width="100%" height={200}>
                <BarChart data={categoryData} layout="vertical"><XAxis type="number" hide /><YAxis dataKey="name" type="category" width={80} tick={{ fill: '#8b8ba0', fontSize: 11 }} axisLine={false} tickLine={false} /><Bar dataKey="count" radius={[0, 4, 4, 0]} fill="#4361ee" /><Tooltip contentStyle={tooltipStyle} /></BarChart>
              </ResponsiveContainer>
            </motion.div>
          )}
        </div>
      )}

      {executive_summary && (
        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.4 }} style={{ marginBottom: '40px' }}>
          <div className="section-header"><h2 className="section-title">Executive Summary</h2></div>
          <div className="executive-summary">{executive_summary.split('\n').filter(Boolean).map((p, i) => <p key={i}>{p}</p>)}</div>
        </motion.div>
      )}

      <div>
        <div className="section-header"><h2 className="section-title">Analyzed Clauses</h2><span className="section-count">{filteredClauses.length} clauses</span></div>
        <div className="filter-tabs">
          <button className={`filter-tab ${filter === 'ALL' ? 'active' : ''}`} onClick={() => setFilter('ALL')}>All</button>
          {SEVERITY_ORDER.filter((s) => s !== 'NONE').map((s) => <button key={s} className={`filter-tab ${filter === s ? 'active' : ''}`} onClick={() => setFilter(s)}>{s} ({report.score?.breakdown?.[s] || 0})</button>)}
        </div>
        <div className="clauses-grid">
          {filteredClauses.map((entry, i) => {
            const clause = entry.clause || entry
            const bestResult = entry.agent_results?.length ? entry.agent_results.reduce((best, r) => { const o = { CRITICAL: 4, HIGH: 3, MEDIUM: 2, LOW: 1, NONE: 0 }; return (o[r.severity] || 0) > (o[best.severity] || 0) ? r : best }, entry.agent_results[0]) : (entry.risk_analysis || {})
            return <ClauseCard key={clause.clause_id || i} clause={clause} analysis={bestResult} severity={entry.max_severity || 'NONE'} index={i} onClick={() => { sessionStorage.setItem('lexguard_clause_detail', JSON.stringify(entry)); navigate(`/clause/${clause.clause_id}`) }} />
          })}
        </div>
        {filteredClauses.length === 0 && <div style={{ textAlign: 'center', padding: '40px', color: 'var(--text-muted)' }}>No clauses match this filter.</div>}
      </div>
    </div>
  )
}
