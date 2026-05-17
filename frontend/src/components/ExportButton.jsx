/**
 * ExportButton — PDF download button with loading state.
 */

import { useState } from 'react'
import { motion } from 'framer-motion'
import { downloadPDF } from '../api/lexguard'

export default function ExportButton({ reportId }) {
  const [loading, setLoading] = useState(false)
  const [success, setSuccess] = useState(false)

  const handleExport = async () => {
    if (!reportId || loading) return

    setLoading(true)
    setSuccess(false)

    try {
      await downloadPDF(reportId)
      setSuccess(true)
      setTimeout(() => setSuccess(false), 3000)
    } catch (err) {
      console.error('PDF export failed:', err)
      alert('Failed to export PDF. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <motion.button
      className="btn btn-secondary"
      onClick={handleExport}
      disabled={loading || !reportId}
      whileHover={{ scale: 1.02 }}
      whileTap={{ scale: 0.98 }}
    >
      {loading ? (
        <>
          <span className="spinner" style={{ width: 16, height: 16, borderWidth: 2 }} />
          Exporting...
        </>
      ) : success ? (
        <>✅ Downloaded</>
      ) : (
        <>📥 Export PDF</>
      )}
    </motion.button>
  )
}
