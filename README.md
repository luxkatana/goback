# goback - A pocket-sized version of wayback

> What if we could make websites last 4ever?

## About the project

I think we all are familiar with the wayback machine, it's a site that makes backups of sites.

Goback is based on wayback, but then more simplified, and written in Python, it uses FastAPI as backend and React typescript as the frontend.

**This project was made for a computer science assignment**

## Requirements to run this project using docker

- Docker
- Docker-compose
- an API key from appwrite (https://appwrite.io/)
- A storage bucket made within an appwrite project
- A MySQL server (required if you're planning to run it manually)
- A computer that at least can run doom

## Requirements to run this project manually (without docker)
- Python3 
- Git
- an API key from appwrite (https://appwrite.io/)
- A storage bucket made within an appwrite project
- A MySQL server (or any SQL server)
- Node.js 20+ with npm
- A computer that at least can run doom

## Running goback

> There are two ways to run this project

First of all, clone the master branch of this repository

```
git clone https://github.com/luxkatana/goback
cd goback
```

Here is how you can collect the required appwrite credentials:

- For ``GOBACK_PROJECT_ID``, go to Overview and then you'll find two buttons that are next to the name of the project, one is the project ID, another one is the endpoint URL, click on the project ID and it'll automatically put the project ID in your clipboard.

- For ``GOBACK_ENDPOINT_URL``, Is next to the project ID you found above, it is a button with the text "API endpoint", click on it and then it'll put the endpoint url in your clipboard

- For ``GOBACK_KEY``, go to Overview, scroll down until you see a section called "Integrations", click on API keys, and create a new API key.
> The API key must have the files.read and files.write scopes  enabled in Storage

Don't forget to copy the secret (is marked with dots)

- For ``GOBACK_STORAGE_BUCKET_ID``, head to **Storage**, and then create a new storage bucket. When you finished creating a storage bucket and then copy the long text that is next to your storage bucket's name

### Running goback with docker-compose

Open the ``.env`` file  with your favorite editor, and fill in the secrets you just have collected.

Start the container with:
```shell
sudo docker-compose up  # In linux, macos and WSL
# Run it without the -d flag to check if it can run normally, without issues
# If there are no errors in the output, do ctrl-C, and then run
sudo docker-compose up -d # To run the container detached, in the background
```

To stop the container, run
```shell
sudo docker-compose down
```

The default port that docker exposes goback to is ``8000``, if you want to run goback through a different port, open the ``compose.yaml`` file and head to line 8, change the 2nd 8000 to your desired port so that you'll have 
```
- "8000:your_desired_port"
```

Save and exit, start the container with the previous commands.

### Running goback without docker

Open the goback.toml file, and fill in the appwrite credentials you just have collected.

db_connection_string must be a database URI scheme, such as 
```
mysql+pymysql://youruser:yourpassword@hostname_or_ip:3306_or_another_port/database_name
```

for MySQL.

**NOTE: This database uri will not work for any other database server such as PostgreSQL. For example, if you want to use PostgreSQL, you'll have to replace the ``mysql+pymysql`` part with other drivers that are compatible with sqlalchemy**

Set ``use_sqlite_as_fallback_option`` to ``false`` if you don't want goback to use the fallback option (which is sqlite) when the main database (db_connection_string) fails.

Save goback.toml and exit, run in the goback directory the following commands:
```shell
pip3 install -r requirements.txt # Install python3 dependencies
cd goback-frontend
npm i && npm run build  # Install npm dependencies and build the react frontend
cd ..
uvicorn webserver:app --host "0.0.0.0" --port 80 # Run the webserver
```

Open your browser and head to 127.0.0.1:80 and you'll find the home page of goback
