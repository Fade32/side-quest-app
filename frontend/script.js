const API_URL = 'http://localhost:5000/api';
let currentUser = null;

// Show message to user
function showMessage(text, type = 'success') {
    const messageEl = document.getElementById('message');
    messageEl.textContent = text;
    messageEl.className = `message ${type} show`;
    
    setTimeout(() => {
        messageEl.classList.remove('show');
    }, 3000);
}

// Login function
async function login() {
    const username = document.getElementById('username').value.trim();
    const password = document.getElementById('password').value;
    
    if (!username || !password) {
        showMessage('Please enter username and password', 'error');
        return;
    }
    
    try {
        const response = await fetch(`${API_URL}/login`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ username, password })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            currentUser = username;
            document.getElementById('current-user').textContent = username;
            document.getElementById('login-section').classList.add('hidden');
            document.getElementById('app-section').classList.remove('hidden');
            showMessage(data.message);
            loadSidequests();
            loadFriends();
            loadChallenges();
        } else {
            showMessage(data.error, 'error');
        }
    } catch (error) {
        showMessage('Error connecting to server. Make sure backend is running!', 'error');
        console.error('Error:', error);
    }
}

// Logout function
function logout() {
    currentUser = null;
    document.getElementById('login-section').classList.remove('hidden');
    document.getElementById('app-section').classList.add('hidden');
    document.getElementById('username').value = '';
    document.getElementById('password').value = '';
    showMessage('Logged out successfully');
}

// Add sidequest
async function addSidequest() {
    const title = document.getElementById('quest-title').value.trim();
    const description = document.getElementById('quest-description').value.trim();
    
    if (!title) {
        showMessage('Please enter a quest title', 'error');
        return;
    }
    
    try {
        const response = await fetch(`${API_URL}/sidequest/add`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                username: currentUser,
                title,
                description
            })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            showMessage('Sidequest added!');
            document.getElementById('quest-title').value = '';
            document.getElementById('quest-description').value = '';
            loadSidequests();
        } else {
            showMessage(data.error, 'error');
        }
    } catch (error) {
        showMessage('Error adding sidequest', 'error');
        console.error('Error:', error);
    }
}

// Load sidequests
async function loadSidequests() {
    try {
        const response = await fetch(`${API_URL}/sidequests/${currentUser}`);
        const data = await response.json();
        
        const listEl = document.getElementById('sidequests-list');
        
        if (data.sidequests.length === 0) {
            listEl.innerHTML = '<div class="empty-state">No sidequests yet. Add your first one!</div>';
            return;
        }
        
        listEl.innerHTML = data.sidequests.map(quest => `
            <div class="quest-item ${quest.completed ? 'completed' : ''}">
                <div class="quest-info">
                    <div class="quest-title">${quest.title}</div>
                    ${quest.description ? `<div class="quest-description">${quest.description}</div>` : ''}
                    <div class="quest-status">
                        ${quest.completed 
                            ? `✅ Completed on ${new Date(quest.completed_at).toLocaleDateString()}`
                            : '⏳ In Progress'
                        }
                    </div>
                </div>
                <button 
                    class="complete-btn" 
                    onclick="completeSidequest(${quest.id})"
                    ${quest.completed ? 'disabled' : ''}
                >
                    ${quest.completed ? '✓ Done' : 'Complete'}
                </button>
            </div>
        `).join('');
    } catch (error) {
        showMessage('Error loading sidequests', 'error');
        console.error('Error:', error);
    }
}

// Complete sidequest
async function completeSidequest(questId) {
    try {
        const response = await fetch(`${API_URL}/sidequest/complete`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                username: currentUser,
                sidequest_id: questId
            })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            showMessage('Sidequest completed! 🎉');
            loadSidequests();
        } else {
            showMessage(data.error, 'error');
        }
    } catch (error) {
        showMessage('Error completing sidequest', 'error');
        console.error('Error:', error);
    }
}

