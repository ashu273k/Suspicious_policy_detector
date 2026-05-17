/**
 * FlagBadge — Severity indicator badge with color coding.
 */

export default function FlagBadge({ severity = 'NONE' }) {
  const severityClass = severity.toLowerCase()
  const icons = {
    CRITICAL: '🔴',
    HIGH: '🟠',
    MEDIUM: '🟡',
    LOW: '🟢',
    NONE: '⚪',
  }

  return (
    <span className={`badge badge-${severityClass}`}>
      <span>{icons[severity] || '⚪'}</span>
      {severity}
    </span>
  )
}
