#! /usr/bin/env python

import sys
import getopt
import os
import serial
import struct
from math import log

def usage(utyp, *msg):
    sys.stderr.write('Usage: %s\n' % os.path.split(sys.argv[0])[1])
    if msg:
        sys.stderr.write('Error: %s\n' % (repr(msg),))
    sys.exit(1)

def query(read_at = None):
    if read_at is None:
        b = bytearray(13)
        b[0] = 0xaa
        b[1] = 0x22
    else:
        b = bytearray(13)
        b[0] = 0xaa
        b[1] = 0x20
        b[2] = read_at & 0xff
        b[3] = 0x10 + ((read_at >> 8) & 0xff)
        b[4] = 0x08
    return bytes(b)

def bhex(b):
    s = bytes(b).hex()
    return ' ' .join(s[i:i+2] for i in range(0,len(s),2))

class Global:
    wl_decode0 = {
        0x00: 850,
        0x01: 1300,
        0x02: 1310,
        0x03: 1490,
        0x04: 1550,
        0x05: 1625,
        }
    cw_decode0 = {
        0x00: 'CW',
        0x01: '270Hz',
        0x02: '1kHz',
        0x03: '2kHz',
        }
                     
    def wl_decode(self,x):
        r = self.wl_decode0.get(x)
        if not r:
            r = '?? <%d>' % (x,)
        else:
            r = '%d nm' % (r,)
        return r

    def cw_decode(self,x):
        r = self.cw_decode0.get(x)
        if not r:
            r = '?? <%d>' % (x,)
        return r

    def __init__(self):
        self.vflag = 0
        return

    def send(self,q):
        self.s.write(q)
        return

    def receive(self):
        d = self.s.read(13)
        return d

    def doit(self,args):
        fout = sys.stdout
        
        port = args.pop(0)
        self.s = serial.Serial(port=port,baudrate=9600)

        q1 = query()
        self.send(q1)
        d = self.receive()

        n_entries = struct.unpack('<H',d[5:7])[0]

        fout.write('%s    %5d entries\n' % (bhex(d),n_entries))
        
        for i in range(n_entries):
            q1 = query(read_at = i*0x10)
            self.send(q1)
            d1 = self.receive()
            q1 = query(read_at = i*0x10+0x08)
            self.send(q1)
            d2 = self.receive()
            d = d1[5:]+d2[5:]
            x1,x2 = struct.unpack('<ff',d[0:8])
            x1 = log(x1,10)*10
            x2 = log(x2,10)*10
            x1b = x1-x2
            # x2 = 15.5*x2-9.87
            fout.write('%4d %s    %s  %4d  %9s %7.2f %7.2f %7.2f %s\n' %
                           (i,bhex(q1[:5]),bhex(d),
                            i+1,self.wl_decode(d[9]),
                            x1,x1b,x2,self.cw_decode(d[10])))
            fout.flush()

        return

def main(argv):
    gp = Global()
    try:
        opts, args = getopt.getopt(argv[1:],
                                   'hv',
                                   ['help',
                                    'verbose',
                                    ])
    except getopt.error as msg:
        usage(1, msg)

    for opt, arg in opts:
        if opt in ('-h', '--help'):
            usage(0)
        elif opt in ('-v', '--verbose'):
            gp.vflag += 1

    gp.doit(args)
        
if __name__ == '__main__':
    main(sys.argv)
