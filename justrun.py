from hmon.core import *
import argparse
import os

parser = argparse.ArgumentParser(description="arguments")
parser.add_argument('-hostname', dest='hostname', help='provide hostname if you want to examine only one', nargs='?',
                    required=False)
args = parser.parse_args()

newfile = "/var/lib/node_exporter/textfile_collector/node_network_hosts_up.prom.tmp"
oldfile = "/var/lib/node_exporter/textfile_collector/node_network_hosts_up.prom"

hosts = "/etc/hosts"
prom = open(newfile, 'w')
hosts = read_hosts(hosts)

if args.hostname is not None:
    host = args.hostname
    hosts = {host: host}
    print(type(hosts))
    print(hosts[host])

for ip, hostname in hosts.items():
    if ping_return_code(ip) == 0:
        line = "node_network_hosts_up{hostname=\"%s\"} %s" % (hostname, "1")
    else:
        if arp_return_code(ip) == 0:
            line = "node_network_hosts_up{hostname=\"%s\"} %s" % (hostname, "1")
        else:
            line = "node_network_hosts_up{hostname=\"%s\"} %s" % (hostname, "0")
    log.info("Writing: \"%s\" into: %s" % (line, newfile))
    prom.write(line + "\n")
prom.close()
try:
    os.rename(newfile, oldfile)
    log.info("renamed: %s -> %s" % (newfile,oldfile))
except Exception as e:
    log.error("could not rename: %s -> %s" % (newfile,oldfile))
    log.error("exception content: %s" % (e))


