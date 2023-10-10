# Navigate to the migrations directory
Set-Location -Path "./migrations"

# Generate the Alembic migration script
# Note: This assumes you have alembic available in your environment and the required DB connections are available.
alembic revision --autogenerate -m "Description of your changes"

# Navigate back to the main directory
Set-Location -Path ".."

# This will use the cloudbuild-migrations.yaml for building and tagging the Docker image
gcloud builds submit --config=migrations/cloudbuild-migrations.yaml .

# Define the region
$REGION = "us-central1"  # Choose your desired region

# Deploy the built image to Cloud Run
gcloud run deploy migrations-service `
    --image gcr.io/arcs-391022/migrations:latest `
    --platform managed `
    --region $REGION `
    --no-allow-unauthenticated

# Give it some time for the migrations to run (adjust as needed)
Start-Sleep -Seconds 20

# Check the logs to confirm if migrations ran successfully:
gcloud functions logs read --limit=50 --service=migrations-service --region=$REGION

# Optionally, delete the service after you've verified the logs
gcloud run services delete migrations-service --region $REGION --quiet

# alembic windows 11 desktop location
# C:\Users\Junah\AppData\Local\Packages\PythonSoftwareFoundation.Python.3.10_qbz5n2kfra8p0\LocalCache\local-packages\Python310\Scripts\

# gcloud command to connect
# gcloud sql connect arcs-sql-instance --user=arcs-postgres-user --database=arcs-db --quiet