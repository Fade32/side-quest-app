# Side Quest App - Backend

Flask-based REST API for managing sidequests and friends.

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Run the server:
```bash
python app.py
```

The server will start on `http://localhost:5000`

## API Endpoints

### Authentication
- `POST /api/login` - Login or create new user
  ```json
  {
    "username": "john",
    "password": "secret123"
  }
  ```

### Sidequests
- `POST /api/sidequest/add` - Add a new sidequest
  ```json
  {
    "username": "john",
    "title": "Learn Python",
    "description": "Complete a Python tutorial"
  }
  ```

- `POST /api/sidequest/complete` - Mark sidequest as complete
  ```json
  {
    "username": "john",
    "sidequest_id": 1
  }
  ```

- `GET /api/sidequests/<username>` - Get all sidequests for a user

### Friends
- `POST /api/friend/add` - Add a friend
  ```json
  {
    "username": "john",
    "friend_username": "jane"
  }
  ```

- `GET /api/friends/<username>` - Get all friends for a user

### Challenges
- `POST /api/challenge/create` - Create a challenge for a friend
  ```json
  {
    "challenger": "john",
    "challenged": "jane",
    "title": "Do 50 pushups",
    "description": "Complete 50 pushups in one set"
  }
  ```

- `POST /api/challenge/upload-proof` - Upload proof image (base64)
  ```json
  {
    "challenge_id": 1,
    "username": "jane",
    "proof_image": "data:image/png;base64,..."
  }
  ```

- `POST /api/challenge/review` - Accept or reject challenge proof
  ```json
  {
    "challenge_id": 1,
    "username": "john",
    "accept": true
  }
  ```

- `GET /api/challenges/sent/<username>` - Get challenges you sent
- `GET /api/challenges/received/<username>` - Get challenges you received
