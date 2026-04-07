from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime
import json
import os

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "*"}})

# Simple file-based storage (replace with database later)
DATA_FILE = 'data.json'

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r') as f:
            return json.load(f)
    return {'users': {}, 'sidequests': [], 'friendships': [], 'challenges': []}

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
            return jsonify({
                'success': True,
                'message': 'Login successful',
                'user': {'username': username}
            }), 200
        else:
            return jsonify({'error': 'Invalid password'}), 401
    else:
        # Create new user
        db['users'][username] = {
            'password': password,
            'created_at': datetime.now().isoformat()
        }
        save_data(db)
        return jsonify({
            'success': True,
            'message': 'User created and logged in',
            'user': {'username': username}
        }), 201

@app.route('/api/sidequest/add', methods=['POST'])
def add_sidequest():
    data = request.json
    username = data.get('username')
    title = data.get('title')
    description = data.get('description', '')
    
    if not username or not title:
        return jsonify({'error': 'Username and title required'}), 400
    
    db = load_data()
    
    if username not in db['users']:
        return jsonify({'error': 'User not found'}), 404
    
    sidequest = {
        'id': len(db['sidequests']) + 1,
        'username': username,
        'title': title,
        'description': description,
        'completed': False,
        'created_at': datetime.now().isoformat(),
        'completed_at': None
    }
    
    db['sidequests'].append(sidequest)
    save_data(db)
    
    return jsonify({
        'success': True,
        'message': 'Sidequest added',
        'sidequest': sidequest
    }), 201

@app.route('/api/sidequest/complete', methods=['POST'])
def complete_sidequest():
    data = request.json
    sidequest_id = data.get('sidequest_id')
    username = data.get('username')
    
    if not sidequest_id or not username:
        return jsonify({'error': 'Sidequest ID and username required'}), 400
    
    db = load_data()
    
    for quest in db['sidequests']:
        if quest['id'] == sidequest_id and quest['username'] == username:
            if quest['completed']:
                return jsonify({'error': 'Sidequest already completed'}), 400
            
            quest['completed'] = True
            quest['completed_at'] = datetime.now().isoformat()
            save_data(db)
            
            return jsonify({
                'success': True,
                'message': 'Sidequest completed!',
                'sidequest': quest
            }), 200
    
    return jsonify({'error': 'Sidequest not found'}), 404

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
    
    if not challenger or not challenged or not title:
        return jsonify({'error': 'Challenger, challenged user, and title required'}), 400
    
    if challenger == challenged:
        return jsonify({'error': 'Cannot challenge yourself'}), 400
    
    db = load_data()
    
    if challenger not in db['users'] or challenged not in db['users']:
        return jsonify({'error': 'User not found'}), 404
    
    challenge = {
        'id': len(db['challenges']) + 1,
        'challenger': challenger,
        'challenged': challenged,
        'title': title,
        'description': description,
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

if __name__ == '__main__':
    app.run(debug=True, port=5000)
