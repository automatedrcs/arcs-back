FROM tiangolo/uvicorn-gunicorn-fastapi:python3.9

WORKDIR /app

# Copy the requirements and install
COPY requirements.txt requirements.txt
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire src directory
COPY ./src /app/src

# Adjusted command to reference the main.py inside the src directory
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8080"]