# WhatsApp Bot

## Preparation
```shell
# create a folder for git
mkdir ~/git && cd ~/git

# get the project
git clone https://github.com/namnamir/bots.git

# move to the WhatsApp project
cd bots/WhatsApp

# install python virtual environment
pip install virtualenv
virtualenv venv

# activate the virtual environment
source venv/bin/activate

# install requirements
pip install -r requirements.txt
```
## Run
```shell
# go to the project
cd ~/git/bots/WhatsApp/;

# activate the virtual environment
source venv/bin/activate;

# set Flask variables
export FLASK_APP=app.py;
export FLASK_ENV=development;
export FLASK_DEBUG=1;

# launch the app
flask run --host=0.0.0.0 --cert=/etc/letsencrypt/live/ames.site.com/fullchain.pem --key=/etc/letsencrypt/live/ames.site.com/privkey.pem;
```

## API Keys
### Meta
Follow [this instruction](https://www.pragnakalp.com/automate-messages-using-whatsapp-business-api-flask-part-1/) 
to create APIs.

