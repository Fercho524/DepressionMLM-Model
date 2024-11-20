import torch

import bitsandbytes as bnb

from PIL import Image

# Blip 2
from transformers import AutoProcessor
from transformers import Blip2ForConditionalGeneration

# Llama + Lora
from transformers import AutoModelForCausalLM, AutoTokenizer
from peft import PeftModel, PeftConfig


TORCH_DEVICE = "cuda" if torch.cuda.is_available() else "cpu"


def load_transcriptor():
    config = dict(
        load_in_4bit=True,
        bnb_4bit_quant_type="nf4",
        bnb_4bit_use_double_quant=True,
        bnb_4bit_compute_dtype=torch.bfloat16
    )
  
    processor = AutoProcessor.from_pretrained(
        "Salesforce/blip2-opt-2.7b"
    )
    model = Blip2ForConditionalGeneration.from_pretrained(
        "Salesforce/blip2-opt-2.7b",
        device_map="auto",
        quantization_config=config
    )

    return processor,model


def get_caption(file,processor,model):
    image= Image.open(file).convert('RGB')
    inputs = processor(images=image,return_tensors="pt").to(TORCH_DEVICE, torch.float16)
    generated_ids = model.generate(**inputs, max_new_tokens=30)
    generated_text = processor.batch_decode(generated_ids, skip_special_tokens=True)[0].strip()
    return generated_text


def load_model(adapter_model="fercho524/depressmultimodal"):
    # No toda la culpa es del mal entrenamiento, el modelo que elegí como base está medio chafa y no puede hablar bien en español
    base_model = "NousResearch/Hermes-3-Llama-3.1-8B"
    adapter_model="fercho524/depressmultimodal"

    bnb_config = dict(
        load_in_4bit=True,
        bnb_4bit_quant_type="nf4",
        bnb_4bit_use_double_quant=True,
        bnb_4bit_compute_dtype=torch.bfloat16
    )

    model = AutoModelForCausalLM.from_pretrained(
        base_model, 
        quantization_config=bnb_config
    )

    model = PeftModel.from_pretrained(
        model, 
        adapter_model, 
        quantization_config=bnb_config
    )
    
    tokenizer = AutoTokenizer.from_pretrained(base_model)

    model = model.to("cuda")
    return model,tokenizer


def prepare_prompt(texto):
    SYSTEM_PROMPT = """Bienvenido, Senti. Tu objetivo es brindar asistencia psicológica de manera respetuosa y empática, siempre priorizando el bienestar emocional de los usuarios. Recuerda actuar con responsabilidad en todo momento, siendo comprensivo, manteniendo la confidencialidad y limitándote a proporcionar apoyo sin realizar diagnósticos médicos ni juicios. Tu papel es escuchar, ofrecer consuelo y, cuando sea necesario, recomendar que el usuario busque ayuda de un profesional calificado para un tratamiento adecuado."""

    # Convert the data to a Pandas DataFrame
    text_prompt = "<|im_start|>system\n" + SYSTEM_PROMPT + "<|im_end|>\n<|im_start|>user\n" + texto + "<|im_end|>\n<|im_start|>assistant\n"
    return text_prompt


def inference_model(input_text,model,tokenizer):
    inputs = tokenizer(prepare_prompt(input_text),return_tensors="pt")
    response_tokens = []

    with torch.no_grad():
        outputs = model.generate(
            input_ids=inputs["input_ids"].to("cuda"), 
            max_new_tokens=4096
        )
        response_tokens.append(
            tokenizer.batch_decode(
                outputs.detach().cpu().numpy(), 
                skip_special_tokens=True
            )[0]
        )

    del inputs, outputs
    torch.cuda.empty_cache()
    return "".join(response_tokens)



if __name__ == "__main__":
    processor,transcriptor = load_transcriptor()
    model,tokenizer = load_model()

    image_test = input("Ingresa una ruta de una imagen")

    if image_test:
        generated_text = get_caption(image_test,processor,transcriptor)
        print(generated_text)
    
    response = inference_model("Es 9.11 mayor a 9.9?",model,tokenizer)
    print(response)