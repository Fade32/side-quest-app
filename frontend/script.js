const API_URL = window.location.protocol === 'file:'
    ? 'http://127.0.0.1:5000/api'
    : `${window.location.origin}/api`;
let currentUser = null;
let currentGroupId = null;
let refreshInterval = null;

function escapeHtml(str) {
    const div = document.createElement('div');
    div.textContent = str;
    return div.innerHTML;
}

// Show message to user
function showMessage(text, type = 'success') {
    const messageEl = document.getElementById('message');
    messageEl.textContent = text;
    messageEl.className = `message ${type} show`;
    
    setTimeout(() => {
        messageEl.classList.remove('show');
    }, 3000);
}

// Start auto-refresh
function startAutoRefresh() {
    // Clear any existing interval
    if (refreshInterval) {
        clearInterval(refreshInterval);
    }
    
    // Refresh every 5 seconds
    refreshInterval = setInterval(() => {
        if (currentUser) {
            updatePoints();
            loadFriends();
            loadGroups();
            loadSideQuests();
            
            // If a group modal is open, refresh its data
            if (currentGroupId && !document.getElementById('group-modal').classList.contains('hidden')) {
                updateUserPoints(currentGroupId);
                loadGroupChallenges(currentGroupId);
                loadGroupLeaderboard(currentGroupId);
                checkChallengeCreationStatus(currentGroupId);
            }
        }
    }, 5000); // 5 seconds
}

// Stop auto-refresh
function stopAutoRefresh() {
    if (refreshInterval) {
        clearInterval(refreshInterval);
        refreshInterval = null;
    }
}

// Update user points for current group
async function updateUserPoints(groupId = null) {
    try {
        // If viewing a group modal, update group-specific points
        if (groupId && !document.getElementById('group-modal').classList.contains('hidden')) {
            const response = await fetch(`${API_URL}/user/${currentUser}/points?group_id=${groupId}`);
            const data = await response.json();
            
            if (response.ok) {
                document.getElementById('modal-user-points').textContent = data.points || 0;
            }
        }
    } catch (error) {
        // Silently fail - don't show error messages for background updates
        console.error('Error updating points:', error);
    }
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
            loadFriends();
            loadGroups();
            loadSideQuests();
            updatePoints();
            startAutoRefresh(); // Start auto-refresh after login
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
    stopAutoRefresh(); // Stop auto-refresh on logout
    currentUser = null;
    document.getElementById('login-section').classList.remove('hidden');
    document.getElementById('app-section').classList.add('hidden');
    document.getElementById('username').value = '';
    document.getElementById('password').value = '';
    showMessage('Logged out successfully');
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
        
        if (data.friends.length === 0) {
            listEl.innerHTML = '<div class="empty-state">No friends yet. Add some!</div>';
            return;
        }
        
        listEl.innerHTML = data.friends.map(friend => `
            <div class="friend-item">
                <div>👤 ${escapeHtml(friend)}</div>
            </div>
        `).join('');
    } catch (error) {
        showMessage('Error loading friends', 'error');
        console.error('Error:', error);
    }
}

// Update user points
async function updatePoints() {
    try {
        const response = await fetch(`${API_URL}/user/${currentUser}/points`);
        const data = await response.json();
        
        if (response.ok) {
            document.getElementById('user-points').textContent = data.points;
        }
    } catch (error) {
        console.error('Error updating points:', error);
    }
}

// Add side quest
async function addSideQuest() {
    const title = document.getElementById('sidequest-title').value.trim();
    const description = document.getElementById('sidequest-description').value.trim();

    if (!title) {
        showMessage('Please enter a quest title', 'error');
        return;
    }

    try {
        const response = await fetch(`${API_URL}/sidequest/add`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username: currentUser, title, description })
        });

        const data = await response.json();

        if (response.ok) {
            showMessage('Side quest added!');
            document.getElementById('sidequest-title').value = '';
            document.getElementById('sidequest-description').value = '';
            loadSideQuests();
        } else {
            showMessage(data.error, 'error');
        }
    } catch (error) {
        showMessage('Error adding side quest', 'error');
        console.error('Error:', error);
    }
}

// Complete side quest
async function completeSideQuest(questId) {
    try {
        const response = await fetch(`${API_URL}/sidequest/${questId}/complete`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username: currentUser })
        });

        const data = await response.json();

        if (response.ok) {
            showMessage(data.message);
            loadSideQuests();
            updatePoints();
        } else {
            showMessage(data.error, 'error');
        }
    } catch (error) {
        showMessage('Error completing side quest', 'error');
        console.error('Error:', error);
    }
}

