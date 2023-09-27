FROM python:3.9-slim

WORKDIR /app/arcs-back

COPY migrations/requirements.txt requirements.txt
RUN pip install -r requirements.txt

COPY src /app/src
COPY migrations/alembic.ini /app/
COPY migrations/run_migrations.py /app/
COPY migrations/alembic /app/alembic

CMD ["python", "run_migrations.py"]
