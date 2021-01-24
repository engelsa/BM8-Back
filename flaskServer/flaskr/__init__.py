import os
import sqlite3
import json
import ssl

from flask_cors import CORS
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

def get_stats_city(city,state,cursor,query):
    state_abbrev = us_state_abbrev[state]

    query = query.replace("PLACEHOLDER_CITY",city).replace("PLACEHOLDER_STATE_UPPER",state.upper()).replace("PLACEHOLDER_STATE_ABBREV",state_abbrev).replace("PLACEHOLDER_STATE",state)

    # print(query)

    cursor.execute(query)

    # print(query)
    query_result = cursor.fetchall()
    if (len(query_result) != 0):
        # print(query_result)
        return query_result[0][0]
    else:
        # print(query_result)
        return None
    

@app.route('/get-city', methods=['GET', 'POST'])
def get_city():
    '''
    cost: cost of living
    age: age
    crime: homicide rate
    income: household income
    travel_time: mean travel time for commute
    employment: employment rate/percentage
    disability: disability
    education: education spending/student
    airport: distance to airport
    transportation: commute miles
    in_tax: income tax
    climate: climate
    '''
    print('=====================================================')
    #print(temp['query', default={}, type=dict))
    temp = request.get_json()
    print(temp)
    parameters = {
        "cost": {
            "quantity": temp['cost_val'],
            "importance": temp['cost_imp']
        },
        "age": {
            "quantity": temp['age_val'],
            "importance": temp['age_imp']
        },
        "crime": {
            "importance": temp['crime_imp']
        },
        "income": {
            "quantity": temp['house_val'],
            "importance": temp['house_imp']
        },
        "travel_time": {
            "quantity": temp['travel_time_val'],
            "importance": temp['travel_time_imp']
        },
        "employment": {
            "quantity": temp['employment_val'],
            "importance": temp['employment_imp']
        },
        "disability": {
            "importance": temp['disability_imp']
        },
        "education": {
            "quantity": temp['edu_val'],
            "importance": temp['edu_imp']
        },
        "airport": {
            "quantity": temp['airport_val'],
            "importance": temp['airport_imp']
        },
        "transportation": {
            "quantity": temp['dist_val'],
            "importance": temp['dist_imp']
        },
        "in_tax": {
            "quantity": temp['income_val'],
            "importance": temp['income_imp']
        },
        "climate": {
            "high": temp['climate_high'],
            "low": temp['climate_low'],
            "importance": temp['climate_imp']
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

    cursor.execute(query)
    results = ""
    cities_found = []
    for row in cursor.fetchall():
        city = row[0]+","+row[1]
        if (city not in cities_found):
            cities_found.append(city)
            results += str(row) + "\n"
    
    queries = {
        "cost": "SELECT ind FROM cost_living WHERE city='PLACEHOLDER_CITY' AND state_abbrev='PLACEHOLDER_STATE_ABBREV'",
        "age": "SELECT age FROM age WHERE city='PLACEHOLDER_CITY' AND state_abbrev='PLACEHOLDER_STATE_ABBREV'",
        "crime": "SELECT murders FROM crime WHERE state='PLACEHOLDER_STATE'",
        "employment": "SELECT 1 - (employed / civ_force) FROM employment WHERE city='PLACEHOLDER_CITY' AND state_abbrev='PLACEHOLDER_STATE_ABBREV'",
        "income": "SELECT house_income FROM employment WHERE city='PLACEHOLDER_CITY' AND state_abbrev='PLACEHOLDER_STATE_ABBREV'",
        "travel_time": "SELECT travel_time FROM employment WHERE city='PLACEHOLDER_CITY' AND state_abbrev='PLACEHOLDER_STATE_ABBREV'",
        "disability": "SELECT score FROM disability WHERE city='PLACEHOLDER_CITY' AND state_abbrev='PLACEHOLDER_STATE_ABBREV'",
        "education": "SELECT spending FROM ed WHERE state='PLACEHOLDER_STATE'",
        "airport": "SELECT dist FROM airport WHERE city='PLACEHOLDER_CITY' AND state_abbrev='PLACEHOLDER_STATE_ABBREV'",
        "transportation": "SELECT miles FROM transportation WHERE city='PLACEHOLDER_CITY' AND state_abbrev='PLACEHOLDER_STATE_ABBREV'",
        "income_tax_high": "SELECT high FROM in_tax WHERE state='PLACEHOLDER_STATE_UPPER'",
        "income_tax_low": "SELECT low FROM in_tax WHERE state='PLACEHOLDER_STATE_UPPER'",
        "climate_high": "SELECT high FROM climate WHERE state='PLACEHOLDER_STATE' AND city='PLACEHOLDER_CITY'",
        "climate_low": "SELECT low FROM climate WHERE state='PLACEHOLDER_STATE' AND city='PLACEHOLDER_CITY'",
        "climate_precip": "SELECT low FROM climate WHERE state='PLACEHOLDER_STATE' AND city='PLACEHOLDER_CITY'"
    }

    cities = []
    states = []
    for city_state in cities_found[:10]:
        city,state = city_state.split(",")
        cities.append(city)
        states.append(state)
    
    results_json = {
        "cities": cities,
        "states": states,
        "states_abbrev": [us_state_abbrev[state] for state in states],
        "cost": [get_stats_city(city,state,cursor,queries["cost"]) for city,state in zip(cities,states)],
        "age": [get_stats_city(city,state,cursor,queries["age"]) for city,state in zip(cities,states)],
        "crime": [get_stats_city(city,state,cursor,queries["crime"]) for city,state in zip(cities,states)],
        "employment": [get_stats_city(city,state,cursor,queries["employment"]) for city,state in zip(cities,states)],
        "income": [get_stats_city(city,state,cursor,queries["income"]) for city,state in zip(cities,states)],
        "travel_time": [get_stats_city(city,state,cursor,queries["travel_time"]) for city,state in zip(cities,states)],
        "disability": [get_stats_city(city,state,cursor,queries["disability"]) for city,state in zip(cities,states)],
        "education": [get_stats_city(city,state,cursor,queries["education"]) for city,state in zip(cities,states)],
        "airport": [get_stats_city(city,state,cursor,queries["airport"]) for city,state in zip(cities,states)],
        "transportation": [get_stats_city(city,state,cursor,queries["transportation"]) for city,state in zip(cities,states)],
        "income_tax_high": [get_stats_city(city,state,cursor,queries["income_tax_high"]) for city,state in zip(cities,states)],
        "income_tax_low": [get_stats_city(city,state,cursor,queries["income_tax_low"]) for city,state in zip(cities,states)],
        "climate_high": [get_stats_city(city,state,cursor,queries["climate_high"]) for city,state in zip(cities,states)],
        "climate_low": [get_stats_city(city,state,cursor,queries["climate_low"]) for city,state in zip(cities,states)],
        "climate_precip": [get_stats_city(city,state,cursor,queries["climate_precip"]) for city,state in zip(cities,states)]
    }


    # print(get_stats_city("Phoenix","Arizona",cursor,"SELECT * FROM in_tax"))

    return json.dumps(results_json,indent = 2, separators=(',', ': '));

if __name__ == '__main__':
    config_app()
    CORS(app)
    app.run()