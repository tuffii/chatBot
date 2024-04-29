# Python bot schedule tracker

## Запуск контейера с db

`docker build -t my_postgres .`

`docker run -d --name my_postgres_container -p 5432:5432 my_postgres`