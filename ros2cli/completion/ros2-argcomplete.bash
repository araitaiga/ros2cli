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

if type register-python-argcomplete3 > /dev/null 2>&1; then
  eval "$(register-python-argcomplete3 ros2)"
elif type register-python-argcomplete > /dev/null 2>&1; then
  eval "$(register-python-argcomplete ros2)"
fi

# Add -o nosort to preserve the completion order set by argcomplete
# (options first, then other completions like file names)
# This requires bash 4.4 or later
if [[ "${BASH_VERSINFO[0]}" -ge 5 ]] || [[ "${BASH_VERSINFO[0]}" -eq 4 && "${BASH_VERSINFO[1]}" -ge 4 ]]; then
  complete -o nosort -o nospace -o default -o bashdefault -F _python_argcomplete ros2
fi
