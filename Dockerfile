FROM tiangolo/uvicorn-gunicorn-fastapi:python3.9

WORKDIR /app

# Environment variables
ENV DATABASE_URL=your_database_url_here

# Copy the requirements and install
COPY requirements.txt requirements.txt
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt
RUN apt-get clean && rm -rf /var/lib/apt/lists/*

# Copy the entire src directory
COPY ./src /app/src

# Use a shell to substitute the value of PORT and run the uvicorn command
CMD sh -c "uvicorn src.main:app --host 0.0.0.0 --port ${PORT:-8080}"
