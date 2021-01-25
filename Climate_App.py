import numpy as py
import datetime as dt
import sqlalchemy

from flask import Flask, jsonify
from sqlalchemy import create_engine, func
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session

# Create engine to hawaii.sqlite
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# Reflect an existing database into a new model
Base = automap_base()

# Reflect the tables
Base.prepare(engine, reflect=True)

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Flask Routes
app = Flask(__name__)
@app.route("/")
def welcome():
    """List all available api routes."""
    return(
        f"/api/v1.0/precipitation<br/><br/>"
        f"/api/v1.0/stations<br/><br/>"
        f"/api/v1.0/tobs<br/><br/>"
        f"/api/v1.0/&ltstart&gt</br>"
        f"/api/v1.0/&ltstart&gt&&ltend&gt</br>"
    )

begin_date = dt.date(2017, 8, 23) - dt.timedelta(days=365)
@app.route("/api/v1.0/precipitation")
def precipitation():

    session = Session(engine)
    # Find the most recent date in the data set.
    recent_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()


    # Calculate the date one year from the last date in data set.
    recent_date = recent_date[0]
    past_year = dt.datetime.strptime(recent_date, "%Y-%m-%d") - dt.timedelta(days=365)  

    # Perform a query to retrieve the data and precipitation scores
    rain_data = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date >= past_year).order_by(Measurement.date).all()
    session.close()

# Convert the query results to a dictionary using date as the key and prcp as the value.
    prcp_data = []
    for date, prcp in rain_data:
        prcp_dict={}
        prcp_dict = {date:prcp}
        prcp_data.append(prcp_dict)

    return jsonify(prcp_data)

@app.route("/api/v1.0/stations")
def stations():

    session = Session(engine)
    active_station = session.query(Station.station, Station.name, Station.longitude, Station.latitude, Station.elevation).all()

    session.close()

    # Return a JSON list of stations from the dataset.
    station_list = []
    for station in active_station:
        station_dict={}
        station_dict["station"]=station
        station_list.append(station_dict)

    return jsonify(station_list)





if __name__ == '__main__':
    app.run(debug=True)