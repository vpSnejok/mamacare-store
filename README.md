# Running Instructions

This file contains instructions for setting up and running the project.

## 1. Setting Up Environment

1. Copy the `example.env` file and rename it to `.env`.
2. Configure the `.env` file as needed, filling in all necessary environment variables.

## 2. Running with Docker Compose

1. Open your command line or terminal in the project directory.
2. Run the following command to build and start the containers:

```bash
docker-compose up --build
```

## 3. Api docs

```link
http://localhost:8000/api/docs/
```

## 4  Api docs
Create admin
```bash
docker exec -it mamacare-store-backend-1 python manage.py createsuperuser
```

```link
http://localhost:8000/admin/
```