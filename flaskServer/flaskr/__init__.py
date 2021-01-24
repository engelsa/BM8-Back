import os
import sqlite3
import json

from flask import *

app = Flask(__name__, instance_relative_config=True)

us_state_abbrev = {
    'Alabama': 'AL',
    'Alaska': 'AK',
    'American Samoa': 'AS',
    'Arizona': 'AZ',
    'Arkansas': 'AR',
    'California': 'CA',
    'Colorado': 'CO',
    'Connecticut': 'CT',
    'Delaware': 'DE',
    'District of Columbia': 'DC',
    'Florida': 'FL',
    'Georgia': 'GA',
    'Guam': 'GU',
    'Hawaii': 'HI',
    'Idaho': 'ID',
    'Illinois': 'IL',
    'Indiana': 'IN',
    'Iowa': 'IA',
    'Kansas': 'KS',
    'Kentucky': 'KY',
    'Louisiana': 'LA',
    'Maine': 'ME',
    'Maryland': 'MD',
    'Massachusetts': 'MA',
    'Michigan': 'MI',
    'Minnesota': 'MN',
    'Mississippi': 'MS',
    'Missouri': 'MO',
    'Montana': 'MT',
    'Nebraska': 'NE',
    'Nevada': 'NV',
    'New Hampshire': 'NH',
    'New Jersey': 'NJ',
    'New Mexico': 'NM',
    'New York': 'NY',
    'North Carolina': 'NC',
    'North Dakota': 'ND',
    'Northern Mariana Islands':'MP',
    'Ohio': 'OH',
    'Oklahoma': 'OK',
    'Oregon': 'OR',
    'Pennsylvania': 'PA',
    'Puerto Rico': 'PR',
    'Rhode Island': 'RI',
    'South Carolina': 'SC',
    'South Dakota': 'SD',
    'Tennessee': 'TN',
    'Texas': 'TX',
    'Utah': 'UT',
    'Vermont': 'VT',
    'Virgin Islands': 'VI',
    'Virginia': 'VA',
    'Washington': 'WA',
    'West Virginia': 'WV',
    'Wisconsin': 'WI',
    'Wyoming': 'WY'
}

def config_app():
    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'flaskr.sqlite')
    )

    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

def get_stats_city(city,state,cursor):
    state_abbrev = us_state_abbrev[state]
    

@app.route('/get-city')
def get_city():
    parameters = {
        "cost": {
            "importance": 50
        },
        "age": {
            "quantity": 25,
            "importance": 30
        },
        "crime": {
            "importance": 80
        },
        "income": {
            "importance": 90
        },
        "travel_time": {
            "importance": 30
        },
        "employment": {
            "importance": 95
        },
        "disability": {
            "importance": 10
        },
        "education": {
            "importance": 90
        },
        "airport": {
            "importance": 25
        },
        "transportation": {
            "importance": 100
        },
        "in_tax": {
            "importance": 25
        },
        "climate": {
            "high": 120,
            "low": 70,
            "importance": 100
        }
    }

    connection = sqlite3.connect('../data_backup.db')
    cursor = connection.cursor()

    query = """SELECT DISTINCT cities.city, cities.state, (1 - (cost_living.ind / 183)) * {} AS _cost,
                    1 / ((ABS(age.age - {}) / age.age) + 1) * {} AS _age,
                   (1 - (crime.murders / 12.4)) * {} AS _crime,
                   employment.employed / employment.civ_force * {} AS _employment,
                   employment.house_income / 130865 * {} AS _income,
                   (1 - (employment.travel_time / 35.9)) * {} AS _travel_time,
                   disability.score / 57 * {} AS _disability,
                   ed.spending / 23091 * {} AS _ed,
                   (1 - (airport.dist / 1400)) * {} AS _airport,
                   transportation.miles / 10000000000 * {} AS _transportation,
                   (1 - ((in_tax.high + in_tax.low) / 24.6)) * {} AS _in_tax,
                   (1 / (ABS(climate.high - {}) / climate.high + 1) + 
                   1 / (ABS(climate.low - {}) / climate.low + 1)) * {} AS _climate 
                   FROM cities INNER JOIN cost_living ON (LOWER(cost_living.city)=LOWER(cities.city) AND 
                   LOWER(cost_living.state_abbrev)=LOWER(cities.state_abbrev)) LEFT JOIN age ON 
                   (LOWER(age.city)=LOWER(cities.city) AND LOWER(age.state_abbrev)=LOWER(cities.state_abbrev)) INNER JOIN 
                   crime ON (LOWER(crime.state)=LOWER(cities.state)) INNER JOIN employment ON 
                   (LOWER(employment.city)=LOWER(cities.city) AND 
                   LOWER(employment.state_abbrev)=LOWER(cities.state_abbrev)) LEFT JOIN disability 
                   ON (LOWER(disability.city)=LOWER(cities.city) AND LOWER(disability.state_abbrev)=LOWER(cities.state_abbrev)) 
                   INNER JOIN ed ON (LOWER(ed.state)=LOWER(cities.state)) LEFT JOIN airport 
                   ON (LOWER(airport.city)=LOWER(cities.city) AND LOWER(airport.state_abbrev)=LOWER(cities.state_abbrev)) 
                   LEFT JOIN transportation ON (LOWER(transportation.city)=LOWER(cities.city) AND 
                   LOWER(transportation.state_abbrev)=LOWER(cities.state_abbrev)) INNER JOIN in_tax ON 
                   LOWER(in_tax.state)=LOWER(cities.state) INNER JOIN climate ON (LOWER(climate.city)=LOWER(cities.city) AND LOWER(climate.state)=LOWER(cities.state)) ORDER BY 
                   _age * _age + _crime * _crime + _employment * _employment + _income * _income 
                   + _travel_time * travel_time + _disability * _disability + _ed * _ed + 
                   _airport * _airport + _transportation * _transportation + _climate * _climate DESC"""\
                    .format(str(parameters["cost"]["importance"]),
                            str(parameters["age"]["quantity"]),
                            str(parameters["age"]["importance"]),
                            str(parameters["crime"]["importance"]),
                            str(parameters["employment"]["importance"]),
                            str(parameters["income"]["importance"]),
                            str(parameters["travel_time"]["importance"]),
                            str(parameters["disability"]["importance"]),
                            str(parameters["education"]["importance"]),
                            str(parameters["airport"]["importance"]),
                            str(parameters["transportation"]["importance"]),
                            str(parameters["in_tax"]["importance"]),
                            str(parameters["climate"]["high"]),
                            str(parameters["climate"]["low"]),
                            str(parameters["climate"]["importance"]))

    print(query)

    cursor.execute(query)
    results = ""
    cities_found = []
    for row in cursor.fetchall():
        # rows_found.append(row)
        # if (row not in rows_found):
        city = row[0]+" "+row[1]
        if (city not in cities_found):
            cities_found.append(city)
            results += str(row) + "\n"
    
    results_json = {
        "cities": cities_found[:10]
    }

    return json.dumps(results_json);


if __name__ == '__main__':
    config_app()
    app.run()
