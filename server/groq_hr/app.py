from flask import Flask
from flask_cors import CORS
from routes import routes

app = Flask(__name__)
CORS(app,
     origins=["http://localhost:5173"],
     methods=["GET", "POST", "OPTIONS"],
     allow_headers=["Content-Type", "X-Requested-With", "Authorization"])

app.register_blueprint(routes)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5025, debug=True)
