# nba-predictions
An ETL pipeline with an airflow orchestrator that uses web scraping and interaction with APIs to create an NBA pdf report of a team of your choice.
It also includes a basic program that uses web scrapping as well to predict the winner of a game based on betting odds.

## Installation
In order to run this project on airflow you will need to have docker installed on your machine. You can download it from [here](https://docs.docker.com/get-docker/). Once you have docker installed you will need to run the following command in the root directory of the project:
```bash
    docker-compose up
```
That will run the airflow server on port 8080. You can access it by going to [http://localhost:8080](http://localhost:8080). The account credentials are:
```bash
    username: airflow
    password: airflow
```
