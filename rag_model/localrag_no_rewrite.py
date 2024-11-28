import torch
import ollama
import os
import time
import logging
import requests
from transformers import AutoTokenizer, AutoModelForCausalLM
from gpt4all import GPT4All
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

# ANSI escape codes for colors
NEON_GREEN = '\033[92m'
RESET_COLOR = '\033[0m'

SERVER_BASE_URL = 'http://192.168.182.31'
SERVER_PORT = 5050

# Function to dynamically load the model
def load_model(model_name, model_type):
    try:
        if model_type == "huggingface":
            tokenizer = AutoTokenizer.from_pretrained(model_name)
            model = AutoModelForCausalLM.from_pretrained(model_name)
            return tokenizer, model
        elif model_type == "gpt4all":
            model = GPT4All(model_name)
            return None, model
        elif model_type == "ollama":
            model = ollama
            return None, model
        elif model_type == "dolphin-llama3":
            model = load_dolphin_llama3(model_name)
            return None, model
        else:
            raise ValueError(f"Unknown model_type: {model_type}")
    except Exception as e:
        logging.error(f"Failed to load model {model_name}: {e}")
        raise

# Placeholder function to load dolphin-llama3 (if needed)
def load_dolphin_llama3(model_name):
    logging.info(f"Loading dolphin-llama3 model: {model_name}")
    return "dolphin-llama3-model-object"

# Function to generate response based on model type
def generate_response(model_type, model, tokenizer, prompt, model_name=None, max_length=100):
    try:
        if model_type == "huggingface":
            inputs = tokenizer(prompt, return_tensors="pt")
            outputs = model.generate(inputs["input_ids"], max_length=max_length)
            return tokenizer.decode(outputs[0], skip_special_tokens=True)
        elif model_type == "gpt4all":
            return model.generate(prompt)
        elif model_type == "ollama":
            logging.info(f"Sending prompt to Ollama: {prompt}")
            response = model.chat(model_name, prompt)
            logging.info(f"Ollama response: {response}")
            
            if isinstance(response, dict):
                return response.get("content", "No response generated.")
            elif isinstance(response, list) and len(response) > 0:
                return response[0].get("content", "No response generated.")
            else:
                return "Invalid response format."
        elif model_type == "dolphin-llama3":
            logging.info(f"Generating response from dolphin-llama3 model: {model_name}")
            return "Mock response from dolphin-llama3"
        else:
            raise ValueError("Unsupported model type.")
    except Exception as e:
        logging.error(f"Error generating response: {e}")
        return "Error generating response."

# Function to process tasks from the server
def process_task(server_url, vault_embeddings, vault_content):
    while True:
        try:
            response = requests.get(f"{server_url}/model_task")
            if response.status_code == 200:
                task = response.json()
                prompt = task.get('prompt', "")
                task_id = task.get('task_id', "")
                model_name = task.get('model_name', "gpt4all-lora")
                model_type = task.get('model_type', "gpt4all")
                chunk_size = task.get('chunk_size', 100)

                tokenizer, model = load_model(model_name, model_type)
                result = generate_response(model_type, model, tokenizer, prompt, model_name, max_length=chunk_size)

                if not isinstance(result, str):
                    result = str(result)  # Ensure result is a string
                
                payload = {"task_id": task_id, "response": result}
                logging.info(f"Sending payload to {server_url}/task_completed/{task_id}: {payload}")
                post_response = requests.post(f"{server_url}/task_completed/{task_id}", json=payload)

                if post_response.status_code == 200:
                    logging.info(f"Task {task_id} completed successfully.")
                else:
                    logging.error(f"Failed to send result for task {task_id}: {post_response.status_code}")
            elif response.status_code == 404:
                logging.info("No tasks available. Waiting...")
            else:
                logging.warning(f"Unexpected server response: {response.status_code}")
        except requests.ConnectionError as e:
            logging.error(f"Connection error: {e}")
        except Exception as e:
            logging.error(f"Unexpected error: {e}")
        time.sleep(5)

# Load vault embeddings if available
vault_content = []
if os.path.exists("vault.txt"):
    with open("vault.txt", "r", encoding='utf-8') as vault_file:
        vault_content = vault_file.readlines()

vault_embeddings = []
for content in vault_content:
    response = ollama.embeddings(model="mxbai-embed-large", prompt=content)
    vault_embeddings.append(response["embedding"])

vault_embeddings_tensor = torch.tensor(vault_embeddings)

if __name__ == "__main__":
    server_url = f"{SERVER_BASE_URL}:{SERVER_PORT}"
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    print(NEON_GREEN + "Starting model tasks..." + RESET_COLOR)
    process_task(server_url, vault_embeddings_tensor, vault_content)
