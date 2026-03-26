#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Hosts monitoring utility - checks hosts via ping/arp and exports Prometheus metrics.
"""
import argparse
import os
import logging
import sys
from pathlib import Path
from typing import Dict, Optional

from hmon.core import read_hosts, ping_return_code, arp_return_code, write_metric_line, log

# Configuration from environment variables
HOSTS_FILE = os.getenv('HOSTS_FILE', '/etc/hosts')
OUTPUT_DIR = os.getenv('OUTPUT_DIR', '/var/lib/node_exporter/textfile_collector')
OUTPUT_FILE_BASE = os.getenv('OUTPUT_FILE_BASE', 'node_network_hosts_up.prom')
LOG_DIR = os.getenv('LOG_DIR', '/tmp')

# Construct paths
OUTPUT_FILE_TMP = os.path.join(OUTPUT_DIR, f"{OUTPUT_FILE_BASE}.tmp")
OUTPUT_FILE_FINAL = os.path.join(OUTPUT_DIR, OUTPUT_FILE_BASE)


def validate_config() -> bool:
    """Validate configuration before running.

    Returns:
        True if valid, False otherwise
    """
    errors = []

    # Check hosts file
    if not Path(HOSTS_FILE).exists():
        errors.append(f"Hosts file not found: {HOSTS_FILE}")

    # Check output directory
    if not Path(OUTPUT_DIR).exists():
        errors.append(f"Output directory doesn't exist: {OUTPUT_DIR}")

    if not Path(OUTPUT_DIR).is_dir():
        errors.append(f"Output path is not a directory: {OUTPUT_DIR}")

    # Check write permissions
    if not os.access(OUTPUT_DIR, os.W_OK):
        errors.append(f"No write permission for: {OUTPUT_DIR}")

    if errors:
        for error in errors:
            log.error(error)
        return False

    return True


def main() -> int:
    """Main entry point."""
    # Parse command-line arguments
    parser = argparse.ArgumentParser(
        description="Monitor LAN hosts via ping/arp, export Prometheus metrics"
    )
    parser.add_argument(
        '-hostname',
        dest='hostname',
        help='Monitor specific hostname only',
        required=False
    )
    args = parser.parse_args()

    log.info("Starting hosts monitoring")
    log.info(f"Hosts file: {HOSTS_FILE}")
    log.info(f"Output directory: {OUTPUT_DIR}")

    # Validate configuration
    if not validate_config():
        log.error("Configuration validation failed")
        return 1

    # Load hosts
    try:
        hosts_dict = read_hosts(HOSTS_FILE)
    except FileNotFoundError as e:
        log.error(f"Failed to read hosts: {e}")
        return 1

    if not hosts_dict:
        log.error("No hosts found in hosts file")
        return 1

    # Filter to single host if specified
    if args.hostname:
        if args.hostname not in hosts_dict:
            log.error(f"Hostname not found in hosts file: {args.hostname}")
            return 1
        hosts_dict = {args.hostname: hosts_dict[args.hostname]}
        log.info(f"Monitoring single host: {args.hostname}")

    # Check host reachability
    metrics = []
    for ip, hostname in hosts_dict.items():
        try:
            # Try ping first
            if ping_return_code(ip, hosts_dict) == 0:
                status = 1
            else:
                # Fall back to ARP if ping fails
                if arp_return_code(ip, hosts_dict) == 0:
                    status = 1
                else:
                    status = 0

            metric_line = write_metric_line(hostname, status)
            metrics.append(metric_line)
            log.debug(f"Generated metric for {hostname}: {status}")

        except Exception as e:
            log.error(f"Error checking host {hostname}: {e}")
            # Still write metric (as down) to avoid gaps in data
            metric_line = write_metric_line(hostname, 0)
            metrics.append(metric_line)

    # Write metrics to temporary file
    try:
        with open(OUTPUT_FILE_TMP, 'w') as f:
            for line in metrics:
                f.write(line + '\n')
        log.info(f"Wrote {len(metrics)} metrics to {OUTPUT_FILE_TMP}")
    except IOError as e:
        log.error(f"Failed to write metrics: {e}")
        return 1

    # Atomically move temp file to final location
    try:
        os.replace(OUTPUT_FILE_TMP, OUTPUT_FILE_FINAL)
        log.info(f"Metrics published: {OUTPUT_FILE_FINAL}")
    except OSError as e:
        log.error(f"Failed to publish metrics: {e}")
        return 1

    log.info("Hosts monitoring completed successfully")
    return 0


if __name__ == '__main__':
    sys.exit(main())
