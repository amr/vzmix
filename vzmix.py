#!/usr/bin/env python
#
# vzmix - generate container configuration files based on existing ones.
#
# Copyright (C) 2009 Amr Mostafa <amr.mostafa@egyptdc.com>
# Copyright (c) 2009 EgyptDC (http://egyptdc.com)
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

# Represents a User Beancounter
# See: http://wiki.openvz.org/UBC
class UBC:
    name = None
    barrier = None
    limit = None

    # Maximum number that can be represented by an 8-byte integer
    # This is the largest number that OpenVZ can accept AFAIK
    cap = 9223372036854775807

    def __init__(self, name=None, barrier=None, limit=None):
        self.name = name
        self.barrier = int(barrier)
        if limit is not None:
            self.limit = int(limit)
        
    def __str__(self):
        if self.limit is not None:
            return '%s="%d:%d"' % (self.name, self.barrier, self.limit)
        else:
            return '%s="%d"' % (self.name, self.barrier)

    def ensureCap(self, value):
        if value > self.cap:
            return self.cap
        return value

    def __mul__(self, factor):
        self.barrier = self.ensureCap(int(self.barrier * factor))
        if self.limit is not None:
            self.limit = self.ensureCap(int(self.limit * factor))

    def __add__(self, other):
        self.barrier = self.ensureCap(self.barrier + other.barrier)
        if self.limit is not None and other.limit is not None:
            self.limit = self.ensureCap(self.limit + other.limit)
        return self

    def __sub__(self, other):
        self.barrier = self.ensureCap(self.barrier - other.barrier)
        if self.limit is not None and other.limit is not None:
            self.limit = self.ensureCap(self.limit - other.limit)
        return self


# Represents a Container Configuration file
class CTConfig:
    # Internal storage of UBCs and other file contents
    data = []

    # Initializes CTConfig from a given optional file
    def __init__(self, filename=None):
        if filename is not None:
            self.fromFile(filename)

    # Populates CTConfig from given container configuration file
    def fromFile(self, filename):
        f = open(filename, 'r')
        lines = f.readlines();
        f.close()

        return self.fromLines(lines)

    # Populates CTConfig from given container configuration lines
    def fromLines(self, lines):
        self.data = [self.parseLine(line) for line in lines]

    def parseLine(self, line):
        line = line.strip()
        if self.isEmpty(line) or self.isComment(line):
            return line
        else:
            parts = line.strip().replace('"', "").split("=")
            name, value = parts[0], parts[1]
            if not name or not value:
                raise ValueError("Can not parse line: %s" % line);

            name = name.strip()

            parts = value.split(":")
            barrier = parts[0]
            if len(parts) > 1:
                limit = parts[1]
            else:
                limit = None

            return UBC(name=name, barrier=barrier, limit=limit)

    def isEmpty(self, s):
        return len(s) == 0

    def isComment(self, s):
        return s.startswith("#")

    def toString(self):
        for line in self.data:
            print line

    def getUBC(self, name):
        for ubc in self.data:
            if isinstance(ubc, UBC):
                if ubc.name == name:
                    return ubc

    def __mul__(self, factor):
        for ubc in self.data:
            if isinstance(ubc, UBC):
                ubc *= factor
        return self

    def __add__(self, other):
        for oubc in other.data:
            if isinstance(oubc, UBC):
                ubc = self.getUBC(oubc.name)
                if ubc is not None:
                    ubc += oubc
        return self

    def __sub__(self, other):
        for oubc in other.data:
            if isinstance(oubc, UBC):
                ubc = self.getUBC(oubc.name)
                if ubc is not None:
                    ubc -= oubc
        return self


def main():
    from optparse import OptionParser

    cli = OptionParser(usage="%prog [options] <base-file>",
                       description="Generate OpenVZ container configuration files based on an existing file")
    cli.add_option("-m", "--multiply", dest="multiply", type="float", metavar="FACTOR",
                      help="multiply by given factor")
    cli.add_option("-a", "--add", dest="add", type="string", action="append", metavar="FILE",
                      help="add (as in sum) given file, you can add as many files as you need by specifying this option multiple times")
    cli.add_option("-s", "--substract", dest="substract", type="string", action="append", metavar="FILE",
                      help="substract given file, you can add as many files as you need by specifying this option multiple times")
    cli.add_option("-d", "--debug", dest="debug", action="store_true",
                      help="do not catch python exceptions, useful for debugging")
    (options, args) = cli.parse_args();

    if not len(args):
        cli.error("No base file provided")

    try:
        # Require Python >= 2.4
        import sys
        if sys.version_info[0] < 2 or sys.version_info[1] < 4:
            cli.error("Python 2.4.0 or higher is required")

        c = CTConfig(args[0])

        # Multiply
        if options.multiply:
            if options.multiply <= 0:
                cli.error("Invalid multiplication factor %s" % str(options.multiply))
        
            c *= options.multiply

        # Addition
        if options.add is not None:
            for f in options.add:
                c += CTConfig(f)

        # Substract
        if options.substract is not None:
            for f in options.substract:
                c -= CTConfig(f)

        c.toString()
    except Exception, e:
        if options.debug:
            raise

        else:
            cli.print_usage()
            cli.exit(2, "%s: %s\n" % (cli.get_prog_name(), e))

if __name__ == "__main__":
    main()
