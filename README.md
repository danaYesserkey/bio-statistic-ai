# Biostatistics Learning Platform

## Project Overview

Biostatistics Learning Platform is an AI-powered educational web application designed to support medical students in learning biostatistics in the Kazakh language.

The platform combines structured educational materials, interactive quizzes, personalized statistics, and an AI assistant that explains statistical concepts and answers students' questions. The project aims to improve statistical literacy through an accessible and modern learning environment.



## Project Objectives

The main objective of the project is to simplify the study of biostatistics by providing:

- interactive learning modules;
- AI-assisted explanations;
- practical quizzes;
- student progress tracking;
- personalized learning statistics.



## Main Features

- User registration and authentication using JWT
- Personal user profile
- Course management
- Modular learning system
- Interactive lessons
- Quiz system
- AI chat assistant
- Personal learning statistics
- REST API
- Admin panel for course management



## Technology Stack

### Backend

- Python 3.12
- Django 6
- Django REST Framework
- SQLite
- JWT Authentication
- Groq API
- Django ORM

### Frontend

- React
- Vite
- Axios
- CSS3



## Project Structure

```
biostatistics_backend/
    apps/
        users/
        courses/
        quizzes/
        stats/

biostatistics_frontend/
    src/
        components/
        pages/
        services/
```



## Database Models

The project contains the following main models:

- User
- Course
- Module
- Lesson
- Quiz
- Question
- Statistics



## Authentication

Authentication is implemented using JSON Web Tokens (JWT).

Supported operations:

- Register
- Login
- Logout
- Refresh Token



## API

Main endpoints:

```
POST /api/users/register/
POST /api/users/login/
POST /api/users/token/refresh/

GET /api/courses/
GET /api/courses/{id}

GET /api/quizzes/
POST /api/quizzes/

GET /api/stats/
```



## Installation

### Backend

```
cd biostatistics_backend

python -m venv venv

source venv/bin/activate

pip install -r requirements.txt

python manage.py migrate

python manage.py runserver
```

### Frontend

```
cd biostatistics_frontend

npm install

npm run dev
```



## AI Integration

The platform integrates the Groq API to provide intelligent explanations of statistical concepts and personalized educational assistance.



## Authors

Developed as a Web Development course project at Kazakh-British Technical University.
