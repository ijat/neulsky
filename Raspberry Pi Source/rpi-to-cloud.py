import socket, ssl, zlib, codecs, json, sys, os
from pymongo import MongoClient
from colorama import Fore, Back, Style

client = MongoClient()
db = client['neulsky']
col = db['raw_data']


os.system('clear')
print(Fore.GREEN + "\nMain Cloud Interface for " + Fore.WHITE + "Neul"+ Fore.BLUE + "Sky\n" + Fore.GREEN +"--------------------------------" + Style.RESET_ALL)

bindsocket = socket.socket()
bindsocket.bind(('', 10093))
bindsocket.listen(5)

def do_something(connstream, data):
	x=codecs.decode(data, "zlib")
	try:
		s = bytes(x).decode('ascii')
		j = json.loads(s)
		_id = col.insert(j)
		sys.stdout.write(Fore.YELLOW + "\rReceiving data... "+ Fore.WHITE +"[ Last ID: {0} ]".format(_id) + Style.RESET_ALL)
		sys.stdout.flush()
		#print(_id)
	#	print(j['time']['hour'])
	except Exception as e:
		print(e)
	return False

def deal_with_client(connstream):
    data = connstream.read()
    while data:
        if not do_something(connstream, data):
            break
        data = connstream.read()

print(Fore.YELLOW + "\nWaiting for data..." + Style.RESET_ALL)
while True:
    newsocket, fromaddr = bindsocket.accept()
    connstream = ssl.wrap_socket(newsocket,
                                 server_side=True,
                                 certfile="server.crt",
                                 keyfile="server.key")
    try:
        deal_with_client(connstream)
#    finally:
        #connstream.shutdown(socket.SHUT_RDWR)
        #connstream.close()
    except Exception as e:
       print(e)

