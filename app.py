import os
from flask import Flask, render_template, request, redirect, url_for
from werkzeug.utils import secure_filename
from dotenv import load_dotenv
import google.generativeai as genai
from PIL import Image

load_dotenv()

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max-limit

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

# Configure the Gemini API
genai.configure(api_key=os.getenv('GOOGLE_API_KEY'))
model = genai.GenerativeModel('gemini-1.5-flash')  # Updated model name

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        if 'file' not in request.files:
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            return redirect(url_for('analyze_circuit', filename=filename))
    return render_template('index.html')


@app.route('/analyze/<filename>', methods=['GET', 'POST'])
def analyze_circuit(filename):
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    
    if request.method == 'POST':
        question = request.form['question']
        
        try:
            # Open the image file
            with Image.open(filepath) as img:
                # Generate content using the image and question
                response = model.generate_content([question, img])
                answer = response.text
        except Exception as e:
            answer = f"An error occurred: {str(e)}"
        
        return render_template('result.html', filename=filename, question=question, answer=answer)
    
    return render_template('result.html', filename=filename)

if __name__ == '__main__':
    app.run(debug=True)