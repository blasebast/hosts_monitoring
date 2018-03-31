from hmon.core import *

file="/var/lib/node_exporter/textfile_collector/node_network_hosts_up.prom"
hosts="/etc/hosts"
open(file, 'w').close()
prom = open(file,'w')
hosts=read_hosts(hosts)

for ip, hostname in hosts.items():
    if ping_return_code(ip) == 0:
        line = "node_network_hosts_up{hostname=\"%s\"} %s" % (hostname, "1")
    else:
        if arp_return_code(ip) == 0:
            line = "node_network_hosts_up{hostname=\"%s\"} %s" % (hostname, "1")
        else:
            line = "node_network_hosts_up{hostname=\"%s\"} %s" % (hostname, "0")
    log.info("Writing: \"%s\" into: %s" % (line,file))
    prom.write(line+"\n")
prom.close()


