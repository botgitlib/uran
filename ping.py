#!/usr/bin/python3

import subprocess
from threading import Thread

def pingsite(site="8.8.8.8", interface=None):
  if interface == None:
    interface = ""
  else:
    interface = " -I " + interface
  connect_result_good = "true"
  connect_result_bad = "false"
  status,ping_result = subprocess.getstatusoutput("ping " + site + \
    interface + " -c 10 -i 0.5 -W 5 -q 2>/dev/null")
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
  print(connect_result)

sites = ["8.8.8.8","google.com","ya.ru","10.20.30.40"]

threads = []

for i in range(len(sites)):
  threads.insert(i, Thread(target=pingsite, args=(sites[i],)))

for i in range(len(sites)):
  threads[i].start()

for i in range(len(sites)):
  threads[i].join()
