import os
from PyPDF2 import PdfReader
import psycopg2
from decouple import config

DB_USER = config('DB_USER')
DB_PASSWORD = config('DB_PASSWORD')
DB_HOST = config('DB_HOST')
DB_PORT = config('DB_PORT')
DB_NAME = config('DB_NAME')

conn = psycopg2.connect(
    user=DB_USER,
    password=DB_PASSWORD,
    host=DB_HOST,
    port=DB_PORT,
    database=DB_NAME,
)

cursor = conn.cursor()

cursor.execute("DROP TABLE IF EXISTS pdf_text")

cursor.execute("""
    CREATE TABLE pdf_text (
        id int,
        title VARCHAR(100),
        text VARCHAR
    )
""")

conn.commit()


def extract_text_pypdf2(pdf_path):
    with open(pdf_path, 'rb') as file:
        pdf_reader = PdfReader(file)
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text()
        return text


def store_pdf_data_in_database(pdf_id, title, text):
    text = text.replace('\x00', '')
    query = """
        INSERT INTO pdf_text (id, title, text) VALUES (%s, %s, %s)
    """
    cursor.execute(query, (pdf_id, title, text))
    conn.commit()


def process_pdfs(folder_path):
    pdf_id = 0
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            if file.endswith(".pdf"):
                pdf_path = os.path.join(root, file)
                title = os.path.splitext(file)[0]
                text = extract_text_pypdf2(pdf_path)
                store_pdf_data_in_database(pdf_id, title, text)
                pdf_id += 1


pdf_folder_path = './pdfs'
process_pdfs(pdf_folder_path)

cursor.close()
conn.close()
