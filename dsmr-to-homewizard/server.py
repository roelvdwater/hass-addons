from http.server import BaseHTTPRequestHandler, HTTPServer
import logging
import json
import requests
from sys import argv
from datetime import datetime
from zeroconf import Zeroconf, ServiceInfo
from ipaddress import ip_address
import socket
import time
import urllib3

product_name = "P1 Meter"
product_type =  "HWE-P1"
firmware_version = "5.19"
api_version = "v1"
wifi_ssid = "MyWifiNetwork"
wifi_strength = 100
smr_version = 42
meter_model = "Kaifa AIFA-METER"
unique_id = "4530923235303056303786273439341236"
gas_unique_id = "4767300939332530333230483593323136"

url = f"{argv[2]}/api/template"

cached_data = None
cache_refresh_time = None
cache_interval = 12
disable_ssl_checks = argv[4] == "true"

if disable_ssl_checks is True:
    urllib3.disable_warnings(category=urllib3.exceptions.InsecureRequestWarning)

headers = {
    'Authorization': argv[1],
    'content-type': 'application/json'
}

payload = {
    "template": "{% set data = namespace(entities=[]) %}{% for entity in integration_entities('dsmr') %}{% set e = {'name': entity, 'state': states(entity)} %}{% set data.entities = data.entities + [e] %}{% endfor %}{{data.entities|tojson}}"
}

def advertise_service():
    hostname = "p1meter-1BC34C.local."
    ip = ip_address(socket.gethostbyname(socket.gethostname()))

    info = ServiceInfo(
        type_="_hwenergy._tcp.local.",
        name="p1meter-1BC34C._hwenergy._tcp.local.",
        port=80,
        properties={
            "api_enabled": "1",
            "path": "/api/v1/data",
            "product_name": "P1 Meter",
            "product_type": "HWE-P1",
            "serial": argv[3]
        },
        addresses=[ip.packed],
        server=hostname
    )

    zeroconf = Zeroconf()
    logging.info("[Zeroconf] Registering mDNS service")
    zeroconf.register_service(info)
    logging.info("[Zeroconf] Registered mDNS service")

def build_response(data):
    importT1 = float(data[4]["state"])
    importT2 = float(data[5]["state"])
    exportT1 = float(data[6]["state"])
    exportT2 = float(data[7]["state"])
    energyConsumption = float(data[1]["state"]) * 1000
    energyProduction = float(data[2]["state"]) * 1000
    energyConsumptionL1 = float(data[8]["state"]) * 1000
    energyProductionL1 = float(data[9]["state"]) * 1000
    activeCurrent = float(data[14]["state"])
    timestamp = int(datetime.fromisoformat(data[0]["state"]).strftime("%y%m%d%H%M%S"))
    voltageSagCount = data[12]["state"]
    voltageSwellCount = data[13]["state"]

    return {
        "wifi_ssid": wifi_ssid,
        "wifi_strength": wifi_strength,
        "smr_version": smr_version,
        "meter_model": meter_model,
        "unique_id": unique_id,
        "active_tariff": 2 if data[3]["state"] == "normal" else 1,
        "total_power_import_kwh": round(importT1 + importT2, 3),
        "total_power_import_t1_kwh": importT1,
        "total_power_import_t2_kwh": importT2,
        "total_power_export_kwh": round(exportT1 + exportT2, 3),
        "total_power_export_t1_kwh": exportT1,
        "total_power_export_t2_kwh": exportT2,
        "active_power_w": -energyProduction if energyProduction > 0 else energyConsumption,
        "active_power_l1_w": -energyProductionL1 if energyProductionL1 > 0 else energyConsumptionL1,
        "active_current_a": activeCurrent,
        "active_current_l1_a": activeCurrent,
        "voltage_sag_l1_count": 0 if voltageSagCount == "unknown" else float(voltageSagCount),
        "voltage_swell_l1_count": 0 if voltageSwellCount == "unknown" else float(voltageSwellCount),
        "any_power_fail_count": float(data[10]["state"]),
        "long_power_fail_count": float(data[11]["state"]),
        "total_gas_m3": float(data[15]["state"]),
        "gas_timestamp": timestamp,
        "gas_unique_id": gas_unique_id,
        "external": [
            {
                "unique_id": gas_unique_id,
                "type": "gas_meter",
                "timestamp": timestamp,
                "value": float(data[15]["state"]),
                "unit": "m3"
            }]
    }

class RequestHandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        pass
    
    def do_PUT(self):
        try:
            if self.path == '/api/v1/identify' or self.path == '/api/v1/identify/':
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()

                self.wfile.write(json.dumps({"identify": "ok"}).encode('utf-8'))
            else:
                self.send_response(404)
                self.send_header('Content-type', 'text/html')
                self.end_headers()

                self.wfile.write("Nothing matches the given URI".encode('utf-8'))
        except Exception as e:
            self.send_response(503)
            self.end_headers()
            print(str(e))
    def do_GET(self):
        global cached_data, cache_refresh_time, cache_interval
        
        try:
            if self.path == '/api' or self.path == '/api/':
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({"product_name": product_name, "product_type": product_type, "serial": argv[3], "firmware_version": firmware_version, "api_version": api_version}).encode('utf-8'))
            elif self.path == '/api/v1/system' or self.path == '/api/v1/system/':
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({"cloud_enabled": False}).encode('utf-8'))
            elif self.path == '/refresh-data':
                try:
                    resp = requests.post(url=url, headers=headers, json=payload, verify=not disable_ssl_checks)
                    data = resp.json()

                    cached_data = build_response(data)
                    cache_refresh_time = time.time()

                    self.send_response(200)
                    self.send_header('Content-type', 'application/json')
                    self.end_headers()
                    self.wfile.write(json.dumps({"update": "ok"}).encode('utf-8'))
                except Exception as e:
                    logging.error(f"Failed to refresh cache: {e}")
                    self.send_response(503)
            elif self.path == '/api/v1/data' or self.path == '/api/v1/data/':
                if cached_data is None or cache_refresh_time is None:
                    logging.warning("Requested data while cache is empty")
                    self.send_response(503)
                    self.end_headers()
                else:
                    seconds_since_last_update = time.time() - cache_refresh_time

                    if seconds_since_last_update >= cache_interval:
                        # The actual HomeWizard P1 Meter returns the last known data when it fails to
                        # retrieve new data, e.g. when the cable between the device and the smart meter
                        # gets disconnected. This can happen when using the HomeWizard P1 Splitter.
                        # When the connection between the P1 Splitter and the smart meter is interrupted,
                        # the HomeWizard P1 Meter remains powered on, but will return outdated data.
                        # As it can potentially be dangerous to use outdated data, this emulator returns
                        # internal server error instead so that consumers will get an error.
                        logging.warning("Cache is stale")
                        self.send_response(503)
                        self.end_headers()
                    else:
                        self.send_response(200)
                        self.send_header('Content-type', 'application/json')
                        self.end_headers()
                        self.wfile.write(json.dumps(cached_data).encode('utf-8'))
            else:
                self.send_response(404)
                self.send_header('Content-type', 'text/html')
                self.end_headers()

                self.wfile.write("Nothing matches the given URI".encode('utf-8'))
        except Exception as e:
            self.send_response(503)
            self.end_headers()
            print(str(e))

def run(server_class=HTTPServer, handler_class=RequestHandler):
    logging.basicConfig(level=logging.INFO)

    advertise_service()

    server_address = ('', 80)
    httpd = server_class(server_address, handler_class)
    logging.info('Starting httpd...\n')
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    httpd.server_close()
    logging.info('Stopping httpd...\n')

if __name__ == '__main__':
    run()