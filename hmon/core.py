# -*- coding: utf-8 -*-
import os
import platform
import re
import subprocess
import logging
from pathlib import Path
from typing import Dict, Optional
from smoothlogging import SmoothLogging

# Initialize logging
SCRIPT_NAME = os.path.basename(__file__)
LOG_DIR = os.getenv('LOG_DIR', '/tmp')
smooth = SmoothLogging()
log = smooth.get_logger(LOG_DIR, SCRIPT_NAME, level=logging.INFO)

# Configuration
HOSTS_FILE = os.getenv('HOSTS_FILE', '/etc/hosts')
PING_TIMEOUT = int(os.getenv('PING_TIMEOUT', '1'))

# IP regex pattern - validates 1-3 digits per octet
IP_PATTERN = re.compile(r'^(\d{1,3})\.(\d{1,3})\.(\d{1,3})\.(\d{1,3})')

# Platform-specific ping configuration
PLATFORM = platform.system()
if PLATFORM == "Windows":
    PING_CMD = ["ping", "-n", "1", "-l", "1", "-w", str(PING_TIMEOUT * 1000)]
    log.info(f"Platform: Windows, Ping timeout: {PING_TIMEOUT}s")
elif PLATFORM == "Linux":
    PING_CMD = ["ping", "-c", "1", "-W", str(PING_TIMEOUT), "-w", str(PING_TIMEOUT)]
    log.info(f"Platform: Linux, Ping timeout: {PING_TIMEOUT}s")
elif PLATFORM == "Darwin":
    PING_CMD = ["ping", "-c", "1", "-W", str(PING_TIMEOUT * 1000)]
    log.info(f"Platform: macOS, Ping timeout: {PING_TIMEOUT}s")
else:
    log.error(f"Unsupported platform: {PLATFORM}")
    raise ValueError(f"Unsupported platform: {PLATFORM}")

# Validate hosts file exists
if not Path(HOSTS_FILE).exists():
    log.warning(f"Hosts file not found: {HOSTS_FILE}")


def _validate_ip(ip: str) -> bool:
    """Validate IP address format (1-255.1-255.1-255.1-255)"""
    # Must be exactly 4 octets separated by dots
    parts = ip.split('.')
    if len(parts) != 4:
        return False

    try:
        octets = [int(x) for x in parts]
        return all(0 <= octet <= 255 for octet in octets)
    except ValueError:
        return False


def read_hosts(file: str) -> Dict[str, str]:
    """Read hosts file and parse IP-hostname mappings.

    Args:
        file: Path to hosts file

    Returns:
        Dictionary mapping IP addresses to hostnames

    Raises:
        FileNotFoundError: If hosts file doesn't exist
    """
    hosts_dict = {}

    if not Path(file).exists():
        log.error(f"Hosts file not found: {file}")
        raise FileNotFoundError(f"Hosts file not found: {file}")

    try:
        with open(file, 'r') as f:
            for line in f:
                line = line.strip()
                # Skip comments and empty lines
                if not line or line.startswith('#'):
                    continue

                # Skip localhost entries
                if '127.0.' in line or '::1' in line:
                    continue

                # Parse IP and hostname
                match = IP_PATTERN.search(line)
                if match:
                    ip = match.group(0)
                    if _validate_ip(ip):
                        # Get hostname (first non-IP token after IP)
                        parts = line.split()
                        if len(parts) >= 2:
                            hostname = parts[1]
                            hosts_dict[ip] = hostname
    except IOError as e:
        log.error(f"Error reading hosts file {file}: {e}")
        raise

    log.info(f"Loaded {len(hosts_dict)} hosts from {file}")
    return hosts_dict


def ping_return_code(ip: str, hosts_dict: Dict[str, str]) -> int:
    """Check if host is reachable via ping.

    Args:
        ip: IP address to ping
        hosts_dict: Dictionary mapping IPs to hostnames

    Returns:
        0 if reachable, 1 if not
    """
    if not _validate_ip(ip):
        log.error(f"Invalid IP address: {ip}")
        return 1

    hostname = hosts_dict.get(ip, ip)

    try:
        ping = subprocess.Popen(
            PING_CMD + [ip],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        out, error = ping.communicate(timeout=PING_TIMEOUT + 2)

        # Check for success - different patterns for different platforms
        if re.search(r'1\s+received|1\s+packets\s+received|bytes=|time=', out):
            log.info(f"Ping successful: {ip} ({hostname})")
            return 0
        else:
            log.warning(f"Ping failed: {ip} ({hostname})")
            return 1
    except subprocess.TimeoutExpired:
        log.warning(f"Ping timeout: {ip} ({hostname})")
        return 1
    except FileNotFoundError:
        log.error("Ping command not found")
        return 1
    except Exception as e:
        log.error(f"Error pinging {ip}: {e}")
        return 1


def write_metric_line(hostname: str, status: int) -> str:
    """Format a Prometheus metric line.

    Args:
        hostname: Hostname label value
        status: 1 (up) or 0 (down)

    Returns:
        Formatted metric line for Prometheus
    """
    # Escape quotes in hostname for Prometheus format
    safe_hostname = hostname.replace('"', '\\"')
    return f'node_network_hosts_up{{hostname="{safe_hostname}"}} {status}'


def arp_return_code(ip: str, hosts_dict: Dict[str, str]) -> int:
    """Check if host is in ARP table.

    Args:
        ip: IP address to check in ARP
        hosts_dict: Dictionary mapping IPs to hostnames

    Returns:
        0 if found in ARP table, 1 if not
    """
    if not _validate_ip(ip):
        log.error(f"Invalid IP address: {ip}")
        return 1

    hostname = hosts_dict.get(ip, ip)
    arp_cmd = os.getenv('ARP_CMD', '/usr/sbin/arp')

    # Check if arp command exists
    if not Path(arp_cmd).exists():
        log.warning(f"ARP command not found: {arp_cmd}")
        return 1

    try:
        arp = subprocess.Popen(
            [arp_cmd, "-a", str(ip)],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        out, error = arp.communicate(timeout=5)

        if re.search(r'<incomplete>|not found', out):
            log.warning(f"ARP incomplete: {ip} ({hostname})")
            return 1
        else:
            log.info(f"ARP successful: {ip} ({hostname})")
            return 0
    except subprocess.TimeoutExpired:
        log.warning(f"ARP timeout: {ip} ({hostname})")
        return 1
    except FileNotFoundError:
        log.warning(f"ARP command not found: {arp_cmd}")
        return 1
    except Exception as e:
        log.error(f"Error checking ARP for {ip}: {e}")
        return 1
