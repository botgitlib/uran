#!/usr/bin/python3

import subprocess
from threading import Thread
import datetime

################################################################################
#                          Проверка доступности сайта                          #
################################################################################
def pingsite(interface=None,site="8.8.8.8"):
  if interface == None:
    interface_option = ""
  else:
    interface_option = " -I " + interface
  connect_result_good = True
  connect_result_bad = False
  status,ping_result = subprocess.getstatusoutput("ping " + site + \
    interface_option + " -c 10 -i 0.5 -W 5 -q 2>/dev/null")
  if status != 0:
    connect_result = connect_result_bad
  else:
    ping_result = ping_result.split("\n")
    ping_result_packets = ping_result[3].split(",")
    ping_result_rtt = ping_result[4].split(" ")[3].split("/")
    packets_transmitted = \
      int( ping_result_packets[0].replace("packets transmitted","").strip() )
    packets_received = \
      int( ping_result_packets[1].replace("received","").strip() )
    packets_loss = \
      float( ping_result_packets[2].replace("packet loss","").replace("%","").strip() )
    packets_time = \
      int( ping_result_packets[3].replace("time","").replace("ms","").strip() )
    rtt_min = float( ping_result_rtt[0] )
    rtt_avg = float( ping_result_rtt[1] )
    rtt_max = float( ping_result_rtt[2] )
    rtt_mdev = float( ping_result_rtt[3] )
    if (packets_loss < 35) and (rtt_avg < 100.0):
      connect_result = connect_result_good
    else:
      connect_result = connect_result_bad
  interfaces_results[interface][site] = connect_result

################################################################################
#                          Проверка доступности сетей                          #
################################################################################
def pingnets():

  threads = dict()

  for interface in interfaces:
    threads[interface] = dict()
    interfaces_results[interface] = dict()
    for site in sites:
      threads[interface][site] = Thread(target=pingsite, args=(interface,site))
  for interface in interfaces:
    for site in sites:
      threads[interface][site].start()
  for interface in interfaces:
    for site in sites:
      threads[interface][site].join()

  for interface in interfaces:
    for site in sites:
      if interfaces_results[interface][site] == True:
        interfaces_results[interface]["result"] = True
        break
    else:
      interfaces_results[interface]["result"] = False

################################################################################
#                              Основная программа                              #
################################################################################
sites = ["8.8.8.8", "google.com", "ya.ru"]
interfaces = ["wlan0", "eth0"]
interfaces_results = dict()

#logfile = "/var/log/netswitcher/history.log"
logfile = open("history.log", "a")
now =  datetime.datetime.now().strftime("%Y.%m.%d %H:%M:%S %z")
logfile.write("\nStart: " + now + "\n")

rtc_gateway_ip = "82.151.118.65"
beeline_gateway_ip = "81.211.51.5"

error = False

if not error:
  pingnets()
  now =  datetime.datetime.now().strftime("%Y.%m.%d %H:%M:%S %z")
  logfile.write("Stop: " + now + "\n")
  logfile.write("Results:")
  for interface in interfaces:
    interface_result = \
      " " + interface + "=" + str( interfaces_results[interface]["result"] )
    print( interface_result )
    logfile.write(interface_result)
  logfile.write("\n")

logfile.close()
