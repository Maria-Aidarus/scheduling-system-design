from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__, template_folder="../templates")  # Adjust the path if needed
app.config.from_object('config.Config')

db = SQLAlchemy(app)

# Import and register the Blueprint
from app.routes import routes
app.register_blueprint(routes)
