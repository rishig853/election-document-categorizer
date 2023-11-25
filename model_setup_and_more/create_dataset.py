# used to create the training dataset; not necessary for running the model but here for reference
import os
from PyPDF2 import PdfReader
import psycopg2

conn = psycopg2.connect(
    user="",
    password="",
    host="",
    port="",
    database="",
)

cursor = conn.cursor()

cursor.execute("DROP TABLE IF EXISTS pdf_categories_int")

cursor.execute("""
    CREATE TABLE pdf_categories_int (
        id int,
        title VARCHAR(100),
        text VARCHAR,
        category int
    )
""")

conn.commit()


def extract_text_pypdf2(pdf_path, max_words):
    with open(pdf_path, 'rb') as file:
        pdf_reader = PdfReader(file)
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text()

        # words = text.split()
        # if len(words) > max_words:
        #     text = ' '.join(words[:max_words])

        return text


def store_pdf_data_in_database(pdf_id, title, text, category):
    text = text.replace('\x00', '')
    query = """
        INSERT INTO pdf_categories_int (id, title, text, category) VALUES (%s, %s, %s, %s)
    """
    print(title)
    cursor.execute(query, (pdf_id, title, text, category))
    conn.commit()


label2id = {"misc": 0, "court_filings": 1, "depositions": 2, "exhibits": 3}


def process_pdfs(folder_path):
    pdf_id = 0
    for root, dirs, files in os.walk(folder_path):
        if len(root.split("/")) <= 2:
            continue
        category = label2id[root.split("/")[2]]
        for file in files:
            if file.endswith(".pdf"):
                pdf_path = os.path.join(root, file)
                title = os.path.splitext(file)[0]
                text = extract_text_pypdf2(pdf_path, 1024)
                store_pdf_data_in_database(pdf_id, title, text, category)
                pdf_id += 1


pdf_folder_path = './docs'
process_pdfs(pdf_folder_path)

cursor.close()
conn.close()
