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

# Explicitly set the entrypoint and command
ENTRYPOINT ["uvicorn"]
CMD ["src.main:app", "--host", "0.0.0.0", "--port", "8080"]
