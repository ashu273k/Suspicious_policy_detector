/**
 * ClauseDetail Page — Per-clause drill-down with full analysis.
 */

import { useState, useEffect } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import { motion } from 'framer-motion'
import FlagBadge from '../components/FlagBadge'

export default function ClauseDetail() {
  const [data, setData] = useState(null)
  const navigate = useNavigate()
  const { clauseId } = useParams()

  useEffect(() => {
    const stored = sessionStorage.getItem('lexguard_clause_detail')
    if (stored) {
      try { setData(JSON.parse(stored)) } catch { navigate('/dashboard') }
    } else { navigate('/dashboard') }
  }, [navigate])

  if (!data) return <div className="loading-container"><div className="spinner" /></div>

  const clause = data.clause || {}
  const severity = data.max_severity || 'NONE'
  const agents = data.agent_results || []
  const primary = data.risk_analysis || agents.reduce((best, r) => {
    const o = { CRITICAL: 4, HIGH: 3, MEDIUM: 2, LOW: 1, NONE: 0 }
    return (o[r.severity] || 0) > (o[best?.severity] || 0) ? r : best
  }, agents[0]) || {}

  const displayType = (clause.clause_type || 'GENERAL').replace(/_/g, ' ')

  return (
    <div className="clause-detail animate-fade-in-up">
      <button className="back-btn" onClick={() => navigate('/dashboard')}>← Back to Dashboard</button>

      <motion.div className="clause-detail-header" initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '16px', marginBottom: '8px', flexWrap: 'wrap' }}>
          <h1 style={{ fontSize: '1.5rem' }}>Clause {clause.clause_id}: {displayType}</h1>
          <FlagBadge severity={severity} />
        </div>
        {clause.parties_affected && (
          <p style={{ color: 'var(--text-muted)', fontSize: '0.85rem' }}>Affects: {clause.parties_affected}</p>
        )}
      </motion.div>

      {/* Original Text */}
      <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.1 }}>
        <div className="detail-section">
          <h3>Original Contract Text</h3>
          <div className="clause-original-text">{clause.original_text || 'No text available'}</div>
        </div>
      </motion.div>

      {/* Plain English */}
      {primary.plain_english && (
        <motion.div className="glass-card" style={{ marginBottom: '24px' }} initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.2 }}>
          <div className="detail-section" style={{ marginBottom: 0 }}>
            <h3>💡 What This Actually Means</h3>
            <p>{primary.plain_english}</p>
          </div>
        </motion.div>
      )}

      {/* Risk Summary */}
      {primary.risk_summary && (
        <motion.div className="detail-section" initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.25 }}>
          <h3>⚠️ Risk Summary</h3>
          <p>{primary.risk_summary}</p>
        </motion.div>
      )}

      {/* Real World Impact */}
      {primary.real_world_impact && (
        <motion.div className="detail-section" initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.3 }}>
          <h3>🌍 Real-World Impact</h3>
          <p>{primary.real_world_impact}</p>
        </motion.div>
      )}

      {/* Red Flags */}
      {primary.red_flags?.length > 0 && (
        <motion.div className="detail-section" initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.35 }}>
          <h3>🚩 Red Flags</h3>
          <ul className="red-flags-list">
            {primary.red_flags.map((flag, i) => <li key={i} className="red-flag-tag">{flag}</li>)}
          </ul>
        </motion.div>
      )}

      {/* Negotiation Tip */}
      {(primary.negotiation_tip || primary.recommendation) && (
        <motion.div className="detail-section" initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.4 }}>
          <h3>💬 Negotiation Tip</h3>
          <div className="negotiation-tip">{primary.negotiation_tip || primary.recommendation}</div>
        </motion.div>
      )}

      {/* Standard clause indicator */}
      {primary.is_standard !== undefined && (
        <motion.div className="detail-section" initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.45 }}>
          <h3>📋 Industry Standard?</h3>
          <p>{primary.is_standard ? '✅ This is a standard industry clause.' : '❌ This clause is unusually one-sided compared to industry norms.'}</p>
        </motion.div>
      )}

      {/* Agent Results */}
      {agents.length > 1 && (
        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.5 }} style={{ marginTop: '32px' }}>
          <h3 style={{ fontSize: '0.85rem', textTransform: 'uppercase', letterSpacing: '0.1em', color: 'var(--text-muted)', marginBottom: '16px' }}>All Agent Analyses</h3>
          <div style={{ display: 'grid', gap: '12px' }}>
            {agents.map((r, i) => (
              <div key={i} className="glass-card" style={{ padding: '20px' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px' }}>
                  <span style={{ fontSize: '0.85rem', fontWeight: 600 }}>{r.agent || `Agent ${i + 1}`}</span>
                  <FlagBadge severity={r.severity || 'NONE'} />
                </div>
                {r.plain_english && <p style={{ fontSize: '0.85rem', color: 'var(--text-secondary)' }}>{r.plain_english}</p>}
                {r.risk_summary && <p style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', marginTop: '4px' }}>{r.risk_summary}</p>}
              </div>
            ))}
          </div>
        </motion.div>
      )}
    </div>
  )
}
