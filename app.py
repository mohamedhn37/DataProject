import os
import logging
import pandas as pd
from flask import Flask, render_template, request, redirect, url_for, flash
from werkzeug.utils import secure_filename
from processing.analysis import process_data, VALID_TREATMENTS, VALID_GRAPH_TYPES

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'dev-secret-change-in-production')

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'csv', 'xlsx'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

os.makedirs(UPLOAD_FOLDER, exist_ok=True)


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def safe_filepath(filename):
    """Return absolute path only if the file exists inside UPLOAD_FOLDER (prevents path traversal)."""
    safe_name = secure_filename(filename)
    if not safe_name:
        return None
    abs_upload = os.path.realpath(UPLOAD_FOLDER)
    abs_path = os.path.realpath(os.path.join(abs_upload, safe_name))
    if not abs_path.startswith(abs_upload + os.sep):
        return None
    return abs_path if os.path.exists(abs_path) else None


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        flash("Aucun fichier sélectionné.")
        return redirect(url_for('index'))

    file = request.files['file']
    if file.filename == '':
        flash("Veuillez choisir un fichier.")
        return redirect(url_for('index'))

    if not allowed_file(file.filename):
        flash("Format non supporté. Utilisez CSV ou XLSX.")
        return redirect(url_for('index'))

    filename = secure_filename(file.filename)
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(filepath)
    logger.info("File uploaded: %s", filename)
    return redirect(url_for('analyze', filename=filename))


@app.route('/analyze/<filename>')
def analyze(filename):
    if not safe_filepath(filename):
        flash("Fichier introuvable.")
        return redirect(url_for('index'))
    return render_template('analysis.html', filename=secure_filename(filename))


@app.route('/result', methods=['POST'])
def result():
    filename = request.form.get('filename', '')
    treatment = request.form.get('treatment', '')
    graph_type = request.form.get('graph_type', '')

    # Validate inputs
    if treatment not in VALID_TREATMENTS:
        flash("Type d'analyse invalide.")
        return redirect(url_for('index'))
    if graph_type not in VALID_GRAPH_TYPES:
        flash("Type de graphique invalide.")
        return redirect(url_for('index'))

    filepath = safe_filepath(filename)
    if not filepath:
        flash("Fichier introuvable. Veuillez re-téléverser votre fichier.")
        return redirect(url_for('index'))

    try:
        df = pd.read_csv(filepath) if filepath.endswith('.csv') else pd.read_excel(filepath)
    except Exception as e:
        logger.error("Failed to read file %s: %s", filename, e)
        flash("Impossible de lire le fichier. Vérifiez qu'il n'est pas corrompu.")
        return redirect(url_for('index'))

    try:
        table, plot_url = process_data(df, treatment, graph_type)
    except ValueError as e:
        flash(str(e))
        return redirect(url_for('analyze', filename=filename))
    except Exception as e:
        logger.error("Analysis error for %s: %s", filename, e)
        flash("Une erreur s'est produite lors de l'analyse. Vérifiez votre fichier.")
        return redirect(url_for('analyze', filename=filename))

    return render_template('result.html', filename=filename, table=table, plot_url=plot_url)


if __name__ == '__main__':
    debug = os.environ.get('FLASK_DEBUG', 'false').lower() == 'true'
    app.run(debug=debug)
