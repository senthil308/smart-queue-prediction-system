// ============================================================
// common.js — Shared across all pages
// ============================================================
const API_URL = 'http://127.0.0.1:5000/api';

// Axios interceptor: attach JWT from THIS tab's sessionStorage
axios.interceptors.request.use(config => {
    const token = sessionStorage.getItem('token');
    if (token) config.headers.Authorization = `Bearer ${token}`;
    return config;
});

// Axios interceptor: handle auth errors globally
axios.interceptors.response.use(response => response, error => {
    if (error.response) {
        if (error.response.status === 401) {
            sessionStorage.clear();
            window.location.href = '/login.html';
        } else if (error.response.status === 403 && error.response.data?.error?.includes('Detected role')) {
            alert('Role mismatch detected! Logging out...');
            sessionStorage.clear();
            window.location.href = '/login.html';
        }
    }
    return Promise.reject(error);
});

function getUsername() { return sessionStorage.getItem('username') || ''; }
function getRole()     { return sessionStorage.getItem('user_role') || 'user'; }
function getToken()    { return sessionStorage.getItem('token'); }

function logout() {
    sessionStorage.clear();
    window.location.href = '/login.html';
}

// Guard: redirect to login if not authenticated
function requireAuth() {
    if (!getToken()) window.location.href = '/login.html';
}

// Guard: redirect if not admin
function requireAdmin() {
    requireAuth();
    if (getRole() !== 'admin') window.location.href = '/user.html';
}

// Guard: redirect if not user
function requireUser() {
    requireAuth();
    if (getRole() === 'admin') window.location.href = '/admin.html';
}

// Set the username in navbar
function setNavUsername() {
    const el = document.getElementById('nav-username');
    if (el) el.textContent = getUsername();
}
