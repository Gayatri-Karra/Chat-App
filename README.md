# Web Chat App - `v1.0.0`: Initial version
This is a Web Real-Time Chat Application built using Django and Websockets with Partial End-to-End Encryption

## Requirements
- Python 3

## Installation
Clone the repository

```
git clone https://github.com/Anand-ReddyK/Real-Time-Chat-App.git
```

Create a Virtual Environment with Python and activate it
```
python -m venv venv
.\venv\Scripts\activate
```

Go inside the Cloned Repo and install the modules inside `requirements.txt`
```
cd Real-Time-Chat-App
pip install -r requirements.txt
```

Now the setup is complete, to run the project first make migrations
```
python manage.py makemigrations
python manage.py migrate
```
This will create a DataBase file `db.sqlite3`

To run the Project
```
python manage.py runserver
```
Open another terminal and run the `socket_server.py` file inside `Real-Time-Chat-App\chat`
```
python .\socket_server.py
```

open the link `http://127.0.0.1:8000/` in your browser

## Installation with Docker
Clone the repository
```
git clone https://github.com/Anand-ReddyK/Real-Time-Chat-App.git
```

Navigate to the root directory where the `Dockerfile` exists

Create a Docker image
```
docker build -t chat-app:1.0 .
```

Run the container using the newly created Docker image `chat-app:1.0`
```
docker run -p 8000:8000 -p 8001:8001 chat-app:1.0
```

open the link `http://127.0.0.1:8000/` in your browser
