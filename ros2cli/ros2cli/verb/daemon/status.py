# Copyright 2017 Open Source Robotics Foundation, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import socket

from ros2cli.node.daemon import DaemonNode
from ros2cli.node.daemon import is_daemon_running
from ros2cli.verb.daemon import VerbExtension


class StatusVerb(VerbExtension):
    """Output the status of the daemon."""

    def add_arguments(self, parser, cli_name):
        parser.add_argument(
            '--verbose', '-v', action='store_true',
            help='Show detailed network and cache information')

    def main(self, *, args):
        if not is_daemon_running(args):
            print('The daemon is not running')
            return

        print('The daemon is running')

        if args.verbose:
            # Get detailed information from daemon
            with DaemonNode(args) as node:
                if not node.connected:
                    return

                # Get daemon information
                try:
                    daemon_info = node.get_daemon_info()
                    print('\nDaemon Information:')
                    self._print_daemon_info(daemon_info)
                except (ConnectionError, TimeoutError, OSError) as e:
                    print(f'\nFailed to get daemon information: {e}')

                # Get network interfaces
                try:
                    network_info = node.get_network_interfaces()
                    print('\nNetwork Interfaces:')
                    self._print_network_interfaces(network_info)
                except (ConnectionError, TimeoutError, OSError) as e:
                    print(f'\nFailed to get network interfaces: {e}')

                # Get cache information
                try:
                    cache_info = node.get_cache_info()
                    print('\nCached ROS Graph Information:')
                    self._print_cache_info(cache_info)
                except (ConnectionError, TimeoutError, OSError) as e:
                    print(f'\nFailed to get cache information: {e}')

    def _print_daemon_info(self, daemon_info):
        """Print daemon process information in a readable format."""
        if not daemon_info:
            print('  No daemon information available')
            return

        print(f'  XML-RPC URL: {daemon_info.get("xmlrpc_url", "N/A")}')
        print(f'  ROS Domain ID: {daemon_info.get("ros_domain_id", "N/A")}')

    def _print_network_interfaces(self, network_info):
        """Print network interface information in a readable format."""
        if not network_info:
            print('  No network interfaces found')
            return

        # Address family constants
        AF_INET = socket.AF_INET
        AF_INET6 = socket.AF_INET6

        for iface_name, addrs in sorted(network_info.items()):
            ipv4_addrs = []
            ipv6_addrs = []

            for addr in addrs:
                family = addr['family']
                address = addr['address']

                if family == AF_INET:
                    ipv4_addrs.append(address)
                elif family == AF_INET6:
                    ipv6_addrs.append(address)

            if ipv4_addrs or ipv6_addrs:
                print(f'  {iface_name}:')
                if ipv4_addrs:
                    for addr in ipv4_addrs:
                        print(f'    IPv4: {addr}')
                if ipv6_addrs:
                    for addr in ipv6_addrs:
                        print(f'    IPv6: {addr}')

    def _print_cache_info(self, cache_info):
        """Print cached ROS graph information in a readable format."""
        if not cache_info:
            print('  No cache information available')
            return

        if 'error' in cache_info:
            print(f'  Error: {cache_info["error"]}')
            return

        # Print summary counts
        print(f'  Nodes: {cache_info["nodes"]["count"]}')
        print(f'  Topics: {cache_info["topics"]["count"]}')
        print(f'  Services: {cache_info["services"]["count"]}')
        print(f'  Actions: {cache_info["actions"]["count"]}')

        # Print detailed lists
        if cache_info["nodes"]["count"] > 0:
            print('\n  Node List:')
            for node in cache_info["nodes"]["list"]:
                print(f'    - {node}')

        if cache_info["topics"]["count"] > 0:
            print('\n  Topic List:')
            for topic in cache_info["topics"]["list"]:
                print(f'    - {topic}')

        if cache_info["services"]["count"] > 0:
            print('\n  Service List:')
            for service in cache_info["services"]["list"]:
                print(f'    - {service}')

        if cache_info["actions"]["count"] > 0:
            print('\n  Action List:')
            for action in cache_info["actions"]["list"]:
                print(f'    - {action}')
