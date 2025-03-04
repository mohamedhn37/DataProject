from flask import Flask, render_template, request, redirect, url_for, send_file
import os
import pandas as pd
from werkzeug.utils import secure_filename

UPLOAD_FOLDER = 'uploads/'
ALLOWED_EXTENSIONS = {'csv', 'xlsx'}

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Vérifier si le fichier est autorisé
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Page principale (upload du fichier)
@app.route('/')
def index():
    return render_template('index.html')

# Route pour gérer l'upload
@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return "Aucun fichier sélectionné"

    file = request.files['file']
    if file.filename == '':
        return "Fichier vide"

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        return redirect(url_for('process_file', filename=filename))

    return "Format de fichier non supporté"

# Route pour afficher les options de traitement
@app.route('/process/<filename>')
def process_file(filename):
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    df = pd.read_csv(filepath) if filename.endswith('.csv') else pd.read_excel(filepath)

    return render_template('result.html', filename=filename, columns=df.columns.tolist(), preview=df.head().to_html())

if __name__ == '__main__':
    app.run(debug=True)
