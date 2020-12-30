#!/usr/bin/python3

import subprocess
from threading import Thread

def pingsite(site="8.8.8.8", interface=None):
  if interface == None:
    interface = ""
  else:
    interface = " -I " + interface   
  status,result = subprocess.getstatusoutput("ping " + site + \
    interface + " -c 10 -i 0.5 -W 5 -q 2>/dev/null")
  print(result)

sites = ["8.8.8.8","google.com","ya.ru"]

threads = []

for i in range(len(sites)):
  threads.insert(i, Thread(target=pingsite, args=(sites[i],)))

for i in range(len(sites)):
  threads[i].start()

for i in range(len(sites)):
  threads[i].join()
