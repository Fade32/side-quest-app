from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from datetime import datetime, timedelta
import json
import os

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes and origins

# Simple file-based storage (replace with database later)
DATA_FILE = 'data.json'

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r') as f:
            return json.load(f)
    return {'users': {}, 'friendships': [], 'groups': [], 'group_challenges': []}

def save_data(data):
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f, indent=2)

@app.route('/api/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    
    if not username or not password:
        return jsonify({'error': 'Username and password required'}), 400
    
    db = load_data()
    
    if username in db['users']:
        if db['users'][username]['password'] == password:
            # Ensure user has group_points field (for existing users)
            if 'group_points' not in db['users'][username]:
                db['users'][username]['group_points'] = {}
                save_data(db)
            return jsonify({
                'success': True,
                'message': 'Login successful',
                'user': {'username': username, 'group_points': db['users'][username]['group_points']}
            }), 200
        else:
            return jsonify({'error': 'Invalid password'}), 401
    else:
        # Create new user
        db['users'][username] = {
            'password': password,
            'group_points': {},
            'created_at': datetime.now().isoformat()
        }
        save_data(db)
        return jsonify({
            'success': True,
            'message': 'User created and logged in',
            'user': {'username': username, 'group_points': {}}
        }), 201

@app.route('/api/friend/add', methods=['POST'])
def add_friend():
    data = request.json
    username = data.get('username')
    friend_username = data.get('friend_username')
    
    if not username or not friend_username:
        return jsonify({'error': 'Username and friend username required'}), 400
    
    if username == friend_username:
        return jsonify({'error': 'Cannot add yourself as friend'}), 400
    
    db = load_data()
    
    if username not in db['users']:
        return jsonify({'error': 'User not found'}), 404
    
    if friend_username not in db['users']:
        return jsonify({'error': 'Friend not found'}), 404
    
    friendship = {
        'user1': username,
        'user2': friend_username,
        'created_at': datetime.now().isoformat()
    }
    
    # Check if friendship already exists
    for f in db['friendships']:
        if (f['user1'] == username and f['user2'] == friend_username) or \
           (f['user1'] == friend_username and f['user2'] == username):
            return jsonify({'error': 'Friendship already exists'}), 400
    
    db['friendships'].append(friendship)
    save_data(db)
    
    return jsonify({
        'success': True,
        'message': f'Friend {friend_username} added',
        'friendship': friendship
    }), 201

@app.route('/api/sidequests/<username>', methods=['GET'])
def get_sidequests(username):
    db = load_data()
    user_quests = [q for q in db['sidequests'] if q['username'] == username]
    return jsonify({'sidequests': user_quests}), 200

@app.route('/api/friends/<username>', methods=['GET'])
def get_friends(username):
    db = load_data()
    friends = []
    for f in db['friendships']:
        if f['user1'] == username:
            friends.append(f['user2'])
        elif f['user2'] == username:
            friends.append(f['user1'])
    return jsonify({'friends': friends}), 200

@app.route('/api/challenge/create', methods=['POST'])
def create_challenge():
    data = request.json
    challenger = data.get('challenger')
    challenged = data.get('challenged')
    title = data.get('title')
    description = data.get('description', '')
    difficulty = data.get('difficulty', 'easy')  # easy, medium, hard
    
    if not challenger or not challenged or not title:
        return jsonify({'error': 'Challenger, challenged user, and title required'}), 400
    
    if challenger == challenged:
        return jsonify({'error': 'Cannot challenge yourself'}), 400
    
    if difficulty not in ['easy', 'medium', 'hard']:
        return jsonify({'error': 'Invalid difficulty. Must be easy, medium, or hard'}), 400
    
    db = load_data()
    
    if challenger not in db['users'] or challenged not in db['users']:
        return jsonify({'error': 'User not found'}), 404
    
    # Check cooldown - 2 hours between challenges to the same user
    two_hours_ago = datetime.now().timestamp() - (2 * 60 * 60)
    for challenge in db['challenges']:
        if challenge['challenger'] == challenger and challenge['challenged'] == challenged:
            challenge_time = datetime.fromisoformat(challenge['created_at']).timestamp()
            if challenge_time > two_hours_ago:
                time_remaining = int((challenge_time + (2 * 60 * 60) - datetime.now().timestamp()) / 60)
                return jsonify({'error': f'Cooldown active. Wait {time_remaining} more minutes'}), 400
    
    # Set points based on difficulty
    points_map = {'easy': 10, 'medium': 25, 'hard': 50}
    points = points_map[difficulty]
    
    challenge = {
        'id': len(db['challenges']) + 1,
        'challenger': challenger,
        'challenged': challenged,
        'title': title,
        'description': description,
        'difficulty': difficulty,
        'points': points,
        'status': 'pending',  # pending, proof_uploaded, accepted, rejected
        'proof_image': None,
        'created_at': datetime.now().isoformat(),
        'uploaded_at': None,
        'reviewed_at': None
    }
    
    db['challenges'].append(challenge)
    save_data(db)
    
    return jsonify({
        'success': True,
        'message': f'Challenge sent to {challenged}',
        'challenge': challenge
    }), 201

@app.route('/api/challenge/upload-proof', methods=['POST'])
def upload_proof():
    data = request.json
    challenge_id = data.get('challenge_id')
    username = data.get('username')
    proof_image = data.get('proof_image')  # base64 encoded image
    
    if not challenge_id or not username or not proof_image:
        return jsonify({'error': 'Challenge ID, username, and proof image required'}), 400
    
    db = load_data()
    
    for challenge in db['challenges']:
        if challenge['id'] == challenge_id and challenge['challenged'] == username:
            if challenge['status'] != 'pending':
                return jsonify({'error': 'Challenge already has proof or is completed'}), 400
            
            challenge['proof_image'] = proof_image
            challenge['status'] = 'proof_uploaded'
            challenge['uploaded_at'] = datetime.now().isoformat()
            save_data(db)
            
            return jsonify({
                'success': True,
                'message': 'Proof uploaded! Waiting for review.',
                'challenge': challenge
            }), 200
    
    return jsonify({'error': 'Challenge not found or you are not the challenged user'}), 404

@app.route('/api/challenge/review', methods=['POST'])
def review_challenge():
    data = request.json
    challenge_id = data.get('challenge_id')
    username = data.get('username')
    accept = data.get('accept')  # True or False
    
    if not challenge_id or not username or accept is None:
        return jsonify({'error': 'Challenge ID, username, and accept status required'}), 400
    
    db = load_data()
    
    for challenge in db['challenges']:
        if challenge['id'] == challenge_id and challenge['challenger'] == username:
            if challenge['status'] != 'proof_uploaded':
                return jsonify({'error': 'No proof uploaded yet or already reviewed'}), 400
            
            challenge['status'] = 'accepted' if accept else 'rejected'
            challenge['reviewed_at'] = datetime.now().isoformat()
            
            # Award points if accepted
            if accept:
                challenged_user = challenge['challenged']
                if 'points' not in db['users'][challenged_user]:
                    db['users'][challenged_user]['points'] = 0
                db['users'][challenged_user]['points'] += challenge['points']
            
            save_data(db)
            
            return jsonify({
                'success': True,
                'message': f'Challenge {"accepted" if accept else "rejected"}!',
                'challenge': challenge
            }), 200
    
    return jsonify({'error': 'Challenge not found or you are not the challenger'}), 404

@app.route('/api/challenges/sent/<username>', methods=['GET'])
def get_sent_challenges(username):
    db = load_data()
    sent = [c for c in db['challenges'] if c['challenger'] == username]
    return jsonify({'challenges': sent}), 200

@app.route('/api/challenges/received/<username>', methods=['GET'])
def get_received_challenges(username):
    db = load_data()
    received = [c for c in db['challenges'] if c['challenged'] == username]
    return jsonify({'challenges': received}), 200

@app.route('/api/user/<username>/points', methods=['GET'])
def get_user_points(username):
    db = load_data()
    if username not in db['users']:
        return jsonify({'error': 'User not found'}), 404
    
    group_id = request.args.get('group_id')
    
    # Initialize group_points if not exists
    if 'group_points' not in db['users'][username]:
        db['users'][username]['group_points'] = {}
        save_data(db)
    
    if group_id:
        # Return points for specific group
        group_id_str = str(group_id)
        points = db['users'][username]['group_points'].get(group_id_str, 0)
        return jsonify({'username': username, 'group_id': group_id, 'points': points}), 200
    else:
        # Return all group points
        return jsonify({
            'username': username, 
            'group_points': db['users'][username]['group_points']
        }), 200

@app.route('/api/group/create', methods=['POST'])
def create_group():
    data = request.json
    creator = data.get('creator')
    name = data.get('name')
    
    if not creator or not name:
        return jsonify({'error': 'Creator and group name required'}), 400
    
    db = load_data()
    
    if creator not in db['users']:
        return jsonify({'error': 'User not found'}), 404
    
    group = {
        'id': len(db['groups']) + 1,
        'name': name,
        'creator': creator,
        'members': [creator],
        'created_at': datetime.now().isoformat()
    }
    
    db['groups'].append(group)
    save_data(db)
    
    return jsonify({
        'success': True,
        'message': f'Group "{name}" created',
        'group': group
    }), 201

@app.route('/api/group/<int:group_id>/add-member', methods=['POST'])
def add_group_member(group_id):
    data = request.json
    username = data.get('username')
    member_to_add = data.get('member')
    
    if not username or not member_to_add:
        return jsonify({'error': 'Username and member required'}), 400
    
    db = load_data()
    
    if member_to_add not in db['users']:
        return jsonify({'error': 'Member not found'}), 404
    
    for group in db['groups']:
        if group['id'] == group_id:
            if username != group['creator']:
                return jsonify({'error': 'Only group creator can add members'}), 403
            
            if member_to_add in group['members']:
                return jsonify({'error': 'User already in group'}), 400
            
            group['members'].append(member_to_add)
            save_data(db)
            
            return jsonify({
                'success': True,
                'message': f'{member_to_add} added to group',
                'group': group
            }), 200
    
    return jsonify({'error': 'Group not found'}), 404

@app.route('/api/group/<int:group_id>/pick-challenger', methods=['POST'])
def pick_random_challenger(group_id):
    db = load_data()
    
    # Find the group
    group = None
    for g in db['groups']:
        if g['id'] == group_id:
            group = g
            break
    
    if not group:
        return jsonify({'error': 'Group not found'}), 404
    
    if len(group['members']) < 2:
        return jsonify({'error': 'Group needs at least 2 members'}), 400
    
    # Check if there's already a pending challenge selection
    for challenge in db['group_challenges']:
        if challenge['group_id'] == group_id and challenge.get('status') == 'awaiting_creation':
            return jsonify({'error': 'Already waiting for a challenge to be created'}), 400
    
    # Check if a challenge was already created today for this group
    today = datetime.now().date()
    for challenge in db['group_challenges']:
        if challenge['group_id'] == group_id and challenge.get('created_at'):
            challenge_date = datetime.fromisoformat(challenge['created_at']).date()
            if challenge_date == today:
                # Calculate time until next challenge
                tomorrow = datetime.combine(today + timedelta(days=1), datetime.min.time())
                time_remaining = tomorrow - datetime.now()
                hours = int(time_remaining.total_seconds() // 3600)
                minutes = int((time_remaining.total_seconds() % 3600) // 60)
                
                return jsonify({
                    'error': f'Only one challenge per day allowed. Next challenge available in {hours}h {minutes}m',
                    'next_available': tomorrow.isoformat(),
                    'hours_remaining': hours,
                    'minutes_remaining': minutes
                }), 400
    
    # Randomly select a challenger from group members
    import random
    challenger = random.choice(group['members'])
    
    # Create a placeholder challenge
    group_challenge = {
        'id': len(db['group_challenges']) + 1,
        'group_id': group_id,
        'group_name': group['name'],
        'challenger': challenger,
        'title': None,
        'description': None,
        'difficulty': None,
        'points': None,
        'status': 'awaiting_creation',  # awaiting_creation, active
        'submissions': [],
        'created_at': datetime.now().isoformat(),
        'challenge_created_at': None
    }
    
    db['group_challenges'].append(group_challenge)
    save_data(db)
    
    return jsonify({
        'success': True,
        'message': f'{challenger} was randomly chosen to create the challenge!',
        'challenge': group_challenge
    }), 201

@app.route('/api/group-challenge/<int:challenge_id>/define', methods=['POST'])
def define_group_challenge(challenge_id):
    data = request.json
    username = data.get('username')
    title = data.get('title')
    description = data.get('description', '')
    difficulty = data.get('difficulty', 'easy')
    
    if not username or not title:
        return jsonify({'error': 'Username and title required'}), 400
    
    if difficulty not in ['easy', 'medium', 'hard']:
        return jsonify({'error': 'Invalid difficulty'}), 400
    
    db = load_data()
    
    for challenge in db['group_challenges']:
        if challenge['id'] == challenge_id:
            if challenge['challenger'] != username:
                return jsonify({'error': 'Only the chosen challenger can define this challenge'}), 403
            
            if challenge.get('status') != 'awaiting_creation':
                return jsonify({'error': 'Challenge already defined'}), 400
            
            points_map = {'easy': 10, 'medium': 25, 'hard': 50}
            
            challenge['title'] = title
            challenge['description'] = description
            challenge['difficulty'] = difficulty
            challenge['points'] = points_map[difficulty]
            challenge['status'] = 'active'
            challenge['challenge_created_at'] = datetime.now().isoformat()
            challenge['deadline'] = (datetime.now() + timedelta(hours=24)).isoformat()
            
            save_data(db)
            
            return jsonify({
                'success': True,
                'message': 'Challenge created!',
                'challenge': challenge
            }), 200
    
    return jsonify({'error': 'Challenge not found'}), 404

@app.route('/api/group/<int:group_id>/challenge/create', methods=['POST'])
def create_group_challenge(group_id):
    # This endpoint is now deprecated, keeping for backwards compatibility
    # Use /pick-challenger and /define instead
    data = request.json
    title = data.get('title')
    description = data.get('description', '')
    difficulty = data.get('difficulty', 'easy')
    
    if not title:
        return jsonify({'error': 'Title required'}), 400
    
    if difficulty not in ['easy', 'medium', 'hard']:
        return jsonify({'error': 'Invalid difficulty'}), 400
    
    db = load_data()
    
    # Find the group
    group = None
    for g in db['groups']:
        if g['id'] == group_id:
            group = g
            break
    
    if not group:
        return jsonify({'error': 'Group not found'}), 404
    
    if len(group['members']) < 2:
        return jsonify({'error': 'Group needs at least 2 members'}), 400
    
    # Randomly select a challenger from group members
    import random
    challenger = random.choice(group['members'])
    
    points_map = {'easy': 10, 'medium': 25, 'hard': 50}
    points = points_map[difficulty]
    
    group_challenge = {
        'id': len(db['group_challenges']) + 1,
        'group_id': group_id,
        'group_name': group['name'],
        'challenger': challenger,
        'title': title,
        'description': description,
        'difficulty': difficulty,
        'points': points,
        'status': 'active',
        'submissions': [],  # [{username, proof_image, status, uploaded_at}]
        'created_at': datetime.now().isoformat(),
        'challenge_created_at': datetime.now().isoformat(),
        'deadline': (datetime.now() + timedelta(hours=24)).isoformat()
    }
    
    db['group_challenges'].append(group_challenge)
    save_data(db)
    
    return jsonify({
        'success': True,
        'message': f'Group challenge created! {challenger} was randomly chosen',
        'challenge': group_challenge
    }), 201

@app.route('/api/group-challenge/<int:challenge_id>/submit', methods=['POST'])
def submit_group_challenge(challenge_id):
    data = request.json
    username = data.get('username')
    proof_image = data.get('proof_image')
    
    if not username or not proof_image:
        return jsonify({'error': 'Username and proof image required'}), 400
    
    db = load_data()
    
    for challenge in db['group_challenges']:
        if challenge['id'] == challenge_id:
            # Check if challenge is active
            if challenge.get('status') != 'active':
                return jsonify({'error': 'Challenge is not active yet'}), 400
            
            # Check if user is in the group
            group = next((g for g in db['groups'] if g['id'] == challenge['group_id']), None)
            if not group or username not in group['members']:
                return jsonify({'error': 'You are not in this group'}), 403
            
            # Challenger cannot submit
            if username == challenge['challenger']:
                return jsonify({'error': 'You created this challenge, you cannot submit proof'}), 400
            
            # Check if already submitted
            if any(s['username'] == username for s in challenge['submissions']):
                return jsonify({'error': 'You already submitted proof'}), 400
            
            submission = {
                'username': username,
                'proof_image': proof_image,
                'status': 'pending',
                'uploaded_at': datetime.now().isoformat(),
                'reviewed_at': None
            }
            
            challenge['submissions'].append(submission)
            save_data(db)
            
            return jsonify({
                'success': True,
                'message': 'Proof submitted!',
                'challenge': challenge
            }), 200
    
    return jsonify({'error': 'Challenge not found'}), 404

@app.route('/api/group-challenge/<int:challenge_id>/review', methods=['POST'])
def review_group_submission(challenge_id):
    data = request.json
    reviewer = data.get('reviewer')
    target_username = data.get('target_username')
    accept = data.get('accept')
    
    if not reviewer or not target_username or accept is None:
        return jsonify({'error': 'Reviewer, target username, and accept status required'}), 400
    
    db = load_data()
    
    for challenge in db['group_challenges']:
        if challenge['id'] == challenge_id:
            if reviewer != challenge['challenger']:
                return jsonify({'error': 'Only the challenger can review submissions'}), 403
            
            # Find the submission
            for submission in challenge['submissions']:
                if submission['username'] == target_username:
                    if submission['status'] != 'pending':
                        return jsonify({'error': 'Submission already reviewed'}), 400
                    
                    submission['status'] = 'accepted' if accept else 'rejected'
                    submission['reviewed_at'] = datetime.now().isoformat()
                    
                    # Award points if accepted (group-specific)
                    if accept:
                        if 'group_points' not in db['users'][target_username]:
                            db['users'][target_username]['group_points'] = {}
                        
                        group_id_str = str(challenge['group_id'])
                        if group_id_str not in db['users'][target_username]['group_points']:
                            db['users'][target_username]['group_points'][group_id_str] = 0
                        
                        db['users'][target_username]['group_points'][group_id_str] += challenge['points']
                    
                    save_data(db)
                    
                    return jsonify({
                        'success': True,
                        'message': f'Submission {"accepted" if accept else "rejected"}',
                        'challenge': challenge
                    }), 200
            
            return jsonify({'error': 'Submission not found'}), 404
    
    return jsonify({'error': 'Challenge not found'}), 404

@app.route('/api/group/<int:group_id>/can-create-challenge', methods=['GET'])
def can_create_challenge(group_id):
    db = load_data()
    
    # Check if a challenge was already created today for this group
    today = datetime.now().date()
    for challenge in db['group_challenges']:
        if challenge['group_id'] == group_id and challenge.get('created_at'):
            challenge_date = datetime.fromisoformat(challenge['created_at']).date()
            if challenge_date == today:
                # Calculate time until next challenge
                tomorrow = datetime.combine(today + timedelta(days=1), datetime.min.time())
                time_remaining = tomorrow - datetime.now()
                hours = int(time_remaining.total_seconds() // 3600)
                minutes = int((time_remaining.total_seconds() % 3600) // 60)
                
                return jsonify({
                    'can_create': False,
                    'next_available': tomorrow.isoformat(),
                    'hours_remaining': hours,
                    'minutes_remaining': minutes,
                    'message': f'Next challenge available in {hours}h {minutes}m'
                }), 200
    
    return jsonify({
        'can_create': True,
        'message': 'You can create a challenge now'
    }), 200

@app.route('/api/groups/user/<username>', methods=['GET'])
def get_user_groups(username):
    db = load_data()
    user_groups = [g for g in db['groups'] if username in g['members']]
    return jsonify({'groups': user_groups}), 200

@app.route('/api/group/<int:group_id>/challenges', methods=['GET'])
def get_group_challenges(group_id):
    db = load_data()
    challenges = [c for c in db['group_challenges'] if c['group_id'] == group_id]
    return jsonify({'challenges': challenges}), 200

@app.route('/api/group/<int:group_id>/leaderboard', methods=['GET'])
def get_group_leaderboard(group_id):
    db = load_data()
    
    # Find the group
    group = None
    for g in db['groups']:
        if g['id'] == group_id:
            group = g
            break
    
    if not group:
        return jsonify({'error': 'Group not found'}), 404
    
    # Build leaderboard from group members
    leaderboard = []
    for member in group['members']:
        if member in db['users']:
            # Get group-specific points
            group_id_str = str(group_id)
            if 'group_points' not in db['users'][member]:
                db['users'][member]['group_points'] = {}
            points = db['users'][member]['group_points'].get(group_id_str, 0)
            leaderboard.append({'username': member, 'points': points})
    
    # Sort by points descending
    leaderboard.sort(key=lambda x: x['points'], reverse=True)
    
    return jsonify({'leaderboard': leaderboard}), 200

# Serve frontend files
@app.route('/')
def index():
    return send_from_directory('../frontend', 'index.html')

@app.route('/<path:path>')
def serve_static(path):
    return send_from_directory('../frontend', path)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
