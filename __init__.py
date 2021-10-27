from flask import Flask
from flask import request
from scraper import get_hackathons, get_projects, get_hackathon_projects, get_hackathon_categories, \
    get_profile_projects
from flask_cors import CORS, cross_origin

app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'




if __name__ == "__main__":
    app.run(port=5000)
