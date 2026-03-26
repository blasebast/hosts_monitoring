===============================
Hosts Monitoring
===============================

Monitor LAN hosts via ping/ARP and export metrics to Prometheus.

Features
--------

* Monitors hosts from ``/etc/hosts`` file
* Checks reachability via ping (falls back to ARP)
* Exports Prometheus metrics for Node Exporter textfile collector
* Environment-based configuration
* Proper error handling and logging
* Cross-platform support (Linux, macOS, Windows)
* Python 3.9+ with type hints

Installation
------------

From PyPI:

.. code-block:: bash

    pip install hosts-monitoring

From source:

.. code-block:: bash

    git clone https://github.com/blasebast/hosts_monitoring
    cd hosts_monitoring
    pip install -e .

Quick Start
-----------

**Basic usage:**

.. code-block:: bash

    # Copy configuration template
    cp .env.example .env
    
    # Edit configuration
    nano .env
    
    # Run monitoring
    hosts-monitoring

**Monitor single host:**

.. code-block:: bash

    hosts-monitoring -hostname 192.168.1.1

**Docker usage:**

.. code-block:: bash

    docker-compose up -d

Configuration
-------------

Configure via environment variables in ``.env`` file:

- ``HOSTS_FILE`` - Path to hosts file (default: ``/etc/hosts``)
- ``OUTPUT_DIR`` - Output directory for metrics (default: ``/var/lib/node_exporter/textfile_collector``)
- ``OUTPUT_FILE_BASE`` - Output filename (default: ``node_network_hosts_up.prom``)
- ``PING_TIMEOUT`` - Ping timeout in seconds (default: ``1``)
- ``LOG_DIR`` - Log directory (default: ``/tmp``)
- ``ARP_CMD`` - Path to arp command (default: ``/usr/sbin/arp``)
- ``LOG_LEVEL`` - Logging level (default: ``INFO``)

Docker
------

**Using docker-compose (recommended):**

.. code-block:: bash

    docker-compose up -d

**Using Docker image directly:**

.. code-block:: bash

    docker build -t hosts-monitoring .
    docker run --rm \
      -v /etc/hosts:/etc/hosts:ro \
      -v /var/lib/node_exporter/textfile_collector:/metrics \
      -e HOSTS_FILE=/etc/hosts \
      -e OUTPUT_DIR=/metrics \
      hosts-monitoring

Integration with Prometheus
---------------------------

Add to ``prometheus.yml``:

.. code-block:: yaml

    scrape_configs:
      - job_name: 'node'
        static_configs:
          - targets: ['localhost:9100']

The ``node_network_hosts_up`` metric will be collected via Node Exporter's textfile collector.

Metrics
-------

**Metric name:** ``node_network_hosts_up``

**Labels:**
- ``hostname``: Hostname from ``/etc/hosts``

**Values:**
- ``1``: Host is reachable (ping or ARP success)
- ``0``: Host is unreachable

**Example output:**

.. code-block:: text

    node_network_hosts_up{hostname="router"} 1
    node_network_hosts_up{hostname="server"} 1
    node_network_hosts_up{hostname="offline-host"} 0

Running as Cron Job
-------------------

Add to crontab to run every minute:

.. code-block:: bash

    * * * * * /usr/local/bin/hosts-monitoring

Or with custom configuration:

.. code-block:: bash

    * * * * * source /etc/hosts-monitoring/.env && hosts-monitoring

Development
-----------

**Setup development environment:**

.. code-block:: bash

    pip install -e ".[dev]"
    pytest

**Run tests:**

.. code-block:: bash

    pytest tests/
    pytest --cov=hmon tests/

Troubleshooting
---------------

**"Output directory doesn't exist"**
- Ensure output directory exists and is writable
- Usually ``/var/lib/node_exporter/textfile_collector`` for Node Exporter

**"Hosts file not found"**
- Check ``HOSTS_FILE`` environment variable
- Default is ``/etc/hosts`` on Linux/macOS
- Windows: typically ``C:\Windows\System32\drivers\etc\hosts``

**"ARP command not found"**
- ARP checking is optional and will be skipped if unavailable
- Ping will still be used for reachability checks

**"Permission denied" writing metrics**
- Container/process needs write permissions to output directory
- In docker-compose, metrics directory is volume-mounted
- For manual setup: ``chmod 777 /var/lib/node_exporter/textfile_collector``

Performance
-----------

* Default ping timeout: 1 second (configurable via ``PING_TIMEOUT``)
* Falls back to ARP if ping fails
* Metrics written atomically (temp file + rename)
* Suitable for cron execution every 1-5 minutes

License
-------

GNU General Public License v3.0 - See LICENSE file

Contributing
------------

Contributions welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure tests pass: ``pytest``
5. Submit a pull request

Author
------

Sebastian Blasiak - https://github.com/blasebast
