from flask import Flask
from flask import jsonify
from flask import after_this_request

app = Flask(__name__)

@app.route('/test_data',methods=['GET'])
def get_data():
    @after_this_request
    def add_header(response):
        response.headers['Access-Control-Allow-Origin'] = '*'
        return response
    data = 'dd'
    return jsonify(data)

if __name__ == '__main__':
    app.run(debug=True)
