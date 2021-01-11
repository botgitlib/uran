#!/bin/bash

##### Отключение проверки обратного адреса (Reverse Path Filtering) #####
for i in /proc/sys/net/ipv4/conf/*/rp_filter
do
    echo 0 > $i
done

##### Очистка таблиц и установка политик по умолчанию #####
iptables -t mangle -F
iptables -t nat -F
iptables -t filter -F

iptables -t filter -P INPUT ACCEPT
iptables -t filter -P FORWARD DROP
iptables -t filter -P OUTPUT ACCEPT

##### Маркировка пакетов и соединений #####

# Маркировка новых соединений
#   от провайдера Ростелеком маркером 2
#   от провайдера Билайн маркером 3
# -- маркировка новых входящих соединений из Интернета:
iptables -t mangle -A PREROUTING -i rtc -m conntrack --ctstate NEW -j CONNMARK --set-mark 2
iptables -t mangle -A PREROUTING -i beeline -m conntrack --ctstate NEW -j CONNMARK --set-mark 3
# -- маркировка новых исходящих TCP и UDP соединений от виртуальных сетевых интерфесов:
iptables -t mangle -A OUTPUT -o rtc -p tcp,udp -m conntrack --ctstate NEW -j CONNMARK --set-mark 2
iptables -t mangle -A OUTPUT -o beeline -p tcp,udp -m conntrack --ctstate NEW -j CONNMARK --set-mark 3

# Маркировка новых исходящих соединений по протоколу ICMP для тестирования сети
#   от провайдера Ростелеком маркером 102
#   от провайдера Билайн маркером 103
iptables -t mangle -A OUTPUT -o rtc -p icmp -m conntrack --ctstate NEW -j CONNMARK --set-mark 102
iptables -t mangle -A OUTPUT -o beeline -p icmp -m conntrack --ctstate NEW -j CONNMARK --set-mark 103

# Восстановление маркировки в исходящих пакетах
iptables -t mangle -A OUTPUT -m connmark ! --mark 0 -j CONNMARK --restore-mark

# Маркировка пакетов по другим условиям (пример)
iptables -t mangle -A OUTPUT -d eth0.me -j MARK --set-mark=2
iptables -t mangle -A OUTPUT -d ipecho.me -j MARK --set-mark=3

# Изменение адреса источника в зависимости от того, через какого провайдера идет отправка пакета
iptables -t nat -A POSTROUTING -o rtc -j MASQUERADE
iptables -t nat -A POSTROUTING -o beeline -j MASQUERADE
