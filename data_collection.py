#macOS 13.5.1
#before running the code you should allow location services for Python and VSCode 
#due to Apple's limitation for retrieving BSSID

#the code is referenced from github page below
#https://github.com/pkruk/osx-wifi-scanner/blob/master/wifi-scan.py
import objc
from datetime import datetime
import time
import csv
import socket
import subprocess
import re
import sys

def get_local_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))  # Connect to a public DNS server
    local_ip = s.getsockname()[0]
    s.close()
    return local_ip

def ping_host(host = "cse.unsw.edu.au",count = 10):
    command = f"ping -c {count} {host}"
    result = subprocess.run(command, shell=True, capture_output=True, text=True)

    return result.stdout

def get_wifi_standard(i):

    if i.supportsPHYMode_(0):
        return "Unknown"
    elif i.supportsPHYMode_(1):
        return "802.11a"
    elif i.supportsPHYMode_(2):
        return "802.11b"
    elif i.supportsPHYMode_(3):
        return "802.11g"
    elif i.supportsPHYMode_(4):
        return "802.11n"
    elif i.supportsPHYMode_(5):
        return "802.11ac"
    elif i.supportsPHYMode_(6):
        return "802.11ax"
    else:
        return "Unsupported"
    
def get_connected_bssid():
    connected_wifi = subprocess.check_output("sudo /System/Library/PrivateFrameworks/Apple80211.framework/Versions/Current/Resources/airport -I", shell=True, text=True)
    print(connected_wifi)
    match = re.search(r'(([0-9A-Fa-f]?[0-9A-Fa-f][:-]){5}[0-9A-Fa-f][0-9A-Fa-f]?)', connected_wifi)
    
    if match:
        BSSID = match.group()  # Access the first capturing group
        #sometimes hexadecimal number between semicolons are single character, in this case we should put 0 before the character.
        if(len(BSSID) < 17):
            b_list = BSSID.split(":")
            #print(b_list)
            for i in range(len(b_list)):
                    if(len(b_list[i]) < 2):
                        b_list[i]="0"+b_list[i]
            BSSID = ':'.join(b_list)
        print(BSSID)
        return BSSID
    else:
        print("BSSID not found")
        return None

def scan(concrete_ssid=None):
    bundle_path = '/System/Library/Frameworks/CoreWLAN.framework'
    objc.loadBundle('CoreWLAN',
                    bundle_path=bundle_path,
                    module_globals=globals())

    iface = CWInterface.interface()
    networks = iface.scanForNetworksWithName_includeHidden_error_(concrete_ssid, True, None)

    os="MACOS"
    network_interface="AirPort"
    local_ip = get_local_ip()
    current_time = datetime.now().strftime("%A, %d %B %Y %H:%M:%S")
    timestamp = int(time.time())
    print(timestamp)
    #sys.exit()
    row_t = [timestamp]
    row_data = []
    row_data.append(row_t)
    connected_SSID = iface.ssid()
    connected_BSSID = get_connected_bssid()
    #sys.exit()
    ap_count = len(networks[0].allObjects())
    strings = f"""
    Current time: {current_time}
    Timestamp: {timestamp}
    WiFi status: Connected ({connected_SSID})
    There are {ap_count} APs visible:\n\n"""
    output = ping_host()
    # Use regular expression to find the average time
    match = re.search(r'(\d+\.\d+)/(\d+\.\d+)', output)
    delay = "timeout"
    avg_time = ""
    if match:
        min_time, avg_time = map(float, match.groups())
        print(f"The average time is: {avg_time} ms")
        delay = avg_time

    print(strings)

    print("         SSID         |      BSSID      | Frequency | Channel | RSSI | channel")
    print("                      |                 |   (GHz)   |         | (dBm)|  width ")
    print("----------------------+-----------------+-----------+---------+------+-----------")
    x=False
    rows = []
    for i in networks[0].allObjects():
        temp_local_ip = local_ip
        #average time for ping(network delay)
        if(avg_time != ""):
            delay = avg_time
        else:
            delay = "timeout"
        ssid=""
        if(i.ssid() != None):
            ssid = i.ssid()
        bssid = i.bssid()
        if(str(bssid) != connected_BSSID):
            temp_local_ip = ""
            delay = ""
        else:
            x=True
        if(bssid == None):
            continue
        
        frequency=""
        channel=i.wlanChannel().channelNumber()
        rssi=i.rssiValue()
        channel_width=""
        protocol = get_wifi_standard(i)
        noise = i.noiseMeasurement()
        
        if(i.wlanChannel().channelWidth() == 1):
            channel_width = "20"
        elif(i.wlanChannel().channelWidth() == 2):
            channel_width = "40"
        elif(i.wlanChannel().channelWidth() == 3):
            channel_width = "80"
        elif(i.wlanChannel().channelWidth() == 4):
            channel_width = "160"
        else:
            channel_width = i.wlanChannel().channelWidth()

        if(rssi <= -60):
            frequency = 5
        else:
            frequency = 2.4
        
        print(f"{ssid[:22]:22}|{bssid:12}|{frequency:7}    |{channel:6}   |{rssi:5} | {channel_width:12} | {protocol} | {noise} | {temp_local_ip} | {delay}")
        print("----------------------+-----------------+-----------+---------+------+-----------")

        print(delay)
        row = [timestamp, os, network_interface, "","","", ssid, bssid, protocol, frequency, channel, channel_width, rssi, noise, temp_local_ip, delay]
        rows.append(row)
    export_timestamp_to_csv('timestamp.csv', row_data)
    
    if(x):
        print("yesss!!")
    return rows

def export_to_csv(filename, data):
    with open(filename, mode='a', newline='') as file:
        writer = csv.writer(file)
        #writer.writerow(['time', 'os', 'network interface', 'gps latitude', 'gps longitude', 'gps accuracy (meters)', 'ssid', 'bssid', 'wi-fi standard', 'frequency', 'network channel', 'channel width (in mhz)', 'rssi (in dbm)', 'noise level (in dbm)', 'public ip address', 'network delay (in ms)'])
        writer.writerows(data)
    
def export_timestamp_to_csv(filename, data):
    with open(filename, mode='a', newline='') as file:
        writer = csv.writer(file)
        #writer.writerow(['time', 'os', 'network interface', 'gps latitude', 'gps longitude', 'gps accuracy (meters)', 'ssid', 'bssid', 'wi-fi standard', 'frequency', 'network channel', 'channel width (in mhz)', 'rssi (in dbm)', 'noise level (in dbm)', 'public ip address', 'network delay (in ms)'])
        writer.writerows(data)

def main():
    data = scan()
    
    export_to_csv('wifi_data_ts.csv', data)

if __name__ == "__main__":
    main()