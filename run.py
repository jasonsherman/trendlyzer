from flask import Flask, request, render_template_string
import os

app = Flask(__name__)

# Set upload folder
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Allowed file extensions
ALLOWED_EXTENSIONS = {'pdf', 'docx', 'xlsx', 'txt'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def home():
    return '''
    <h1>Welcome to Trendlyzer! 🚀</h1>
    <p>Upload your file below:</p>
    <form method="post" action="/upload" enctype="multipart/form-data">
      <input type="file" name="file">
      <input type="submit" value="Upload">
    </form>
    '''

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return 'No file part in the request.'

    file = request.files['file']

    if file.filename == '':
        return 'No selected file.'

    if file and allowed_file(file.filename):
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(filepath)

        # Analyze file (basic version)
        file_extension = file.filename.rsplit('.', 1)[1].lower()

        if file_extension == 'txt':
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()

            word_count = len(content.split())
            line_count = len(content.splitlines())

            return f'''
            <h2>File Uploaded and Analyzed ✅</h2>
            <p><b>Filename:</b> {file.filename}</p>
            <p><b>Total Lines:</b> {line_count}</p>
            <p><b>Total Words:</b> {word_count}</p>
            '''

        else:
            return f'File {file.filename} uploaded, but advanced analysis not yet available.'

    return 'Invalid file type. Allowed: PDF, DOCX, XLSX, TXT.'

if __name__ == '__main__':
    app.run(debug=True)
