#import flask
from flask import Flask, url_for
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask import abort, request
from flask import Response
from flask_sslify import SSLify
from flask_cors import CORS
from pymongo import MongoClient
import json
from bson import Binary, Code
from bson.json_util import dumps


# Pymongo
client = MongoClient()
db = client['neulsky']
col_new = db['data']

# Flask
trusted_proxies = ('42.42.42.42', '82.42.82.42', '127.0.0.1')

app = Flask(__name__)
CORS(app)
sslify = SSLify(app)

limiter = Limiter(
    app,
    key_func=get_remote_address,
    global_limits=["10240 per minute", "1 per second"],
)

#@app.before_request
#def limit_remote_addr():
#    if request.remote_addr != '188.166.227.52' and request.remote_addr != '149.56.160.34' and request.remote_addr != '173.232.19.228':
#        abort(403)  # Forbidden

@app.route('/neulsky/')
@limiter.limit("10240/minute")
def api_root():
	resp = Response("<h2>NeulSky API v0.01</h2>\n\nVisit <a href=\"https://ijat.my\">here</a> to learn more.")
	resp.headers['Server'] = "NeulSky API v0.01"
	return resp

@app.route('/neulsky/getData', methods = ['GET'])
@limiter.limit("10240/minute")
def api_getData():
	#latest_data = col_new.find().sort("$natural",1).limit(1)
	latest_data = col_new.find().sort("_id",-1).limit(1)
	try:
		jdata = dumps(latest_data[0])
		resp = Response(jdata, status=200, mimetype='application/json')
		resp.headers['Server'] = "NeulSky API v0.01"
		return resp
	except Exception as e:
		print(e)


if __name__ == '__main__':
	context = ('cert1.pem', 'privkey1.pem')
	app.run(host= '0.0.0.0', debug = False, ssl_context=context)