// Delete side quest
async function deleteSideQuest(questId) {
    try {
        const response = await fetch(`${API_URL}/sidequest/${questId}/delete`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username: currentUser })
        });

        const data = await response.json();

        if (response.ok) {
            showMessage('Side quest deleted');
            loadSideQuests();
        } else {
            showMessage(data.error, 'error');
        }
    } catch (error) {
        showMessage('Error deleting side quest', 'error');
        console.error('Error:', error);
    }
}

// Load side quests
async function loadSideQuests() {
    try {
        const response = await fetch(`${API_URL}/sidequests/${currentUser}`);
        const data = await response.json();

        const listEl = document.getElementById('sidequests-list');

        if (data.sidequests.length === 0) {
            listEl.innerHTML = '<div class="empty-state">No side quests yet. Add one!</div>';
            return;
        }

        listEl.innerHTML = data.sidequests.map(quest => `
            <div class="quest-item ${quest.completed ? 'completed' : ''}">
                <div class="quest-info">
                    <div class="quest-title">${escapeHtml(quest.title)}</div>
                    ${quest.description ? `<div class="quest-description">${escapeHtml(quest.description)}</div>` : ''}
                    <div class="quest-status">${quest.completed ? '✅ Completed' : '⏳ Active'} • ${new Date(quest.created_at).toLocaleDateString()}</div>
                </div>
                <div style="display: flex; gap: 8px;">
                    ${!quest.completed ? `<button class="complete-btn" onclick="completeSideQuest(${quest.id})">✓ Complete</button>` : ''}
                    <button class="reject-btn" onclick="deleteSideQuest(${quest.id})" style="padding: 8px 12px; font-size: 14px;">🗑</button>
                </div>
            </div>
        `).join('');
    } catch (error) {
        console.error('Error loading side quests:', error);
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

// Create group
async function createGroup() {
    const name = document.getElementById('group-name').value.trim();
    
    if (!name) {
        showMessage('Please enter a group name', 'error');
        return;
    }
    
    try {
        const response = await fetch(`${API_URL}/group/create`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                creator: currentUser,
                name
            })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            showMessage('Group created!');
            document.getElementById('group-name').value = '';
            loadGroups();
        } else {
            showMessage(data.error, 'error');
        }
    } catch (error) {
        showMessage('Error creating group', 'error');
        console.error('Error:', error);
    }
}

// Load groups
async function loadGroups() {
    try {
        const response = await fetch(`${API_URL}/groups/user/${currentUser}`);
        const data = await response.json();
        
        const listEl = document.getElementById('groups-list');
        
        if (data.groups.length === 0) {
            listEl.innerHTML = '<div class="empty-state">No groups yet. Create one!</div>';
            return;
        }
        
        listEl.innerHTML = data.groups.map(group => `
            <div class="group-item" onclick="openGroupModal(${group.id})">
                <div class="group-name">${escapeHtml(group.name)}</div>
                <div class="group-info">
                    ${group.members.length} member(s) • 
                    Creator: ${escapeHtml(group.creator)}
                </div>
            </div>
        `).join('');
    } catch (error) {
        showMessage('Error loading groups', 'error');
        console.error('Error:', error);
    }
}

// Open group modal
async function openGroupModal(groupId) {
    currentGroupId = groupId;
    
    try {
        const response = await fetch(`${API_URL}/groups/user/${currentUser}`);
        const data = await response.json();
        
        const group = data.groups.find(g => g.id === groupId);
        if (!group) return;
        
        document.getElementById('modal-group-name').textContent = group.name;
        
        // Show add member section only for creator
        const addMemberSection = document.getElementById('add-member-section');
        if (group.creator === currentUser) {
            addMemberSection.style.display = 'block';
            await loadFriendsForGroup(group.members);
        } else {
            addMemberSection.style.display = 'none';
        }
        
        // Display members
        const membersHtml = group.members.map(member => 
            `<span class="member-item ${member === group.creator ? 'creator' : ''}">${escapeHtml(member)}${member === group.creator ? ' 👑' : ''}</span>`
        ).join('');
        document.getElementById('modal-members-list').innerHTML = membersHtml;
        
        // Update user's points in this group
        await updateUserPoints(groupId);
        
        // Load group challenges
        await loadGroupChallenges(groupId);
        
        // Load group leaderboard
        await loadGroupLeaderboard(groupId);
        
        // Check if new challenge can be created
        await checkChallengeCreationStatus(groupId);
        
        document.getElementById('group-modal').classList.remove('hidden');
    } catch (error) {
        showMessage('Error loading group', 'error');
        console.error('Error:', error);
    }
}

