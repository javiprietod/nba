# NBA
An ETL pipeline with an airflow orchestrator that uses web scraping and interaction with APIs to create an NBA pdf report of a team of your choice.
It also includes a basic program that uses web scrapping as well to predict the winner of a game based on betting odds.

## Configuration
Before running the project you will need to create an account on [https://sportsdata.io/cart/free-trial/nba](https://sportsdata.io/cart/free-trial/nba). When you register click on 'Launch Developer Portal' to get your API key. 
Now go to your root directory and in the data folder you will find a file called `config.txt` where you will need to paste your API key and the team you want to get the report for. The team name should be the same as the one in the [nba website](https://www.nba.com/teams) or else the program will not work. For example if you want to get the report for the Golden State Warriors you will need to write `Golden State Warriors` in the config file.

## Running the project

### Airflow
Beforehand, go to the command line on your root directory and run the following command:
```bash
pip install apache-airflow
```
or if you have a mac:
```bash
pip3 install apache-airflow
```
After that you will need to run the following command in the root directory of the project:
```bash
export AIRFLOW_HOME=$(pwd)
```

In order to run this project on airflow you will need to have docker installed on your machine. You can download it from [here](https://docs.docker.com/get-docker/). Once you have docker installed you will need to run the following command in the root directory of the project:
```bash
docker-compose up
```
That will run the airflow server on port 8080. You can access it by going to [http://localhost:8080](http://localhost:8080). The account credentials are:
```bash
username: airflow
password: airflow
```
The program will run at 15:00 CET every day. You can change the schedule by going to the `nba_dag.py` file and changing the schedule variable. This variable uses the cron syntax and it is UTC based. You can read more about it [here](https://crontab.guru/).

### Locally
In order to run the project locally you will need to have python 3.7 installed on your machine. You can download it from [here](https://www.python.org/downloads/). Once you have python installed you will need to install the dependencies by running the following command in the root directory of the project:
```bash
pip install -r requirements.txt
```
After that you will need to run the following command in the root directory of the project:
```bash
python plugins/team_stats.py run
```

## Consuming the output
All the output files will be stored in the `data` directory. The pdf will have the name of the team you chose in the config file. For example if you chose the Golden State Warriors the pdf will be called `Golden State Warriors.pdf`. You will also find a file called `pronostico.txt` that contains the prediction of the winner of the game based on the betting odds.

