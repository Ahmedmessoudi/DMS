// src/api.js
import axios from 'axios';

const API = axios.create({
  baseURL: 'http://localhost:5000/api', // Added /api prefix which is common for backend APIs
  timeout: 10000, // Set timeout to 10 seconds
});

// Add Authorization header with token
API.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Add response interceptor to handle errors globally
API.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response) {
      // The request was made and the server responded with a status code
      // that falls out of the range of 2xx
      console.error('API Error:', error.response.data);
      
      if (error.response.status === 401) {
        // Handle unauthorized access (token expired, invalid, etc.)
        localStorage.removeItem('token');
        window.location.href = '/login'; // Redirect to login
      }
    } else if (error.request) {
      // The request was made but no response was received
      console.error('API Error: No response received', error.request);
    } else {
      // Something happened in setting up the request that triggered an Error
      console.error('API Error:', error.message);
    }
    
    return Promise.reject(error);
  }
);

// Folder-related API endpoints
const folders = {
  getAll: () => API.get('/folders'),
  create: (folderData) => API.post('/folders', folderData),
  update: (id, folderData) => API.put(`/folders/${id}`, folderData),
  delete: (id) => API.delete(`/folders/${id}`),
  getById: (id) => API.get(`/folders/${id}`),
};

// User-related API endpoints
const users = {
  login: (credentials) => API.post('/auth/login', credentials),
  verifyToken: () => API.get('/auth/verify'),
};

// Document-related API endpoints
const documents = {
  upload: (fileData) => API.post('/documents', fileData, {
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  }),
  getByFolder: (folderId) => API.get(`/documents?folder_id=${folderId}`),
};
// Create a named object before exporting
const apiInstance = {
  ...API,
  folders,
  users,
  documents
};

export default apiInstance;