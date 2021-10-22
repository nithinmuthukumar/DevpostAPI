from flask import Flask
from flask import request
from DevpostScraper import get_hackathons, get_projects, get_hackathon_projects,get_hackathon_categories,get_profile_projects
from flask_cors import CORS, cross_origin

app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'


@app.route('/hackathons/', methods=['GET'])
def hackathons():
    options = request.get_json()
    return get_hackathons(amount=int(request.args.get('amount')), options=options)


@app.route('/projects/', methods=['GET'])
def projects():
    return get_projects(amount=int(request.args.get('amount')))

@app.route('/hackathons/projects/')
def hackathon_projects():
    data = request.get_json()
    category = data['category'] if 'category' in data else None
    sort_by = data['sortBy'] if 'sortBy' in data else None
    return get_hackathon_projects(data['hackathonUrl'],category,sort_by)

@app.route('/hackathons/categories/')
def hackathon_categories():
    data = request.get_json()
    return get_hackathon_categories(data['hackathonUrl'])
@app.route('/profile/projects')
def profile_projects():
    data = request.get_json()
    return get_profile_projects(data['profileUrl'])

if __name__ == "__main__":
    app.run(port=5000)
