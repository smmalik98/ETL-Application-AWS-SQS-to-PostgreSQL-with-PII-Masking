# ETL Application: AWS SQS to PostgreSQL with PII Masking

## Overview

Welcome to the ETL Application project! This project is designed to showcase your ability to build a small application that reads data from an AWS SQS Queue, masks sensitive information, transforms the data, and writes it to a Postgres database. The entire setup is orchestrated using Docker to ensure a consistent and isolated environment for running the components locally.

This README will guide you through the entire process, from setting up your environment to running the application. It also includes details on the design decisions made during development, how to handle potential issues, and suggestions for deploying the application in a production environment. Whether you are a technical evaluator or someone with limited technical background, this document aims to make the process as smooth and understandable as possible.

The main objectives of this project are:

1. **Read JSON data**: Extract user login behavior data from an AWS SQS Queue. For this project, the queue is simulated using a custom Localstack Docker image preloaded with test data.
2. **Mask Personal Identifiable Information (PII)**: Protect user privacy by masking fields such as `device_id` and `ip`. The masking should allow data analysts to identify duplicate values.
3. **Transform and Write Data**: Flatten the JSON data structure and insert the transformed records into a Postgres database. The database is provided via a custom Postgres Docker image with a pre-created table schema.

Throughout the project, you'll encounter and solve various technical challenges, such as connecting to AWS services locally, handling JSON data transformation, and ensuring secure data handling practices. This README includes all necessary commands, explanations, and debugging tips to help you complete the task successfully.

## Table of Contents

1. [Project Setup](#project-setup)
2. [Running the Application](#running-the-application)
3. [Design Decisions](#design-decisions)
4. [Handling PII](#handling-pii)
5. [Assumptions](#assumptions)
6. [Debugging Localstack Issue](#debugging-localstack-issue)
7. [Next Steps](#next-steps)

## Project Setup

### Prerequisites

- Docker
- Docker-compose
- AWS CLI (Local version: `pip install awscli-local`)
- PostgreSQL client (psql)

### Clone the Repository

```bash
git clone https://github.com/yourusername/ETL-Application-AWS-SQS-to-PostgreSQL-with-PII-Masking.git
cd ETL-Application-AWS-SQS-to-PostgreSQL-with-PII-Masking
```
### Docker Setup

1. Ensure Docker and Docker Compose are installed on your machine.
2. Use the provided docker-compose.yaml to set up the local environment.

```yaml
version: "3.9"
services:
  localstack:
    image: fetchdocker/data-takehome-localstack
    platform: linux/amd64
    ports:
      - "4566:4566"
    environment:
      - SERVICES=sqs
      - DEFAULT_REGION=us-east-1
  postgres:
    image: fetchdocker/data-takehome-postgres
    platform: linux/amd64
    ports:
      - 5432:5432
```
3. Start the docker container

```bash
docker-compose up -d
```
### Verify Setup

1. Access Localstack SQS Queue:

```bash
awslocal sqs receive-message --queue-url http://localhost:4566/000000000000/login-queue
```
2. Access Postgres Database:

```bash
psql -d postgres -U postgres -p 5432 -h localhost -W
# Password: ********
# Verify table creation:
SELECT * FROM user_logins;
```
## Running the Application

### Install Dependencies

Ensure you have Python installed. Then, install the required Python packages:

```bash
pip install -r requirements.txt
```
```bash
brew install postgresql
```
### Run the ETL Application

Execute the script to read from the SQS queue, transform the data, and write to the Postgres database:

```bash
python app.py
```
## Design Decisions

1. **Reading Messages from the Queue:**
Using boto3 library to interact with AWS SQS.

2. **Data Structures:**
JSON for incoming data, dictionaries for intermediate processing, and a structured object for database insertion.

3. **Masking PII:**
Hashing device_id and ip fields to mask PII while preserving the ability to identify duplicates.

4. **Connecting to Postgres:**
Using psycopg2 library for database interactions.

5. **Application Runtime:**
The application runs locally in a Docker environment for easy setup and testing.

## Handling PII

### Masking Strategy

Hashing: Use SHA-256 hashing to mask device_id and ip. This ensures PII is hidden but duplicate values can be identified.

### PII Recovery

Reversible Hashing: Store salt keys securely to reverse hash if necessary (not implemented in this project for security reasons).

## Assumptions

1. The data structure in the queue matches the expected JSON format.

2. Docker images provided are functional and compatible with the current project setup.

3. No real PII recovery is needed, focusing on data analysis use cases.

## Debugging Localstack Issue

### Issue: "Error 500" from Localstack

#### Problem

I encountered a persistent "Error 500" from the start when attempting to verify the connection by sending, receiving, or creating a queue. This error indicates an internal server issue.

#### Investigation

Upon further investigation, it became evident that the Localstack version in use was outdated, having been created two years ago and lacking subsequent updates. This outdated version does not support certain JSON functionalities, which is necessary for our ETL process. As discussed in a related issue on the Localstack GitHub repository, Localstack versions prior to 3.0 do not fully support JSON processing, leading to internal server errors during operations ([reference](https://github.com/localstack/localstack/issues/10247)).

Given that I am not the maintainer of the Localstack Docker image, I could not perform a direct update of the Localstack version and neither adding the version number on top of the .yaml file solves the problem. To mitigate this, I attempted to migrate the existing data from the older Docker image to a newer Localstack image. This approach is detailed in another discussion on the Localstack GitHub repository, where community members have outlined steps for data migration to newer versions ([reference](https://stackoverflow.com/questions/63389984/what-is-the-correct-way-to-update-a-docker-image)). However, this migration process led to compatibility issues due to discrepancies between the configurations and dependencies of the older and newer versions.

#### Conclusion

The "Error 500" issue is attributable to the outdated Localstack version, which lacks support for necessary JSON functionalities. The Localstack image specified in the provided `docker-compose.yaml` is insufficient for the operations required by this project. To resolve this issue, the Localstack image must be updated to version 3.0 or higher, which supports the required JSON functionalities and avoids the internal server errors.

## Next Steps

### Deployment and Scalability

#### Production Deployment

- **Containerization:** Use Docker to ensure the application runs the same way in any environment.
- **Orchestration:** Use Kubernetes to manage and scale the Docker containers efficiently.
- **CI/CD:** Set up automated pipelines with tools like Jenkins or GitHub Actions to streamline code integration and deployment.
- **Error Handling:** Implement strong error handling and logging to track and resolve issues.
- **Unit Tests:** Write unit tests for each function and integration tests for the entire ETL process to ensure everything works correctly.
- **CI/CD Pipeline:** Set up an automated pipeline using CI/CD tools to run tests and deploy the application seamlessly.

#### Scaling with Growing Dataset

- **Queue Management:** Use AWS SQS with Auto Scaling to handle more messages as the load increases.
- **Database Scaling:** Use read replicas and partitioning in PostgreSQL to improve database performance and handle more data.
- **Caching:** Implement caching with Redis or Memcached to speed up access to frequently used data.








