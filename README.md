# Crop-Management-Simulator
Description:
A farming simulator application where users manage inventory, and grow crops. 

Current status:
SQL database and base game logic implemented

Feature roadmap: (To be implemented)
Login/signup + other database logic (plant crops, harvest crops, etc)
Real world weather data will be used within the game through the use of a weather API.
Interactive GUI that will be ran in docker.

USAGE:
## Requirements:
Python 3.14+
pip
uv
A running database (I am using PostgreSQL version 18)
Docker (optional)

## Install UV:
curl -LsSf https://astral.sh/uv/install.sh | sh
OR
pip install uv

## Setup
Clone the repo and create your .env file
git clone repo-url
cd repo-name
cp .env.example .env # set your own .env variables

## Install dependencies
uv sync
OR
pip install -r requirements.txt

## Running in terminal (GUI not implemented)

If running in docker, the DB_HOST must be overridden.
Run docker with these commands:
docker build -t application_name .
docker run -t -i --env-file .env -e DB_HOST=host.docker.internal crop-app

Otherwise, if running locally:
cd src/src_backend
python main.py
