# Sashick Bot

Sachick is a Telegram bot that is ready to help anyone who wants to learn new things from a kid trying to memorize multiplication table, to med students studying anatomy, and even for language learners. Sashick is happy to give you a choice of topics right away.

Sashick uses a spaced repetition technique to decide what card to show, and scientifically proven time intervals to show cards to users, 1, 7, 16 and 35 days.

Find Sashick bot on Telegram, and you will get a welcome message, with a list of user commands so that you can control the bot.

## Components

Sashick bot uses a Bot Framework SDK running on Django server. Django provides admin interface that is used for populating bot content with topics, questions, answers, and media.

Bot Framework SDK is asynchronous, but Django does not support asynchronous operations natively. It uses `@async_to_sync` decorator to connect Bot Framework handler to Django view.

Dialogs are written with Bot Framework Dialog library dialog graph. Content and user state (learning progress) are stored in the database which is accessed through Django ORM.

## Installation

Sashick uses Azure infrastructure. In Azure Portal create:

* Resource group. Within this resource group create:
* App Service Plan
* App Service
* Bot Channels Registration
* Azure Database for PostgreSQL server

### Running locally

Clone the repository. Change working directory to the cloned folder.

Create Virtual environment:
```
pip install virtualenv
virtualenv venv 
```

Activate virtual environment: `source venv/bin/activate`.

Install dependencies: `pip install -r requirements.txt`

Install [Bot Framework Emulator](https://github.com/Microsoft/BotFramework-Emulator/blob/master/README.md). 

In the folder `sashick-bot` create `.env` file, using the template:

```
SECRET_KEY = "<DJANGO_GENERATED_SECRET_KEY>"
APP_ID = "<AZURE_BOT_CHANNEL_APP_ID>"
APP_PASSWORD = "<AZURE_BOT_CHANNEL_APP_PASSWORD>"

DBNAME = "<POSTGRESQL_DATABASE_NAME>"
DBHOST = "<POSTGRESQL_DATABASE_HOST>"
DBUSER = "<POSTGRESQL_DATABASE_USER>"
DBPASS = "<POSTGRESQL_DATABASE_PASSWORD>"
```

(replace value in `<...>`).

Run Django server: `python manage.py runserver`

Start Azure Bot Framework. Open new connection, provide path to http://localhost:8000 (the host of the running server). Fill APP_ID and APP_PASSWORD in start dialog.

The bot now  is running locally and responding to messages in Bot Emulator.

### Deployment

Refer to [Tutorial: Deploy a Django web app with PostgreSQL in Azure App Service](https://docs.microsoft.com/en-us/azure/app-service/containers/tutorial-python-postgresql-app?tabs=bash%2Cclone) for additional information.

Install the [Azure CLI](https://docs.microsoft.com/en-us/cli/azure/install-azure-cli) 2.0.80 or higher, with which you run commands in any shell to provision and configure Azure resources.

Then sign in to Azure through the CLI: `az login`.

Configure environment variables to connect the database: 
```az webapp config appsettings set --settings DJANGO_ENV="production" DBHOST="<postgres-server-name>.postgres.database.azure.com" DBNAME="<database_name>" DBUSER="<username>" DBPASS="<password>"```

Replace template values in `<...>` with actual values.

Deploy the code to the container: `az webapp up --name sashick`.

Open an SSH session with Azure App:
`az webapp ssh --name <APP_NAME> -g <RESOURCE_GROUP> -t 30`. Replace template values with Azure WebApp name and resource groups.

Run following commands:
```
cd site/wwwroot

# Activate default virtual environment in App Service container
source /antenv/bin/activate
# Unpack dependencies archive
tar -xf wheelhouse.tar.gz
# Install dependencies
pushd wheelhouse
pip install *.whl
popd
# Run database migrations
python manage.py migrate
# Create the super user (follow prompts)
python manage.py createsuperuser
```

Note that the project dependencies are installed from precompiled Wheel packages (*.whl) rather than from PIP index. The reason for that is that the Bot Framework dialog library takes a dependency on `requests` package which requires compilation when installed from PIP index. The `gcc` compiler is not available on Azure WebApp container and regular installation fails. Precompiled Wheel packages contain assembled binaries for Linux x64_86 Python 3.7 platform (WebApp container platform).

Check that backend is running by opening `https://<WEBAPP_NAME>.azurewebsites.net/admin`.

Open Azure Bot Channels Registration in Azure Portal and set Messaging endpoint to `https://<WEBAPP_NAME>.azurewebsites.net/api/messages`

Connect your bot to Telegram - [instructions](https://docs.microsoft.com/en-us/azure/bot-service/bot-service-channel-connect-telegram?view=azure-bot-service-4.0).
