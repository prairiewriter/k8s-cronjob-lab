FROM python:3.12-slim
WORKDIR /app
COPY app/app.py .
CMD ["python", "app.py"]
