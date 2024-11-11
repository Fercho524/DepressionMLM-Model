from flask import Flask, request, jsonify
import os
import zipfile
import tempfile
from dataprocessor import process_user_data
from modelInference import *
from datetime import datetime
from scraper import FacebookScraper



# Inicializar Flask
app = Flask(__name__)

# Variables para el modelo y el transcriptor, cargados una sola vez
model_context = {
    'processor': None,
    'transcriptor': None,
    'model': None,
    'tokenizer': None
}

# Función para cargar los modelos (solo se ejecuta una vez)
def load_models_once():
    if model_context['processor'] is None or model_context['transcriptor'] is None:
        print("Cargando modelos y transcriptores...")
        model_context['processor'], model_context['transcriptor'] = load_transcriptor()
        model_context['model'], model_context['tokenizer'] = load_model()
        print("Modelos y transcriptores cargados")

# Ejecutar esta función al inicio para asegurar la carga
load_models_once()

# Directorio de trabajo
WORK_FOLDER = 'Working'
os.makedirs(WORK_FOLDER, exist_ok=True)


@app.route('/inference', methods=['POST'])
def model_inference():
    # Obtener el nombre del archivo desde el cuerpo de la solicitud
    profile_link = request.json.get("profile_link")
    print(request.json)
    
    if not profile_link:
        return jsonify({"error": "No username provided"}), 400

    username = profile_link.split("/")[-1]

    # Intentar obtener los datos de facebook
    try:
        scraper = FacebookScraper(base_dir=WORK_FOLDER, headless=True)

        # Descargar publicaciones
        user_data, user_data_dir = scraper.download_user_posts(
            profile_link=profile_link,
            private_profile=False,
            credentials={
                "username": "your_username",
                "password": "your_password"
            }
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 400

    # Procesar los datos con el modelo de IA
    try:
        response = process_user_data(
            user_data_dir,
            model_context['model'],
            model_context['tokenizer'],
            model_context['processor'],
            model_context['transcriptor']
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 500

    return jsonify({"response": response}), 200


# Ruta de prueba
@app.route('/')
def index():
    return "API for processing user data with AI is running"

if __name__ == '__main__':
    app.run(debug=False,host="0.0.0.0", port=5000)
