import axios from 'axios';

const API_BASE_URL = 'https://badminton-backend-ixk8.onrender.com/api';
//http://127.0.0.1:8000/api
// Create axios instance with base configuration
const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add request interceptor to include auth token
apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Add response interceptor to handle token refresh
apiClient.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;

    // If401 and not already retried, try to refresh token
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;

      try {
        const refreshToken = localStorage.getItem('refresh_token');
        const response = await axios.post(`${API_BASE_URL}/auth/refresh/`, {
          refresh: refreshToken,
        });

        const { access } = response.data;
        localStorage.setItem('access_token', access);

        originalRequest.headers.Authorization = `Bearer ${access}`;
        return apiClient(originalRequest);
      } catch (refreshError) {
        // Refresh failed, logout user
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        window.location.href = '/login';
        return Promise.reject(refreshError);
      }
    }

    return Promise.reject(error);
  }
);

// Auth API
export const authAPI = {
  register: (data) => apiClient.post('/auth/register/', data),
  login: (data) => apiClient.post('/auth/login/', data),
  refresh: (refresh) => apiClient.post('/auth/refresh/', { refresh }),
};

// Resources API
export const resourcesAPI = {
  getCourts: () => apiClient.get('/courts/'),
  getEquipment: () => apiClient.get('/equipment/'),
  getCoaches: () => apiClient.get('/coaches/'),
};

// Booking API
export const bookingAPI = {

  createBooking: (data) => apiClient.post('/bookings/', data),
  getBookings: () => apiClient.get('/bookings/'),
  getBooking: (id) => apiClient.get(`/bookings/${id}/`),
  cancelBooking: (id) => apiClient.post(`/bookings/${id}/cancel/`),
  getHistory: () => apiClient.get('/bookings/history/'),
  getDailyMatrix: (date) => apiClient.get(`/daily-matrix/?date=${date}`),
  getAddonAvailability: (date, startTime, endTime) =>
    apiClient.get(`/addon-availability/?date=${date}&start_time=${startTime}&end_time=${endTime}`),
};

// Pricing API
export const pricingAPI = {
  getConfig: () => apiClient.get('/pricing/config/'),
};

export default apiClient;
