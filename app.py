from flask import Flask, request, render_template, redirect, url_for, send_from_directory, flash, session
from markitdown import MarkItDown
import markdown
import os
from github import Github
import base64
from datetime import datetime
import requests
from urllib.parse import urlencode

app = Flask(__name__)
app.secret_key = os.urandom(24)  # Better secret key for sessions
markitdown = MarkItDown()

ALLOWED_EXTENSIONS = {
    'pdf', 'pptx', 'docx', 'xlsx', 'jpg', 'jpeg', 'png', 
    'mp3', 'wav', 'html', 'csv', 'json', 'xml', 'md', 'zip'
}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# GitHub OAuth configuration
GITHUB_CLIENT_ID = os.getenv('GITHUB_CLIENT_ID')
GITHUB_CLIENT_SECRET = os.getenv('GITHUB_CLIENT_SECRET')
GITHUB_AUTHORIZE_URL = 'https://github.com/login/oauth/authorize'
GITHUB_TOKEN_URL = 'https://github.com/login/oauth/access_token'
GITHUB_API_URL = 'https://api.github.com'

@app.route('/render/<style>')
@app.route('/render')
def render_page(style='default'):
    """Endpoint to show the render page with a specific style"""
    return render_template('render.html', 
                         markdown_content=session.get('pending_content', ''),
                         html_content=session.get('pending_html', ''),
                         style=style,
                         original_file=session.get('pending_filename', 'New Document'),
                         github_authenticated='github_token' in session)

@app.route('/login/github')
def github_login():
    # Store the current state
    session['pending_content'] = request.args.get('content', '')
    session['pending_style'] = request.args.get('style', 'default')
    session['pending_filename'] = request.args.get('filename', 'New Document')
    
    # Generate the rendered HTML and store it
    if session['pending_content']:
        session['pending_html'] = render_markdown(
            session['pending_content'], 
            session['pending_style']
        )
    
    params = {
        'client_id': GITHUB_CLIENT_ID,
        'scope': 'public_repo',
        'redirect_uri': url_for('github_callback', _external=True)
    }
    return redirect(f'{GITHUB_AUTHORIZE_URL}?{urlencode(params)}')

@app.route('/logout/github')
def github_logout():
    session.pop('github_token', None)
    return redirect(url_for('index'))

@app.route('/login/github/callback')
def github_callback():
    if 'error' in request.args:
        flash(f"GitHub Error: {request.args['error']}")
        return redirect(url_for('index'))
    
    code = request.args.get('code')
    response = requests.post(GITHUB_TOKEN_URL, data={
        'client_id': GITHUB_CLIENT_ID,
        'client_secret': GITHUB_CLIENT_SECRET,
        'code': code
    }, headers={'Accept': 'application/json'})
    
    data = response.json()
    if 'access_token' in data:
        session['github_token'] = data['access_token']
        # Redirect to render page with stored content and style
        return redirect(url_for('render_page', 
                              style=session.get('pending_style', 'default')))
    return 'Failed to get access token'

@app.route('/')
def index():
    github_username = None
    if 'github_token' in session:
        # Get GitHub username if authenticated
        headers = {'Authorization': f'token {session["github_token"]}'}
        response = requests.get(f'{GITHUB_API_URL}/user', headers=headers)
        if response.status_code == 200:
            github_username = response.json()['login']
        else:
            # Token might be invalid, remove it
            session.pop('github_token', None)

    return render_template('index.html', 
                         allowed_extensions=ALLOWED_EXTENSIONS,
                         github_authenticated='github_token' in session,
                         github_username=github_username)

@app.route('/change_style', methods=['POST'])
def change_style():
    data = request.get_json()
    content = data.get('content', '')
    style = data.get('style', 'default')
    return render_markdown(content, style)

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        flash('No file provided')
        return redirect(url_for('index'))
    
    file = request.files['file']
    if file.filename == '':
        flash('No file selected')
        return redirect(url_for('index'))
    
    if not allowed_file(file.filename):
        flash('File type not supported')
        return redirect(url_for('index'))

    try:
        # Save the file temporarily
        temp_path = os.path.join('temp', file.filename)
        os.makedirs('temp', exist_ok=True)
        file.save(temp_path)

        # Convert to markdown using MarkItDown
        result = markitdown.convert(temp_path)
        markdown_content = result.text_content

        # Store content in session
        session['pending_content'] = markdown_content
        session['pending_filename'] = file.filename
        session['pending_style'] = request.form.get('style', 'default')

        # Convert markdown to HTML with selected style
        html_content = render_markdown(markdown_content, session['pending_style'])
        session['pending_html'] = html_content

        # Clean up temp file
        os.remove(temp_path)

        return render_template('render.html', 
                            markdown_content=markdown_content,
                            html_content=html_content, 
                            style=session['pending_style'],
                            original_file=file.filename,
                            github_authenticated='github_token' in session)
    except Exception as e:
        flash(f'Error processing file: {str(e)}')
        return redirect(url_for('index'))

