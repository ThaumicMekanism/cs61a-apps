from flask import Flask

from common.oauth_client import create_oauth_client
from common.jobs import job
from fa20 import update

from auth import authenticate, update_storage

app = Flask(__name__)
create_oauth_client(app, "grade-display-exports", return_response=update_storage)


@app.route("/")
def index():
    return authenticate(app)


@job(app, "update_grades")
def run():
    update()


if __name__ == "__main__":
    app.run(debug=True)