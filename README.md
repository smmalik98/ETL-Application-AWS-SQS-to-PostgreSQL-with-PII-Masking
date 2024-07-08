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

After running the above code you should expect the following output in your terminal:
```
(pii) smitmalik@x86_64-apple-darwin13 pii % python app.py
Starting application...
Altered app_version column type to varchar.
Attempting to fetch messages from SQS queue...
Received response from SQS.
Number of messages received: 10
Processing message: {'user_id': '424cdd21-063a-43a7-b91b-7ca1a833afae', 'app_version': '2.3.0', 'device_type': 'android', 'ip': '199.172.111.135', 'locale': 'RU', 'device_id': '593-47-5928'}
Data inserted for user_id: 424cdd21-063a-43a7-b91b-7ca1a833afae
Processing message: {'user_id': 'c0173198-76a8-4e67-bfc2-74eaa3bbff57', 'app_version': '0.2.6', 'device_type': 'ios', 'ip': '241.6.88.151', 'locale': 'PH', 'device_id': '104-25-0070'}
Data inserted for user_id: c0173198-76a8-4e67-bfc2-74eaa3bbff57
Processing message: {'user_id': '66e0635b-ce36-4ec7-aa9e-8a8fca9b83d4', 'app_version': '2.2.1', 'device_type': 'ios', 'ip': '130.111.167.54', 'locale': None, 'device_id': '127-42-0862'}
Data inserted for user_id: 66e0635b-ce36-4ec7-aa9e-8a8fca9b83d4
Processing message: {'user_id': '181452ad-20c3-4e93-86ad-1934c9248903', 'app_version': '0.96', 'device_type': 'android', 'ip': '118.79.6.245', 'locale': 'ID', 'device_id': '190-44-3099'}
Data inserted for user_id: 181452ad-20c3-4e93-86ad-1934c9248903
Processing message: {'user_id': '60b9441c-e39d-406f-bba0-c7ff0e0ee07f', 'app_version': '0.4.6', 'device_type': 'android', 'ip': '223.31.97.46', 'locale': 'FR', 'device_id': '149-99-5185'}
Data inserted for user_id: 60b9441c-e39d-406f-bba0-c7ff0e0ee07f
Processing message: {'user_id': '5082b1ae-6523-4e3b-a1d8-9750b4407ee8', 'app_version': '3.7', 'device_type': 'android', 'ip': '235.167.63.6', 'locale': None, 'device_id': '346-96-4168'}
Data inserted for user_id: 5082b1ae-6523-4e3b-a1d8-9750b4407ee8
Processing message: {'user_id': '5bc74293-3ca1-4f34-bb89-523887d0cc2f', 'app_version': '2.2.8', 'device_type': 'ios', 'ip': '240.162.230.101', 'locale': 'PT', 'device_id': '729-06-2799'}
Data inserted for user_id: 5bc74293-3ca1-4f34-bb89-523887d0cc2f
Processing message: {'user_id': '92d8ceec-2e12-49f3-81bd-518fe66971ec', 'app_version': '0.5.5', 'device_type': 'android', 'ip': '194.99.130.72', 'locale': 'BR', 'device_id': '762-96-1217'}
Data inserted for user_id: 92d8ceec-2e12-49f3-81bd-518fe66971ec
Processing message: {'user_id': '05e153b1-4fa1-474c-bd7e-9f74d1c495e7', 'app_version': '0.5.0', 'device_type': 'android', 'ip': '163.2.96.136', 'locale': None, 'device_id': '431-77-3545'}
Data inserted for user_id: 05e153b1-4fa1-474c-bd7e-9f74d1c495e7
Processing message: {'user_id': '325c0f3d-da25-45ff-aff4-81816db069bc', 'app_version': '0.60', 'device_type': 'android', 'ip': '172.99.101.28', 'locale': 'RU', 'device_id': '649-26-7827'}
Data inserted for user_id: 325c0f3d-da25-45ff-aff4-81816db069bc

Contents of user_logins table:

user_id | device_type | masked_ip | masked_device_id | locale | app_version | create_date
424cdd21-063a-43a7-b91b-7ca1a833afae | android | a6d0e2f27f6111e10b06790db42f34123e724aa0fd24b280f4a0ef5ee986784c | 4f00c1a807b673887c7af517d0df68e6b41aecf8cbec26c71fe4c580664669ed | RU | 2.3.0 | None
c0173198-76a8-4e67-bfc2-74eaa3bbff57 | ios | 7b03f7d723535706b4777384fc906d18a4376bb84cebb50dc22c6eb9bddf00cb | a857e702f98990716938a0d74c3dc2dc565e4448833e2cf91c6ab26fc0e9971f | PH | 0.2.6 | None
66e0635b-ce36-4ec7-aa9e-8a8fca9b83d4 | ios | fa7fca28c658d75a751b60e262602e1b11f4149274af6ec0d8c82a8619a51437 | e84fb3e15175d0a2492de6c02a99595c1343db73:
```

