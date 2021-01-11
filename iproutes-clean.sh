#!/bin/bash

:			# пустая команда
while [ $? -eq 0 ]	# $? - результат выполнения предыдущей команды
do
    ip rule del from all fwmark 2 lookup rtc 2> /dev/null
done

:			# пустая команда
while [ $? -eq 0 ]	# $? - результат выполнения предыдущей команды
do
    ip rule del from all fwmark 3 lookup beeline 2> /dev/null
done

:			# пустая команда
while [ $? -eq 0 ]	# $? - результат выполнения предыдущей команды
do
    ip rule del from all fwmark 3 lookup rtc 2> /dev/null
done

:			# пустая команда
while [ $? -eq 0 ]	# $? - результат выполнения предыдущей команды
do
    ip rule del from all fwmark 2 lookup beeline 2> /dev/null
done

:			# пустая команда
while [ $? -eq 0 ]	# $? - результат выполнения предыдущей команды
do
    ip rule del from all fwmark 102 lookup rtc_icmp 2> /dev/null
done

:			# пустая команда
while [ $? -eq 0 ]	# $? - результат выполнения предыдущей команды
do
    ip rule del from all fwmark 103 lookup beeline_icmp 2> /dev/null
done

ip route del default via 82.151.118.65 dev rtc table rtc
ip route del default via 81.211.51.5 dev beeline table beeline

# Удаление записей об использованных таблицах маршрутизации в файле rt_tables
sed -i '/2\trtc/d' /etc/iproute2/rt_tables
sed -i '/3\tbeeline/d' /etc/iproute2/rt_tables
sed -i '/102\trtc_icmp/d' /etc/iproute2/rt_tables
sed -i '/103\tbeeline_icmp/d' /etc/iproute2/rt_tables
