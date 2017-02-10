import time, statistics, urllib.request, urllib.error, json, codecs, sys, os
from pymongo import MongoClient
from colorama import Fore, Back, Style

# Global variable
global last_predict

os.system('clear')
print(Fore.GREEN + "\nMongoDB and Azure Interface  for " + Fore.WHITE + "Neul"+ Fore.BLUE + "Sky\n" + Fore.GREEN +"----------------------------------------" + Style.RESET_ALL)

client = MongoClient()
db = client['neulsky']
col = db['raw_data']
col_new = db['data']

temp = dict()
humid = dict()
pres = dict()
dew = dict()
wpre = dict()

last_predict = 0

print(Fore.YELLOW + "\nRunning..." + Style.RESET_ALL)

while 1:
	
	
	#latest_data = col.find().sort("$natural",-1).limit(1)	#get last / latest records in collection
	latest_data = col.find().sort("_id",-1).limit(1)	#get last / latest records in collection
	#add_data = col.find({"time.hour": time.strftime("%H")})
	add_data = col.find({})

	if ( int(time.strftime("%H"))  == 0):
		col.remove({})
		col_new.remove({})
		print("Database reseted!")

	# START PREDICTION
	
	if (( int(time.strftime("%M")) % 5 ) == 0) and (time.strftime("%H:%M") != last_predict):
		list_temp = list()
		list_humid = list()
		list_pres = list()
		list_dew = list()

		for a in add_data:
			try:
				list_temp.append(a['temperature_bmp180'])
				list_humid.append(a['humidity'])
				list_pres.append(a['pressure_sealevel'])
				list_dew.append(a['dew_point'])
			except:
				print("Error - Removing records")
				col.remove({})
				
		temp['max'] = "%.0f" % max(list_temp)
		temp['min'] = "%.0f" % min(list_temp)
		temp['mean'] = "%.0f" % statistics.mean(list_temp)
		humid['max'] = "%.0f" % max(list_humid)
		humid['min'] = "%.0f" % min(list_humid)
		humid['mean'] = "%.0f" % statistics.mean(list_humid)
		pres['max'] = "%.0f" % max(list_pres)
		pres['min'] = "%.0f" % min(list_pres)
		pres['mean'] = "%.0f" % statistics.mean(list_pres)
		dew['max'] = "%.0f" % max(list_dew)
		dew['min'] = "%.0f" % min(list_dew)
		dew['mean'] = "%.0f" % statistics.mean(list_dew)

		data = {
				"Inputs": {
						"input1":
						{
							"ColumnNames": ["temp_max", "temp_mean", "temp_min", "dew", "dew_mean", "dew_min", "humid_max", "humid_mean", "humid_min", "p_max", "p_mean", "p_min"],
							"Values": [ [ temp['max'], temp['mean'], temp['min'], dew['max'], dew['mean'], dew['min'], humid['max'], humid['mean'], humid['min'], dew['max'], dew['mean'], dew['min'] ] ]
						},        },
					"GlobalParameters": {}
					}

		body = str.encode(json.dumps(data))

		url = 'https://ussouthcentral.services.azureml.net/workspaces/1034d1758c4c47dcb14bd607ced47c1c/services/e2bfdc3d0e9247b0aec1b9d7a54b7686/execute?api-version=2.0&details=true'
		api_key = 'LwEQoiGtKF3ZXQPVYkbUaVWUA8oV2iG2VBB6u6vtsUg72QwSrTcXHEbt5kKMTnVDAOhA3x/8w4zniwCTOCzZ9w==' # Replace this with the API key for the web service
		headers = {'Content-Type':'application/json', 'Authorization':('Bearer '+ api_key)}
		req = urllib.request.Request(url, body, headers) 

		try:
			response = urllib.request.urlopen(req)
			result = response.read()
			sres = bytes(result).decode('utf-8')
			jres = json.loads(sres)
			wpre['dict'] = jres['Results']['output1']['value']['Values'][0][12]
			wpre['time'] = time.strftime("%H:%M")
			last_predict = time.strftime("%H:%M")
			print(Fore.YELLOW + "\rFetched Azure-ML prediction at {0}.".format(wpre['time']) + Style.RESET_ALL)
		except Exception as error:
			print(error)
			
		# END OF PREDICTION

	try:
		wpre['dict']
		wpre['time']
	except:
		wpre['dict'] = "Not enough data"
		wpre['time'] = "Not enough data"
		
	try:
		tdata = {
				'node'	: latest_data[0]['node'],
				'status': latest_data[0]['status'],
				'temp'	: "%.2f" % latest_data[0]['temperature_bmp180'],
				'heat'	: latest_data[0]['heat_index'],
				'dew'	: latest_data[0]['dew_point'],
				'humid'	: latest_data[0]['humidity'],
				'pres'	: "%.2f" % latest_data[0]['pressure_sealevel'],
				'wpre'	: {
					'dict'	: wpre['dict'],
					'time'	: wpre['time']
				},
				'time'	: latest_data[0]['time']['hour']+":"+latest_data[0]['time']['minute']+":"+latest_data[0]['time']['second']
			}
	except:
		tdata = {
				'node'	: "1",
				'status': "offline",
				'temp'	: "-",
				'heat'	: "-",
				'dew'	: "-",
				'humid'	: "-",
				'pres'	: "-",
				'wpre'	: {
					'dict'	: "-",
					'time'	: "-"
				},
				'time'	: "-"
			}

	# Add to database
	id = col_new.insert(tdata)

	sys.stdout.write(Fore.YELLOW + "\rUpdating database... "+ Fore.WHITE +"[ Last ID: {0} | Time: {1} ]".format(id,tdata['time']) + Style.RESET_ALL)
	#print(Fore.YELLOW + "\rUpdating database... "+ Fore.WHITE +"[ Last ID: {0} ]".format(id) + Style.RESET_ALL)
	#print(tdata)
	sys.stdout.flush()
		
	add_data = None
	latest_data = None
	list_temp = None
	list_humid = None
	list_pres = None
	list_dew = None
	
	#print(tdata)
	
	tdata = None
	time.sleep(2)