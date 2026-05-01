async function loadQueues() {
    try {
        const res = await axios.get(`${API_URL}/queue/`);
        const container = document.getElementById('queues-container');
        container.innerHTML = '';
        
        if (res.data.length === 0) {
            container.innerHTML = '<p>No active queues found.</p>';
            return;
        }

        res.data.forEach(q => {
            const div = document.createElement('div');
            div.className = 'queue-card';
            div.innerHTML = `
                <div class="queue-info">
                    <h3>${q.queue_name}</h3>
                    <div class="queue-stats">
                        <p>Available: <span>${q.capacity - q.total_issued} left</span> (out of ${q.capacity})</p>
                        <p>Currently Serving: <span>${q.serving_token || 'None'}</span></p>
                        <p>Est. Wait Time: <span>${q.estimated_wait_time} mins</span></p>
                    </div>
                </div>
                <button onclick="bookToken(${q.queue_id})" ${q.total_issued >= q.capacity ? 'disabled style="background:grey"' : ''}>
                    ${q.total_issued >= q.capacity ? 'Queue Full' : 'Generate Token'}
                </button>
            `;
            container.appendChild(div);
        });
    } catch (err) {
        console.error("Error loading queues", err);
    }
}

async function bookToken(queueId) {
    try {
        await axios.post(`${API_URL}/tokens/book`, { queue_id: queueId });
        alert('Token booked successfully!');
        loadQueues(); // refresh instantly
    } catch (err) {
        alert(err.response?.data?.error || 'Booking failed');
    }
}

async function loadMyTokens() {
    try {
        const res = await axios.get(`${API_URL}/tokens/my_tokens`);
        const container = document.getElementById('my-tokens-container');
        container.innerHTML = '';
        
        if (res.data.length === 0) {
            container.innerHTML = '<p>You have no tokens.</p>';
            return;
        }

        res.data.forEach(t => {
            const div = document.createElement('div');
            div.className = 'token-card';
            div.innerHTML = `
                <div>
                    <strong>Queue: ${t.queue_name || '...'} (Token #${t.token_number})</strong>
                    <p>Status: <span style="font-weight:bold; color: ${t.status === 'serving' ? 'green' : 'blue'}">${t.status.toUpperCase()}</span></p>
                    ${t.status === 'waiting' ? `<p style="color:#e74c3c; font-weight:bold;">People ahead of you: ${t.people_ahead} <br> Your Wait Time: ~${t.my_wait_time} mins</p>` : ''}
                    <p style="font-size: 0.9em; color: grey;">Token ID to Share: ${t.id}</p>
                </div>
            `;
            container.appendChild(div);
        });
    } catch (err) {
        console.error("Error loading my tokens", err);
    }
}

document.getElementById('share-token-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    const tokenId = document.getElementById('share-token-id').value;
    const toUserId = document.getElementById('share-user-id').value;

    try {
        const res = await axios.post(`${API_URL}/sharing/transfer`, { 
            token_id: parseInt(tokenId), 
            to_username: toUserId 
        });
        alert(res.data.message);
        loadMyTransfers();
    } catch (err) {
        alert(err.response?.data?.error || 'Transfer request failed');
    }
});

async function loadMyTransfers() {
    try {
        const res = await axios.get(`${API_URL}/sharing/my_transfers`);
        const container = document.getElementById('my-transfers-container');
        container.innerHTML = '';
        
        if (res.data.length === 0) {
            container.innerHTML = '<p>No transfer requests found.</p>';
            return;
        }

        res.data.forEach(t => {
            const div = document.createElement('div');
            div.className = 'transfer-card';
            div.innerHTML = `
                <div>
                    <strong>Token Number: ${t.token_number || '-'}</strong>
                    <p>From: ${t.from_username}</p>
                    <p>To: ${t.to_username}</p>
                    <p>Status: <span style="font-weight:bold; color: ${t.status === 'approved' ? 'green' : (t.status === 'rejected' ? 'red' : 'orange')}">${t.status}</span></p>
                </div>
            `;
            container.appendChild(div);
        });
    } catch (err) {
        console.error("Error loading my transfers", err);
    }
}
