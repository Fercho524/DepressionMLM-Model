from scraper import FacebookScraper
from dataprocessor import process_user_data
from modelInference import *

profile_link = input()
username = profile_link.split("/")[-1]

print(f"PROCESSING {username}")
WORK_FOLDER="/content"


print(f"GETTING USER_DATA {username}")
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
    print("ERROR AL OBTENER LOS DATOS")

# Procesar los datos con el modelo de IA
try:
    processor,transcriptor = load_transcriptor()
    model,tokenizer = load_model()

    response = process_user_data(
        user_data_dir,
        model,
        tokenizer,
        processor,
        transcriptor       
    )
except Exception as e:
    print("Ha Ocurrido un error : " + str(e))