<h1 align="center">WAYD</h1>

[WAYD](https://faresi.pythonanywhere.com) is a web application to show "What Are You Doing?"

[![WAYD project image 1](https://github.com/mf210/WAYD/blob/main/project-images/page1.png)](https://faresi.pythonanywhere.com)

I built this web application because  I wanted to answer to one of the frequently asked question in my life, "How did I spend my time today?". In [WAYD](https://faresi.pythonanywhere.com) you can see how much time you spent on different subjects and how much time you were focused or happy or sad or etc.  
Also in this website you can determine a date range to filter results based on the days you want.  

Website address: https://faresi.pythonanywhere.com


## The challenges I Faced

### Passing data from django web application to javascript in secure mode

At first, I tried some methods that other developers had taught on youtube to solve this problem but I realized that they were unsafe and I implemented some XSS attacks on it for fun.  
So I needed to safely outputted a Python object as JSON, and after a bit of googling, I used django built-in filter called **json_script**.

### Solving Performance Problems in the Django ORM

I saw some identical and some similar queries via **Django Debug Toolbar** that was causing n+1 issue.  
To getting good performance I used some of methods in QuerySet object like select_related and prefetch_related to retrieve everything I need at once insted of hitting the database multiple times for different parts of a single ‘set’ of data.

## Install and Run Project without Docker

1. If you don't have **pipenv** on your machine, first install it with this command:

    ```
    pip install pipenv
    ```
    
2. Install the dependencies:
    
    ```
    pipenv install --dev
    ```

    > **_NOTE:_** if you're deploying to production or you don't want to use coverge, then remove --dev flag

3. Pay attention and set these environment variables on your server if you're deploying to production
    - DJANGO_DEBUG = FALSE
    - DJANGO_SECURE_SSL_REDIRECT = TRUE
    - DJANGO_SECURE_HSTS_INCLUDE_SUBDOMAINS = TRUE
    - DJANGO_SECURE_HSTS_PRELOAD = TRUE
    - DJANGO_SECURE_HSTS_SECONDS = 31536000
    - DJANGO_SESSION_COOKIE_SECURE = TRUE
    - DJANGO_CSRF_COOKIE_SECURE = TRUE
    - DJANGO_SECRET_KEY = secretkey
    - DJANGO_HOST_NAME = myhostname
    - DJANGO_EMAIL_HOST_USER = example@gmail.com
    - DJANGO_EMAIL_HOST_PASSWORD = password

4. After config the MySQL database, apply migrations to the database:

    ```
    pipenv run python manage.py migrate
    ```

5. Then run the server:

    ```
    pipenv run python manage.py runserver 0.0.0.0:8000
    ```

## How to Run Project Using Docker
You can simply run project with docker-compose:

    docker-compose up -d

> **_NOTE:_** if you're deploying to production you should uncomment environment section in **docker-compose** file and fill them according to your own configuration.

## Run Tests
Quick test:

    pipenv run python manage.py test

For test and measuring code coverage:
    
    pipenv run coverage run manage.py test


## Used Technologies

### Backend:

- MySQL
- Django
    - django-allauth (for using OAuth 2 protocol)
    - Django Debug Toolbar (analyzing the database queries and ...)
    - django-crispy-forms (styling forms)

### Frontend:

- Chart.js
- Bootstrap


<h2 align="center">Some Other Pictures</h2>

<p align="center"> Sign In Page </p>

[![WAYD project image 3](https://github.com/mf210/WAYD/blob/main/project-images/page3.png)](https://faresi.pythonanywhere.com/accounts/login/)

<p align="center">One Part of Home Page </p>

[![WAYD project image 2](https://github.com/mf210/WAYD/blob/main/project-images/page2.png)](https://faresi.pythonanywhere.com)
