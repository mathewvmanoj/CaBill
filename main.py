from fastapi import FastAPI
from transformers import AutoModelForSeq2SeqLM, AutoTokenizer

app = FastAPI()

model = AutoModelForSeq2SeqLM.from_pretrained("./trained_model")
tokenizer = AutoTokenizer.from_pretrained("./trained_model")

@app.post("/generate_query")
async def generate_query(question: str):
    inputs = tokenizer(question, return_tensors="pt", max_length=128, truncation=True)
    outputs = model.generate(inputs["input_ids"], max_length=128)
    print(outputs[0])
    query = tokenizer.decode(outputs[0], skip_special_tokens=True)
    return {"query": query}