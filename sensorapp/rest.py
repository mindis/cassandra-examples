import datetime
import json
import os
import time_uuid
import uuid
from cassandra.cluster import Cluster
from flask import Flask, request

def _connect_to_cassandra(keyspace):
    """
    Connect to the Cassandra cluster and return the session. 
    """

    if 'BACKEND_STORAGE_IP' in os.environ:
        host = os.environ['BACKEND_STORAGE_IP']
    else:
        host = 'localhost'

    cluster = Cluster([host])
    session = cluster.connect(keyspace)
    
    return session

"""
Create the Flask application, connect to Cassandra, and then
set up all the routes. 
"""
app = Flask(__name__)
session = _connect_to_cassandra('sensorapp')

@app.route('/api/sensors', methods=['GET'])
def get_sensors():
    """
    Fetch the sensor data from the Cassandra cluster. 
    The user can filter by sensor, and the number
    of days in the past. 
    """

    sensor = str(request.args['sensor'])
    days = int(request.args['days'])

    day = datetime.datetime.utcnow() - datetime.timedelta(days=days)
    ts = time_uuid.TimeUUID.with_utc(day, randomize=False, lowest_val=True)

    query = """SELECT * FROM sensor_data 
               WHERE sensor_id=%(sensor)s 
               and time>%(time)s
               ORDER BY time DESC"""

    values = { 'time': ts,
               'sensor': sensor }

    rows = session.execute(query, values)
    reply = { 'rows' : [] }
    for r in rows:
        ts = time_uuid.TimeUUID(str(r.time))
        dt = str(ts.get_datetime())
        reply['rows'].append({ 'sensor' : str(r.sensor_id),
                               'reading': str(r.reading),
                               'time': str(dt) })
    return json.dumps(reply)

@app.route('/api/sensors', methods=['POST'])
def put_sensors():
    """
    Insert some sensor data into Cassandra. 
    The sensor data is encoded as a JSON string. 
    """

    value = request.form['value']
    value_parsed = json.loads(value)

    query = """INSERT INTO sensor_data 
               (sensor_id, time, reading)
               VALUES (%(sensor_id)s, %(time)s, %(reading)s)"""

    values = { 'sensor_id':str(value_parsed['sensor']),
               'time': time_uuid.TimeUUID(value_parsed['time']),
               'reading': float(value_parsed['reading']) }

    session.execute(query, values)
    return ""

if __name__ == '__main__':
    app.run()
