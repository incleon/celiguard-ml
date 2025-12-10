FROM python:3.11-slim

WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy training script and entrypoint
COPY train_model.py .
COPY entrypoint.sh .
RUN chmod +x entrypoint.sh

# Run the entrypoint script
CMD ["./entrypoint.sh"]
