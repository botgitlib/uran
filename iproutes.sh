#!/bin/bash

# Добавление таблиц маршрутизации в файл /etc/iproute2/rt_table
# "2	rtc"		- для маршрутизации через Ростелеком
# "3	beeline"	- для маршрутизации через Билайн
# "102	rtc_icmp"	- для маршрутизации ICMP-пакетов через Ростелеком
# "103	beeline_icmp"	- для маршрутизации ICMP-пакетов через Билайн

echo -e "2\trtc" >> /etc/iproute2/rt_tables
echo -e "3\tbeeline" >> /etc/iproute2/rt_tables
echo -e "102\trtc_icmp" >> /etc/iproute2/rt_tables
echo -e "103\tbeeline_icmp" >> /etc/iproute2/rt_tables

# Добавление маршрутов по умолчанию в таблицы
# 82.151.118.65 - для Ростелекома
# 81.211.51.5   - для Билайна
ip route add default via 82.151.118.65 dev rtc table rtc 2>/dev/null
ip route add default via 81.211.51.5 dev beeline table beeline 2>/dev/null
ip route add default via 82.151.118.65 dev rtc table rtc_icmp 2>/dev/null
ip route add default via 81.211.51.5 dev beeline table beeline_icmp 2>/dev/null

# Добавление правил маршрутизации
# Пакеты с меткой 2 и 102 маршрутизируются по таблицам rtc и rtc_icmp
#   (пересылаются через Ростелеком)
# Пакеты с меткой 3 и 103 маршрутизируются по таблице beeline и beeline_icmp
#   (пересылаются через Билайн)
ip rule add fwmark 2 table rtc
ip rule add fwmark 3 table beeline
ip rule add fwmark 102 table rtc_icmp
ip rule add fwmark 103 table beeline_icmp
