```bash
# Install kubectl and update environment
sudo apt install gcloud
gcloud components install kubectl
gcloud config set project [PROJECT_ID]
gcloud config set compute/zone us-central1-a

# Export the following to your bash.rc file
export GOOGLE_APPLICATION_CREDENTIALS="<PATH-TO-JSON-FILE>"
```
