# -*- coding: utf-8 -*-
"""Comprehensive test suite for hosts_monitoring."""

import unittest
import tempfile
import os
from pathlib import Path

from hmon.core import read_hosts, _validate_ip, write_metric_line, ping_return_code, arp_return_code


class TestIPValidation(unittest.TestCase):
    """Test IP address validation."""

    def test_valid_ips(self):
        """Test valid IP addresses."""
        valid_ips = [
            "192.168.1.1",
            "10.0.0.1",
            "172.16.0.1",
            "0.0.0.0",
            "255.255.255.255",
            "127.0.0.1",
        ]
        for ip in valid_ips:
            self.assertTrue(_validate_ip(ip), f"IP {ip} should be valid")

    def test_invalid_ips(self):
        """Test invalid IP addresses."""
        invalid_ips = [
            "256.1.1.1",  # Octet > 255
            "1.1.1",  # Missing octet
            "1.1.1.1.1",  # Too many octets
            "abc.def.ghi.jkl",  # Non-numeric
            "1.1.1.a",  # Mixed
            "",  # Empty
        ]
        for ip in invalid_ips:
            self.assertFalse(_validate_ip(ip), f"IP {ip} should be invalid")


class TestHostsFileParsing(unittest.TestCase):
    """Test hosts file parsing."""

    def setUp(self):
        """Create temporary hosts file."""
        self.temp_dir = tempfile.mkdtemp()
        self.hosts_file = os.path.join(self.temp_dir, 'hosts')

    def tearDown(self):
        """Clean up temporary files."""
        if os.path.exists(self.hosts_file):
            os.remove(self.hosts_file)
        os.rmdir(self.temp_dir)

    def test_read_valid_hosts(self):
        """Test reading valid hosts entries."""
        with open(self.hosts_file, 'w') as f:
            f.write("""# Comment line
127.0.0.1 localhost
192.168.1.1 router.local
10.0.0.5 server.local
::1 localhost  # IPv6

# Another comment
172.16.0.1 host1
172.16.0.2 host2
""")
        hosts = read_hosts(self.hosts_file)

        # Should skip localhost entries
        self.assertNotIn("127.0.0.1", hosts)
        self.assertNotIn("::1", hosts)

        # Should include valid entries
        self.assertEqual(hosts.get("192.168.1.1"), "router.local")
        self.assertEqual(hosts.get("10.0.0.5"), "server.local")
        self.assertEqual(hosts.get("172.16.0.1"), "host1")
        self.assertEqual(hosts.get("172.16.0.2"), "host2")

    def test_read_empty_file(self):
        """Test reading empty hosts file."""
        with open(self.hosts_file, 'w') as f:
            f.write("")
        hosts = read_hosts(self.hosts_file)
        self.assertEqual(len(hosts), 0)

    def test_read_comments_only(self):
        """Test reading file with only comments."""
        with open(self.hosts_file, 'w') as f:
            f.write("# Comment 1\n# Comment 2\n")
        hosts = read_hosts(self.hosts_file)
        self.assertEqual(len(hosts), 0)

    def test_file_not_found(self):
        """Test reading non-existent file."""
        with self.assertRaises(FileNotFoundError):
            read_hosts("/nonexistent/path/hosts")


class TestMetricFormatting(unittest.TestCase):
    """Test Prometheus metric formatting."""

    def test_metric_format_simple(self):
        """Test simple metric formatting."""
        metric = write_metric_line("myhost", 1)
        self.assertEqual(metric, 'node_network_hosts_up{hostname="myhost"} 1')

    def test_metric_format_down(self):
        """Test down metric formatting."""
        metric = write_metric_line("myhost", 0)
        self.assertEqual(metric, 'node_network_hosts_up{hostname="myhost"} 0')

    def test_metric_format_with_quotes(self):
        """Test metric with hostname containing quotes."""
        metric = write_metric_line('host"with"quotes', 1)
        # Should escape quotes
        self.assertIn('\\"', metric)

    def test_metric_format_with_domain(self):
        """Test metric with FQDN hostname."""
        metric = write_metric_line("myhost.example.com", 1)
        self.assertEqual(
            metric,
            'node_network_hosts_up{hostname="myhost.example.com"} 1'
        )


class TestPingReturnCode(unittest.TestCase):
    """Test ping reachability check."""

    def test_ping_invalid_ip(self):
        """Test ping with invalid IP."""
        result = ping_return_code("invalid.ip", {})
        self.assertEqual(result, 1)

    def test_ping_with_hostname_lookup(self):
        """Test ping with hostname lookup."""
        hosts_dict = {"192.168.1.1": "router"}
        # This will fail because router doesn't exist, but should not crash
        result = ping_return_code("192.168.1.1", hosts_dict)
        self.assertIn(result, [0, 1])


class TestARPReturnCode(unittest.TestCase):
    """Test ARP table check."""

    def test_arp_invalid_ip(self):
        """Test ARP with invalid IP."""
        result = arp_return_code("invalid.ip", {})
        self.assertEqual(result, 1)

    def test_arp_with_hostname_lookup(self):
        """Test ARP with hostname lookup."""
        hosts_dict = {"192.168.1.1": "router"}
        # This will likely fail on most systems, but should not crash
        result = arp_return_code("192.168.1.1", hosts_dict)
        self.assertIn(result, [0, 1])


if __name__ == '__main__':
    unittest.main()
