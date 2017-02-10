import socket, ssl, pprint, zlib, codecs, serial, time, sys, json, signal, os
from colorama import Fore, Back, Style

os.system('clear')

print(Fore.GREEN + "\nRasPi Arduino Interface for " + Fore.WHITE + "Neul"+ Fore.BLUE + "Sky\n" + Fore.GREEN +"-----------------------------------" + Style.RESET_ALL)

def signal_handler(signal, frame):
	print(Fore.RED + 'Pressed Ctrl+C!' + Style.RESET_ALL)
	try:
		arduino.close()
		ssl_sock.close()
	except:
		print(Fore.RED + "Nothing to close!" + Style.RESET_ALL)
		
	sys.exit(0)
signal.signal(signal.SIGINT, signal_handler)

try:
	arduino=serial.Serial('/dev/ttyUSB0',115200)
	
	try:
		s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		ssl_sock = ssl.wrap_socket(s,
					   ca_certs="server.crt",
					   cert_reqs=ssl.CERT_REQUIRED)
		ssl_sock.connect(('s5.ijat.my', 10070))
	except Exception as e:
		print(Fore.RED + "Socket error! " + e + Style.RESET_ALL)
	
except Exception as eeee:
	print(Fore.RED + "Arduino not connected! " + str(eeee) + Style.RESET_ALL)	


count = 0;
while 1:
	try:
		x=arduino.readline()
		y=bytes(x).decode('ascii')
		y=y.strip("'<>() ").replace('\'', '\"')
		if len(y) < 150:
			print(Fore.YELLOW + "\nPlease wait..." + Style.RESET_ALL)
			continue
		#print(y)
		#j = json.loads(y)
		#sys.exit()
		
		try:
			j = json.loads(y)
			
			hh = time.strftime("%H")
			mm = time.strftime("%M")
			ss = time.strftime("%S")
			
			j['time'] = dict();
			j['time']['hour'] = hh
			j['time']['minute'] = mm
			j['time']['second'] = ss
			
			jdat = json.dumps(j)
			jdat = bytes(jdat,'UTF-8')
			 
			try:
				s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
				ssl_sock = ssl.wrap_socket(s,
									   ca_certs="server.crt",
									   cert_reqs=ssl.CERT_REQUIRED)

				ssl_sock.connect(('s5.ijat.my', 10070))
								
				dat = codecs.encode(jdat, "zlib")
				ssl_sock.write(dat)
				ssl_sock.close()
				
				count = count + 1
				sys.stdout.write(Fore.YELLOW + "\rStreaming data to cloud... "+ Fore.WHITE +"[ Total data: #{0} | Time: {1}:{2}:{3} ]".format(count,hh,mm,ss) + Style.RESET_ALL)
				sys.stdout.flush()
			except Exception as e:
				print(Fore.RED + "Connection error: " + str(e) + Style.RESET_ALL)
			
		except Exception as ee:
			print(Fore.RED + "Arduino error: " + str(ee) + Style.RESET_ALL)

	except NameError:
		print(Fore.RED + "Arduino data error!" + Style.RESET_ALL)
		break
	
try:
	arduino.close()
except:
	print(Fore.RED + "Arduino context not exists!" + Style.RESET_ALL)
	
sys.exit()

