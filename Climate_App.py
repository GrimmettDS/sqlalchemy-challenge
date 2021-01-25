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
        f"<h1>Welcome to the Climate App API</h1>"
        f"/api/v1.0/precipitation<p>"
        f"/api/v1.0/stations<p>"
        f"/api/v1.0/tobs<p>"
        f"/api/v1.0/&ltstart&gt - (Please use yyyy-mm-dd format)<p>"
        f"/api/v1.0/&ltstart&gt&&ltend&gt - (Please use 'yyyy-mm-dd & yyyy-mm-dd' format)<p>"
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


@app.route("/api/v1.0/tobs")
def tobs():
    
    session = Session(engine)
    
    # Find the most recent date in the data set.
    recent_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    
    # Calculate the date one year from the last date in data set.
    recent_date = recent_date[0]
    past_year = dt.datetime.strptime(recent_date, "%Y-%m-%d") - dt.timedelta(days=365)  
    
    # Query the dates and temperature observations of the most active station for the last year of data.
    most_active_station = session.query(Measurement.station, Measurement.date, Measurement.tobs).filter(Measurement.date >= past_year).order_by(Measurement.date).all()
    station_list = list(most_active_station)
    
    session.close()

    # Return a JSON list of temperature observations (TOBS) for the previous year.
    return jsonify(station_list)


@app.route("/api/v1.0/<start>")
def start(start):
    
    session = Session(engine)

    # Return a JSON list of the minimum temperature, the average temperature, and the max temperature for a given start or start-end range.
    recent_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    recent_date = recent_date[0]
    
    # When given the start only, calculate TMIN, TAVG, and TMAX for all dates greater than and equal to the start date.
    min_temp = session.query(Measurement.tobs, func.min(Measurement.tobs)).filter(Measurement.date.between (start, recent_date))
    avg_temp = session.query(Measurement.tobs, func.avg(Measurement.tobs)).filter(Measurement.date.between (start, recent_date))
    max_temp = session.query(Measurement.tobs, func.max(Measurement.tobs)).filter(Measurement.date.between (start, recent_date))

    temp_list = {"Tmin": min_temp[0][0], "Tmax": max_temp[0][0], "Tavg": avg_temp[0][0]}

    start_calc = session.query(Measurement.date, func.min(Measurement.tobs), func.max(Measurement.tobs), func.avg(Measurement.tobs)).\
        filter(Measurement.date >= start).group_by(Measurement.date).all()
    
    calc_list = list(start_calc)

    session.close()

    return jsonify(temp_list, calc_list)


@app.route("/api/v1.0/<start>&<end>")
def start_date(start, end):
    
    session = Session(engine)
    
    # When given the start and the end date, calculate the TMIN, TAVG, and TMAX for dates between the start and end date inclusive.
    min_temp = session.query(Measurement.tobs, func.min(Measurement.tobs)).filter(Measurement.date.between (start, end))
    avg_temp = session.query(Measurement.tobs, func.avg(Measurement.tobs)).filter(Measurement.date.between (start, end))
    max_temp = session.query(Measurement.tobs, func.max(Measurement.tobs)).filter(Measurement.date.between (start, end))    
    
    temp_list = {"Tmin": min_temp[0][0], "Tmax": max_temp[0][0], "Tavg": avg_temp[0][0]}

    start_calc = session.query(Measurement.date, func.min(Measurement.tobs), func.max(Measurement.tobs), func.avg(Measurement.tobs)).\
        filter(Measurement.date.between(start, end)).group_by(Measurement.date).all()

    calc_list = list(start_calc)

    session.close()

    return jsonify(temp_list, calc_list)

if __name__ == '__main__':
    app.run(debug=True)