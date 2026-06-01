import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000'

export const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
})

function extractErrorMessage(err) {
  if (!err) return 'Unknown error'
  if (err.response?.data) {
    const d = err.response.data
    if (typeof d === 'string') return d
    if (d?.detail) return d.detail
    if (d?.message) return d.message
    return JSON.stringify(d)
  }
  if (err.message) return err.message
  return 'Request failed'
}

api.interceptors.response.use(
  (res) => res,
  (err) => {
    // Normalize error so UI can be consistent
    err.normalizedMessage = extractErrorMessage(err)
    return Promise.reject(err)
  }
)

export function getErrorMessage(err) {
  return err?.normalizedMessage || extractErrorMessage(err)
}