// Close group modal
function closeGroupModal() {
    document.getElementById('group-modal').classList.add('hidden');
    currentGroupId = null;
}

// Load friends for group (exclude existing members)
async function loadFriendsForGroup(existingMembers) {
    try {
        const response = await fetch(`${API_URL}/friends/${currentUser}`);
        const data = await response.json();
        
        const selectEl = document.getElementById('modal-friend-select');
        const availableFriends = data.friends.filter(f => !existingMembers.includes(f));
        
        if (availableFriends.length === 0) {
            selectEl.innerHTML = '<option value="">No friends to add</option>';
            return;
        }
        
        selectEl.innerHTML = '<option value="">Select a friend to add</option>' +
            availableFriends.map(friend => `<option value="${escapeHtml(friend)}">${escapeHtml(friend)}</option>`).join('');
    } catch (error) {
        console.error('Error:', error);
    }
}

// Add group member
async function addGroupMember() {
    const member = document.getElementById('modal-friend-select').value;
    
    if (!member) {
        showMessage('Please select a friend', 'error');
        return;
    }
    
    try {
        const response = await fetch(`${API_URL}/group/${currentGroupId}/add-member`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                username: currentUser,
                member
            })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            showMessage('Member added!');
            openGroupModal(currentGroupId);
            loadGroups();
        } else {
            showMessage(data.error, 'error');
        }
    } catch (error) {
        showMessage('Error adding member', 'error');
        console.error('Error:', error);
    }
}

// Pick random challenger
async function pickRandomChallenger() {
    try {
        const response = await fetch(`${API_URL}/group/${currentGroupId}/pick-challenger`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            }
        });
        
        const data = await response.json();
        
        if (response.ok) {
            showMessage(data.message);
            loadGroupChallenges(currentGroupId);
        } else {
            showMessage(data.error, 'error');
        }
    } catch (error) {
        showMessage('Error picking challenger', 'error');
        console.error('Error:', error);
    }
}

// Check if a new challenge can be created today
async function checkChallengeCreationStatus(groupId) {
    try {
        const response = await fetch(`${API_URL}/group/${groupId}/can-create-challenge`);
        const data = await response.json();
        
        const button = document.querySelector('button[onclick="pickRandomChallenger()"]');
        
        if (!data.can_create) {
            // Disable button and show countdown
            button.disabled = true;
            button.innerHTML = `🎲 Next Challenge in ${data.hours_remaining}h ${data.minutes_remaining}m`;
            button.style.opacity = '0.6';
            button.style.cursor = 'not-allowed';
        } else {
            // Enable button
            button.disabled = false;
            button.innerHTML = '🎲 Pick Random Member to Create Challenge';
            button.style.opacity = '1';
            button.style.cursor = 'pointer';
        }
    } catch (error) {
        console.error('Error checking challenge status:', error);
    }
}

// Define group challenge (by chosen member)
async function defineGroupChallenge() {
    const title = document.getElementById('modal-challenge-title').value.trim();
    const description = document.getElementById('modal-challenge-description').value.trim();
    const difficulty = document.getElementById('modal-challenge-difficulty').value;
    
    if (!title) {
        showMessage('Please enter a challenge title', 'error');
        return;
    }
    
    // Find the pending challenge
    try {
        const challengesResponse = await fetch(`${API_URL}/group/${currentGroupId}/challenges`);
        const challengesData = await challengesResponse.json();
        const pendingChallenge = challengesData.challenges.find(c => c.status === 'awaiting_creation' && c.challenger === currentUser);
        
        if (!pendingChallenge) {
            showMessage('No pending challenge found', 'error');
            return;
        }
        
        const response = await fetch(`${API_URL}/group-challenge/${pendingChallenge.id}/define`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                username: currentUser,
                title,
                description,
                difficulty
            })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            showMessage('Challenge created!');
            document.getElementById('modal-challenge-title').value = '';
            document.getElementById('modal-challenge-description').value = '';
            document.getElementById('modal-challenge-difficulty').value = 'easy';
            document.getElementById('challenge-creator-section').classList.add('hidden');
            loadGroupChallenges(currentGroupId);
        } else {
            showMessage(data.error, 'error');
        }
    } catch (error) {
        showMessage('Error defining challenge', 'error');
        console.error('Error:', error);
    }
}

