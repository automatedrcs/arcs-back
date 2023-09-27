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
gcloud logs read --limit=50 --service=migrations-service --region=$REGION

# Optionally, delete the service after you've verified the logs
gcloud run services delete migrations-service --region $REGION --quiet