To check if the data has been loaded in your postgres database try:

```bash
psql -d postgres -U postgres -p 5432 -h localhost -W
# Password: ********
# Verify table creation:
SELECT * FROM user_logins;
```
You should see the following result in your terminal:

```bash
               user_id                | device_type |                            masked_ip                             |                         masked_device_id                         | locale | app_version | create_date 
--------------------------------------+-------------+------------------------------------------------------------------+------------------------------------------------------------------+--------+-------------+-------------
 424cdd21-063a-43a7-b91b-7ca1a833afae | android     | a6d0e2f27f6111e10b06790db42f34123e724aa0fd24b280f4a0ef5ee986784c | 4f00c1a807b673887c7af517d0df68e6b41aecf8cbec26c71fe4c580664669ed | RU     | 2.3.0       | 
 c0173198-76a8-4e67-bfc2-74eaa3bbff57 | ios         | 7b03f7d723535706b4777384fc906d18a4376bb84cebb50dc22c6eb9bddf00cb | a857e702f98990716938a0d74c3dc2dc565e4448833e2cf91c6ab26fc0e9971f | PH     | 0.2.6       | 
 66e0635b-ce36-4ec7-aa9e-8a8fca9b83d4 | ios         | fa7fca28c658d75a751b60e262602e1b11f4149274af6ec0d8c82a8619a51437 | e84fb3e15175d0a2492de6c02a99595c1343db7321ad6bb5f62052edd00a84f8 |        | 2.2.1       | 
 181452ad-20c3-4e93-86ad-1934c9248903 | android     | b21d1c922d9e9d1b913ade3265baa7fc43c757976dcd7cac3ed2043176655396 | 94b571f680b8f41547047f24e385334265773d33ab643bfc6f1684e21b8b34d9 | ID     | 0.96        | 
 60b9441c-e39d-406f-bba0-c7ff0e0ee07f | android     | 587f5a111a1f2adb462f778574a91b93de3b29889deca6e25dd363588a5e0ccb | 3102ec6d1310b3db007305eaa5802b3831d4b4ae5f165e21ee1e3298f55e5616 | FR     | 0.4.6       | 
 5082b1ae-6523-4e3b-a1d8-9750b4407ee8 | android     | 8ff1dcf25f4b6b831000c6af50fe0ca5c03b8db525d3c8b955531d20e5904457 | 8d99f03f520c4faaf8cc1b0c2fcb88f9ece87e7984ca36bdb7feb98d53ba023d |        | 3.7         | 
 5bc74293-3ca1-4f34-bb89-523887d0cc2f | ios         | 4535674cdeafe9e1bbc4792de6891ddf6a6c21c7accd8087036402aefc7dc31e | facaa527add19a6ad0a9d3bc806b80e6e8b9cb2fcdedf4122ddc352035022832 | PT     | 2.2.8       | 
 92d8ceec-2e12-49f3-81bd-518fe66971ec | android     | befc41fae56d97b40286a8ca77c179ae8e513388c74a73608c234463a1cb7d5c | 19ca7209461ccf164747bc93d56efb2f16fc3f14b1e3cf404dc157746adb7063 | BR     | 0.5.5       | 
 05e153b1-4fa1-474c-bd7e-9f74d1c495e7 | android     | 0d7f5fae97d2b525c78ce18b97fc4eb814e54c3874917aaaefc5ee15802c457e | bd1bcce6493944b297b2e9d87163d7aa01856c8f23f1a660152e5c8ed54d85eb |        | 0.5.0       | 
 325c0f3d-da25-45ff-aff4-81816db069bc | android     | 5f1bb1f8901076482ca745b88ef02071bcf0abc887eabdb1d1a6c8b47dcdd841 | 16efd8b6baabc95d04083e6d573aa6aa95a0dba3f4ee594d1ed3f60ddd909b19 | RU     | 0.60        | 
(10 rows)
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








