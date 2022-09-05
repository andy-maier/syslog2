# Copyright 2022 Andreas Maier. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
Utility functions of the syslog2 package.
"""

import inspect


def _stacklevel_above_syslog2():
    """
    Return the stack level (with 1 = caller of this function) of the first
    caller that is not defined in the _syslog2 module and that is not
    a method of a class named 'NocaseDict' (case insensitively). The second
    check skips user classes derived from syslog2.NocaseDict.

    The returned stack level can be used directly by the caller of this
    function as an argument for the stacklevel parameter of warnings.warn().
    """
    stacklevel = 2  # start with caller of our caller
    frame = inspect.stack()[stacklevel][0]  # stack() level is 0-based
    while True:
        if frame.f_globals.get('__name__', None) != '_syslog2':
            try:
                class_name = frame.f_locals['self'].__class__.__name__.lower()
            except KeyError:
                class_name = None
            if class_name != 'syslog2':
                break
        stacklevel += 1
        frame = frame.f_back
    del frame
    return stacklevel
