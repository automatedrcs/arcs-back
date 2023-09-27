gcloud builds submit --tag gcr.io/arcs-391022/migrations:latest .

gcloud run deploy migrations-service \
    --image gcr.io/arcs-391022/migrations:latest \
    --platform managed \
    --no-allow-unauthenticated

SERVICE_URL=$(gcloud run services describe migrations-service --format "value(status.url)")
curl $SERVICE_URL

# If you wish to delete the service afterward
gcloud run services delete migrations-service --quiet
