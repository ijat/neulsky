// Includes
#include <DHT.h>
#include <ArduinoJson.h>
#include <SFE_BMP180.h>
#include <Wire.h>

// Defines
#define DHTPIN 5        // Digital Pin 5
#define DHTTYPE DHT11   // DHT 11
#define NODE 1          // Node 1 @ UPM

// DHT11 Conf
DHT dht(DHTPIN, DHTTYPE);

// JSON Conf
StaticJsonBuffer<512> jBuf;
JsonObject& jData = jBuf.createObject();

// BMP180 Conf
SFE_BMP180 pressure;
#define ALTITUDE 45.904 // From https://www.daftlogic.com/sandbox-google-maps-find-altitude.htm

// dewPoint function NOAA
// reference (1) : http://wahiduddin.net/calc/density_algorithms.htm
// reference (2) : http://www.colorado.edu/geography/weather_station/Geog_site/about.htm
//
double dewPoint(double celsius, double humidity)
{
  // (1) Saturation Vapor Pressure = ESGG(T)
  double RATIO = 373.15 / (273.15 + celsius);
  double RHS = -7.90298 * (RATIO - 1);
  RHS += 5.02808 * log10(RATIO);
  RHS += -1.3816e-7 * (pow(10, (11.344 * (1 - 1/RATIO ))) - 1) ;
  RHS += 8.1328e-3 * (pow(10, (-3.49149 * (RATIO - 1))) - 1) ;
  RHS += log10(1013.246);

        // factor -3 is to adjust units - Vapor Pressure SVP * humidity
  double VP = pow(10, RHS - 3) * humidity;

        // (2) DEWPOINT = F(Vapor Pressure)
  double T = log(VP/0.61078);   // temp var
  return (241.88 * T) / (17.558 - T);
}

void setup() {

  Serial.begin(115200);
  //Serial.println("Debug");

  jData["node"] = 1;

  dht.begin();
  if (pressure.begin()) jData["status"] = "online";
  else jData["status"] = "offline";
  

}

void loop() {
  char status;
  double T,P,p0,a;
  bool dhts, bmp;
  
  // Wait a few seconds between measurements.
  delay(1000);

  // ===== DHT11 =====
  // Reading temperature or humidity takes about 250 milliseconds!
  // Sensor readings may also be up to 2 seconds 'old' (its a very slow sensor)
  float h = dht.readHumidity();
  //jData["humidity"] = h;
  jData.set<float>("humidity", h);

  // Read temperature as Celsius (the default)
  float t = dht.readTemperature();
  //jData["temperature"] = t;
  jData.set<float>("temperature_dht11", t);

  // Check if any reads failed and exit early (to try again).
  if (isnan(h) || isnan(t)) dhts = false;
  else dhts = true;
  
  // Compute heat index in Celsius (isFahreheit = false)
  float hic = dht.computeHeatIndex(t, h, false);
  //jData["heat_index"] = hic;
  jData.set<float>("heat_index", hic);

  // Dew points
  jData.set<double>("dew_point", dewPoint(t, h));


  // ===== BMP180 =====
  // Altitude
  jData.set<float>("altitude_local", ALTITUDE);

  status = pressure.startTemperature();
  if (status != 0) {
    delay(status);

    status = pressure.getTemperature(T);
    if (status != 0) jData["temperature_bmp180"].set(T,6);

    status = pressure.startPressure(3);
    if (status != 0) {
      delay(status);

      status = pressure.getPressure(P,T);
        if (status != 0) {

          p0 = pressure.sealevel(P,ALTITUDE);
          a = pressure.altitude(P,p0);
          
          jData["pressure_absolute"].set(P,8);
          jData["pressure_sealevel"].set(p0,8);
          jData["altitude_calc"].set(a,8);

          bmp = true;

        } else bmp = false;
    } else bmp = false;
  } else bmp = false;

  if (bmp && dhts) jData["status"] = "online";
  else jData["status"] = "offline";
  
  //jData.prettyPrintTo(Serial);
  jData.printTo(Serial);
  Serial.println();
  //Serial.print(P);
}
