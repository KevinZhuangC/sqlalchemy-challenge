# Import the dependencies.
import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from datetime import datetime, timedelta

from flask import Flask, jsonify


#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")


# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(autoload_with=engine)

# Save references to each table
measurement = Base.classes.measurement
station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)
#################################################
# Flask Setup
#################################################
app = Flask(__name__)

#################################################
# Flask Routes
#################################################

@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/&lt;start&gt<br/>"
        f"/api/v1.0/&lt;start&gt/&lt;end&gt;"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    session = Session(engine)
    latest_date = session.query(measurement.date).order_by(measurement.date.desc()).first()[0]
    latest_date = datetime.strptime(latest_date, '%Y-%m-%d')
    one_year_ago = latest_date - timedelta(days=365)
    results = session.query(measurement.date, measurement.prcp).filter(measurement.date >= one_year_ago).all()
    session.close()
    precipitation_values = {date: prcp for date, prcp in results}
    return jsonify(precipitation_values)

@app.route("/api/v1.0/stations")
def stations():
    session = Session(engine)
    results = session.query(station.station).all()
    session.close()
    stations_list = list(np.ravel(results))
    return jsonify(stations_list)

@app.route("/api/v1.0/tobs")
def tobs():
    session = Session(engine)
    most_active_station = session.query(measurement.station, func.count(measurement.station)).group_by(measurement.station).order_by(func.count(measurement.station).desc()).first()[0]
    latest_date = session.query(measurement.date).order_by(measurement.date.desc()).first()[0]
    latest_date = datetime.strptime(latest_date, '%Y-%m-%d')
    one_year_ago = latest_date - timedelta(days=365)
    results = session.query(measurement.date, measurement.tobs).filter(measurement.date >= one_year_ago).filter(measurement.station == most_active_station).all()
    session.close()
    temps = list(np.ravel(results))
    return jsonify(temps)

@app.route("/api/v1.0/<start>")
def start(start):
    session = Session(engine)
    results = session.query(func.min(measurement.tobs), func.avg(measurement.tobs), func.max(measurement.tobs)).filter(measurement.date >= start).all()
    session.close()
    temps = list(np.ravel(results))
    return jsonify(temps)

@app.route("/api/v1.0/<start>/<end>")
def start_end(start, end):
    session = Session(engine)
    results = session.query(func.min(measurement.tobs), func.avg(measurement.tobs), func.max(measurement.tobs)).filter(measurement.date >= start).filter(measurement.date <= end).all()
    session.close()
    temps = list(np.ravel(results))
    return jsonify(temps)

if __name__ == '__main__':
    app.run(debug=True)