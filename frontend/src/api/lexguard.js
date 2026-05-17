/**
 * LexGuard API Client
 * Axios-based client for all backend interactions.
 */

import axios from 'axios'

const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api'

const api = axios.create({
  baseURL: API_BASE,
  timeout: 300000, // 5 minutes — analysis can take a while
  headers: {
    Accept: 'application/json',
  },
})

/**
 * Upload a contract document.
 * @param {File} file - The file to upload
 * @returns {Promise<Object>} Upload response with document_id
 */
export async function uploadContract(file) {
  const formData = new FormData()
  formData.append('file', file)

  const response = await api.post('/upload', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  })
  return response.data
}

/**
 * Upload raw contract text (pasted into textarea).
 * @param {string} text - The contract text
 * @param {string} filename - Optional filename for metadata
 */
export async function uploadText(text, filename = 'pasted_contract.txt') {
  const response = await api.post('/upload_text', { text, filename })
  return response.data
}

/**
 * Run full analysis on an uploaded document.
 * @param {string} documentId - The document ID from upload
 * @returns {Promise<Object>} Analysis report
 */
export async function analyzeContract(documentId) {
  if (!documentId) {
    throw new Error('Missing document id for analysis')
  }
  const response = await api.post('/analyze', {
    document_id: documentId,
  })
  return response.data
}

/**
 * Get a cached analysis report.
 * @param {string} reportId - The report ID
 * @returns {Promise<Object>} Analysis report
 */
export async function getReport(reportId) {
  const response = await api.get(`/report/${reportId}`)
  return response.data
}

/**
 * Download the analysis report as PDF.
 * @param {string} reportId - The report ID
 */
export async function downloadPDF(reportId) {
  const response = await api.get(`/report/${reportId}/pdf`, {
    responseType: 'blob',
  })

  // Create download link
  const url = window.URL.createObjectURL(new Blob([response.data]))
  const link = document.createElement('a')
  link.href = url
  link.setAttribute('download', `lexguard_report_${reportId}.pdf`)
  document.body.appendChild(link)
  link.click()
  link.remove()
  window.URL.revokeObjectURL(url)
}

/**
 * Compare two analyzed contracts.
 * @param {string} docId1 - First document ID
 * @param {string} docId2 - Second document ID
 * @returns {Promise<Object>} Comparison results
 */
export async function compareContracts(docId1, docId2) {
  const response = await api.post('/compare', {
    document_id_1: docId1,
    document_id_2: docId2,
  })
  return response.data
}

export default api
