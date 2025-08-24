# Deployment Guide for Trading Strategy Web Application

This guide provides step-by-step instructions for deploying the Trading Strategy Web Application to Google Cloud Platform.

## Prerequisites

Before you begin, make sure you have the following:

1. A Google Cloud Platform (GCP) account
2. Google Cloud SDK installed and configured on your local machine
3. Docker installed on your local machine
4. Git repository with your application code

## Step 1: Set Up Google Cloud Project

1. Create a new Google Cloud project (or use an existing one):

```bash
# Create a new project
gcloud projects create trading-strategy-app --name="Trading Strategy App"

# Set the project as the default
gcloud config set project trading-strategy-app
```

2. Enable the required APIs:

```bash
gcloud services enable cloudbuild.googleapis.com
gcloud services enable run.googleapis.com
gcloud services enable artifactregistry.googleapis.com
gcloud services enable firestore.googleapis.com
gcloud services enable storage.googleapis.com
```

## Step 2: Set Up Google Cloud Storage

1. Create a storage bucket for application data:

```bash
gsutil mb -l us-central1 gs://trading-strategy-app-storage
```

2. Set appropriate permissions:

```bash
gsutil iam ch allUsers:objectViewer gs://trading-strategy-app-storage
```

## Step 3: Set Up Firestore Database

1. Create a Firestore database in Native mode:

```bash
gcloud firestore databases create --region=us-central
```

## Step 4: Set Up Container Registry

1. Create a Docker repository in Artifact Registry:

```bash
gcloud artifacts repositories create trading-strategy-app \
    --repository-format=docker \
    --location=us-central1 \
    --description="Trading Strategy App Docker repository"
```

2. Configure Docker to use the Google Cloud credential helper:

```bash
gcloud auth configure-docker us-central1-docker.pkg.dev
```

## Step 5: Build and Push Docker Images

1. Build and push the backend image:

```bash
# Navigate to the backend directory
cd trading_app/backend

# Build the Docker image
docker build -t us-central1-docker.pkg.dev/trading-strategy-app/trading-strategy-app/backend:latest .

# Push the image to Artifact Registry
docker push us-central1-docker.pkg.dev/trading-strategy-app/trading-strategy-app/backend:latest
```

2. Build and push the frontend image:

```bash
# Navigate to the frontend directory
cd ../frontend

# Build the Docker image
docker build -t us-central1-docker.pkg.dev/trading-strategy-app/trading-strategy-app/frontend:latest .

# Push the image to Artifact Registry
docker push us-central1-docker.pkg.dev/trading-strategy-app/trading-strategy-app/frontend:latest
```

## Step 6: Deploy Backend to Cloud Run

1. Deploy the backend service:

```bash
gcloud run deploy backend \
    --image us-central1-docker.pkg.dev/trading-strategy-app/trading-strategy-app/backend:latest \
    --platform managed \
    --region us-central1 \
    --allow-unauthenticated \
    --memory 512Mi \
    --set-env-vars="FLASK_ENV=production,STORAGE_BUCKET=trading-strategy-app-storage"
```

2. Get the backend service URL:

```bash
BACKEND_URL=$(gcloud run services describe backend --platform managed --region us-central1 --format="value(status.url)")
echo $BACKEND_URL
```

## Step 7: Deploy Frontend to Cloud Run

1. Deploy the frontend service with the backend URL:

```bash
gcloud run deploy frontend \
    --image us-central1-docker.pkg.dev/trading-strategy-app/trading-strategy-app/frontend:latest \
    --platform managed \
    --region us-central1 \
    --allow-unauthenticated \
    --memory 256Mi \
    --set-env-vars="REACT_APP_API_URL=${BACKEND_URL}/api"
```

2. Get the frontend service URL:

```bash
FRONTEND_URL=$(gcloud run services describe frontend --platform managed --region us-central1 --format="value(status.url)")
echo $FRONTEND_URL
```

## Step 8: Set Up Cloud Scheduler for Daily Monitoring (Optional)

If you want to set up automated daily monitoring:

1. Create a service account for the scheduler:

```bash
gcloud iam service-accounts create scheduler-sa \
    --display-name="Scheduler Service Account"
```

2. Grant the service account permission to invoke Cloud Run:

```bash
gcloud run services add-iam-policy-binding backend \
    --member="serviceAccount:scheduler-sa@trading-strategy-app.iam.gserviceaccount.com" \
    --role="roles/run.invoker" \
    --region us-central1 \
    --platform managed
```

3. Create a Cloud Scheduler job:

```bash
gcloud scheduler jobs create http daily-monitoring \
    --schedule="0 16 * * *" \
    --uri="${BACKEND_URL}/api/monitoring/scan-all" \
    --http-method=POST \
    --oidc-service-account-email="scheduler-sa@trading-strategy-app.iam.gserviceaccount.com" \
    --oidc-token-audience="${BACKEND_URL}"
```

