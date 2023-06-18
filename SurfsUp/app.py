# Import the dependencies.
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func, inspect
from flask import Flask, jsonify
import numpy as np

#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite", echo=False)

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(autoload_with=engine)
Base.classes.keys()

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

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
def home():
    print("Server received request for 'Home' page...")
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/start (enter as YYYY-MM-DD)<br/>"
        f"/api/v1.0/start/end (enter as YYYY-MM-DD/YYYY-MM-DD)"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
     #put in session queries
    results = session.query(Measurement.date).all()
    results = list(np.ravel(results))
    return jsonify(results=results)


@app.route("/api/v1.0/stations")
def stations():
    session = Session(engine)
    sel = [Station.station,Station.name,Station.latitude,Station.longitude,Station.elevation]
    queryresult = session.query(*sel).all()
    session.close()

    stations = []
    for station,name,lat,lon,el in queryresult:
        station_dict = {}
        station_dict["Station"] = station
        station_dict["Name"] = name
        station_dict["Lat"] = lat
        station_dict["Lon"] = lon
        station_dict["Elevation"] = el
        stations.append(station_dict)

    return jsonify(stations)

@app.route("/api/v1.0/tobs")
def tobs():
    session = Session(engine)
    results = session.query(Measurement.date, Measurement.tobs, Measurement.prcp).\
              filter(Measurement.date >= '2016-08-03').\
              filter(Measurement.station=='USC00519281').\
              order_by(Measurement.date).all()
    session.close()    


    total_tobs = []
    for date,tobs,prcp in results:
        tobs_dict = {}
        tobs_dict["date"] = date
        tobs_dict["tobs"] = tobs
        tobs_dict["prcp"] = prcp
        
        total_tobs.append(tobs_dict)

    return jsonify(total_tobs)         


@app.route("/api/v1.0/<start>")
def start():
    session = Session(engine)
    queryresult = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start).all()
    session.close()

    start_tobs = []
    for min,avg,max in queryresult:
        start_dict = {}
        start_dict["Min"] = min
        start_dict["Average"] = avg
        start_dict["Max"] = max
        start_tobs.append(start_dict)

    return jsonify(start_tobs)


@app.route("/api/v1.0/<start>/<end>")
def end():
    session = Session(engine)
    results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
                filter(Measurement.date >= start).filter(Measurement.date <= end).all()
    session.close()

    end_tobs=[]
    for min, avg, max in results:
        end_dict = {}
        end_dict["min_temp"] = min
        end_dict["avg_temp"] = avg
        end_dict["max_temp"] = max
        end_tobs.append(end_dict) 
    

    return jsonify(end_tobs)


if __name__ == "__main__":
    app.run(debug=True)
