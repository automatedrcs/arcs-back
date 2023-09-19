FROM tiangolo/uvicorn-gunicorn-fastapi:python3.9

WORKDIR /app

# Copy the requirements and install
RUN pip install --upgrade pip
COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt
RUN apt-get clean && rm -rf /var/lib/apt/lists/*

# Download and install Cloud SQL Proxy
RUN wget https://dl.google.com/cloudsql/cloud_sql_proxy.linux.amd64 -O cloud_sql_proxy \
&& chmod +x cloud_sql_proxy

# Copy the entire src directory
COPY ./src /app/src

# Change the working directory to /app/src
WORKDIR /app/src

# Use a shell to substitute the value of PORT and run the uvicorn command
CMD sh -c "uvicorn main:app --host 0.0.0.0 --port ${PORT:-8080}"
