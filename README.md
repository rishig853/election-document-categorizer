Election Document Categorizer

This model categorizes election-security-related documents based on their text content. Currently, it supports four categories: court filings, exhibits, deposition, and miscellaneous (something other than the first three categories).

Setup instructions:\
Install dependencies by running “pip install -r requirements.txt”

Create a .env file in the root folder of the format below. Replace the values to the right of the equal sign with appropriate ones for your environment.\
DB_USER=user\
DB_PASSWORD=password\
DB_HOST=localhost\
DB_PORT=5432\
DB_NAME=database

Preparing PDFs for categorization:\
Store each of your election PDF documents in the “pdfs” folder, which is located in the root of the project.\
From the root of the project, run the command “python load_pdfs.py”. This will likely take some time depending on how many pdfs you have and how much text they have. My 519 pdfs take about 20 minutes to load into the database.

Running the model:\
From the root of the project, run the command “python categorize_pdfs.py”. This function will output a csv called “categories.csv” that contains the title of each of your documents, its label (category) according to the model, and a score indicating how confident the model is in its selection.

NOTE: python scripts in the "model_setup_and_more" folder are the scripts that I used to create the BERT model and process each PDF's text using EvaDB's ChatGPT function. They are not necessary for running the model.
