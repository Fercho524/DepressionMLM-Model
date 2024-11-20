# Model API

Servidor dedicado a correr el modelo y descargar los datos directamente desde facebook utilizando Selenium. El modelo se encuentra en Huggingface : [Descargar modelo](https://huggingface.co/fercho524/depressmultimodal)

Pasos
1. Recibe el link del perfil en la ruta inference. POST localhost:5000/inference

```
{
  "profile_link" : "facebook profile link"
}
```

2. Descarga los datos utilizando Selenium y los guarda en un directorio.
3. Procesa los datos con Blip2 y algunas funciones básicas para formar el prompt.
4. Procesa el texto y devuelve una respuesta en formato json.
