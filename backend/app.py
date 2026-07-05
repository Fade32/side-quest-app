from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import and_, or_, func
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash, check_password_hash
import re
import os
import json
import random

app = Flask(__name__)
CORS(app)

# Database configuration (PostgreSQL in production, SQLite for local dev fallback)
_db_url = os.getenv('DATABASE_URL', 'sqlite:///side_quest.db')
if _db_url.startswith('postgresql'):
    from sqlalchemy.engine.url import make_url
    _url = make_url(_db_url)
    _url = _url.set(drivername='postgresql+psycopg')
    app.config['SQLALCHEMY_DATABASE_URI'] = _url
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = _db_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)


class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now)

    def to_dict(self):
        group_points = GroupPoints.query.filter_by(user_id=self.id).all()
        return {
            'username': self.username,
            'group_points': {gp.group_id: gp.points for gp in group_points}
        }


class UserPoints(db.Model):
    __tablename__ = 'user_points'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, unique=True)
    points = db.Column(db.Integer, default=0)


class Friendship(db.Model):
    __tablename__ = 'friendships'
    id = db.Column(db.Integer, primary_key=True)
    user1 = db.Column(db.String(80), nullable=False)
    user2 = db.Column(db.String(80), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now)


class SideQuest(db.Model):
    __tablename__ = 'sidequests'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), nullable=False)
    title = db.Column(db.String(120), nullable=False)
    description = db.Column(db.Text, default='')
    completed = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.now)

    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'title': self.title,
            'description': self.description,
            'completed': self.completed,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class DirectChallenge(db.Model):
    __tablename__ = 'direct_challenges'
    id = db.Column(db.Integer, primary_key=True)
    challenger = db.Column(db.String(80), nullable=False)
    challenged = db.Column(db.String(80), nullable=False)
    title = db.Column(db.String(120), nullable=False)
    description = db.Column(db.Text, default='')
    difficulty = db.Column(db.String(20), nullable=False)
    points = db.Column(db.Integer, nullable=False)
    status = db.Column(db.String(30), default='pending')  # pending, proof_uploaded, accepted, rejected
    proof_image = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.now)
    uploaded_at = db.Column(db.DateTime, nullable=True)
    reviewed_at = db.Column(db.DateTime, nullable=True)

    def to_dict(self):
        return {
            'id': self.id,
            'challenger': self.challenger,
            'challenged': self.challenged,
            'title': self.title,
            'description': self.description,
            'difficulty': self.difficulty,
            'points': self.points,
            'status': self.status,
            'proof_image': self.proof_image,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'uploaded_at': self.uploaded_at.isoformat() if self.uploaded_at else None,
            'reviewed_at': self.reviewed_at.isoformat() if self.reviewed_at else None
        }


class Group(db.Model):
    __tablename__ = 'groups'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    creator = db.Column(db.String(80), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now)


class GroupMember(db.Model):
    __tablename__ = 'group_members'
    id = db.Column(db.Integer, primary_key=True)
    group_id = db.Column(db.Integer, db.ForeignKey('groups.id'), nullable=False)
    username = db.Column(db.String(80), nullable=False)
    __table_args__ = (db.UniqueConstraint('group_id', 'username', name='uq_group_member'),)


class GroupChallenge(db.Model):
    __tablename__ = 'group_challenges_v2'
    id = db.Column(db.Integer, primary_key=True)
    group_id = db.Column(db.Integer, db.ForeignKey('groups.id'), nullable=False)
    group_name = db.Column(db.String(120), nullable=False)
    challenger = db.Column(db.String(80), nullable=False)
    title = db.Column(db.String(120), nullable=True)
    description = db.Column(db.Text, nullable=True)
    difficulty = db.Column(db.String(20), nullable=True)
    points = db.Column(db.Integer, nullable=True)
    status = db.Column(db.String(30), nullable=False)  # awaiting_creation, active
    created_at = db.Column(db.DateTime, default=datetime.now)
    challenge_created_at = db.Column(db.DateTime, nullable=True)
    deadline = db.Column(db.DateTime, nullable=True)

    def to_dict(self):
        submissions = GroupChallengeSubmission.query.filter_by(challenge_id=self.id).all()
        return {
            'id': self.id,
            'group_id': self.group_id,
            'group_name': self.group_name,
            'challenger': self.challenger,
            'title': self.title,
            'description': self.description,
            'difficulty': self.difficulty,
            'points': self.points,
            'status': self.status,
            'submissions': [s.to_dict() for s in submissions],
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'challenge_created_at': self.challenge_created_at.isoformat() if self.challenge_created_at else None,
            'deadline': self.deadline.isoformat() if self.deadline else None
        }


