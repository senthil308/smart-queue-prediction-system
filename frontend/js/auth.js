document.getElementById('login-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    const username = document.getElementById('login-user-id').value;
    const password = document.getElementById('login-password').value;

    try {
        const res = await axios.post(`${API_URL}/auth/login`, { username, password, role: currentPortal });
        
        if (res.data.user.role !== currentPortal) {
            alert(`Access Denied: You are trying to log into the ${currentPortal.toUpperCase()} portal using a ${res.data.user.role.toUpperCase()} account.`);
            return;
        }

        sessionStorage.setItem('token', res.data.token);
        sessionStorage.setItem('user_role', res.data.user.role);
        sessionStorage.setItem('username', res.data.user.username);
        checkAuth();
    } catch (err) {
        alert(err.response?.data?.error || 'Login failed');
    }
});

document.getElementById('register-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    const username = document.getElementById('reg-username').value;
    const password = document.getElementById('reg-password').value;
    const role = document.getElementById('reg-role').value;

    try {
        const res = await axios.post(`${API_URL}/auth/register`, { username, password, role });
        document.getElementById('reg-result').innerText = `Registered! You can now login globally securely.`;
    } catch (err) {
        document.getElementById('reg-result').innerText = err.response?.data?.error || 'Registration failed';
    }
});
