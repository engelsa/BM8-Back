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
    parameters = {
        "politics": {
            "quantity": 50,
            "importance": 30
        },
        "cost": {
            "importance": 10
        },
        "transport": {
            "importance": 70
        },
        "crime": {
            "importance": 100
        },
        "education": {
            "importance": 100
        },
        "climate": {
            "high": 100,
            "low": 20,
            "importance": 45
        },
        "density": {
            "quantity": 80,
            "importance": 100
        },
        "elevation": {
            "quantity": 1000,
            "importance": 10
        },
        "age": {
            "quantity": 25,
            "importance": 90
        },
        "airport": {
            "importance": 15
        },
        "disability": {
            "importance": 5
        }
    }

    connection = sqlite3.connect('../data.db')
    cursor = connection.cursor()

    query = """SELECT cities.city, cities.state, cost_living.ind *
                   {} AS _cost, (age.age -
                    {}) *
                   {} AS _age, crime.murders * 
                   {} AS _crime 
                   FROM cities INNER JOIN cost_living ON (cost_living.city=cities.city AND 
                   cost_living.state_abbrev=cities.state_abbrev) INNER JOIN age ON 
                   (age.city=cities.city AND age.state_abbrev=cities.state_abbrev) INNER JOIN 
                   crime ON (crime.state=cities.state)"""\
                    .format(str(parameters["cost"]["importance"]),
                            str(parameters["age"]["quantity"]),
                            str(parameters["age"]["importance"]),
                            str(parameters["crime"]["importance"])
                            )

    print(query)

    cursor.execute(query)
    results = ""
    for row in cursor.fetchall():
        results += str(row) + "\n"
    return results


if __name__ == '__main__':
    config_app()
    app.run()