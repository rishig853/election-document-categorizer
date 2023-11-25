# used to help build chatgpt_categories.xlsx; not necessary for running the model but here for reference
import evadb
import os
import time

cursor = evadb.connect().cursor()
os.environ["OPENAI_API_KEY"] = "sk-..."
df = cursor.query("SELECT * FROM postgres_data.pdf_categories_int").df()
rows, _ = df.shape
dfs = []

start = 0
for i in range(start, rows):
    try:
        result_df = cursor.query(f"""
        SELECT id, title, ChatGPT(
          "Based on the text of each election security related document, do you think the
          document falls in the category of 'court_filings', 'depositions', 'exhibits', or 'misc'
          (miscellaneous, or not in any of the previous categories)? Respond with just one word: the category name",
          text
        ), category
        FROM postgres_data.pdf_categories WHERE id = {i};
        """).df()
        result_df.to_csv('chatgpt_categories.csv', mode='a', header=(i == 0), index=False)
        print(f"Processed row {i}")
        dfs = []

    except Exception as e:
        print(f"Error at row {i}: {e}")
    time.sleep(20)
