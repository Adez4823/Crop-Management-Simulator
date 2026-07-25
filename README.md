# Crop-Management-Simulator
Description:
A farming simulator application where users manage inventory, and grow crops. 

Current status:
Login/signup implemented

Feature roadmap: (To be implemented)<br>
Interactive React frontend

## Requirements:
Python 3.14+<br>
pip<br>
uv<br>
A running PostgreSQL (ver. 18)<br>
Docker (optional)

## Install UV:
curl -LsSf https://astral.sh/uv/install.sh | sh<br>
OR<br>
pip install uv

## Setup
Clone the repo and create your .env file<br>
git clone repo-url<br>
cd repo-name,<br>
cp .env.example .env # set your own .env variables

## Install dependencies
uv sync<br>
OR<br>
pip install -r requirements.txt

## Running in terminal (GUI not implemented)

If running in docker, the DB_HOST must be overridden.<br>
Run docker with these commands:<br>
docker build -t application_name .<br>
docker run -t -i --env-file .env -e DB_HOST=host.docker.internal application_name<br>

Otherwise, if running locally:<br>
cd src/src_backend<br>
python main.py
