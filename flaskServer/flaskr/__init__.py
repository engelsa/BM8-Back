import os
import sqlite3

from flask import *

app = Flask(__name__, instance_relative_config=True)


def config_app():
    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'flaskr.sqlite')
    )

    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass


@app.route('/hello')
def hello():
    connection = sqlite3.connect('data.db')
    connection.execute('')
    return "Hello world!"


if __name__ == '__main__':
    config_app()
    app.run()