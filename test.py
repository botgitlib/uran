#!/usr/bin/python3

a = dict()

a['wlan0'] = dict()

a['wlan0']['google.com'] = 'true'
a['wlan0']['ya.ru'] = 'false'

a['eth0'] = dict()

a['eth0']['google.com'] = '1'
a['eth0']['ya.ru'] = '0'

for i in a:
  print(i," --- ",a[i])
