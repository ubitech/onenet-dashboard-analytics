# Analytics service

## Project Overview

The OneNet Monitoring and Analytics Dashboard is an open-source project part of the European Horizon project called OneNet. It is designed to enhance cybersecurity in the OneNet Interoperable Network of Platforms. This repository implements the anomaly detection component to prevent DDoS attacks, featuring a comprehensive set of tools for security analytics.

## Repository Structure
The repository includes two main Django apps: elastic and anomaly_detection.

elastic: Handles interactions with Elasticsearch, including actions like read_from_index, write_to_index, and form_query. It includes utils.py for retrieving Nginx access logs and using the anomaly detection model from the anomaly_detection app.
anomaly_detection: Manages the training and prediction phases of the anomaly detection model.
The project also includes various utility scripts, configuration files, and Docker components for easy deployment.

## Running the Application

1. Clone the Repository:

```
git clone https://github.com/ubitech/onenet-dashboard-analytics
cd onenet-dashboard-analytics
```

2. Set Up Environment Variables: Create a `.env` file at the root directory and populate it with necessary environment variables.

3. Build and Run with Docker:

```
docker-compose build
docker-compose up
```

4. Accessing the Application:

Execute `python3 manage.py runsever`

The application should now be running and accessible via http://localhost:8000.

## Build the docker image
```
docker build . -t onenet-dashboard-analytics-image
```

