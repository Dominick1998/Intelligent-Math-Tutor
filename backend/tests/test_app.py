import pytest
from backend.app import app, db
from backend.models import User, Problem, Progress

@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
            yield client
        db.drop_all()

def test_register(client):
    response = client.post('/register', json={
        'username': 'testuser',
        'email': 'test@example.com',
        'password': 'password123'
    })
    assert response.status_code == 201
    assert b'User registered successfully' in response.data

def test_login(client):
    client.post('/register', json={
        'username': 'testuser',
        'email': 'test@example.com',
        'password': 'password123'
    })
    response = client.post('/login', json={
        'email': 'test@example.com',
        'password': 'password123'
    })
    assert response.status_code == 200
    assert b'access_token' in response.data

def test_logout(client):
    client.post('/register', json={
        'username': 'testuser',
        'email': 'test@example.com',
        'password': 'password123'
    })
    login_response = client.post('/login', json={
        'email': 'test@example.com',
        'password': 'password123'
    })
    access_token = login_response.json['access_token']
    response = client.post('/logout', headers={'Authorization': f'Bearer {access_token}'})
    assert response.status_code == 200
    assert b'Logout successful' in response.data

def test_get_profile(client):
    client.post('/register', json={
        'username': 'testuser',
        'email': 'test@example.com',
        'password': 'password123'
    })
    login_response = client.post('/login', json={
        'email': 'test@example.com',
        'password': 'password123'
    })
    access_token = login_response.json['access_token']
    response = client.get('/profile', headers={'Authorization': f'Bearer {access_token}'})
    assert response.status_code == 200
    assert b'testuser' in response.data
    assert b'test@example.com' in response.data

def test_update_profile(client):
    client.post('/register', json={
        'username': 'testuser',
        'email': 'test@example.com',
        'password': 'password123'
    })
    login_response = client.post('/login', json={
        'email': 'test@example.com',
        'password': 'password123'
    })
    access_token = login_response.json['access_token']
    response = client.put('/profile', json={
        'username': 'updateduser',
        'email': 'updated@example.com'
    }, headers={'Authorization': f'Bearer {access_token}'})
    assert response.status_code == 200
    assert b'Profile updated successfully' in response.data

def test_get_dashboard(client):
    client.post('/register', json={
        'username': 'testuser',
        'email': 'test@example.com',
        'password': 'password123'
    })
    login_response = client.post('/login', json={
        'email': 'test@example.com',
        'password': 'password123'
    })
    access_token = login_response.json['access_token']
    response = client.get('/dashboard', headers={'Authorization': f'Bearer {access_token}'})
    assert response.status_code == 200
    assert b'testuser' in response.data
    assert b'test@example.com' in response.data

def test_recommend(client):
    user = User(username='testuser', email='test@example.com', password='password123')
    db.session.add(user)
    db.session.commit()
    problem = Problem(question='2+2', answer='4', difficulty='easy')
    db.session.add(problem)
    db.session.commit()
    login_response = client.post('/login', json={
        'email': 'test@example.com',
        'password': 'password123'
    })
    access_token = login_response.json['access_token']
    response = client.get(f'/recommend/{user.id}', headers={'Authorization': f'Bearer {access_token}'})
    assert response.status_code == 200
    assert b'2+2' in response.data

def test_progress(client):
    user = User(username='testuser', email='test@example.com', password='password123')
    db.session.add(user)
    db.session.commit()
    problem = Problem(question='2+2', answer='4', difficulty='easy')
    db.session.add(problem)
    db.session.commit()
    login_response = client.post('/login', json={
        'email': 'test@example.com',
        'password': 'password123'
    })
    access_token = login_response.json['access_token']
    response = client.post('/progress', json={
        'user_id': user.id,
        'problem_id': problem.id,
        'status': 'completed'
    }, headers={'Authorization': f'Bearer {access_token}'})
    assert response.status_code == 201
    assert b'Progress tracked successfully' in response.data
