#!/bin/bash

for i in /proc/sys/net/ipv4/conf/*/rp_filter
do
    echo 1 > $i
done

iptables -t mangle -F
iptables -t nat -F
iptables -t filter -F

iptables -t filter -P INPUT ACCEPT
iptables -t filter -P FORWARD DROP
iptables -t filter -P OUTPUT ACCEPT
