# 1. Define Python 3.10 base image
FROM python:3.10-slim

# 2. Stop Python from writing .pyc files and force stdout to be unbuffered (better logging)
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# 3. Set the directory inside the container where the code will live
WORKDIR /app

# 4. Copy the requirements file first to leverage Docker layer caching
COPY requirements.txt .

# 5. Install the dependencies
RUN pip install --no-cache-dir -r requirements.txt

# 6. Copy the rest of the application code into the container
COPY . .

# 7. Expose the port that Cloud Run expects (8000)
EXPOSE 8000

# 8. The command to start the web server (--reload flag is dropped for production)
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]