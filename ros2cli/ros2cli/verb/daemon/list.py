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

import psutil

from ros2cli.verb.daemon import VerbExtension


def find_daemon_processes():
    """
    Find all running ros2 daemon processes.

    :return: List of dictionaries containing daemon process information.
    """
    daemon_processes = []

    for proc in psutil.process_iter(['pid', 'name', 'cmdline', 'create_time']):
        try:
            cmdline = proc.info.get('cmdline', [])
            if not cmdline:
                continue

            # Check if this is a ros2 daemon process
            # daemon processes are started with: python -c "from ros2cli.daemon.daemonize import main; main()"
            # and contain --ros-domain-id and --rmw-implementation arguments
            ros_domain_id = None
            rmw_implementation = None

            # Look for daemon-specific command line arguments
            cmdline_str = ' '.join(cmdline)
            if 'daemonize' in cmdline_str:
                # Parse command line arguments
                for i, arg in enumerate(cmdline):
                    if arg == '--ros-domain-id' and i + 1 < len(cmdline):
                        try:
                            ros_domain_id = int(cmdline[i + 1])
                        except (ValueError, IndexError):
                            continue
                    elif arg == '--rmw-implementation' and i + 1 < len(cmdline):
                        rmw_implementation = cmdline[i + 1]

            # Only add if we found both required arguments
            if ros_domain_id is not None and rmw_implementation is not None:
                # Calculate port number: base_port (11511) + ROS_DOMAIN_ID
                port = 11511 + ros_domain_id

                try:
                    status = proc.status()
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    status = 'unknown'

                daemon_info = {
                    'pid': proc.info['pid'],
                    'ros_domain_id': ros_domain_id,
                    'rmw_implementation': rmw_implementation,
                    'port': port,
                    'create_time': proc.info.get('create_time', 0),
                    'status': status
                }
                daemon_processes.append(daemon_info)
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            # Process may have terminated or we don't have permission
            continue

    return daemon_processes


class ListVerb(VerbExtension):
    """List all running ros2 daemon processes."""

    def add_arguments(self, parser, cli_name):
        parser.add_argument(
            '--verbose', '-v', action='store_true',
            help='Show detailed information about each daemon')
        parser.add_argument(
            '--format', choices=['table', 'json'], default='table',
            help='Output format (default: table)')

    def main(self, *, args):
        daemon_processes = find_daemon_processes()

        if not daemon_processes:
            print('No ros2 daemon processes are running.')
            return 0

        if args.format == 'json':
            import json
            print(json.dumps(daemon_processes, indent=2))
            return 0

        # Table format
        if args.verbose:
            print(f'Found {len(daemon_processes)} ros2 daemon process(es):\n')
            print(f'{"PID":<8} {"ROS_DOMAIN_ID":<12} {"RMW":<20} {"PORT":<8} {"STATUS":<10}')
            print('-' * 70)
            for daemon in sorted(daemon_processes, key=lambda x: x['ros_domain_id']):
                print(f"{daemon['pid']:<8} "
                      f"{daemon['ros_domain_id']:<12} "
                      f"{daemon['rmw_implementation']:<20} "
                      f"{daemon['port']:<8} "
                      f"{daemon['status']:<10}")
        else:
            print(f'Found {len(daemon_processes)} ros2 daemon process(es):')
            for daemon in sorted(daemon_processes, key=lambda x: x['ros_domain_id']):
                print(f"  PID {daemon['pid']}: "
                      f"ROS_DOMAIN_ID={daemon['ros_domain_id']}, "
                      f"RMW={daemon['rmw_implementation']}, "
                      f"PORT={daemon['port']}")

        return 0
