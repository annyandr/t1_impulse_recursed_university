import os
import tkinter as tk
import PyPDF2
import re
import json

UPLOAD_FOLDER = "backend/uploads"


# Function to convert PDFs to text and append to vault.txt
def convert_pdf_to_text():
    for file_name in os.listdir(UPLOAD_FOLDER):
        if file_name.endswith(".pdf"):
            file_path = os.path.join(UPLOAD_FOLDER, file_name)
            with open(file_path, 'rb') as pdf_file:
                pdf_reader = PyPDF2.PdfReader(pdf_file)
                num_pages = len(pdf_reader.pages)
                text = ''
                for page_num in range(num_pages):
                    page = pdf_reader.pages[page_num]
                    if page.extract_text():
                        text += page.extract_text() + " "

                # Normalize whitespace and clean up text
                text = re.sub(r'\s+', ' ', text).strip()

                # Split text into chunks by sentences, respecting a maximum chunk size
                sentences = re.split(r'(?<=[.!?]) +', text)
                chunks = []
                current_chunk = ""
                for sentence in sentences:
                    if len(current_chunk) + len(sentence) + 1 < 1000:
                        current_chunk += (sentence + " ").strip()
                    else:
                        chunks.append(current_chunk)
                        current_chunk = sentence + " "
                if current_chunk:
                    chunks.append(current_chunk)

                with open("vault.txt", "a", encoding="utf-8") as vault_file:
                    for chunk in chunks:
                        vault_file.write(chunk.strip() + "\n")
                print(f"PDF file '{file_name}' content appended to vault.txt.")


# Function to upload text files and append to vault.txt
def upload_txtfile():
    for file_name in os.listdir(UPLOAD_FOLDER):
        if file_name.endswith(".txt"):
            file_path = os.path.join(UPLOAD_FOLDER, file_name)
            with open(file_path, 'r', encoding="utf-8") as txt_file:
                text = txt_file.read()

                # Normalize whitespace and clean up text
                text = re.sub(r'\s+', ' ', text).strip()

                # Split text into chunks by sentences, respecting a maximum chunk size
                sentences = re.split(r'(?<=[.!?]) +', text)
                chunks = []
                current_chunk = ""
                for sentence in sentences:
                    if len(current_chunk) + len(sentence) + 1 < 1000:
                        current_chunk += (sentence + " ").strip()
                    else:
                        chunks.append(current_chunk)
                        current_chunk = sentence + " "
                if current_chunk:
                    chunks.append(current_chunk)

                with open("vault.txt", "a", encoding="utf-8") as vault_file:
                    for chunk in chunks:
                        vault_file.write(chunk.strip() + "\n")
                print(f"Text file '{file_name}' content appended to vault.txt.")


# Function to upload JSON files and append to vault.txt
def upload_jsonfile():
    for file_name in os.listdir(UPLOAD_FOLDER):
        if file_name.endswith(".json"):
            file_path = os.path.join(UPLOAD_FOLDER, file_name)
            with open(file_path, 'r', encoding="utf-8") as json_file:
                data = json.load(json_file)

                # Flatten the JSON data into a single string
                text = json.dumps(data, ensure_ascii=False)

                # Normalize whitespace and clean up text
                text = re.sub(r'\s+', ' ', text).strip()

                # Split text into chunks by sentences, respecting a maximum chunk size
                sentences = re.split(r'(?<=[.!?]) +', text)
                chunks = []
                current_chunk = ""
                for sentence in sentences:
                    if len(current_chunk) + len(sentence) + 1 < 1000:
                        current_chunk += (sentence + " ").strip()
                    else:
                        chunks.append(current_chunk)
                        current_chunk = sentence + " "
                if current_chunk:
                    chunks.append(current_chunk)

                with open("vault.txt", "a", encoding="utf-8") as vault_file:
                    for chunk in chunks:
                        vault_file.write(chunk.strip() + "\n")
                print(f"JSON file '{file_name}' content appended to vault.txt.")


# Create the main window
root = tk.Tk()
root.title("Process Files from 'uploads' Folder")

# Create a button to process PDF files
pdf_button = tk.Button(root, text="Process PDF Files", command=convert_pdf_to_text)
pdf_button.pack(pady=10)

# Create a button to process text files
txt_button = tk.Button(root, text="Process Text Files", command=upload_txtfile)
txt_button.pack(pady=10)

# Create a button to process JSON files
json_button = tk.Button(root, text="Process JSON Files", command=upload_jsonfile)
json_button.pack(pady=10)

# Run the main event loop
root.mainloop()
