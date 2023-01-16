# Imports
from flask import Flask, jsonify
import pandas as pd
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
import numpy as np

# Create app
app = Flask(__name__)

# create engine to hawaii.sqlite
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()

# reflect the tables
Base.prepare(autoload_with = engine)

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)

###### Pre-Loading Precipitation analysis for /api/v1.0/precipitation route ######

data_selection = [Measurement.date, Measurement.prcp]

#query db for last year of prcp data 
data_query_results = session.query(*data_selection).filter(Measurement.date >= '2016-08-23').all()

date_prcp_list = []

#unpack results and insert into list
for x in data_query_results:
    (m_dt, m_prcp) = x
    
    date_prcp_list.append({"date" : m_dt,
                           "prcp" : m_prcp})

###### Pre-Loading Hawaii Stations from dataset for /api/v1.0/stations route ######

station_names = [Station.station, Station.name]

#query db for Hawaii stations  
stations_query = session.query(*station_names).all()

stations_list = []

#unpack results and insert into list
for x in stations_query:
    (s_station, s_name) = x
    
    stations_list.append({"station" : s_station,
                          "name" : s_name})

###### Pre-Loading temperatures observed listing for USC00519281 for last 12 months for /api/v1.0/tobs route ######

tobs_selection = [Measurement.date, Measurement.tobs]

#query db for last 12 months of tobs  
last_year_obs_results = session.query(*tobs_selection).filter(Measurement.station == 'USC00519281')\
                                        .filter(Measurement.date >= '2016-08-18').all()

last_year_obs_list = []

#unpack results and insert into list
for x in last_year_obs_results:
    (m_dt1, m_tobs) = x
    
    last_year_obs_list.append({"date" : m_dt1,
                           "tobs" : m_tobs})
#close session
session.close()   
                        
# Begining definition of main program routes

# Define index/main route
@app.route("/")
def home():
    print("this is my first home page!")
    return (
            f"Welcome to my Hawaii Climate Analysis app <br/>"
            f"Available routes: <br/>"
            f"/about <br/>"
            f"/api/v1.0/precipitation <br/>"
            f"/api/v1.0/stations <br/>"
            f"/api/v1.0/tobs <br/>"
            f"/api/v1.0/get_temp_from_date/yyyy-mm-dd <br/>"
            f"/api/v1.0/enter_start_dt<br/>"
            f"/api/v1.0/enter_start_dt/enter_end_dt "
    )


# Define other routes
@app.route("/about")
def about():
    print("Received request for about page ... work in progress")
    return (f"Welcome to my about page <br/>"
            f"  Designed by Enrique Bouche"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    print("this is the precipitation routine")

    #return json formatted precipitation list
    return jsonify(date_prcp_list)

@app.route("/api/v1.0/stations")
def stations():
    print("This is stations routine")

    #return json formatted stations list
    return jsonify(stations_list)

@app.route("/api/v1.0/tobs")
def tobs():
    print("This is the tobs routine")

    #return json formatted tobs list
    return jsonify(last_year_obs_list)

# an additional route where client passes a date and the tobs for that date is returned
@app.route("/api/v1.0/get_temp_from_date/<date_arg>")
def get_temp_from_date(date_arg):
    print("temperature stats calculations")

    reformat_date = date_arg.replace(" ","").lower()
    for x in last_year_obs_list:
        search_term = x["date"].replace(" ","").lower()

        # if finding date inputed, return back row with date & tobs
        if search_term == reformat_date:
            return x
    # if date inputted is not found, return error message
    return jsonify({"error":f"Date {date_arg} not found"})

@app.route("/api/v1.0/<start>")
def temperature_start_dt(start):

    # Create session with DB
    session = Session(engine)

    # Query database for summary stats for USC00519281 since start date passed in route
    results = session.query(Measurement.station, func.max(Measurement.tobs), func.min(Measurement.tobs),\
                            func.avg(Measurement.tobs)).filter(Measurement.station == 'USC00519281')\
                            .filter(Measurement.date >= start).group_by(Measurement.station).all()

    session.close()

    temp_stats_list = []

    # temp_results = list(np.ravel(results_max))

    # unpack results variable into specific data points
    for station, max_temp, min_temp, avg_temp in results:
        # insert data points into dictionary list
        temp_stats_list.append({"station" : station,
                                "TMAX" : max_temp, 
                                "TMIN" : min_temp, 
                                "TAVG" : avg_temp })


    # return list to client in json format
    return jsonify(temp_stats_list)

@app.route("/api/v1.0/<start>/<end>")
def temperature_start_end_dt(start, end):

    # Create session with DB
    session = Session(engine)

    # Query database for summary stats for USC00519281 given start and end date passed in route
    results = session.query(Measurement.station, func.max(Measurement.tobs), func.min(Measurement.tobs),\
                            func.avg(Measurement.tobs)).filter(Measurement.station == 'USC00519281')\
                            .filter(Measurement.date >= start).filter(Measurement.date <= end).group_by(Measurement.station).all()

    session.close()

    temp_stats_list = []

    # temp_results = list(np.ravel(results_max))

    # unpack results variable into specific data points
    for station, max_temp, min_temp, avg_temp in results:
        # insert data points into dictionary list
        temp_stats_list.append({"station" : station,
                                "TMAX" : max_temp, 
                                "TMIN" : min_temp, 
                                "TAVG" : avg_temp })


    # return list to client in json format
    return jsonify(temp_stats_list)

# execute main program
if __name__ == "__main__":
    app.run(debug=True)

