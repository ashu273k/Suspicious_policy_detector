/**
 * ClauseCard — Color-coded card for displaying a clause with severity badge.
 */

import { motion } from 'framer-motion'
import FlagBadge from './FlagBadge'

export default function ClauseCard({ clause, analysis, severity, index, onClick }) {
  const clauseType = clause?.clause_type || 'GENERAL'
  const summary = clause?.summary || analysis?.risk_summary || analysis?.plain_english || ''

  // Format clause type for display
  const displayType = clauseType.replace(/_/g, ' ')

  return (
    <motion.div
      className="clause-card"
      initial={{ opacity: 0, x: -20 }}
      animate={{ opacity: 1, x: 0 }}
      transition={{ delay: index * 0.05, duration: 0.3 }}
      onClick={onClick}
      role="button"
      tabIndex={0}
      aria-label={`Open clause ${clause?.clause_id || index + 1} details`}
      onKeyDown={(e) => {
        if (e.key === 'Enter' || e.key === ' ') {
          e.preventDefault()
          onClick?.()
        }
      }}
    >
      {/* Severity bar */}
      <div className={`clause-card-severity ${severity?.toLowerCase() || 'none'}`} />

      {/* Content */}
      <div className="clause-card-content">
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '6px' }}>
          <h4>Clause {clause?.clause_id}: {displayType}</h4>
          <FlagBadge severity={severity || 'NONE'} />
        </div>
        <p className="clause-card-summary">{summary}</p>
      </div>

      {/* Arrow */}
      <span className="clause-card-arrow">→</span>
    </motion.div>
  )
}
