import os
import io  # Add this import
import pytest
from app import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['WTF_CSRF_ENABLED'] = False
    app.config['DEBUG'] = False
    client = app.test_client()
    yield client

def test_login_page(client):
    """Test the login page loads correctly"""
    response = client.get('/')
    assert response.status_code == 200
    assert b'Login with GitHub' in response.data

def test_dashboard_redirect(client):
    """Test redirect to dashboard after login"""
    with client.session_transaction() as session:
        session['github_token'] = 'fake_token'
    response = client.get('/')
    assert response.status_code == 302
    assert response.location.endswith('/dashboard')

def test_dashboard_page(client):
    """Test the dashboard page loads correctly"""
    with client.session_transaction() as session:
        session['github_token'] = 'fake_token'
    response = client.get('/dashboard')
    assert response.status_code == 200
    assert b'Convert File to HTML' in response.data

def test_render_page(client):
    """Test the render page loads correctly"""
    with client.session_transaction() as session:
        session['github_token'] = 'fake_token'
        session['pending_content'] = '# Test Markdown'
        session['pending_html'] = '<h1>Test Markdown</h1>'
    response = client.get('/render')
    assert response.status_code == 200
    assert b'Test Markdown' in response.data

def test_github_login_redirect(client):
    """Test GitHub login redirect"""
    response = client.get('/login/github')
    assert response.status_code == 302
    assert 'github.com/login/oauth/authorize' in response.location

def test_github_logout(client):
    """Test GitHub logout"""
    with client.session_transaction() as session:
        session['github_token'] = 'fake_token'
    response = client.get('/logout/github')
    assert response.status_code == 302
    assert response.location.endswith('/')

def test_upload_file_no_file(client):
    """Test upload file with no file provided"""
    with client.session_transaction() as session:
        session['github_token'] = 'fake_token'
    response = client.post('/upload', data={})
    assert response.status_code == 302
    assert response.location.endswith('/dashboard')

def test_upload_file_invalid_extension(client):
    """Test upload file with invalid extension"""
    with client.session_transaction() as session:
        session['github_token'] = 'fake_token'
    data = {
        'file': (io.BytesIO(b"fake content"), 'test.txt')
    }
    response = client.post('/upload', data=data, content_type='multipart/form-data')
    assert response.status_code == 302
    assert response.location.endswith('/dashboard')

def test_change_style(client):
    """Test change style endpoint"""
    data = {
        'content': '# Test Markdown',
        'style': 'default'
    }
    response = client.post('/change_style', json=data)
    assert response.status_code == 200
    assert b'<style>' in response.data

def test_chat_endpoint(client):
    """Test chat endpoint"""
    data = {
        'content': '# Test Markdown',
        'message': 'Improve this'
    }
    response = client.post('/chat', json=data)
    assert response.status_code == 200
    assert b'improved_content' in response.data