// Add friend
async function addFriend() {
    const friendUsername = document.getElementById('friend-username').value.trim();
    
    if (!friendUsername) {
        showMessage('Please enter a friend\'s username', 'error');
        return;
    }
    
    try {
        const response = await fetch(`${API_URL}/friend/add`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                username: currentUser,
                friend_username: friendUsername
            })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            showMessage('Friend added!');
            document.getElementById('friend-username').value = '';
            loadFriends();
        } else {
            showMessage(data.error, 'error');
        }
    } catch (error) {
        showMessage('Error adding friend', 'error');
        console.error('Error:', error);
    }
}

// Load friends
async function loadFriends() {
    try {
        const response = await fetch(`${API_URL}/friends/${currentUser}`);
        const data = await response.json();
        
        const listEl = document.getElementById('friends-list');
        const selectEl = document.getElementById('challenge-friend');
        
        if (data.friends.length === 0) {
            listEl.innerHTML = '<div class="empty-state">No friends yet. Add some!</div>';
            selectEl.innerHTML = '<option value="">No friends to challenge</option>';
            return;
        }
        
        listEl.innerHTML = data.friends.map(friend => `
            <div class="friend-item">
                <div>👤 ${friend}</div>
            </div>
        `).join('');
        
        // Populate challenge dropdown
        selectEl.innerHTML = '<option value="">Select a friend to challenge</option>' +
            data.friends.map(friend => `<option value="${friend}">${friend}</option>`).join('');
    } catch (error) {
        showMessage('Error loading friends', 'error');
        console.error('Error:', error);
    }
}

// Create challenge
async function createChallenge() {
    const challenged = document.getElementById('challenge-friend').value;
    const title = document.getElementById('challenge-title').value.trim();
    const description = document.getElementById('challenge-description').value.trim();
    
    if (!challenged) {
        showMessage('Please select a friend to challenge', 'error');
        return;
    }
    
    if (!title) {
        showMessage('Please enter a challenge title', 'error');
        return;
    }
    
    try {
        const response = await fetch(`${API_URL}/challenge/create`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                challenger: currentUser,
                challenged,
                title,
                description
            })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            showMessage('Challenge sent!');
            document.getElementById('challenge-title').value = '';
            document.getElementById('challenge-description').value = '';
            document.getElementById('challenge-friend').value = '';
            loadChallenges();
        } else {
            showMessage(data.error, 'error');
        }
    } catch (error) {
        showMessage('Error creating challenge', 'error');
        console.error('Error:', error);
    }
}

// Upload proof for challenge
async function uploadProof(challengeId) {
    const input = document.createElement('input');
    input.type = 'file';
    input.accept = 'image/*';
    
    input.onchange = async (e) => {
        const file = e.target.files[0];
        if (!file) return;
        
        // Convert image to base64
        const reader = new FileReader();
        reader.onload = async (event) => {
            const base64Image = event.target.result;
            
            try {
                const response = await fetch(`${API_URL}/challenge/upload-proof`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        challenge_id: challengeId,
                        username: currentUser,
                        proof_image: base64Image
                    })
                });
                
                const data = await response.json();
                
                if (response.ok) {
                    showMessage('Proof uploaded! Waiting for review.');
                    loadChallenges();
                } else {
                    showMessage(data.error, 'error');
                }
            } catch (error) {
                showMessage('Error uploading proof', 'error');
                console.error('Error:', error);
            }
        };
        
        reader.readAsDataURL(file);
    };
    
    input.click();
}

// Review challenge (accept or reject)
async function reviewChallenge(challengeId, accept) {
    try {
        const response = await fetch(`${API_URL}/challenge/review`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                challenge_id: challengeId,
                username: currentUser,
                accept
            })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            showMessage(accept ? 'Challenge accepted! 🎉' : 'Challenge rejected');
            loadChallenges();
        } else {
            showMessage(data.error, 'error');
        }
    } catch (error) {
        showMessage('Error reviewing challenge', 'error');
        console.error('Error:', error);
    }
}

