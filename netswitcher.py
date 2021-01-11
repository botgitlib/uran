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
        #packets_transmitted = \
        #    int( ping_result_packets[0].replace("packets transmitted","").strip() )
        #packets_received = \
        #    int( ping_result_packets[1].replace("received","").strip() )
        packets_loss = \
            float( ping_result_packets[2].replace("packet loss","").replace("%","").strip() )
        #packets_time = \
        #    int( ping_result_packets[3].replace("time","").replace("ms","").strip() )
        #rtt_min = float( ping_result_rtt[0] )
        rtt_avg = float( ping_result_rtt[1] )
        #rtt_max = float( ping_result_rtt[2] )
        #rtt_mdev = float( ping_result_rtt[3] )
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
# Сайты, доступность к которым будет проверена
sites = ["8.8.8.8", "google.com", "ya.ru"]
# Сетевые интерфейсы, через которые будет проводится проверка
interfaces = ["rtc", "beeline"]
# Словарь, в который будут записаны результаты проверки
interfaces_results = dict()
# Адреса шлюзов провайдеров
rtc_gateway_ip = "82.151.118.65"
beeline_gateway_ip = "81.211.51.5"
# Путь к файлу для записи итоговых результатов проверки
logfile_path = "/var/log/netswitcher/history.log"

logfile = open(logfile_path, "a")
now =  datetime.datetime.now().strftime("%Y.%m.%d %H:%M:%S %z")
logfile.write("\nStart: " + now + "\n")

error = ""

ip_route = subprocess.run(['ip route show'], shell=True, \
  stdout=subprocess.PIPE).stdout.decode('utf-8').rstrip("\n")

# Проверка наличия линков по таблице маршрутизации main
if ( ip_route.find("default via") == -1 ):
    ip_link_rtc = subprocess.run(['ip link show rtc'], shell=True, \
        stdout=subprocess.PIPE).stdout.decode('utf-8').rstrip("\n")
    if ( ip_link_rtc.find("state UP") != -1 ):
        subprocess.run(["sudo ip route add default via " + rtc_gateway_ip + " dev rtc"], \
            shell=True, stdout=subprocess.PIPE)
    else:
        ip_link_beeline = subprocess.run(['ip link show beeline'], shell=True, \
            stdout=subprocess.PIPE).stdout.decode('utf-8').rstrip("\n")
        if ( ip_link_beeline.find("state UP") != -1 ):
            subprocess.run(["sudo ip route add default via " + beeline_gateway_ip + " dev beeline"], \
                shell=True, stdout=subprocess.PIPE)
        else:
            error = "Error: All link are DOWN"
# Удаление лишних маршрутов по умолчанию из таблицы main
#   при наличии нескольких маршрутов по умолчанию
if ( ip_route.find("default via " + beeline_gateway_ip + " dev beeline") != -1 ) \
    and ( ip_route.find("default via " + rtc_gateway_ip + " dev rtc") != -1 ):
    subprocess.run(["sudo ip route del default via " + beeline_gateway_ip + " dev beeline"], \
        shell=True, stdout=subprocess.PIPE)

if error == "":
    pingnets()
    now = datetime.datetime.now().strftime("%Y.%m.%d %H:%M:%S %z")
    logfile.write("Stop: " + now + "\n")
    logfile.write("Results:")
    for interface in interfaces:
        interface_result = \
            " " + interface + "=" + str( interfaces_results[interface]["result"] )
        print( interface_result.strip() )
        logfile.write(interface_result)
    logfile.write("\n")
# Переключение маршрутов в зависимости от результатов
    rtc_status = interfaces_results["rtc"]["result"]
    beeline_status = interfaces_results["beeline"]["result"]

    ip_rule = subprocess.run(['ip rule show'], shell=True, \
        stdout=subprocess.PIPE).stdout.decode('utf-8').rstrip("\n")

    if ( rtc_status == True ) and ( beeline_status == False ) and \
        ( ip_rule.find("from all fwmark 0x3 lookup beeline") != -1 ):
        subprocess.run(["sudo ip rule del from all fwmark 0x3 lookup beeline"], \
            shell=True, stdout=subprocess.PIPE)
        subprocess.run(["sudo ip rule add from all fwmark 0x3 lookup rtc"], \
            shell=True, stdout=subprocess.PIPE)

    if ( rtc_status == False ) and ( beeline_status == True ) and \
        ( ip_rule.find("from all fwmark 0x2 lookup rtc") != -1 ):
        subprocess.run(["sudo ip rule del from all fwmark 0x2 lookup rtc"], \
            shell=True, stdout=subprocess.PIPE)
        subprocess.run(["sudo ip rule add from all fwmark 0x2 lookup beeline"], \
            shell=True, stdout=subprocess.PIPE)

    if ( rtc_status == True ) and ( beeline_status == True ) and \
        ( ip_rule.find("from all fwmark 0x2 lookup beeline") != -1 ) and \
        ( ip_rule.find("from all fwmark 0x3 lookup beeline") != -1 ):
        subprocess.run(["sudo ip rule del from all fwmark 0x2 lookup beeline"], \
            shell=True, stdout=subprocess.PIPE)
        subprocess.run(["sudo ip rule add from all fwmark 0x2 lookup rtc"], \
            shell=True, stdout=subprocess.PIPE)  
    if ( rtc_status == True ) and ( beeline_status == True ) and \
        ( ip_rule.find("from all fwmark 0x2 lookup rtc") != -1 ) and \
        ( ip_rule.find("from all fwmark 0x3 lookup rtc") != -1 ):
        subprocess.run(["sudo ip rule del from all fwmark 0x3 lookup rtc"], \
            shell=True, stdout=subprocess.PIPE)
        subprocess.run(["sudo ip rule add from all fwmark 0x3 lookup beeline"], \
            shell=True, stdout=subprocess.PIPE)

    ip_route = subprocess.run(['ip route show'], shell=True, \
        stdout=subprocess.PIPE).stdout.decode('utf-8').rstrip("\n")

    if ( ip_rule.find("from all fwmark 0x2 lookup rtc") == -1 ) and \
        ( ip_rule.find("from all fwmark 0x3 lookup beeline") == -1 ) and \
        ( ip_route.find("default via " + beeline_gateway_ip + " dev beeline") == -1 ) and \
        ( rtc_status == False ) and ( beeline_status == True ):
        subprocess.run("sudo ip route change default via " + beeline_gateway_ip + " dev beeline", \
            shell=True, stdout=subprocess.PIPE)
    if ( ip_rule.find("from all fwmark 0x2 lookup rtc") == -1 ) and \
        ( ip_rule.find("from all fwmark 0x3 lookup beeline") == -1 ) and \
        ( ip_route.find("default via " + rtc_gateway_ip + " dev beeline") == -1 ) and \
        ( rtc_status == True ) and ( beeline_status == False ):
        subprocess.run("sudo ip route change default via " + rtc_gateway_ip + " dev rtc", \
            shell=True, stdout=subprocess.PIPE)
else:
    now = datetime.datetime.now().strftime("%Y.%m.%d %H:%M:%S %z")
    logfile.write("Stop: " + now + "\n")
    logfile.write("Result: " + error)

logfile.close()
