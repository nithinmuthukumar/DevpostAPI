from flask import Flask
from flask import request
from scraper import *
from flask_cors import CORS, cross_origin

app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'


@app.route('/hackathons/', methods=['GET', 'POST'])
def hackathons():
    options = request.get_json()
    amount = options.pop('amount')
    return {"hackathons": get_hackathons(amount=int(request.args.get('amount')), options=options)}


@app.route('/projects/', methods=['GET', 'POST'])
def projects():
    return get_projects(amount=int(request.args.get('amount')))


@app.route('/hackathon/submissions/', methods=['GET', 'POST'])
def hackathon_projects():
    data = request.get_json()
    return {"projects": get_hackathon_submissions(data['hackathonUrl'], data.pop('category', None),
                                                  data.pop('sortBy', None))}


@app.route('/hackathon/categories/', methods=['GET', 'POST'])
def hackathon_categories():
    data = request.get_json()
    return {'categories': [i['name'] for i in get_hackathon_categories(data['hackathonUrl'])]}


@app.route('/profile/projects/', methods=['GET', 'POST'])
def profile_projects():
    data = request.get_json()
    return {"projects": get_profile_projects(data['username'])}


@app.route('/profile/', methods=['GET', 'POST'])
def profile():
    data = request.get_json()
    return get_profile(data['username'])


# TODO: finish get_hackathon_info
@app.route('/hackathon/', methods=['GET', 'POST'])
def hackathon():
    data = request.get_json()
    return get_hackathon_info(data['hackathonUrl'])


@app.route('/project/', methods=['GET', 'POST'])
def project():
    data = request.get_json()
    return get_project_info(data['projectUrl'])


if __name__ == "__main__":
    app.run(port=5000)
