FROM tiangolo/uvicorn-gunicorn-fastapi:python3.9

WORKDIR /app

# Copy the requirements and install
RUN pip install --upgrade pip
COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt
RUN apt-get clean && rm -rf /var/lib/apt/lists/*

# Copy the entire src directory
COPY ./src /app/src

# Add a debugging step to inspect the contents of /app/src
RUN ls -l /app/src

# Use a shell to substitute the value of PORT and run the uvicorn command
CMD sh -c "uvicorn src.main:app --host 0.0.0.0 --port ${PORT:-8080}"
