import numpy as np
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

import pandas as pd
import datetime as dt

from collections import OrderedDict
from flask import Flask, jsonify

engine=create_engine("sqlite:///Resources/hawaii.sqlite")

Base=automap_base()

Base.prepare(engine, reflect=True)

table_names=Base.classes.keys()

tables={}
for name in table_names:
    title_name=name.title()
    tables[title_name]=Base.classes[name]
    
session=Session(bind=engine)



app=Flask(__name__)

end_date=dt.date(2017, 8, 23)

start_date=end_date-dt.timedelta(days=365)


@app.route("/")
def home():
	return (
		f'/api/v1.0/precipitation<br>'
		f'/api/v1.0/stations<br>'
		f'/api/v1.0/tobs<br>'
		f'/api/v1.0/start<br>'
		f'/api/v1.0/start/end'
		)

# I could have put this information in a dictionary like I did below but, wanted to have
# one where I just sent back the data directly from the query.
@app.route("/api/v1.0/precipitation")
def preciptation():
	# Calculate the date 1 year ago from the last data point in the database
	end_date=dt.date(2017, 8, 23)
	start_date=end_date-dt.timedelta(days=365)

	# Perform a query to retrieve the data and precipitation scores
	data=session.query(tables['Measurement'].date, tables['Measurement'].prcp).\
	filter(tables['Measurement'].date>=start_date).all()
	
	return jsonify(data)


@app.route("/api/v1.0/stations")
def station():
	stations=session.query(tables['Station'].id, tables['Station'].station, tables['Station'].name).all()
	station_dict={}
	for station in stations:
		station_dict[station[0]]=station[1]
	
	return jsonify(station_dict)

@app.route("/api/v1.0/tobs")
def tobs():
	station_activity=session.query(tables['Measurement'].station, func.count(tables['Measurement'].station)).\
	group_by(tables['Measurement'].station).order_by(func.count(tables['Measurement'].station).desc()).all()
	station_temp_activity=session.query(tables['Measurement'].date, tables['Measurement'].tobs).\
	filter(tables['Measurement'].station == station_activity[0][0]).\
	filter(tables['Measurement'].date >= start_date).all()
	temp_dict={}
	for activity in station_temp_activity:
		temp_dict[activity[0]]=activity[1]
		
	return jsonify(temp_dict)
	
@app.route("/api/v1.0/<start_date>")
def vacation_date(start_date):
	results = session.query(tables['Measurement'].date, func.min(tables['Measurement'].tobs), func.avg(tables['Measurement'].tobs), func.max(tables['Measurement'].tobs)).\
	filter(tables['Measurement'].date >= start_date).group_by(tables['Measurement'].date).all()	
	start_dict={}
	for date_data in results:
		start_dict[date_data[0]]={'Minimum Temperature': date_data[1], 'Average Temperature': round(date_data[2], 0), 'Maximum Temperature': date_data[3]}
	
	return jsonify(start_dict)
	
# Example:  127.0.0.1:5000/api/v1.0/2016-11-10/2016-11-25
@app.route("/api/v1.0/<start_date>/<end_date>")
def date_range(start_date, end_date):
	results = session.query(tables['Measurement'].date, func.min(tables['Measurement'].tobs), func.avg(tables['Measurement'].tobs), func.max(tables['Measurement'].tobs)).\
	filter(tables['Measurement'].date >= start_date).\
	filter(tables['Measurement'].date <= end_date).\
	group_by(tables['Measurement'].date).all()	
	range_dict={}
	begin_d={}
	end_d={}
	combine=OrderedDict()
	for date_data in results:
		
		begin_d['Your Vacation Begin Date'] = str(start_date)
		end_d['Your Vacation End Date'] = str(end_date)
		range_dict[date_data[0]]={'Minimum Temperature': date_data[1], 'Average Temperature': round(date_data[2], 0), 'Maximum Temperature': date_data[3]}
		combine['Head Out']=begin_d
		combine['Head Home']=end_d
		combine['Weather for Vacation Time Frame']=range_dict
	
	return jsonify(combine)

if __name__=="__main__":
	app.run(debug=True)


























