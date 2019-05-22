import datetime as dt
from dateutil.relativedelta import relativedelta
import numpy as np
import pandas as pd

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from sqlalchemy import desc

from flask import Flask, jsonify


engine = create_engine("sqlite:///Resources/hawaii.sqlite", connect_args={'check_same_thread': False}, echo=True)

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

Measurement = Base.classes.measurement
Station = Base.classes.station
session = Session(engine)
app = Flask(__name__)


@app.route('/')
def welcome():
   return (
       f'Welcome to the Hawaii Climate Analysis API!<br/>'
       f'Available Routes:<br/>'
       f'/api/v1.0/precipitation<br/>'
       f'/api/v1.0/stations<br/>'
       f'/api/v1.0/tobs<br/>'
       f'/api/v1.0/temp/start/end<br/>'
       f'/api/v1.0/temp/start<br/>'
       )




@app.route("/api/v1.0/precipitation")
def precipitation():

    yearago = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    precip = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date >= yearago).all()
    precip_dictionary = {date: prcp for date, prcp in precip}
    return jsonify(precip_dictionary) 

@app.route("/api/v1.0/stations")
def station():
    station_count = session.query(Measurement.station, func.count(Measurement.station)).\
        group_by(Measurement.station).order_by(func.count(Measurement.station).desc()).all()
    print("Executing Station Function")
    return jsonify(station_count)



@app.route("/api/v1.0/tobs")
def totalob():
    yearago = dt.timedelta(days=365)
    station_temp_counts = session.query(Measurement.station, func.count(Measurement.tobs).label('tobcount')).\
        filter(Measurement.date > yearago).\
            group_by(Measurement.station).\
            order_by(desc('tobcount')).all()

    print("Displaying Temperature Observations")
    return jsonify(station_temp_counts)

@app.route("/api/v1.0/temp/<start>")
def start_temp(start):
    date1 = start

    print(date1)
    return date1

@app.route("/api/v1.0/temp/<start_date>/<end_date>")
def start_end_temp(start_date, end_date):
    start_date1= start_date

    sel = [Station.station, Station.name, Station.latitude, 
       Station.longitude, Station.elevation, func.sum(Measurement.prcp)]

    results = session.query(*sel).\
    filter(Measurement.station == Station.station).\
    filter(Measurement.date >= start_date1).\
    filter(Measurement.date <= end_date).\
    group_by(Station.name).order_by(func.sum(Measurement.prcp).desc()).all()
    #Calculate minimun temp, avg temp and max temp for date >= start date. TBD
    #st_date_inp  = input("input a start date in yyyy-mm-dd format")
    #end_date_inp = input("input an end  date in yyyy-mm-dd format")
    st_date_inp  = start_date
    end_date_inp = end_date
    #Try except for start date.
    try:
        st_date_conv =  dt.datetime.strptime(st_date_inp, '%Y-%m-%d')
    
    #   print(st_date_conv,end_date_conv)
    except:
        print(" Invalid start date or date format. Please input valid date in yyyy-mm-dd format.")
        print(" Using default date. start = 2017-08-21")
        print("start date input: " + st_date_inp)
        print(" ")
        st_date_inp   = '2017-08-21'
        st_date_conv  = dt.datetime.strptime(st_date_inp, '%Y-%m-%d')
        
    #Try except for end date.
    try:
        end_date_conv = dt.datetime.strptime(end_date_inp, '%Y-%m-%d')
    except: 
        print(" Invalid end date or date format. Please input valid date in yyyy-mm-dd format.")
        print(" Using default  end date = current date")
        print("end date input:" + end_date_inp)
        print(" ")
        end_date_conv = dt.datetime.today().strftime('%Y-%m-%d')


    print(st_date_conv, end_date_conv)
    #Calculate minimum temp, avg temp and max temp in between  given 
    #start date and end date. 
    Meas_temp_st = session.query(func.min(Measurement.tobs),func.avg(Measurement.tobs),func.max(Measurement.tobs)).\
                     filter(Measurement.date >= st_date_conv).\
                     filter(Measurement.date <= end_date_conv).\
                     all()
    return jsonify(Meas_temp_st)




if __name__ == '__main__':
    app.run(debug=True)