class GroupChallengeSubmission(db.Model):
    __tablename__ = 'group_challenge_submissions'
    id = db.Column(db.Integer, primary_key=True)
    challenge_id = db.Column(db.Integer, db.ForeignKey('group_challenges_v2.id'), nullable=False)
    username = db.Column(db.String(80), nullable=False)
    proof_image = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(30), default='pending')  # pending, accepted, rejected
    uploaded_at = db.Column(db.DateTime, default=datetime.now)
    reviewed_at = db.Column(db.DateTime, nullable=True)
    __table_args__ = (db.UniqueConstraint('challenge_id', 'username', name='uq_challenge_submission_user'),)

    def to_dict(self):
        return {
            'username': self.username,
            'proof_image': self.proof_image,
            'status': self.status,
            'uploaded_at': self.uploaded_at.isoformat() if self.uploaded_at else None,
            'reviewed_at': self.reviewed_at.isoformat() if self.reviewed_at else None
        }


class GroupPoints(db.Model):
    __tablename__ = 'group_points'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    group_id = db.Column(db.String(80), nullable=False)
    points = db.Column(db.Integer, default=0)
    __table_args__ = (db.UniqueConstraint('user_id', 'group_id', name='uq_group_points_user_group'),)


def _sanitize(s, max_len=255):
    if not isinstance(s, str):
        return s
    s = s.strip()
    if max_len and len(s) > max_len:
        s = s[:max_len]
    return s


def _is_valid_username(username):
    if not username or not isinstance(username, str):
        return False
    return bool(re.match(r'^[a-zA-Z0-9_\-]{1,30}$', username))


def _get_user(username):
    return User.query.filter_by(username=username).first()


def _get_group_members(group_id):
    rows = GroupMember.query.filter_by(group_id=group_id).all()
    return [r.username for r in rows]


def _group_to_dict(group):
    return {
        'id': group.id,
        'name': group.name,
        'creator': group.creator,
        'members': _get_group_members(group.id),
        'created_at': group.created_at.isoformat() if group.created_at else None
    }


def _award_group_points(username, group_id, points):
    user = _get_user(username)
    if not user:
        return
    group_id_str = str(group_id)
    row = GroupPoints.query.filter_by(user_id=user.id, group_id=group_id_str).first()
    if not row:
        row = GroupPoints(user_id=user.id, group_id=group_id_str, points=0)
        db.session.add(row)
    row.points += points


def _award_user_points(username, points):
    user = _get_user(username)
    if not user:
        return
    row = UserPoints.query.filter_by(user_id=user.id).first()
    if not row:
        row = UserPoints(user_id=user.id, points=0)
        db.session.add(row)
    row.points += points


