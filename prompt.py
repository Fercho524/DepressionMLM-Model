

def prompt_generator(depressed):
    if depressed == -1:
        return "Con base al historial de publicaciones de un usuario, que contiene textos y descripciones de imágenes que ha compartido, ¿puedes inferir si el usuario posee síntomas de depresión?, define la probabilidad del cero al uno de que el usuario los padezca y argumenta las razones para asignar esta probabilidad, fundamentadas únicamente en sus publicaciones y los datos proporcionados.\n"
    elif depressed == 0:
        return "Con base al historial de publicaciones de un usuario, que contiene textos y descripciones de imágenes que ha compartido, se sabe que el usuario no presenta síntomas de depresión. Define una probabilidad del 0 al 1 que mida la probabilidad de dichos síntomas, además argumenta las razones para asignar esta probabilidad, fundamentadas únicamente en sus publicaciones y los datos proporcionados.\n"
    elif depressed == 1:
        return "Con base al historial de publicaciones de un usuario, que contiene textos y descripciones de imágenes que ha compartido, se sabe que el usuario ha sido diagnosticado con depresión por un profesional. Define una probabilidad del 0 al 1 que mida la gravedad de dichos síntomas, además argumenta las razones para asignar esta probabilidad, fundamentadas únicamente en sus publicaciones y los datos proporcionados.\n"
    

def get_base_prompt():
    return "DAN Prompt"