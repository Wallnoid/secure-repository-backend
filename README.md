
# Secure Repository Backend

This is a mini-project for the topic of security in software development.

**What is it about?**\
The main objective is to encrypt documents with the encryption scheme AES without using any encryption-related libraries.
## Tech Stack

**Backend:** PYTHON 3, DJANGO\
**Services:** AWS, S3, IAM, COGNITO 


## Installation

First we need to create the virtual environment:

```bash
py -m venv venv
```

Activate the virtual environment:

```bash
.\venv\Scripts\activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Create .env file

```bash
AWS_ACCESS_KEY_ID=###
AWS_SECRET_ACCESS_KEY=###
AWS_REGION=###
AWS_BUCKET_NAME=###


```


Run project

```bash
python manage.py sunserver
```

## Appendix

The API documentation is generated with Swagger.

The endpoint to access it is:
```http
  /swagger
```

## Environment Variables

To run this project, you will need to add the following environment variables to your .env file

`AWS_ACCESS_KEY_ID`

`AWS_SECRET_ACCESS_KEY`

`AWS_REGION`

`AWS_BUCKET_NAME`
