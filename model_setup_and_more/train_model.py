# used to train the model; not necessary for running the model but here for reference
from transformers import AutoTokenizer
from transformers import DataCollatorWithPadding
import evaluate
import numpy as np
from transformers import AutoModelForSequenceClassification, TrainingArguments, Trainer
from datasets import Dataset, DatasetDict
import psycopg2
from tqdm import tqdm

conn = psycopg2.connect(
    user="",
    password="",
    host="",
    port="",
    database="",
)

query = "SELECT id, title, text, category FROM pdf_categories_int"

cursor = conn.cursor()
cursor.execute(query)
rows = cursor.fetchall()

data = {"train": {"label": [], "text": []}, "test": {"label": [], "text": []}}

i = 0
for row in tqdm(rows, desc="Loading dataset"):
    if i == 518:
        break
    if i % 2 == 0:
        data["train"]["label"].append(row[3])
        data["train"]["text"].append(row[2])
    else:
        data["test"]["label"].append(row[3])
        data["test"]["text"].append(row[2])
    i += 1

custom_dataset = DatasetDict({
    "train": Dataset.from_dict(data["train"]),
    "test": Dataset.from_dict(data["test"])
})

tokenizer = AutoTokenizer.from_pretrained("distilbert-base-uncased")


def preprocess_function(examples):
    return tokenizer(examples["text"], truncation=True)


tokenized_docs = custom_dataset.map(preprocess_function, batched=True)

data_collator = DataCollatorWithPadding(tokenizer=tokenizer)

accuracy = evaluate.load("accuracy")


def compute_metrics(eval_pred):
    predictions, labels = eval_pred
    predictions = np.argmax(predictions, axis=1)
    return accuracy.compute(predictions=predictions, references=labels)


id2label = {0: "misc", 1: "court_filings", 2: "depositions", 3: "exhibits"}
label2id = {"misc": 0, "court_filings": 1, "depositions": 2, "exhibits": 3}

model = AutoModelForSequenceClassification.from_pretrained(
    "distilbert-base-uncased", num_labels=4, id2label=id2label, label2id=label2id
)

training_args = TrainingArguments(
    output_dir="esrf_doc_categorizer_model",
    learning_rate=2e-5,
    per_device_train_batch_size=8,
    per_device_eval_batch_size=8,
    num_train_epochs=6,
    weight_decay=0.05,
    evaluation_strategy="epoch",
    save_strategy="epoch",
    load_best_model_at_end=True,
    push_to_hub=True,
)

trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=tokenized_docs["train"],
    eval_dataset=tokenized_docs["test"],
    tokenizer=tokenizer,
    data_collator=data_collator,
    compute_metrics=compute_metrics,
)

trainer.train()

trainer.push_to_hub()
