#
# This file is part of libdebug Python library (https://github.com/io-no/libdebug).
# Copyright (c) 2024 Roberto Alessandro Bertolini, Gabriele Digregorio.
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

import time
import unittest

from libdebug import debugger


class NonWaitingTest(unittest.TestCase):
    def test_bps_non_waiting(self):
        d = debugger("binaries/breakpoint_test")

        d.run()

        bp1 = d.breakpoint("random_function")
        bp2 = d.breakpoint(0x40115B)
        bp3 = d.breakpoint(0x40116D)

        counter = 1

        d.cont()

        while True:
            if d.rip == bp1.address:
                self.assertTrue(bp1.hit_count == 1)
                self.assertTrue(bp1.hit_on(d))
                self.assertFalse(bp2.hit_on(d))
                self.assertFalse(bp3.hit_on(d))
            elif d.rip == bp2.address:
                self.assertTrue(bp2.hit_count == counter)
                self.assertTrue(bp2.hit_on(d))
                self.assertFalse(bp1.hit_on(d))
                self.assertFalse(bp3.hit_on(d))
                counter += 1
            elif d.rip == bp3.address:
                self.assertTrue(bp3.hit_count == 1)
                self.assertTrue(d.rsi == 45)
                self.assertTrue(d.esi == 45)
                self.assertTrue(d.si == 45)
                self.assertTrue(d.sil == 45)
                self.assertTrue(bp3.hit_on(d))
                self.assertFalse(bp1.hit_on(d))
                self.assertFalse(bp2.hit_on(d))
                break

            d.cont()

        d.kill()

    def test_jumpout_non_waiting(self):
        flag = ""
        first = 0x55
        second = 0

        d = debugger("CTF/jumpout")

        r = d.run()

        bp1 = d.breakpoint(0x140B, hardware=True)
        bp2 = d.breakpoint(0x157C, hardware=True)

        d.cont()

        r.sendline(b"A" * 0x1D)

        while True:
            time.sleep(0.001)

            if d.rip == bp1.address:
                second = d.r9
            elif d.rip == bp2.address:
                address = d.r13 + d.rbx
                third = int.from_bytes(d.memory[address, 1], "little")
                flag += chr((first ^ second ^ third ^ (bp2.hit_count - 1)))

            d.cont()

            if flag.endswith("}"):
                break

        r.recvuntil(b"Wrong...")

        d.kill()

        self.assertEqual(flag, "SECCON{jump_table_everywhere}")

class NonWaitingNcuts(unittest.TestCase):
    def setUp(self):
        pass

    def get_passsphrase_from_class_1_binaries(self, previous_flag):
        flag = b""

        d = debugger("CTF/1")
        r = d.run()

        bp = d.breakpoint(0x7EF1, hardware=True)

        d.cont()

        r.recvuntil(b"Passphrase:\n")
        r.send(previous_flag + b"a" * 8)

        count = 0
        while count < 8:
            time.sleep(0.01)

            if d.rip == bp.address:
                offset = ord("a") ^ d.rbp
                d.rbp = d.r13
                flag += (offset ^ d.r13).to_bytes(1, "little")
                count += 1

            d.cont()

        r.recvline()

        d.kill()

        self.assertEqual(flag, b"\x00\x006\x00\x00\x00(\x00")
        return flag

    def get_passsphrase_from_class_2_binaries(self, previous_flag):
        bitmap = {}
        lastpos = 0
        flag = b""

        d = debugger("CTF/2")
        r = d.run()

        bp1 = d.breakpoint(0xD8C1, hardware=True)
        bp2 = d.breakpoint(0x1858, hardware=True)
        bp3 = d.breakpoint(0xDBA1, hardware=True)

        d.cont()

        r.recvuntil(b"Passphrase:\n")
        r.send(previous_flag + b"a" * 8)

        while True:
            time.sleep(0.01)

            if d.rip == bp1.address:
                lastpos = d.rbp
                d.rbp = d.r13 + 1
            elif d.rip == bp2.address:
                bitmap[d.r12 & 0xFF] = lastpos & 0xFF
            elif d.rip == bp3.address:
                d.rbp = d.r13
                wanted = d.rbp
                needed = 0
                for i in range(8):
                    if wanted & (2**i):
                        needed |= bitmap[2**i]
                flag += chr(needed).encode()

                if bp3.hit_count == 8:
                    d.cont()
                    break

            d.cont()

        d.kill()

        self.assertEqual(flag, b"\x00\x00\x00\x01\x00\x00a\x00")

    def get_passsphrase_from_class_3_binaries(self):
        flag = b""

        d = debugger("CTF/0")
        r = d.run()

        bp = d.breakpoint(0x91A1, hardware=True)

        d.cont()

        r.send(b"a" * 8)

        count = 0
        while count < 8:
            time.sleep(0.01)

            if d.rip == bp.address:
                offset = ord("a") - d.rbp
                d.rbp = d.r13
                flag += chr((d.r13 + offset) % 256).encode("latin-1")
                count += 1

            d.cont()

        d.cont()

        r.recvline()

        d.kill()

        self.assertEqual(flag, b"BM8\xd3\x02\x00\x00\x00")
        return flag

    def test_ncuts(self):
        flag = self.get_passsphrase_from_class_3_binaries()
        flag = self.get_passsphrase_from_class_1_binaries(flag)
        self.get_passsphrase_from_class_2_binaries(flag)