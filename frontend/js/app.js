const API_URL = 'http://127.0.0.1:5000/api';
let socket;
let currentPortal = 'user';

// Utility functions
function setPortal(portalType) {
    currentPortal = portalType;
    document.getElementById('login-title').innerText = portalType === 'admin' ? 'Admin Login' : 'User Login';
    document.getElementById('register-title').innerText = portalType === 'admin' ? 'Admin Registration' : 'User Registration';
    document.getElementById('reg-role').value = portalType;
    showPage('login');
}

function showPage(pageId) {
    document.querySelectorAll('.page').forEach(page => page.classList.add('hidden'));
    document.getElementById(`${pageId}-page`).classList.remove('hidden');

    if (pageId === 'dashboard') loadQueues();
    if (pageId === 'my-tokens') { loadMyTokens(); loadMyTransfers(); }
    if (pageId === 'admin') { loadAdminQueues(); loadPendingTransfers(); }
}

// Intercept requests to add token
axios.interceptors.request.use(config => {
    const token = sessionStorage.getItem('token');
    if (token) {
        config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
});

function initSocket() {
    socket = io('http://localhost:5000');
    socket.on('connect', () => {
        console.log('Connected to WebSocket server');
    });

    socket.on('global_queue_update', (status) => {
        // Refresh queues if dashboard is open
        if (!document.getElementById('dashboard-page').classList.contains('hidden')) {
            loadQueues(); 
        }
        // Refresh admin queues if admin open
        if (!document.getElementById('admin-page').classList.contains('hidden')) {
            loadAdminQueues();
        }
        // Refresh my tokens automatically when queue shifts
        if (!document.getElementById('my-tokens-page').classList.contains('hidden')) {
            loadMyTokens();
        }
    });
}

// Auto-refresh silent poller to visually update AI countdowns
setInterval(() => {
    const token = sessionStorage.getItem('token');
    const role = sessionStorage.getItem('user_role');
    if (!token || role === 'admin') return;

    if (!document.getElementById('dashboard-page').classList.contains('hidden')) {
        loadQueues();
    }
    if (!document.getElementById('my-tokens-page').classList.contains('hidden')) {
        loadMyTokens();
    }
}, 60000);

// Global Axios Error Jail to auto-purge dirty caching
axios.interceptors.response.use(response => response, error => {
    if (error.response && error.response.status === 403) {
        if (error.response.data?.error?.includes('Detected role')) {
            alert('SYSTEM MISMATCH: You are logged into the Admin Panel with a regular USER token! Forcing extreme logout reset...');
            // Obliterate cache manually
            sessionStorage.clear();
            window.location.reload(true);
        }
    }
    return Promise.reject(error);
});

function checkAuth() {
    const token = sessionStorage.getItem('token');
    const userRole = sessionStorage.getItem('user_role');
    const username = sessionStorage.getItem('username');

    if (token) {
        const navBar = document.getElementById('navbar');
        if (navBar) navBar.classList.remove('hidden');
        
        const navUser = document.getElementById('nav-username');
        if (navUser) navUser.textContent = username;
        
        initSocket();
        
        const adminBtn = document.getElementById('nav-admin-btn');
        const dashBtn = document.getElementById('nav-dashboard-btn');
        const tokensBtn = document.getElementById('nav-mytokens-btn');

        if (userRole === 'admin') {
            if (adminBtn) adminBtn.classList.remove('hidden');
            if (dashBtn) dashBtn.classList.add('hidden');
            if (tokensBtn) tokensBtn.classList.add('hidden');
            showPage('admin'); 
        } else {
            if (adminBtn) adminBtn.classList.add('hidden');
            if (dashBtn) dashBtn.classList.remove('hidden');
            if (tokensBtn) tokensBtn.classList.remove('hidden');
            showPage('dashboard'); 
        }
    } else {
        const navBar = document.getElementById('navbar');
        if (navBar) navBar.classList.add('hidden');
        showPage('portal');
    }
}

function logout() {
    sessionStorage.clear();
    if(socket) socket.disconnect();
    checkAuth();
}

window.onload = checkAuth;