// Load group challenges
async function loadGroupChallenges(groupId) {
    try {
        const response = await fetch(`${API_URL}/group/${groupId}/challenges`);
        const data = await response.json();
        
        const listEl = document.getElementById('modal-challenges-list');
        
        // Check if there's a pending challenge awaiting creation
        const pendingChallenge = data.challenges.find(c => c.status === 'awaiting_creation');
        if (pendingChallenge) {
            if (pendingChallenge.challenger === currentUser) {
                // Show the form to this user
                document.getElementById('challenge-creator-section').classList.remove('hidden');
            } else {
                // Show waiting message to other users
                document.getElementById('challenge-creator-section').classList.add('hidden');
            }
        } else {
            document.getElementById('challenge-creator-section').classList.add('hidden');
        }
        
        const activeChallenges = data.challenges.filter(c => c.status === 'active' || c.status === 'awaiting_creation');
        
        if (activeChallenges.length === 0) {
            listEl.innerHTML = '<div class="empty-state">No challenges yet</div>';
            return;
        }
        
        listEl.innerHTML = activeChallenges.map(challenge => {
            if (challenge.status === 'awaiting_creation') {
                if (challenge.challenger === currentUser) {
                    return `
                        <div class="challenge-item" style="border-left-color: #ffa500;">
                            <div class="challenge-header">
                                <div class="challenge-title">⏳ You need to create a challenge!</div>
                            </div>
                            <p>Fill out the form above to create the challenge for your group.</p>
                        </div>
                    `;
                } else {
                    return `
                        <div class="challenge-item" style="border-left-color: #ffa500;">
                            <div class="challenge-header">
                                <div class="challenge-title">⏳ Waiting for challenge...</div>
                            </div>
                            <p><strong>${escapeHtml(challenge.challenger)}</strong> was randomly chosen to create the next challenge!</p>
                        </div>
                    `;
                }
            }
            
            const userSubmission = challenge.submissions.find(s => s.username === currentUser);
            const isChallenger = challenge.challenger === currentUser;
            
            return `
                <div class="challenge-item">
                    <div class="challenge-header">
                        <div class="challenge-title">
                            ${escapeHtml(challenge.title)}
                            <span class="difficulty-badge ${escapeHtml(challenge.difficulty)}">${escapeHtml((challenge.difficulty || '').toUpperCase())} - ${challenge.points} pts</span>
                        </div>
                    </div>
                    ${challenge.description ? `<div class="challenge-description">${escapeHtml(challenge.description)}</div>` : ''}
                    <div class="challenge-meta">
                        Created by: <strong>${escapeHtml(challenge.challenger)}</strong> • 
                        ${new Date(challenge.challenge_created_at).toLocaleDateString()}
                        ${challenge.deadline ? ` • ⏰ Deadline: ${new Date(challenge.deadline).toLocaleString()}` : ''}
                    </div>
                    
                    ${!userSubmission && !isChallenger ? `
                        <div class="challenge-actions">
                            <button class="upload-btn" onclick="submitGroupProof(${challenge.id})">📷 Submit Proof</button>
                        </div>
                    ` : ''}
                    
                    ${isChallenger ? `
                        <div style="padding: 10px; background: #fff3cd; border-radius: 6px; margin-top: 10px;">
                            <strong>You created this challenge!</strong> Review submissions below.
                        </div>
                    ` : ''}
                    
                    ${userSubmission ? `
                        <div class="submission-item ${userSubmission.status}">
                            <div class="submission-header">
                                <span>Your submission</span>
                                <span class="challenge-status ${userSubmission.status}">${userSubmission.status.toUpperCase()}</span>
                            </div>
                            <img src="${userSubmission.proof_image}" class="proof-image" alt="Your proof" onclick="window.open('${userSubmission.proof_image}', '_blank')">
                            ${userSubmission.status === 'accepted' ? `
                                <div style="color: #28a745; font-weight: 600; margin-top: 8px;">
                                    ✅ You earned ${challenge.points} points!
                                </div>
                            ` : ''}
                        </div>
                    ` : ''}
                    
                    ${isChallenger && challenge.submissions.length > 0 ? `
                        <div style="margin-top: 15px;">
                            <strong>Submissions to review:</strong>
                            ${challenge.submissions.map(sub => `
                                <div class="submission-item ${sub.status}">
                                    <div class="submission-header">
                                        <span class="submission-user">${escapeHtml(sub.username)}</span>
                                        <span class="challenge-status ${sub.status}">${sub.status.toUpperCase()}</span>
                                    </div>
                                    <img src="${sub.proof_image}" class="proof-image" alt="Proof" onclick="window.open('${sub.proof_image}', '_blank')">
                                    ${sub.status === 'pending' ? `
                                        <div class="submission-actions">
                                            <button class="accept-btn" onclick="reviewGroupSubmission(${challenge.id}, '${escapeHtml(sub.username).replace(/'/g, "\\'")}', true)">✓ Accept</button>
                                            <button class="reject-btn" onclick="reviewGroupSubmission(${challenge.id}, '${escapeHtml(sub.username).replace(/'/g, "\\'")}', false)">✗ Reject</button>
                                        </div>
                                    ` : ''}
                                </div>
                            `).join('')}
                        </div>
                    ` : ''}
                    
                    ${isChallenger && challenge.submissions.length === 0 ? `
                        <div style="padding: 10px; background: #f8f9fa; border-radius: 6px; margin-top: 10px; text-align: center; color: #666;">
                            No submissions yet. Waiting for group members to submit proof...
                        </div>
                    ` : ''}
                </div>
            `;
        }).join('');
    } catch (error) {
        showMessage('Error loading group challenges', 'error');
        console.error('Error:', error);
    }
}

