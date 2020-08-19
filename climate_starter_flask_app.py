import numpy as np
import datetime as dt

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func,and_

from flask import Flask, jsonify

#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the table
Measurement= Base.classes.measurement
Station= Base.classes.station


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
        f"Available Routes:<br/>"
        f"Precipitation: /api/v1.0/precipitation<br/>"
        f"List of Stations: /api/v1.0/stations<br/>"
        f"Temperature observed for previous year: /api/v1.0/tobs<br/>"
        f"Temperature (Min, Max, Avg) for dates gt or eq to start date(yyyy-mm-dd): /api/v1.0/yyyy-mm-dd<br/>"
        f"Temperature (Min, Max, Avg) for dates between start and end dates(yyyy-mm-dd): /api/v1.0/yyyy-mm-dd/yyyy-mm-dd"
    )


@app.route('/api/v1.0/precipitation')
def precipitation():
    session = Session(engine)
    prcp_results = session.query(Measurement.date,Measurement.prcp).all()
    session.close()

    precipitation = []
    for date, prcp in prcp_results:
        prcp_dict = {}
        prcp_dict["Date"] = date
        prcp_dict["Precipitation"] = prcp
        precipitation.append(prcp_dict)

    return jsonify(precipitation)


@app.route('/api/v1.0/stations')
def stations():
    session = Session(engine)
    station_stat = session.query(Station.station,Station.name,Station.latitude,Station.longitude,Station.elevation).all()
    session.close()

    stations = []
    for station, name,lat,lon,elev in station_stat:
        station_stat_dict = {}
        station_stat_dict["Station"] = station
        station_stat_dict["Name"] = name
        station_stat_dict["Latitude"] = lat
        station_stat_dict["Longitute"] = lon
        station_stat_dict["Elevation"] = elev
        stations.append(station_stat_dict)

    return jsonify(stations)


@app.route('/api/v1.0/tobs')
def tobs():
    session = Session(engine)
    mindate = session.query(Measurement.date).order_by(Measurement.date.desc()).first()[0]
    mindatestrp = dt.datetime.strptime(mindate, '%Y-%m-%d')
    one_year_past_date = dt.date(mindatestrp.year -1, mindatestrp.month, mindatestrp.day)
    tobs_result = session.query(Measurement.date,Measurement.tobs).filter(Measurement.date >= one_year_past_date).all()
    session.close()

    tobs_list = []
    for date, tobs in tobs_result:
        tobs_dict = {}
        tobs_dict["Date"] = date
        tobs_dict["Tobs"] = tobs
        tobs_list.append(tobs_dict)

    return jsonify(tobs_list)


@app.route('/api/v1.0/<start>')
def start(start):
    session = Session(engine)
    tobs_stats_4date = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
                    filter(Measurement.date >= start).all()
    session.close()

    tobs_start = []
    for min,avg,max in tobs_stats_4date:
        tobs_dict = {}
        tobs_dict["Min"] = min
        tobs_dict["Average"] = avg
        tobs_dict["Max"] = max
        tobs_start.append(tobs_dict)

    return jsonify(tobs_start)

@app.route('/api/v1.0/<start>/<stop>')
def get_t_start_stop(start,stop):
    session = Session(engine)
    tobs_stats_bwdate = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
                             filter(Measurement.date >= start).filter(Measurement.date <= stop).all()
    session.close()

    tobs_start_stop = []
    for min,avg,max in tobs_stats_bwdate:
        tobs_dict = {}
        tobs_dict["Min"] = min
        tobs_dict["Average"] = avg
        tobs_dict["Max"] = max
        tobs_start_stop.append(tobs_dict)

    return jsonify(tobs_start_stop)

    
if __name__ == '__main__':
    app.run(debug=True)