## Step 9: Set Up Custom Domain (Optional)

1. Map your custom domain to the frontend service:

```bash
gcloud beta run domain-mappings create \
    --service frontend \
    --domain trading-strategy-app.example.com \
    --region us-central1 \
    --platform managed
```

2. Update your DNS records according to the instructions provided by the command output.

## Step 10: Set Up Continuous Deployment with Cloud Build (Optional)

1. Create a `cloudbuild.yaml` file in your repository:

```yaml
steps:
  # Build and push backend image
  - name: 'gcr.io/cloud-builders/docker'
    args: ['build', '-t', 'us-central1-docker.pkg.dev/$PROJECT_ID/trading-strategy-app/backend:$COMMIT_SHA', './backend']
  - name: 'gcr.io/cloud-builders/docker'
    args: ['push', 'us-central1-docker.pkg.dev/$PROJECT_ID/trading-strategy-app/backend:$COMMIT_SHA']
  
  # Build and push frontend image
  - name: 'gcr.io/cloud-builders/docker'
    args: ['build', '-t', 'us-central1-docker.pkg.dev/$PROJECT_ID/trading-strategy-app/frontend:$COMMIT_SHA', './frontend']
  - name: 'gcr.io/cloud-builders/docker'
    args: ['push', 'us-central1-docker.pkg.dev/$PROJECT_ID/trading-strategy-app/frontend:$COMMIT_SHA']
  
  # Deploy backend to Cloud Run
  - name: 'gcr.io/google.com/cloudsdktool/cloud-sdk'
    entrypoint: gcloud
    args:
      - 'run'
      - 'deploy'
      - 'backend'
      - '--image'
      - 'us-central1-docker.pkg.dev/$PROJECT_ID/trading-strategy-app/backend:$COMMIT_SHA'
      - '--region'
      - 'us-central1'
      - '--platform'
      - 'managed'
  
  # Deploy frontend to Cloud Run
  - name: 'gcr.io/google.com/cloudsdktool/cloud-sdk'
    entrypoint: gcloud
    args:
      - 'run'
      - 'deploy'
      - 'frontend'
      - '--image'
      - 'us-central1-docker.pkg.dev/$PROJECT_ID/trading-strategy-app/frontend:$COMMIT_SHA'
      - '--region'
      - 'us-central1'
      - '--platform'
      - 'managed'

images:
  - 'us-central1-docker.pkg.dev/$PROJECT_ID/trading-strategy-app/backend:$COMMIT_SHA'
  - 'us-central1-docker.pkg.dev/$PROJECT_ID/trading-strategy-app/frontend:$COMMIT_SHA'
```

2. Connect your GitHub repository to Cloud Build:

```bash
gcloud builds triggers create github \
    --repo-name=your-repo-name \
    --repo-owner=your-github-username \
    --branch-pattern="^main$" \
    --build-config=cloudbuild.yaml
```

## Monitoring and Maintenance

### Viewing Logs

1. View backend logs:

```bash
gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=backend" --limit 50
```

2. View frontend logs:

```bash
gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=frontend" --limit 50
```

### Updating the Application

1. Make changes to your code
2. Build and push new Docker images
3. Deploy the new images to Cloud Run

If you've set up continuous deployment with Cloud Build, simply push your changes to the main branch, and the application will be automatically updated.

### Scaling

Cloud Run automatically scales based on traffic. You can configure minimum and maximum instances:

```bash
gcloud run services update backend \
    --min-instances=1 \
    --max-instances=10 \
    --region us-central1 \
    --platform managed
```

## Security Considerations

1. **Environment Variables**: Store sensitive information like API keys and database credentials in environment variables.

2. **Authentication**: Implement proper authentication and authorization for your API endpoints.

3. **HTTPS**: Cloud Run services are automatically served over HTTPS.

4. **IAM Permissions**: Follow the principle of least privilege when assigning IAM roles.

5. **API Security**: Implement rate limiting and input validation for your API endpoints.

## Cost Optimization

1. **Cloud Run**: You only pay for the time your containers are running and processing requests.

2. **Firestore**: Consider using the appropriate mode (Native or Datastore) based on your needs.

3. **Cloud Storage**: Use lifecycle policies to automatically delete or archive old data.

4. **Monitoring**: Set up billing alerts to avoid unexpected charges.

## Troubleshooting

1. **Container Crashes**: Check the container logs for error messages.

2. **Deployment Failures**: Verify that your Docker images are built correctly and can run locally.

3. **API Errors**: Check the backend logs for error messages and ensure the frontend is correctly configured to call the backend API.

4. **Performance Issues**: Monitor CPU and memory usage, and adjust the resources allocated to your services if needed.

## Conclusion

You have successfully deployed the Trading Strategy Web Application to Google Cloud Platform. The application is now accessible via the frontend URL, and the backend API is ready to handle requests.

For any issues or questions, refer to the Google Cloud documentation or contact the application developer.