// Submit group proof
async function submitGroupProof(challengeId) {
    const input = document.createElement('input');
    input.type = 'file';
    input.accept = 'image/*';
    
    input.onchange = async (e) => {
        const file = e.target.files[0];
        if (!file) return;
        
        const reader = new FileReader();
        reader.onload = async (event) => {
            const base64Image = event.target.result;
            
            try {
                const response = await fetch(`${API_URL}/group-challenge/${challengeId}/submit`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        username: currentUser,
                        proof_image: base64Image
                    })
                });
                
                const data = await response.json();
                
                if (response.ok) {
                    showMessage('Proof submitted!');
                    loadGroupChallenges(currentGroupId);
                } else {
                    showMessage(data.error, 'error');
                }
            } catch (error) {
                showMessage('Error submitting proof', 'error');
                console.error('Error:', error);
            }
        };
        
        reader.readAsDataURL(file);
    };
    
    input.click();
}

// Review group submission
async function reviewGroupSubmission(challengeId, targetUsername, accept) {
    try {
        const response = await fetch(`${API_URL}/group-challenge/${challengeId}/review`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                reviewer: currentUser,
                target_username: targetUsername,
                accept
            })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            showMessage(accept ? 'Submission accepted! 🎉' : 'Submission rejected');
            updateUserPoints(currentGroupId); // Update points immediately
            loadGroupChallenges(currentGroupId);
            loadGroupLeaderboard(currentGroupId);
        } else {
            showMessage(data.error, 'error');
        }
    } catch (error) {
        showMessage('Error reviewing submission', 'error');
        console.error('Error:', error);
    }
}

// Load group leaderboard
async function loadGroupLeaderboard(groupId) {
    try {
        const response = await fetch(`${API_URL}/group/${groupId}/leaderboard`);
        const data = await response.json();
        
        const listEl = document.getElementById('modal-leaderboard-list');
        
        if (data.leaderboard.length === 0) {
            listEl.innerHTML = '<div class="empty-state">No scores yet</div>';
            return;
        }
        
        listEl.innerHTML = data.leaderboard.map((entry, index) => {
            const rank = index + 1;
            let medal = '';
            if (rank === 1) medal = '🥇';
            else if (rank === 2) medal = '🥈';
            else if (rank === 3) medal = '🥉';
            
            return `
                <div class="leaderboard-item rank-${rank > 3 ? 'other' : rank}">
                    <span class="leaderboard-rank">${medal || rank}</span>
                    <span class="leaderboard-username">${escapeHtml(entry.username)}${entry.username === currentUser ? ' (You)' : ''}</span>
                    <span class="leaderboard-points">${entry.points} pts</span>
                </div>
            `;
        }).join('');
    } catch (error) {
        showMessage('Error loading group leaderboard', 'error');
        console.error('Error:', error);
    }
}


