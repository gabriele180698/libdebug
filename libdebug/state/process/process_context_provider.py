#
# This file is part of libdebug Python library (https://github.com/io-no/libdebug).
# Copyright (c) 2024 Roberto Alessandro Bertolini
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, version 3.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
#

from libdebug.state.process.gdb_process_context import GdbProcessContext
from libdebug.state.process.ptrace_process_context import PtraceProcessContext
from libdebug.interfaces.debugging_interface import DebuggingInterface
from libdebug.interfaces.gdb_interface import GdbInterface
from libdebug.interfaces.ptrace_interface import PtraceInterface


def provide_process_context(interface: DebuggingInterface, argv: list = None):
    """Provides a process context object.

    Args:
        process_id (int): The process' ID.
        interface (DebuggingInterface): The debugging interface object.

    Returns:
        ProcessContext: The process context object.
    """
    if isinstance(interface, PtraceInterface):
        process_id = interface.process_id
        return PtraceProcessContext(process_id, interface, argv)
    elif isinstance(interface, GdbInterface):
        # TODO: implement getGdbProcessContext
        return GdbProcessContext(interface, argv)
    else:
        raise Exception("Unsupported debugging interface")