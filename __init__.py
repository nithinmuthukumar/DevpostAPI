from ariadne import load_schema_from_path, make_executable_schema, constants, QueryType, graphql_sync
from ariadne.constants import PLAYGROUND_HTML
from flask import Flask, request, jsonify
from flask_cors import CORS

from scraper import *

type_defs = load_schema_from_path('schema.graphql')

query = QueryType()





@query.field("hackathons")
def resolve_hackathons(obj, info, amount, orderBy=None, location=None, status=None, length=None,
                       themes=None, organization=None, openTo=None, search=None):
    return get_hackathons(orderBy, location, status, length, themes, organization, openTo, search, amount=amount)


@query.field("projects")
def resolve_projects(obj, info, amount=5):

    return get_projects(amount=amount)


@query.field("categories")
def resolve_categories(obj, info, hackathonUrl=None):
    return get_hackathon_categories(hackathonUrl)


@query.field("profileProjects")
def resolve_profileProjects(obj, info, username=None):
    return get_profile_projects(username)


@query.field("submissions")
def resolve_submissions(obj, info, hackathonUrl=None,category=None,sortBy=None):
    print(hackathonUrl)
    return get_hackathon_submissions(hackathonUrl,category,sortBy)


@query.field("profile")
def resolve_profile(obj, info, username=None):
    return get_profile(username)


@query.field("hackathon")
def resolve_hackathon(obj, info, hackathonUrl=None):
    return get_hackathon_info(hackathonUrl)


@query.field("project")
def resolve_project(obj, info, projectUrl=None):
    return get_project_info(projectUrl)

schema = make_executable_schema(type_defs, query)
app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'

@app.route("/graphql", methods=["GET"])
def graphql_playground():
    # On GET request serve GraphQL Playground
    # You don't need to provide Playground if you don't want to
    # but keep on mind this will not prohibit clients from
    # exploring your API using desktop GraphQL Playground app.
    return PLAYGROUND_HTML, 200


@app.route("/graphql", methods=["POST"])
def graphql_server():
    # GraphQL queries are always sent as POST
    data = request.get_json()

    # Note: Passing the request to the context is optional.
    # In Flask, the current request is always accessible as flask.request
    success, result = graphql_sync(
        schema,
        data,
        context_value=request,
        debug=app.debug
    )
    print(result)

    status_code = 200 if success else 400
    return jsonify(result), status_code


if __name__ == "__main__":
    app.run(port=5000)