// Load all challenges
async function loadChallenges() {
    await loadSentChallenges();
    await loadReceivedChallenges();
}

// Load sent challenges
async function loadSentChallenges() {
    try {
        const response = await fetch(`${API_URL}/challenges/sent/${currentUser}`);
        const data = await response.json();
        
        const listEl = document.getElementById('challenges-sent-list');
        
        if (data.challenges.length === 0) {
            listEl.innerHTML = '<div class="empty-state">No challenges sent yet</div>';
            return;
        }
        
        listEl.innerHTML = data.challenges.map(challenge => `
            <div class="challenge-item ${challenge.status}">
                <div class="challenge-header">
                    <div class="challenge-title">${challenge.title}</div>
                    <span class="challenge-status ${challenge.status}">${challenge.status.replace('_', ' ').toUpperCase()}</span>
                </div>
                ${challenge.description ? `<div class="challenge-description">${challenge.description}</div>` : ''}
                <div class="challenge-meta">
                    Challenged: <strong>${challenge.challenged}</strong> • 
                    Created: ${new Date(challenge.created_at).toLocaleDateString()}
                </div>
                ${challenge.proof_image ? `
                    <img src="${challenge.proof_image}" class="proof-image" alt="Proof" onclick="window.open('${challenge.proof_image}', '_blank')">
                ` : ''}
                ${challenge.status === 'proof_uploaded' ? `
                    <div class="challenge-actions">
                        <button class="accept-btn" onclick="reviewChallenge(${challenge.id}, true)">✓ Accept</button>
                        <button class="reject-btn" onclick="reviewChallenge(${challenge.id}, false)">✗ Reject</button>
                    </div>
                ` : ''}
            </div>
        `).join('');
    } catch (error) {
        showMessage('Error loading sent challenges', 'error');
        console.error('Error:', error);
    }
}

// Load received challenges
async function loadReceivedChallenges() {
    try {
        const response = await fetch(`${API_URL}/challenges/received/${currentUser}`);
        const data = await response.json();
        
        const listEl = document.getElementById('challenges-received-list');
        
        if (data.challenges.length === 0) {
            listEl.innerHTML = '<div class="empty-state">No challenges received yet</div>';
            return;
        }
        
        listEl.innerHTML = data.challenges.map(challenge => `
            <div class="challenge-item ${challenge.status}">
                <div class="challenge-header">
                    <div class="challenge-title">${challenge.title}</div>
                    <span class="challenge-status ${challenge.status}">${challenge.status.replace('_', ' ').toUpperCase()}</span>
                </div>
                ${challenge.description ? `<div class="challenge-description">${challenge.description}</div>` : ''}
                <div class="challenge-meta">
                    From: <strong>${challenge.challenger}</strong> • 
                    Created: ${new Date(challenge.created_at).toLocaleDateString()}
                </div>
                ${challenge.proof_image ? `
                    <img src="${challenge.proof_image}" class="proof-image" alt="Proof" onclick="window.open('${challenge.proof_image}', '_blank')">
                ` : ''}
                ${challenge.status === 'pending' ? `
                    <div class="challenge-actions">
                        <button class="upload-btn" onclick="uploadProof(${challenge.id})">📷 Upload Proof</button>
                    </div>
                ` : ''}
            </div>
        `).join('');
    } catch (error) {
        showMessage('Error loading received challenges', 'error');
        console.error('Error:', error);
    }
}

// Allow Enter key to login
document.addEventListener('DOMContentLoaded', () => {
    document.getElementById('username').addEventListener('keypress', (e) => {
        if (e.key === 'Enter') login();
    });
    document.getElementById('password').addEventListener('keypress', (e) => {
        if (e.key === 'Enter') login();
    });
});
