#!/usr/bin/python3

import subprocess

ip_route = subprocess.run(['ip route show'], shell=True, \
  stdout=subprocess.PIPE).stdout.decode('utf-8').rstrip("\n")
print(ip_route)
