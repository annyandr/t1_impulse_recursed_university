import torch
import ollama
import os
from openai import OpenAI
import argparse
import time
import logging
import requests


# ANSI escape codes for colors
PINK = '\033[95m'
CYAN = '\033[96m'
YELLOW = '\033[93m'
NEON_GREEN = '\033[92m'
RESET_COLOR = '\033[0m'
port = '5000'
server_url = 'http://127.0.0.1'

# Function to get relevant context from the vault based on user input
def get_relevant_context(user_input, vault_embeddings, vault_content, top_k=3):
    if vault_embeddings.nelement() == 0:
        return []
    
    input_embedding = ollama.embeddings(model='mxbai-embed-large', prompt=user_input)["embedding"]
    
    # Compute cosine similarity
    cos_scores = torch.cosine_similarity(torch.tensor(input_embedding).unsqueeze(0), vault_embeddings)
    top_k = min(top_k, len(cos_scores))
    top_indices = torch.topk(cos_scores, k=top_k)[1].tolist()
    
    return [vault_content[idx].strip() for idx in top_indices]

# Function to interact with the Ollama model
def ollama_chat(user_input, system_message, vault_embeddings, vault_content, ollama_model):
    relevant_context = get_relevant_context(user_input, vault_embeddings, vault_content, top_k=3)
    
    if relevant_context:
        context_str = "\n".join(relevant_context)
        shortened_context = context_str[:100] + "..." if len(context_str) > 100 else context_str

        response = client.chat.completions.create(
            model=ollama_model,
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": f"Context: {shortened_context}\n\nQuestion: {user_input}"}
            ],
            max_tokens=100
        )
        return response.choices[0].message.content.strip()
    else:
        return "No relevant context found."
    
def model_tasks(server_url):
    """
    Синхронный вариант выполнения задач модели с использованием requests.Session
    и отправкой обратной связи на сервер.

    :param server_url: URL сервера
    """
    with requests.Session() as session:
        while True:
            try:
                # Запрос задач от сервера
                response = session.get(f'{server_url}/model_task')
                if response.status_code == 200:
                    prompt = response.json().get('prompt', None)  # Получаем prompt
                    task_id = response.json().get('task_id', None)
                    if prompt is None or task_id is None:
                        continue
                    process_updates(prompt)  # Обработка prompt

                    # Уведомление сервера о выполнении задачи
                    feedback_response = session.post(
                        f'{server_url}/task_completed/{task_id}',
                        json={"status": "success", "prompt": prompt}
                    )
                    if feedback_response.status_code == 200:
                        logging.info("Обратная связь успешно отправлена.")
                    else:
                        logging.warning(f"Ошибка отправки обратной связи: {feedback_response.status_code}")
                else:
                    logging.warning(f"Получен некорректный статус: {response.status_code}")
            except Exception as e:
                logging.error(f"Ошибка при выполнении запроса: {e}")
            time.sleep(5)


def process_updates(prompt):
    """
    Обработка prompt, полученного от сервера.

    :param prompt: Данные prompt от сервера
    """

    user_input = prompt

    response = ollama_chat(user_input, system_message, vault_embeddings_tensor, vault_content, args.model)
    print(NEON_GREEN + "Response: \n\n" + response + RESET_COLOR)

    # Логика обработки prompt
    print("Обработан prompt:", prompt)


# Parse command-line arguments
parser = argparse.ArgumentParser(description="Ollama Chat")
parser.add_argument("--model", default="dolphin-llama3", help="Ollama model to use (default: dolphin-llama3)")
args = parser.parse_args()

# Configuration for the Ollama API client
client = OpenAI(
    base_url='http://localhost:11434/v1',
    api_key='dolphin-llama3'
)

# Load the vault content
vault_content = []
if os.path.exists("vault.txt"):
    with open("vault.txt", "r", encoding='utf-8') as vault_file:
        vault_content = vault_file.readlines()

# Generate embeddings for the vault content using Ollama
vault_embeddings = []
for content in vault_content:
    response = ollama.embeddings(model='mxbai-embed-large', prompt=content)
    vault_embeddings.append(response["embedding"])

# Convert embeddings to tensor
vault_embeddings_tensor = torch.tensor(vault_embeddings)

# Conversation loop
system_message = "You are a helpful assistant that is an expert at extracting the most useful information from a given text."



if __name__ == "__main__":
    server_url = f'{server_url}:{port}'
    model_tasks(server_url)