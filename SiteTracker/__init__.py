import stripe
import os

from flask import Flask
from flask_bcrypt import Bcrypt
from datetime import timedelta
from flask_jwt_extended import JWTManager

from dotenv import load_dotenv

from SiteTracker.WebsiteRoutes.routes import website
from SiteTracker.Payment.routes import payment

from SiteTracker.cronjobs import start
start()
load_dotenv()


app=Flask(__name__)
app.config['SECRET_KEY']='hello'
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(hours=int(os.getenv('JWT_TOKEN_EXPIRE_HOURS')))
app.config["JWT_TOKEN_LOCATION"]=['cookies','headers']
app.config['JWT_COOKIE_CSRF_PROTECT']=False

app.config['STRIPE_PUBLIC_KEY']=os.getenv('STRIPE_PUBLIC_KEY')
app.config['STRIPE_SECRET_KEY']=os.getenv('STRIPE_SECRET_KEY')
stripe.api_key=app.config['STRIPE_SECRET_KEY']

bcry=Bcrypt(app)
jwt_app=JWTManager(app)

app.register_blueprint(blueprint=website,url_prefix='/website')
app.register_blueprint(blueprint=payment,url_prefix='/pay')
from SiteTracker import routes