/**
 * Upload Page — Drag-and-drop file upload with progress and analysis trigger.
 */

import { useState, useRef, useCallback } from 'react'
import { useNavigate } from 'react-router-dom'
import { motion, AnimatePresence } from 'framer-motion'
import { uploadContract, uploadText, analyzeContract } from '../api/lexguard'

const STEPS = [
  { label: 'Uploading document', icon: '📤' },
  { label: 'Extracting clauses', icon: '🔍' },
  { label: 'Running AI agents', icon: '🤖' },
  { label: 'Scoring risks', icon: '📊' },
  { label: 'Generating report', icon: '📝' },
]

export default function Upload() {
  const [dragOver, setDragOver] = useState(false)
  const [file, setFile] = useState(null)
  const [status, setStatus] = useState('idle') // idle | uploading | analyzing | done | error
  const [currentStep, setCurrentStep] = useState(0)
  const [error, setError] = useState(null)
  const [pasteMode, setPasteMode] = useState(false)
  const [pastedText, setPastedText] = useState('')
  const fileRef = useRef(null)
  const navigate = useNavigate()

  const handleFile = useCallback(async (selectedFile) => {
    // Validate file type
    const validTypes = ['.pdf', '.docx', '.doc', '.txt']
    const ext = '.' + selectedFile.name.split('.').pop().toLowerCase()
    if (!validTypes.includes(ext)) {
      setError(`Unsupported file type "${ext}". Please upload PDF, DOCX, or TXT files.`)
      return
    }

    setFile(selectedFile)
    setError(null)
    setStatus('uploading')
    setCurrentStep(0)

    try {
      // Step 1: Upload
      const uploadResult = await uploadContract(selectedFile)
      if (!uploadResult?.document_id) {
        throw new Error('Upload succeeded but no document id was returned')
      }

      // Steps 2-5: Analyze
      setStatus('analyzing')
      setCurrentStep(1)

      // Simulate step progression while analysis runs
      const stepInterval = setInterval(() => {
        setCurrentStep((prev) => Math.min(prev + 1, STEPS.length - 1))
      }, 8000)

      const report = await analyzeContract(uploadResult.document_id)

      clearInterval(stepInterval)
      setCurrentStep(STEPS.length - 1)
      setStatus('done')

      // Store report in sessionStorage and navigate
      sessionStorage.setItem('lexguard_report', JSON.stringify(report))
      setTimeout(() => navigate('/dashboard'), 800)
    } catch (err) {
      setStatus('error')
      setError(err.response?.data?.detail || err.message || 'Analysis failed. Please try again.')
    }
  }, [navigate])

  const handleDrop = useCallback((e) => {
    e.preventDefault()
    setDragOver(false)
    const droppedFile = e.dataTransfer.files[0]
    if (droppedFile) handleFile(droppedFile)
  }, [handleFile])

  const handleUploadZoneKeyDown = useCallback((e) => {
    if (e.key === 'Enter' || e.key === ' ') {
      e.preventDefault()
      handleBrowse()
    }
  }, [handleBrowse])

  const handleDragOver = useCallback((e) => {
    e.preventDefault()
    setDragOver(true)
  }, [])

  const handleDragLeave = useCallback(() => {
    setDragOver(false)
  }, [])

  const handleBrowse = useCallback(() => {
    fileRef.current?.click()
  }, [])

  const handleFileInput = useCallback((e) => {
    const selectedFile = e.target.files[0]
    if (selectedFile) handleFile(selectedFile)
  }, [handleFile])

  const handlePasteSubmit = useCallback(async () => {
    if (!pastedText || pastedText.trim().length === 0) {
      setError('Please paste some contract text before submitting.')
      return
    }

    setError(null)
    setStatus('uploading')
    setCurrentStep(0)

    try {
      const uploadResult = await uploadText(pastedText, 'pasted_contract.txt')
      if (!uploadResult?.document_id) {
        throw new Error('Upload succeeded but no document id was returned')
      }

      setStatus('analyzing')
      setCurrentStep(1)

      const stepInterval = setInterval(() => {
        setCurrentStep((prev) => Math.min(prev + 1, STEPS.length - 1))
      }, 8000)

      const report = await analyzeContract(uploadResult.document_id)

      clearInterval(stepInterval)
      setCurrentStep(STEPS.length - 1)
      setStatus('done')

      sessionStorage.setItem('lexguard_report', JSON.stringify(report))
      setTimeout(() => navigate('/dashboard'), 800)
    } catch (err) {
      setStatus('error')
      setError(err.response?.data?.detail || err.message || 'Analysis failed. Please try again.')
    }
  }, [pastedText, navigate])

  return (
    <div className="animate-fade-in-up">
      {/* Hero Section */}
      <div style={{ textAlign: 'center', marginBottom: '48px' }}>
        <motion.h1
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          style={{ marginBottom: '12px' }}
        >
          Analyze Your Contract
        </motion.h1>
        <motion.p
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
          style={{ color: 'var(--text-secondary)', fontSize: '1.05rem', maxWidth: '600px', margin: '0 auto' }}
        >
          Upload a legal document and our AI agents will identify risks,
          exploitative clauses, and missing protections — in plain English.
        </motion.p>
      </div>

      <AnimatePresence mode="wait">
        {status === 'idle' || status === 'error' ? (
          <motion.div
            key="upload"
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0, scale: 0.95 }}
          >
            {/* Upload Zone */}
            <div
              className={`upload-zone ${dragOver ? 'drag-over' : ''}`}
              onDrop={handleDrop}
              onDragOver={handleDragOver}
              onDragLeave={handleDragLeave}
              onClick={handleBrowse}
              role="button"
              tabIndex={0}
              onKeyDown={handleUploadZoneKeyDown}
              aria-label="Upload a contract file"
              aria-describedby="upload-help"
              id="upload-zone"
            >
              <span className="upload-icon">📄</span>
              <h2 className="upload-title">Drop your contract here</h2>
              <p className="upload-subtitle">or click to browse files</p>
              <p id="upload-help" className="sr-only">
                Press Enter or Space to open the file picker. You can upload PDF, DOCX, DOC, or TXT files.
              </p>
              <div className="upload-formats">
                <span className="format-tag">PDF</span>
                <span className="format-tag">DOCX</span>
                <span className="format-tag">TXT</span>
              </div>
              <input
                ref={fileRef}
                type="file"
                accept=".pdf,.docx,.doc,.txt"
                onChange={handleFileInput}
                style={{ display: 'none' }}
                id="file-input"
              />
            </div>

            <div style={{ textAlign: 'center', marginTop: '16px' }}>
              <button
                className="btn btn-ghost"
                onClick={() => setPasteMode((p) => !p)}
                style={{ marginTop: 12 }}
                type="button"
              >
                {pasteMode ? 'Use file upload' : 'Or paste contract text'}
              </button>
            </div>

            {pasteMode && (
              <motion.div
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                style={{ marginTop: 16 }}
              >
                <textarea
                  aria-label="Pasted contract text"
                  placeholder="Paste contract text here..."
                  value={pastedText}
                  onChange={(e) => setPastedText(e.target.value)}
                  rows={10}
                  style={{ width: '100%', padding: 12, borderRadius: 8, border: '1px solid var(--border)' }}
                />
                <div style={{ marginTop: 8, textAlign: 'right' }}>
                  <button className="btn" onClick={handlePasteSubmit} type="button">Analyze pasted text</button>
                </div>
              </motion.div>
            )}

            {/* Error message */}
            {error && (
              <motion.div
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                style={{
                  marginTop: '20px',
                  padding: '16px 24px',
                  background: 'var(--severity-critical-bg)',
                  border: '1px solid rgba(239, 35, 60, 0.25)',
                  borderRadius: 'var(--radius-md)',
                  color: 'var(--severity-critical)',
                  fontSize: '0.9rem',
                  textAlign: 'center',
                }}
              >
                ⚠️ {error}
              </motion.div>
            )}

            <div className="sr-only" aria-live="polite" aria-atomic="true">
              {status === 'uploading' && 'Uploading document.'}
              {status === 'analyzing' && 'Analyzing document.'}
              {status === 'done' && 'Analysis complete.'}
              {status === 'error' && (error || 'An error occurred.')}
            </div>
          </motion.div>
        ) : (
          <motion.div
            key="progress"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            className="glass-card"
            style={{ maxWidth: '600px', margin: '0 auto', textAlign: 'center' }}
          >
            {/* File info */}
            <div style={{ marginBottom: '32px' }}>
              <span style={{ fontSize: '2.5rem' }}>📄</span>
              <h3 style={{ marginTop: '12px', fontSize: '1.1rem' }}>{file?.name}</h3>
              <p style={{ color: 'var(--text-muted)', fontSize: '0.85rem' }}>
                {(file?.size / 1024).toFixed(1)} KB
              </p>
            </div>

            {/* Progress steps */}
            <div style={{ textAlign: 'left' }}>
              {STEPS.map((step, i) => (
                <motion.div
                  key={i}
                  initial={{ opacity: 0, x: -10 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: i * 0.1 }}
                  style={{
                    display: 'flex',
                    alignItems: 'center',
                    gap: '12px',
                    padding: '12px 16px',
                    borderRadius: 'var(--radius-sm)',
                    marginBottom: '4px',
                    background: i === currentStep ? 'var(--bg-glass-hover)' : 'transparent',
                    transition: 'all 0.3s ease',
                  }}
                >
                  <span style={{ fontSize: '1.2rem', minWidth: '28px', textAlign: 'center' }}>
                    {i < currentStep ? '✅' : i === currentStep ? step.icon : '⬜'}
                  </span>
                  <span style={{
                    fontSize: '0.9rem',
                    fontWeight: i === currentStep ? 600 : 400,
                    color: i <= currentStep ? 'var(--text-primary)' : 'var(--text-muted)',
                  }}>
                    {step.label}
                    {i === currentStep && status !== 'done' && '...'}
                  </span>
                  {i === currentStep && status !== 'done' && (
                    <div className="spinner" style={{ width: 16, height: 16, borderWidth: 2, marginLeft: 'auto' }} />
                  )}
                </motion.div>
              ))}
            </div>

            {/* Progress bar */}
            <div style={{ marginTop: '24px' }}>
              <div className="progress-bar">
                <div
                  className="progress-bar-fill"
                  style={{ width: `${((currentStep + 1) / STEPS.length) * 100}%` }}
                />
              </div>
              <p style={{ marginTop: '12px', fontSize: '0.8rem', color: 'var(--text-muted)' }}>
                {status === 'done' ? 'Analysis complete! Redirecting...' : 'This may take a minute for large documents'}
              </p>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Features */}
      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))',
        gap: '20px',
        marginTop: '60px',
      }}>
        {[
          { icon: '🔍', title: 'Clause Extraction', desc: 'Every clause identified and categorized automatically' },
          { icon: '🤖', title: 'Multi-Agent Analysis', desc: '5 specialized AI agents analyze different risk types' },
          { icon: '📊', title: 'Risk Scoring', desc: 'Severity-weighted scoring from A (safe) to F (dangerous)' },
          { icon: '💡', title: 'Plain English', desc: 'Complex legal jargon explained in everyday language' },
        ].map((feature, i) => (
          <motion.div
            key={i}
            className="glass-card"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 + i * 0.1 }}
            style={{ textAlign: 'center', padding: '28px 20px' }}
          >
            <span style={{ fontSize: '2rem', display: 'block', marginBottom: '12px' }}>{feature.icon}</span>
            <h3 style={{ fontSize: '0.95rem', marginBottom: '8px' }}>{feature.title}</h3>
            <p style={{ fontSize: '0.8rem', color: 'var(--text-secondary)' }}>{feature.desc}</p>
          </motion.div>
        ))}
      </div>
    </div>
  )
}
