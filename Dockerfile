FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

ENV HF_URL=https://router.huggingface.co/v1/chat/completions
ENV HF_TOKEN=[your_huggingface_token_here]
ENV HF_MODEL=meta-llama/Llama-3.2-3B-Instruct:novita

# Copy the source code
COPY src/ ./src

# Make sure src is treated as a package
RUN touch src/__init__.py

EXPOSE 8000

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
