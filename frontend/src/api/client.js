import axios from 'axios';

const API_BASE = 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE,
  timeout: 120000, // 2 min timeout for analysis
});

/**
 * Verify a document by uploading it to the backend.
 * @param {File} documentFile - The document file
 * @param {File|null} selfieFile - Optional selfie
 * @param {function} onUploadProgress - Progress callback
 * @returns {Promise<Object>} Verification result
 */
export async function verifyDocument(documentFile, selfieFile = null, onUploadProgress = null) {
  const formData = new FormData();
  formData.append('document', documentFile);
  if (selfieFile) {
    formData.append('selfie', selfieFile);
  }

  const response = await api.post('/api/verify', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
    onUploadProgress,
  });

  return response.data;
}

/**
 * Get verification history from backend.
 */
export async function getHistory() {
  const response = await api.get('/api/history');
  return response.data;
}

/**
 * Health check
 */
export async function checkHealth() {
  try {
    const response = await api.get('/api/health');
    return { ok: true, data: response.data };
  } catch (e) {
    return { ok: false, error: e.message };
  }
}

export default api;
