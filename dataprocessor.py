import os
import json

from modelInference import *

from prompt import *


def process_user_data(user_data_dir, model, tokenizer, processor, transcriptor):
    # Leer el archivo JSON de usuario
    user_json_path = os.path.join(user_data_dir, "user.json")
    
    if not os.path.exists(user_json_path):
        raise FileNotFoundError(f"El archivo user.json no se encuentra en {user_data_dir}")

    with open(user_json_path, "r") as user_file:
        content = user_file.read()
        user_data = json.loads(content)
        
        print(user_data["username"])

        # Etiquetar las imágenes
        for post in user_data["posts"]:
            image_path = os.path.join(user_data_dir, post["image_path"])
            if post["image_path"] != "None" and os.path.exists(image_path):
                post["image_description"] = get_caption(image_path, processor, transcriptor)
                print(post["image_description"])

        # 0 : Sano, 1 Deprimido, -1 No se sabe
        prompt = prompt_generator(-1)

        for i, post in enumerate(user_data["posts"], start=1):
            prompt += f"Publicación {i}\n"
            prompt += f"Texto de la publicación: {post['text']}\n"
            if post["image_description"] != "None":
                prompt += f"Contenido de la imagen: {post['image_description']}\n"
            prompt += "\n"

    # Realizar la inferencia con el modelo
    response = inference_model(prompt, model, tokenizer)
    return response


if __name__ == "__main__":
    processor,transcriptor = load_transcriptor()
    model,tokenizer = load_model()
    response = process_user_data("Working/itziar.dom_data",model,tokenizer,processor,transcriptor)
    print(response)