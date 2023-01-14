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

# Precipitation analysis
data_selection = [Measurement.date, Measurement.prcp]

data_query_results = session.query(*data_selection).filter(Measurement.date >= '2016-08-23').all()

date_prcp_list = []

for x in data_query_results:
    (m_dt, m_prcp) = x
    
    date_prcp_list.append({"date" : m_dt,
                           "prcp" : m_prcp})

date_prcp_df = pd.DataFrame(date_prcp_list, columns=['date','prcp'])
date_prcp_df = date_prcp_df.set_index("date")

########################################################


station_names = [Station.station, Station.name]

stations_query = session.query(*station_names).all()

stations_list = []

for x in stations_query:
    (s_station, s_name) = x
    
    stations_list.append({"station" : s_station,
                          "name" : s_name})
############################################################

tobs_selection = [Measurement.date, Measurement.tobs]

last_year_obs_results = session.query(*tobs_selection).filter(Measurement.station == 'USC00519281')\
                                        .filter(Measurement.date >= '2016-08-18').all()

last_year_obs_list = []

for x in last_year_obs_results:
    (m_dt1, m_tobs) = x
    
    last_year_obs_list.append({"date" : m_dt1,
                           "tobs" : m_tobs})
###########################################################

# Define index route
@app.route("/")
def home():
    print("this is my first home page!")
    return (
            f"Welcome to the weather analysis app <br/>"
            f"Available routes: <br/>"
            f"/about <br/>"
            f"/api/v1.0/precipitation <br/>"
            f"/api/v1.0/stations <br/>"
            f"/api/v1.0/tobs <br/>"
            f"/api/v1.0/<start_date> <br/>"
            F"/api/v1.0/test"
    )


# Define other routes
@app.route("/about")
def about():
    print("Received request for about page ... work in progress")
    return "Welcome to my about page"

@app.route("/api/v1.0/precipitation")
def precipitation():
    print("this is the precipitation routine")

    return jsonify(date_prcp_list)

@app.route("/api/v1.0/stations")
def stations():
    print("This is stations routine")

    return jsonify(stations_list)

@app.route("/api/v1.0/tobs")
def tobs():
    print("This is the tobs subroutine")

    return jsonify(last_year_obs_list)

@app.route("/api/v1.0/get_temp_from_date/<date_arg>")
def get_temp_from_date(date_arg):
    print("temperature stats calculations")

    reformat_date = date_arg.replace(" ","").lower()
    for x in last_year_obs_list:
        search_term = x["date"].replace(" ","").lower()

        if search_term == reformat_date:
            return x

    return jsonify({"error":f"Date {date_arg} not found"})

@app.route("/api/v1.0/<start>")
def temperature_start_dt(start):

    # Create session with DB
    session = Session(engine)

    results = session.query(Measurement.station, func.max(Measurement.tobs), func.min(Measurement.tobs),\
                            func.avg(Measurement.tobs)).filter(Measurement.station == 'USC00519281')\
                            .filter(Measurement.date >= start).group_by(Measurement.station).all()

    session.close()

    temp_stats_list = []

    # temp_results = list(np.ravel(results_max))

    for station, max_temp, min_temp, avg_temp in results:
        #(m_station, m_temp) = x
        temp_stats_list.append({"station" : station,
                                "TMAX" : max_temp, 
                                "TMIN" : min_temp, 
                                "TAVG" : avg_temp })



    return jsonify(temp_stats_list)

@app.route("/api/v1.0/<start>/<end>")
def temperature_start_end_dt(start, end):

    # Create session with DB
    session = Session(engine)

    results = session.query(Measurement.station, func.max(Measurement.tobs), func.min(Measurement.tobs),\
                            func.avg(Measurement.tobs)).filter(Measurement.station == 'USC00519281')\
                            .filter(Measurement.date >= start).filter(Measurement.date <= end).group_by(Measurement.station).all()

    session.close()

    temp_stats_list = []

    # temp_results = list(np.ravel(results_max))

    for station, max_temp, min_temp, avg_temp in results:
        #(m_station, m_temp) = x
        temp_stats_list.append({"station" : station,
                                "TMAX" : max_temp, 
                                "TMIN" : min_temp, 
                                "TAVG" : avg_temp })



    return jsonify(temp_stats_list)

if __name__ == "__main__":
    app.run(debug=True)

