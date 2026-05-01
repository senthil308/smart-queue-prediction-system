document.getElementById('create-queue-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    const name = document.getElementById('new-queue-name').value;
    const avgTime = document.getElementById('new-queue-time').value;
    const capacity = document.getElementById('new-queue-capacity').value;

    try {
        await axios.post(`${API_URL}/admin/queues`, { 
            name, 
            average_service_time: parseInt(avgTime),
            capacity: parseInt(capacity)
        });
        alert('Queue created with tokens!');
        loadAdminQueues();
    } catch (err) {
        alert(err.response?.data?.error || 'Queue creation failed');
    }
});

async function loadAdminQueues() {
    try {
        const res = await axios.get(`${API_URL}/queue/`);
        const container = document.getElementById('admin-queues-container');
        container.innerHTML = '';
        
        res.data.forEach(q => {
            const div = document.createElement('div');
            div.className = 'card';
            div.innerHTML = `
                <div style="border-bottom: 2px solid #ccc; padding-bottom: 10px; margin-bottom: 10px;">
                    <h3 style="margin: 0; color: #2c3e50;">${q.queue_name}</h3>
                    <p style="margin: 5px 0;"><strong>Patients Issued:</strong> ${q.total_issued} / ${q.capacity}</p>
                    <p style="margin: 5px 0;"><strong>Waiting:</strong> <span style="color: #e74c3c; font-weight:bold;">${q.waiting_count}</span> | <strong>Serving Now:</strong> <span style="color: #27ae60; font-weight:bold;">${q.serving_token || 'None'}</span></p>
                </div>
                <div style="display:flex; flex-wrap:wrap; gap:8px;">
                    <button style="background:#3498db; color:white; border:none; border-radius:4px; padding:6px 12px; cursor:pointer; font-weight:bold;" onclick="callNextToken(${q.queue_id})">Next Patient 📢</button>
                    <button style="background:#9b59b6; color:white; border:none; border-radius:4px; padding:6px 12px; cursor:pointer;" onclick="viewTokens(${q.queue_id})">📋 View List</button>
                    <button style="background:#e67e22; color:white; border:none; border-radius:4px; padding:6px 12px; cursor:pointer;" onclick="resetQueue(${q.queue_id})">🔄 Reset Queue</button>
                    <button style="background:#e74c3c; color:white; border:none; border-radius:4px; padding:6px 12px; cursor:pointer;" onclick="deleteQueue(${q.queue_id})">🗑️ Delete DB</button>
                </div>
                <div id="tokens-list-${q.queue_id}" style="margin-top:15px; display:none; background:#f9f9f9; padding:10px; border-radius:5px; border: 1px solid #ddd; max-height: 200px; overflow-y: auto;"></div>
            `;
            container.appendChild(div);
        });
    } catch (err) {
        console.error("Error loading admin queues", err);
    }
}

async function callNextToken(queueId) {
    try {
        const res = await axios.post(`${API_URL}/admin/queues/${queueId}/next`);
        alert(res.data.message);
        loadAdminQueues();
    } catch (err) {
        alert(err.response?.data?.error || 'Failed to call next token');
    }
}

async function increaseCapacity(queueId) {
    const newCap = prompt("Enter new total token capacity for this queue:");
    if (!newCap) return;
    try {
        await axios.post(`${API_URL}/admin/queues/${queueId}/capacity`, { capacity: parseInt(newCap) });
        alert('Capacity updated!');
        loadAdminQueues();
    } catch (err) {
        alert(err.response?.data?.error || 'Update failed');
    }
}

async function deleteQueue(queueId) {
    if(!confirm("⚠️ Wait! Are you absolutely sure you want to permanently delete this queue and all its tokens?")) return;
    try {
        await axios.delete(`${API_URL}/admin/queues/${queueId}`);
        alert('Old queue completely deleted!');
        loadAdminQueues();
    } catch (err) {
        alert(err.response?.data?.error || 'Queue deletion failed');
    }
}

async function generateOfflineToken(queueId) {
    try {
        await axios.post(`${API_URL}/admin/queues/${queueId}/offline_token`);
        loadAdminQueues();
    } catch (err) {
        alert(err.response?.data?.error || 'Offline token generation failed');
    }
}

async function resetQueue(queueId) {
    if(!confirm("Warning: Resetting will delete ALL tokens from this queue and set it to 0. Continue?")) return;
    try {
        await axios.post(`${API_URL}/admin/queues/${queueId}/reset`);
        loadAdminQueues();
    } catch(err) {
        alert('Reset failed');
    }
}

async function viewTokens(queueId) {
    const listDiv = document.getElementById(`tokens-list-${queueId}`);
    if (listDiv.style.display === 'block') {
        listDiv.style.display = 'none';
        return;
    }
    
    try {
        const res = await axios.get(`${API_URL}/admin/queues/${queueId}/tokens`);
        listDiv.innerHTML = '<h4 style="margin-top:0;">📋 All Patients List</h4>';
        if (res.data.length === 0) listDiv.innerHTML += '<p>No patients yet.</p>';
        res.data.forEach(t => {
            const isWaiting = t.status === 'waiting';
            listDiv.innerHTML += `
                <div style="border-bottom:1px solid #ddd; padding:6px 0; display:flex; justify-content:space-between; align-items:center;">
                    <span>Token <strong>#${t.token_number}</strong> - Status: <strong style="color:${t.status==='serving'?'green':'grey'}">${t.status.toUpperCase()}</strong></span>
                    ${isWaiting ? `<button style="background:#e74c3c; color:white; border:none; border-radius:3px; padding:3px 8px; cursor:pointer;" onclick="cancelToken(${t.id}, ${queueId})">Cancel</button>` : ''}
                </div>
            `;
        });
        listDiv.style.display = 'block';
    } catch(err) {
        alert('Failed to load tracked patients');
    }
}

async function cancelToken(tokenId, queueId) {
    if(!confirm("Cancel this patient's token?")) return;
    try {
        await axios.post(`${API_URL}/admin/tokens/${tokenId}/cancel`);
        viewTokens(queueId); 
        loadAdminQueues(); 
    } catch(err) {
        alert('Cancellation failed');
    }
}

async function loadPendingTransfers() {
    try {
        const res = await axios.get(`${API_URL}/admin/transfers`);
        const container = document.getElementById('admin-transfers-container');
        container.innerHTML = '';
        
        if (res.data.length === 0) {
            container.innerHTML = '<p>No pending transfers.</p>';
            return;
        }

        res.data.forEach(t => {
            const div = document.createElement('div');
            div.className = 'transfer-card';
            div.innerHTML = `
                <div>
                    <strong>Transfer ID: ${t.id}</strong> (Token ID: ${t.token_id})
                    <p>From: ${t.from_username} | To: ${t.to_username}</p>
                </div>
                <div>
                    <button style="background: green;" onclick="approveTransfer(${t.id})">Approve</button>
                    <button style="background: red;" onclick="rejectTransfer(${t.id})">Reject</button>
                </div>
            `;
            container.appendChild(div);
        });
    } catch (err) {
        console.error("Error loading transfers", err);
    }
}
