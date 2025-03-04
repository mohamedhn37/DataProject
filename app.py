from flask import Flask, render_template, request, redirect, url_for, send_file
import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import io
import base64
from werkzeug.utils import secure_filename
from processing.analysis import process_data

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads/'
ALLOWED_EXTENSIONS = {'csv', 'xlsx'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Créer le dossier 'uploads/' s'il n'existe pas
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# Vérifier si le fichier est autorisé
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Page d'accueil - Upload du fichier
@app.route('/')
def index():
    return render_template('index.html')

# Upload du fichier et affichage des options
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
        return redirect(url_for('analyze', filename=filename))

    return "Format de fichier non supporté"

# Page pour choisir une analyse
@app.route('/analyze/<filename>')
def analyze(filename):
    return render_template('analysis.html', filename=filename)

# Appliquer un traitement et afficher résultat
@app.route('/result', methods=['POST'])
def result():
    filename = request.form['filename']
    treatment = request.form['treatment']
    graph_type = request.form['graph_type']
    
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    df = pd.read_csv(filepath) if filename.endswith('.csv') else pd.read_excel(filepath)

    # Obtenir les résultats sous forme de tableau et de graphique
    table, plot_url = process_data(df, treatment, graph_type)

    return render_template('result.html', filename=filename, table=table, plot_url=plot_url)

if __name__ == '__main__':
    app.run(debug=True)
