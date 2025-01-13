from flask import Flask, request, render_template, redirect, url_for, send_from_directory, flash
from markitdown import MarkItDown
import markdown
import os

app = Flask(__name__)
app.secret_key = 'your-secret-key'  # Required for flashing messages
markitdown = MarkItDown()

ALLOWED_EXTENSIONS = {
    'pdf', 'pptx', 'docx', 'xlsx', 'jpg', 'jpeg', 'png', 
    'mp3', 'wav', 'html', 'csv', 'json', 'xml', 'md', 'zip'
}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    return render_template('index.html', allowed_extensions=ALLOWED_EXTENSIONS)

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

        # Convert markdown to HTML with selected style
        style = request.form.get('style', 'default')
        html_content = render_markdown(markdown_content, style)

        # Clean up temp file
        os.remove(temp_path)

        return render_template('render.html', 
                            markdown_content=markdown_content,
                            html_content=html_content, 
                            style=style, 
                            original_file=file.filename)
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
    
    if style == 'style1':
        html_content = markdown.markdown(content, extensions=['extra', 'codehilite'])
        css = read_style_file('terminal')
        return f'<style>{css}</style>{base_wrapper}<div class="terminal">{html_content}</div>{base_wrapper_end}'
    elif style == 'style2':
        html_content = markdown.markdown(content, extensions=['fenced_code', 'tables'])
        css = read_style_file('modern_resume')
        return f'<style>{css}</style>{base_wrapper}<div class="resume-layout">{html_content}</div>{base_wrapper_end}'
    else:
        html_content = markdown.markdown(content)
        css = read_style_file('minimal')
        return f'<style>{css}</style>{base_wrapper}<div class="content-wrapper">{html_content}</div>{base_wrapper_end}'

if __name__ == '__main__':
    app.run(debug=True)