def read_style_file(style_name):
    style_path = os.path.join('static', 'styles', f'{style_name}.css')
    with open(style_path, 'r') as f:
        return f.read()

def render_markdown(content, style):
    # Base wrapper to ensure styles only apply to rendered content
    base_wrapper = '<div class="rendered-content">'
    base_wrapper_end = '</div>'
    
    # Common markdown extensions for proper line breaks
    extensions = ['nl2br', 'extra', 'fenced_code', 'tables']
    
    if style == 'style1':
        html_content = markdown.markdown(content, extensions=extensions)
        css = read_style_file('terminal')
        return f'<style>{css}</style>{base_wrapper}<div class="terminal">{html_content}</div>{base_wrapper_end}'
    elif style == 'style2':
        html_content = markdown.markdown(content, extensions=extensions)
        css = read_style_file('modern_resume')
        return f'<style>{css}</style>{base_wrapper}<div class="resume-layout">{html_content}</div>{base_wrapper_end}'
    else:
        html_content = markdown.markdown(content, extensions=extensions)
        css = read_style_file('minimal')
        return f'<style>{css}</style>{base_wrapper}<div class="content-wrapper">{html_content}</div>{base_wrapper_end}'

# GitHub configuration
# Required scope: public_repo (for creating and updating public repositories)
GITHUB_TOKEN = os.getenv('GITHUB_TOKEN')

def save_to_github(html_content, css_content, repo_name):
    if 'github_token' not in session:
        raise Exception("Not authenticated with GitHub")
    
    headers = {
        'Authorization': f'token {session["github_token"]}',
        'Accept': 'application/vnd.github.v3+json'
    }

    # Get user information
    user_response = requests.get(f'{GITHUB_API_URL}/user', headers=headers)
    if user_response.status_code != 200:
        raise Exception("Failed to get user information")
    user = user_response.json()

    # Create or get repository
    repo_response = requests.get(f'{GITHUB_API_URL}/repos/{user["login"]}/{repo_name}', headers=headers)
    
    if repo_response.status_code == 404:
        # Create repository
        create_repo_response = requests.post(
            f'{GITHUB_API_URL}/user/repos',
            headers=headers,
            json={
                'name': repo_name,
                'auto_init': True,
                'private': False,
                'has_pages': True
            }
        )
        if create_repo_response.status_code != 201:
            raise Exception("Failed to create repository")

        # Wait for repository creation
        import time
        time.sleep(2)

    # Create HTML file
    complete_html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <style>{css_content}</style>
</head>
<body>{html_content}</body>
</html>"""

    # Convert content to base64
    content_bytes = complete_html.encode('utf-8')
    content_b64 = base64.b64encode(content_bytes).decode('utf-8')

    # Create or update index.html
    file_url = f'{GITHUB_API_URL}/repos/{user["login"]}/{repo_name}/contents/index.html'
    
    # Check if file exists
    file_response = requests.get(file_url, headers=headers)
    if file_response.status_code == 200:
        # Update existing file
        file_data = file_response.json()
        update_data = {
            'message': 'Update resume',
            'content': content_b64,
            'sha': file_data['sha']
        }
    else:
        # Create new file
        update_data = {
            'message': 'Create resume',
            'content': content_b64
        }

    response = requests.put(file_url, headers=headers, json=update_data)
    if response.status_code not in [200, 201]:
        raise Exception("Failed to save file to GitHub")

    # Enable GitHub Pages
    pages_response = requests.post(
        f'{GITHUB_API_URL}/repos/{user["login"]}/{repo_name}/pages',
        headers={**headers, 'Accept': 'application/vnd.github.switcheroo-preview+json'},
        json={
            'source': {
                'branch': 'main'
            }
        }
    )

    return f"https://{user['login']}.github.io/{repo_name}/"

@app.route('/save_to_github', methods=['POST'])
def handle_github_save():
    if 'github_token' not in session:
        session['return_to'] = request.url
        return {"error": "Not authenticated", "need_auth": True}, 401
    
    try:
        data = request.get_json()
        html_content = data.get('content')
        style = data.get('style')
        repo_name = data.get('repo', 'resume')

        if not html_content:
            return {"error": "Missing content"}, 400

        # Get the rendered HTML with style
        styled_content = render_markdown(html_content, style)
        
        # Extract CSS and HTML
        css_start = styled_content.find('<style>') + 7
        css_end = styled_content.find('</style>')
        css_content = styled_content[css_start:css_end].strip()
        html_content = styled_content[styled_content.find('</style>') + 8:].strip()

        url = save_to_github(html_content, css_content, repo_name)
        return {"url": url}
    except Exception as e:
        return {"error": str(e)}, 500

if __name__ == '__main__':
    app.run(debug=True)
