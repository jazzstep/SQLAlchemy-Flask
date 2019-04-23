import numpy as np
import pandas as pd
import sqlalchemy
import re
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from flask import Flask, jsonify
import datetime as dt

# Database Setup
engine = create_engine("sqlite:///Resources/hawaii.sqlite", echo=True)

# reflect an existing database into a new model
Base = automap_base()

# reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the tables
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB

climate = Flask(__name__)

@climate.route("/")
def home():
    print("Server received request for 'Home' page...")
    return (f"<br/>"
        f"Welcome to my Home page! Below are the available routes:<br/>"
        f"<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"<br/>"
        f"For the following two routes, dates take the format 'yyyy-mm-dd'<br/>"
        f"This will give you the lowest recorded temperature, highest recorded temperature and average temperature of the time between the two dates you inputted (&ltstart&gt/&ltend&gt route), or between the date you entered, and the last available data point(&ltstart&gt route)<br/>"
        f"<br/>"
        f"/api/v1.0/&ltstart&gt<br/>"
        f"/api/v1.0/&ltstart&gt/&ltend&gt<br/>"
        f"<br/>"
        f"Happy exploring!"
    )
@climate.route('/api/v1.0/precipitation')
def precipitation(): 
    session = Session(engine)
# * Convert the query results to a Dictionary using `date` as the key and `prcp` as the value.
# * Return the JSON representation of your dictionary.
    prcp_date = session.query(Measurement.date, Measurement.prcp).all()
    all_dates = list(np.ravel(prcp_date))
    return jsonify(all_dates)
# * `/api/v1.0/stations`
# * Return a JSON list of stations from the dataset.
@climate.route("/api/v1.0/stations")
def stations():
    session = Session(engine)
    stations = session.query(Station.station).all()
    all_stations = list(np.ravel(stations))
    return jsonify(all_stations)

# * query for the dates and temperature observations from a year from the last data point.
# * Return a JSON list of Temperature Observations (tobs) for the previous year.
@climate.route("/api/v1.0/tobs")
def tobs():
    session = Session(engine)
    recent_date_active = session.query(Measurement.date)\
   .order_by(Measurement.date.desc()).first()
    string_date = dt.datetime.strptime(recent_date_active[0], "%Y-%m-%d").date()
    twelve_months = string_date - dt.timedelta(days=365)
    temperature = session.query(Measurement.date, Measurement.tobs)\
    .filter(Measurement.date >= twelve_months).all()
    temperature_list = list(np.ravel(temperature))
    return jsonify(temperature_list)

# /api/v1.0/<start>` and `/api/v1.0/<start>/<end>`
# * Return a JSON list of the minimum temperature, the average temperature, and the max temperature for a given start or start-end range.
# * When given the start only, calculate `TMIN`, `TAVG`, and `TMAX` for all dates greater than and equal to the start date.
# * When given the start and the end date, calculate the `TMIN`, `TAVG`, and `TMAX` for dates between the start and end date inclusive
@climate.route("/api/v1.0/<start>")
@climate.route("/api/v1.0/<start>/<end>")
def start_end (start, end = None):
    session = Session(engine)
    if end == None:
        start_only = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start).all()
        start_list = list(np.ravel(start_only))
        return jsonify (start_list)
    else:
        start_and_end = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start).filter(Measurement.date <= end).all()
        start_and_endlist = list(np.ravel(start_and_end))
        return jsonify(start_and_endlist)

if __name__ == "__main__":
    climate.run(debug=True)