def migrate_json_to_db():
    data_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data.json')
    if not os.path.exists(data_file):
        return

    with open(data_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    users = data.get('users', {})
    for username, payload in users.items():
        if not _get_user(username):
            pw = payload.get('password', '')
            if not pw.startswith('scrypt:'):
                pw = generate_password_hash(pw)
            db.session.add(User(username=username, password=pw))
    db.session.commit()

    for username, payload in users.items():
        points_value = int(payload.get('points', 0) or 0)
        if points_value > 0:
            _award_user_points(username, points_value)

    for f in data.get('friendships', []):
        u1 = f.get('user1')
        u2 = f.get('user2')
        if not u1 or not u2:
            continue
        exists = Friendship.query.filter(
            or_(
                and_(Friendship.user1 == u1, Friendship.user2 == u2),
                and_(Friendship.user1 == u2, Friendship.user2 == u1)
            )
        ).first()
        if not exists:
            db.session.add(Friendship(user1=u1, user2=u2))

    for s in data.get('sidequests', []):
        if not SideQuest.query.filter_by(id=s.get('id')).first():
            db.session.add(SideQuest(
                id=s.get('id'),
                username=s.get('username', ''),
                title=s.get('title', ''),
                description=s.get('description', ''),
                completed=bool(s.get('completed', False)),
                created_at=datetime.fromisoformat(s['created_at']) if s.get('created_at') else datetime.now()
            ))

    for c in data.get('challenges', []):
        if not DirectChallenge.query.filter_by(id=c.get('id')).first():
            db.session.add(DirectChallenge(
                id=c.get('id'),
                challenger=c.get('challenger', ''),
                challenged=c.get('challenged', ''),
                title=c.get('title', ''),
                description=c.get('description', ''),
                difficulty=c.get('difficulty', 'easy'),
                points=int(c.get('points', 0) or 0),
                status=c.get('status', 'pending'),
                proof_image=c.get('proof_image'),
                created_at=datetime.fromisoformat(c['created_at']) if c.get('created_at') else datetime.now(),
                uploaded_at=datetime.fromisoformat(c['uploaded_at']) if c.get('uploaded_at') else None,
                reviewed_at=datetime.fromisoformat(c['reviewed_at']) if c.get('reviewed_at') else None
            ))

    for g in data.get('groups', []):
        existing_group = Group.query.filter_by(id=g.get('id')).first()
        if not existing_group:
            existing_group = Group(
                id=g.get('id'),
                name=g.get('name', ''),
                creator=g.get('creator', ''),
                created_at=datetime.fromisoformat(g['created_at']) if g.get('created_at') else datetime.now()
            )
            db.session.add(existing_group)
            db.session.flush()

        members = g.get('members', [])
        for member in members:
            member_exists = GroupMember.query.filter_by(group_id=existing_group.id, username=member).first()
            if not member_exists:
                db.session.add(GroupMember(group_id=existing_group.id, username=member))

    for gc in data.get('group_challenges', []):
        existing_gc = GroupChallenge.query.filter_by(id=gc.get('id')).first()
        if not existing_gc:
            existing_gc = GroupChallenge(
                id=gc.get('id'),
                group_id=gc.get('group_id'),
                group_name=gc.get('group_name', ''),
                challenger=gc.get('challenger', ''),
                title=gc.get('title'),
                description=gc.get('description'),
                difficulty=gc.get('difficulty'),
                points=gc.get('points'),
                status=gc.get('status', 'active'),
                created_at=datetime.fromisoformat(gc['created_at']) if gc.get('created_at') else datetime.now(),
                challenge_created_at=datetime.fromisoformat(gc['challenge_created_at']) if gc.get('challenge_created_at') else None,
                deadline=datetime.fromisoformat(gc['deadline']) if gc.get('deadline') else None
            )
            db.session.add(existing_gc)
            db.session.flush()

        for sub in gc.get('submissions', []):
            existing_sub = GroupChallengeSubmission.query.filter_by(
                challenge_id=existing_gc.id,
                username=sub.get('username')
            ).first()
            if not existing_sub and sub.get('username'):
                db.session.add(GroupChallengeSubmission(
                    challenge_id=existing_gc.id,
                    username=sub.get('username'),
                    proof_image=sub.get('proof_image', ''),
                    status=sub.get('status', 'pending'),
                    uploaded_at=datetime.fromisoformat(sub['uploaded_at']) if sub.get('uploaded_at') else datetime.now(),
                    reviewed_at=datetime.fromisoformat(sub['reviewed_at']) if sub.get('reviewed_at') else None
                ))

    for username, payload in users.items():
        for group_id, points in payload.get('group_points', {}).items():
            user = _get_user(username)
            if not user:
                continue
            existing_gp = GroupPoints.query.filter_by(user_id=user.id, group_id=str(group_id)).first()
            if not existing_gp:
                db.session.add(GroupPoints(user_id=user.id, group_id=str(group_id), points=int(points or 0)))

    db.session.commit()


@app.route('/api/login', methods=['POST'])
def login():
    data = request.json
    username = _sanitize(data.get('username', ''), max_len=30)
    password = data.get('password', '')

    if not username or not password:
        return jsonify({'error': 'Username and password required'}), 400
    if not _is_valid_username(username):
        return jsonify({'error': 'Username must be 1-30 chars (letters, numbers, _ and -)'}), 400
    if len(password) < 3:
        return jsonify({'error': 'Password must be at least 3 characters'}), 400

    user = _get_user(username)
    if user:
        if check_password_hash(user.password, password):
            return jsonify({'success': True, 'message': 'Login successful', 'user': user.to_dict()}), 200
        return jsonify({'error': 'Invalid password'}), 401

    user = User(username=username, password=generate_password_hash(password))
    db.session.add(user)
    db.session.commit()
    return jsonify({'success': True, 'message': 'User created and logged in', 'user': user.to_dict()}), 201


@app.route('/api/friend/add', methods=['POST'])
def add_friend():
    data = request.json
    username = _sanitize(data.get('username', ''), max_len=30)
    friend_username = _sanitize(data.get('friend_username', ''), max_len=30)

    if not username or not friend_username:
        return jsonify({'error': 'Username and friend username required'}), 400
    if username == friend_username:
        return jsonify({'error': 'Cannot add yourself as friend'}), 400
    if not _get_user(username):
        return jsonify({'error': 'User not found'}), 404
    if not _get_user(friend_username):
        return jsonify({'error': 'Friend not found'}), 404

    existing = Friendship.query.filter(
        or_(
            and_(Friendship.user1 == username, Friendship.user2 == friend_username),
            and_(Friendship.user1 == friend_username, Friendship.user2 == username)
        )
    ).first()
    if existing:
        return jsonify({'error': 'Friendship already exists'}), 400

    friendship = Friendship(user1=username, user2=friend_username)
    db.session.add(friendship)
    db.session.commit()

    return jsonify({
        'success': True,
        'message': f'Friend {friend_username} added',
        'friendship': {
            'user1': friendship.user1,
            'user2': friendship.user2,
            'created_at': friendship.created_at.isoformat()
        }
    }), 201


@app.route('/api/sidequests/<username>', methods=['GET'])
def get_sidequests(username):
    quests = SideQuest.query.filter_by(username=username).all()
    return jsonify({'sidequests': [q.to_dict() for q in quests]}), 200


@app.route('/api/sidequest/add', methods=['POST'])
def add_sidequest():
    data = request.json
    username = _sanitize(data.get('username', ''), max_len=30)
    title = _sanitize(data.get('title', ''), max_len=120)
    description = _sanitize(data.get('description', ''), max_len=500)

    if not username or not title:
        return jsonify({'error': 'Username and title required'}), 400
    if not _get_user(username):
        return jsonify({'error': 'User not found'}), 404

    quest = SideQuest(username=username, title=title, description=description)
    db.session.add(quest)
    db.session.commit()
    return jsonify({'success': True, 'message': 'Side quest created!', 'sidequest': quest.to_dict()}), 201


@app.route('/api/sidequest/<int:quest_id>/complete', methods=['POST'])
def complete_sidequest(quest_id):
    data = request.json
    username = _sanitize(data.get('username', ''), max_len=30)

    quest = SideQuest.query.filter_by(id=quest_id).first()
    if not quest:
        return jsonify({'error': 'SideQuest not found'}), 404
    if quest.username != username:
        return jsonify({'error': 'Not your side quest'}), 403
    if quest.completed:
        return jsonify({'error': 'Already completed'}), 400

    quest.completed = True
    _award_user_points(username, 5)
    db.session.commit()
    return jsonify({'success': True, 'message': 'Side quest completed! +5 pts', 'sidequest': quest.to_dict()}), 200


@app.route('/api/sidequest/<int:quest_id>/delete', methods=['POST'])
def delete_sidequest(quest_id):
    data = request.json
    username = _sanitize(data.get('username', ''), max_len=30)

    quest = SideQuest.query.filter_by(id=quest_id).first()
    if not quest:
        return jsonify({'error': 'SideQuest not found'}), 404
    if quest.username != username:
        return jsonify({'error': 'Not your side quest'}), 403

    db.session.delete(quest)
    db.session.commit()
    return jsonify({'success': True, 'message': 'Side quest deleted'}), 200


@app.route('/api/friends/<username>', methods=['GET'])
def get_friends(username):
    friendships = Friendship.query.filter(
        or_(Friendship.user1 == username, Friendship.user2 == username)
    ).all()
    friends = [f.user2 if f.user1 == username else f.user1 for f in friendships]
    return jsonify({'friends': friends}), 200


@app.route('/api/challenge/create', methods=['POST'])
def create_challenge():
    data = request.json
    challenger = _sanitize(data.get('challenger', ''), max_len=30)
    challenged = _sanitize(data.get('challenged', ''), max_len=30)
    title = _sanitize(data.get('title', ''), max_len=120)
    description = _sanitize(data.get('description', ''), max_len=500)
    difficulty = _sanitize(data.get('difficulty', 'easy'), max_len=20)

    if not challenger or not challenged or not title:
        return jsonify({'error': 'Challenger, challenged user, and title required'}), 400
    if challenger == challenged:
        return jsonify({'error': 'Cannot challenge yourself'}), 400
    if difficulty not in ['easy', 'medium', 'hard']:
        return jsonify({'error': 'Invalid difficulty. Must be easy, medium, or hard'}), 400
    if not _get_user(challenger) or not _get_user(challenged):
        return jsonify({'error': 'User not found'}), 404

    cutoff = datetime.now() - timedelta(hours=2)
    recent = DirectChallenge.query.filter_by(challenger=challenger, challenged=challenged).filter(
        DirectChallenge.created_at > cutoff
    ).first()
    if recent:
        minutes = int((recent.created_at + timedelta(hours=2) - datetime.now()).total_seconds() / 60)
        minutes = max(minutes, 1)
        return jsonify({'error': f'Cooldown active. Wait {minutes} more minutes'}), 400

    points = {'easy': 10, 'medium': 25, 'hard': 50}[difficulty]
    challenge = DirectChallenge(
        challenger=challenger,
        challenged=challenged,
        title=title,
        description=description,
        difficulty=difficulty,
        points=points,
        status='pending'
    )
    db.session.add(challenge)
    db.session.commit()

    return jsonify({'success': True, 'message': f'Challenge sent to {challenged}', 'challenge': challenge.to_dict()}), 201


@app.route('/api/challenge/upload-proof', methods=['POST'])
def upload_proof():
    data = request.json
    challenge_id = data.get('challenge_id')
    username = _sanitize(data.get('username', ''), max_len=30)
    proof_image = data.get('proof_image')

    if not challenge_id or not username or not proof_image:
        return jsonify({'error': 'Challenge ID, username, and proof image required'}), 400

    challenge = DirectChallenge.query.filter_by(id=challenge_id, challenged=username).first()
    if not challenge:
        return jsonify({'error': 'Challenge not found or you are not the challenged user'}), 404
    if challenge.status != 'pending':
        return jsonify({'error': 'Challenge already has proof or is completed'}), 400

    challenge.proof_image = proof_image
    challenge.status = 'proof_uploaded'
    challenge.uploaded_at = datetime.now()
    db.session.commit()
    return jsonify({'success': True, 'message': 'Proof uploaded! Waiting for review.', 'challenge': challenge.to_dict()}), 200


@app.route('/api/challenge/review', methods=['POST'])
def review_challenge():
    data = request.json
    challenge_id = data.get('challenge_id')
    username = _sanitize(data.get('username', ''), max_len=30)
    accept = data.get('accept')

    if not challenge_id or not username or accept is None:
        return jsonify({'error': 'Challenge ID, username, and accept status required'}), 400

    challenge = DirectChallenge.query.filter_by(id=challenge_id, challenger=username).first()
    if not challenge:
        return jsonify({'error': 'Challenge not found or you are not the challenger'}), 404
    if challenge.status != 'proof_uploaded':
        return jsonify({'error': 'No proof uploaded yet or already reviewed'}), 400

    challenge.status = 'accepted' if accept else 'rejected'
    challenge.reviewed_at = datetime.now()
    if accept:
        _award_user_points(challenge.challenged, challenge.points)
    db.session.commit()

    return jsonify({
        'success': True,
        'message': f'Challenge {"accepted" if accept else "rejected"}!',
        'challenge': challenge.to_dict()
    }), 200


@app.route('/api/challenges/sent/<username>', methods=['GET'])
def get_sent_challenges(username):
    challenges = DirectChallenge.query.filter_by(challenger=username).all()
    return jsonify({'challenges': [c.to_dict() for c in challenges]}), 200


@app.route('/api/challenges/received/<username>', methods=['GET'])
def get_received_challenges(username):
    challenges = DirectChallenge.query.filter_by(challenged=username).all()
    return jsonify({'challenges': [c.to_dict() for c in challenges]}), 200


@app.route('/api/user/<username>/points', methods=['GET'])
def get_user_points(username):
    user = _get_user(username)
    if not user:
        return jsonify({'error': 'User not found'}), 404

    group_id = request.args.get('group_id')
    if group_id:
        row = GroupPoints.query.filter_by(user_id=user.id, group_id=str(group_id)).first()
        return jsonify({'username': username, 'group_id': group_id, 'points': row.points if row else 0}), 200

    group_points = GroupPoints.query.filter_by(user_id=user.id).all()
    total_row = UserPoints.query.filter_by(user_id=user.id).first()
    return jsonify({
        'username': username,
        'points': total_row.points if total_row else 0,
        'group_points': {gp.group_id: gp.points for gp in group_points}
    }), 200


@app.route('/api/group/create', methods=['POST'])
def create_group():
    data = request.json
    creator = _sanitize(data.get('creator', ''), max_len=30)
    name = _sanitize(data.get('name', ''), max_len=120)

    if not creator or not name:
        return jsonify({'error': 'Creator and group name required'}), 400
    if not _get_user(creator):
        return jsonify({'error': 'User not found'}), 404

    group = Group(name=name, creator=creator)
    db.session.add(group)
    db.session.flush()
    db.session.add(GroupMember(group_id=group.id, username=creator))
    db.session.commit()

    return jsonify({'success': True, 'message': f'Group "{name}" created', 'group': _group_to_dict(group)}), 201


@app.route('/api/group/<int:group_id>/add-member', methods=['POST'])
def add_group_member(group_id):
    data = request.json
    username = _sanitize(data.get('username', ''), max_len=30)
    member_to_add = _sanitize(data.get('member', ''), max_len=30)

    if not username or not member_to_add:
        return jsonify({'error': 'Username and member required'}), 400
    if not _get_user(member_to_add):
        return jsonify({'error': 'Member not found'}), 404

    group = Group.query.filter_by(id=group_id).first()
    if not group:
        return jsonify({'error': 'Group not found'}), 404
    if username != group.creator:
        return jsonify({'error': 'Only group creator can add members'}), 403

    exists = GroupMember.query.filter_by(group_id=group_id, username=member_to_add).first()
    if exists:
        return jsonify({'error': 'User already in group'}), 400

    db.session.add(GroupMember(group_id=group_id, username=member_to_add))
    db.session.commit()
    return jsonify({'success': True, 'message': f'{member_to_add} added to group', 'group': _group_to_dict(group)}), 200


@app.route('/api/group/<int:group_id>/pick-challenger', methods=['POST'])
def pick_random_challenger(group_id):
    group = Group.query.filter_by(id=group_id).first()
    if not group:
        return jsonify({'error': 'Group not found'}), 404

    members = _get_group_members(group_id)
    if len(members) < 2:
        return jsonify({'error': 'Group needs at least 2 members'}), 400

    pending = GroupChallenge.query.filter_by(group_id=group_id, status='awaiting_creation').first()
    if pending:
        return jsonify({'error': 'Already waiting for a challenge to be created'}), 400

    today = datetime.now().date()
    todays_challenge = GroupChallenge.query.filter_by(group_id=group_id).filter(
        func.date(GroupChallenge.created_at) == today
    ).first()
    if todays_challenge:
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

    challenger = random.choice(members)
    challenge = GroupChallenge(
        group_id=group_id,
        group_name=group.name,
        challenger=challenger,
        status='awaiting_creation'
    )
    db.session.add(challenge)
    db.session.commit()

    return jsonify({
        'success': True,
        'message': f'{challenger} was randomly chosen to create the challenge!',
        'challenge': challenge.to_dict()
    }), 201


@app.route('/api/group-challenge/<int:challenge_id>/define', methods=['POST'])
def define_group_challenge(challenge_id):
    data = request.json
    username = _sanitize(data.get('username', ''), max_len=30)
    title = _sanitize(data.get('title', ''), max_len=120)
    description = _sanitize(data.get('description', ''), max_len=500)
    difficulty = _sanitize(data.get('difficulty', 'easy'), max_len=20)

    if not username or not title:
        return jsonify({'error': 'Username and title required'}), 400
    if difficulty not in ['easy', 'medium', 'hard']:
        return jsonify({'error': 'Invalid difficulty'}), 400

    challenge = GroupChallenge.query.filter_by(id=challenge_id).first()
    if not challenge:
        return jsonify({'error': 'Challenge not found'}), 404
    if challenge.challenger != username:
        return jsonify({'error': 'Only the chosen challenger can define this challenge'}), 403
    if challenge.status != 'awaiting_creation':
        return jsonify({'error': 'Challenge already defined'}), 400

    challenge.title = title
    challenge.description = description
    challenge.difficulty = difficulty
    challenge.points = {'easy': 10, 'medium': 25, 'hard': 50}[difficulty]
    challenge.status = 'active'
    challenge.challenge_created_at = datetime.now()
    challenge.deadline = datetime.now() + timedelta(hours=24)
    db.session.commit()

    return jsonify({'success': True, 'message': 'Challenge created!', 'challenge': challenge.to_dict()}), 200


@app.route('/api/group/<int:group_id>/challenge/create', methods=['POST'])
def create_group_challenge(group_id):
    data = request.json
    title = data.get('title')
    description = data.get('description', '')
    difficulty = data.get('difficulty', 'easy')

    if not title:
        return jsonify({'error': 'Title required'}), 400
    if difficulty not in ['easy', 'medium', 'hard']:
        return jsonify({'error': 'Invalid difficulty'}), 400

    group = Group.query.filter_by(id=group_id).first()
    if not group:
        return jsonify({'error': 'Group not found'}), 404

    members = _get_group_members(group_id)
    if len(members) < 2:
        return jsonify({'error': 'Group needs at least 2 members'}), 400

    challenger = random.choice(members)
    challenge = GroupChallenge(
        group_id=group_id,
        group_name=group.name,
        challenger=challenger,
        title=title,
        description=description,
        difficulty=difficulty,
        points={'easy': 10, 'medium': 25, 'hard': 50}[difficulty],
        status='active',
        challenge_created_at=datetime.now(),
        deadline=datetime.now() + timedelta(hours=24)
    )
    db.session.add(challenge)
    db.session.commit()

    return jsonify({
        'success': True,
        'message': f'Group challenge created! {challenger} was randomly chosen',
        'challenge': challenge.to_dict()
    }), 201


@app.route('/api/group-challenge/<int:challenge_id>/submit', methods=['POST'])
def submit_group_challenge(challenge_id):
    data = request.json
    username = _sanitize(data.get('username', ''), max_len=30)
    proof_image = data.get('proof_image')

    if not username or not proof_image:
        return jsonify({'error': 'Username and proof image required'}), 400

    challenge = GroupChallenge.query.filter_by(id=challenge_id).first()
    if not challenge:
        return jsonify({'error': 'Challenge not found'}), 404
    if challenge.status != 'active':
        return jsonify({'error': 'Challenge is not active yet'}), 400

    members = _get_group_members(challenge.group_id)
    if username not in members:
        return jsonify({'error': 'You are not in this group'}), 403
    if username == challenge.challenger:
        return jsonify({'error': 'You created this challenge, you cannot submit proof'}), 400

    existing = GroupChallengeSubmission.query.filter_by(challenge_id=challenge_id, username=username).first()
    if existing:
        return jsonify({'error': 'You already submitted proof'}), 400

    submission = GroupChallengeSubmission(
        challenge_id=challenge_id,
        username=username,
        proof_image=proof_image,
        status='pending'
    )
    db.session.add(submission)
    db.session.commit()
    return jsonify({'success': True, 'message': 'Proof submitted!', 'challenge': challenge.to_dict()}), 200


@app.route('/api/group-challenge/<int:challenge_id>/review', methods=['POST'])
def review_group_submission(challenge_id):
    data = request.json
    reviewer = _sanitize(data.get('reviewer', ''), max_len=30)
    target_username = _sanitize(data.get('target_username', ''), max_len=30)
    accept = data.get('accept')

    if not reviewer or not target_username or accept is None:
        return jsonify({'error': 'Reviewer, target username, and accept status required'}), 400

    challenge = GroupChallenge.query.filter_by(id=challenge_id).first()
    if not challenge:
        return jsonify({'error': 'Challenge not found'}), 404
    if reviewer != challenge.challenger:
        return jsonify({'error': 'Only the challenger can review submissions'}), 403

    submission = GroupChallengeSubmission.query.filter_by(
        challenge_id=challenge_id,
        username=target_username
    ).first()
    if not submission:
        return jsonify({'error': 'Submission not found'}), 404
    if submission.status != 'pending':
        return jsonify({'error': 'Submission already reviewed'}), 400

    submission.status = 'accepted' if accept else 'rejected'
    submission.reviewed_at = datetime.now()
    if accept and challenge.points:
        _award_group_points(target_username, challenge.group_id, challenge.points)
    db.session.commit()

    return jsonify({
        'success': True,
        'message': f'Submission {"accepted" if accept else "rejected"}',
        'challenge': challenge.to_dict()
    }), 200


@app.route('/api/group/<int:group_id>/can-create-challenge', methods=['GET'])
def can_create_challenge(group_id):
    group = Group.query.filter_by(id=group_id).first()
    if not group:
        return jsonify({'error': 'Group not found'}), 404

    today = datetime.now().date()
    todays_challenge = GroupChallenge.query.filter_by(group_id=group_id).filter(
        func.date(GroupChallenge.created_at) == today
    ).first()
    if todays_challenge:
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

    return jsonify({'can_create': True, 'message': 'You can create a challenge now'}), 200


@app.route('/api/groups/user/<username>', methods=['GET'])
def get_user_groups(username):
    group_ids = db.session.query(GroupMember.group_id).filter_by(username=username).all()
    ids = [g.group_id for g in group_ids]
    groups = Group.query.filter(Group.id.in_(ids)).all() if ids else []
    return jsonify({'groups': [_group_to_dict(g) for g in groups]}), 200


@app.route('/api/group/<int:group_id>/challenges', methods=['GET'])
def get_group_challenges(group_id):
    challenges = GroupChallenge.query.filter_by(group_id=group_id).all()
    return jsonify({'challenges': [c.to_dict() for c in challenges]}), 200


@app.route('/api/group/<int:group_id>/leaderboard', methods=['GET'])
def get_group_leaderboard(group_id):
    group = Group.query.filter_by(id=group_id).first()
    if not group:
        return jsonify({'error': 'Group not found'}), 404

    members = _get_group_members(group_id)
    leaderboard = []
    for username in members:
        user = _get_user(username)
        points = 0
        if user:
            gp = GroupPoints.query.filter_by(user_id=user.id, group_id=str(group_id)).first()
            points = gp.points if gp else 0
        leaderboard.append({'username': username, 'points': points})
    leaderboard.sort(key=lambda x: x['points'], reverse=True)

    return jsonify({'leaderboard': leaderboard}), 200


# Serve frontend files
FRONTEND_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'frontend')
print(f"Frontend directory: {FRONTEND_DIR}")
print(f"Frontend exists: {os.path.exists(FRONTEND_DIR)}")


@app.route('/')
def index():
    print(f"Serving index.html from {FRONTEND_DIR}")
    return send_from_directory(FRONTEND_DIR, 'index.html')


@app.route('/<path:path>')
def serve_static(path):
    if path.startswith('api/'):
        return jsonify({'error': 'Not found'}), 404
    try:
        print(f"Serving {path} from {FRONTEND_DIR}")
        return send_from_directory(FRONTEND_DIR, path)
    except Exception as e:
        print(f"Error serving {path}: {e}")
        return send_from_directory(FRONTEND_DIR, 'index.html')


def _upgrade_plaintext_passwords():
    users = User.query.all()
    for user in users:
        if not user.password.startswith('scrypt:'):
            user.password = generate_password_hash(user.password)
    db.session.commit()


def _init_db():
    db.create_all()
    migrate_json_to_db()
    _upgrade_plaintext_passwords()


with app.app_context():
    _init_db()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
