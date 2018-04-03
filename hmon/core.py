# -*- coding: utf-8 -*-
import os
import platform
import re
import subprocess
from smoothlogging import smoothlogging

script_name = os.path.basename(__file__)
log_obj = smoothlogging()

rexip = re.compile('^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}')

plat = platform.system()
if plat == "Windows":
    log = log_obj.log("c:/temp/", script_name)
    log.info("platform: Windows")
    pingArgs = ["ping", "-n", "1", "-l", "1", "-w", "100"]
elif plat == "Linux":
    log = log_obj.log("/tmp/", script_name)
    log.info("platform: Linux")
    pingArgs = ["ping", "-c", "1", "-W", "1", "-w", "1"]

else:
    raise ValueError("Unknown platform")


def read_hosts(file):
    """Read hosts file"""
    dict = {}
    f = open(file, 'r')
    for line in f.readlines():
        if re.match(rexip, line):
            ip = re.findall(rexip, line)
            if '127.0.' not in line:
                search_hostname = re.search('(?P<ip>^\d{1,3}\S+)\s+(?P<hostname>\S+).*', line)
                ip = search_hostname.group('ip')
                hostname = search_hostname.group('hostname')
                dict[ip] = hostname
    return dict


hosts = read_hosts("/etc/hosts")


def ping_return_code(ip):
    try:
        hostname = hosts[ip]
    except:
        hostname = ip
        log.warning("cannot figure out hostname for: %s" % ip)

    ping = subprocess.Popen(pingArgs + [ip],
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE)
    out, error = ping.communicate()
    result = [out, error]

    code = 1
    if re.search('1\sreceived,\s0.\spacket\sloss', out):
        code = 0
        log.info("Ping success for IP: %s, hostname: %s. Code: %s" % (ip, hostname, code))
    else:
        code = 1
        log.warn("Ping not-success for IP: %s, hostname: %s. Code: %s " % (ip, hostname, code))
    return code


def arp_return_code(ip):
    try:
        hostname = hosts[ip]
    except:
        hostname = ip
        log.warning("cannot figure out hostname for: %s" % ip)

    arp = subprocess.Popen(["/usr/sbin/arp", "-a", str(ip)],
                           stdout=subprocess.PIPE,
                           stderr=subprocess.PIPE)

    out, error = arp.communicate()
    result = [out, error]
    code = 1
    if re.search('<incomplete>', out):
        code = 1
        log.warn(
            "ARP resulted in incomplete ARP table entry for IP: %s, hostname: %s. Code: %s" % (ip, hostname, code))
    else:
        code = 0
        log.info("ARP call -> success for IP: %s, hostname: %s. Code: %s " % (ip, hostname, code))
    return code
