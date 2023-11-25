import evadb

cursor = evadb.connect().cursor()

cursor.query("""
    CREATE FUNCTION IF NOT EXISTS ElectionDocClassifier
    TYPE HuggingFace
    TASK 'text-classification'
    MODEL 'rgoswami31/esrf_doc_categorizer_model';
""").df()

results_df = cursor.query("""
    SELECT title, ElectionDocClassifier(text)
    FROM postgres_data.pdf_text
""").df()

results_df.to_csv("categories.csv", index=False)
