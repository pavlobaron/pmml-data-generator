#
# This file is part of pmml-data-generator
#
# Copyright (c) 2013 by Pavlo Baron (pb at pbit dot org)
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

from lxml.etree import iterparse
from argparse import ArgumentParser
import random
import sys

def rand_categorical(rec):
    if len(rec['values']) > 0:
        return rec['values'][random.randint(0, len(rec['values']) - 1)]

    return None

def rand_continuous(rec):
    return random.randint(0, sys.maxint)

def write_records(outf, a):
    curr = 0
    for rec in a:
        if curr > 0:
            outf.write(';')

        fun = 'rand_%s' % rec['op'] 
        if globals().has_key(fun):
            res = globals()[fun](rec)
            if res:
                outf.write(str(res))
            else:
                outf.write('n/a')
        else:
            outf.write('n/a')

        curr += 1

def collect_meta(inf, outf):
    a = []
    curr = 0
    i = iterparse(inf, events=('start', 'end'))
    for what, elem in i:
        if elem.tag.endswith('DataField'):
            if what == 'start':
                if curr > 0:
                    outf.write(';')

                outf.write(elem.get('name'))
                a.append({'values': [],
                          'type': elem.get('dataType'),
                          'op': elem.get('optype')})
                for c in elem.getchildren():
                    if c.tag.endswith('Value'):
                        a[curr]['values'].append(c.get('value'))
            elif what == 'end':
                curr += 1
        if what == "end" and elem.tag.endswith('DataDictionary'):
            break

    return a

def run_it(infile, outfile, n):
    inf = open(infile, 'r')
    outf = open(outfile, 'w')
    a = collect_meta(inf, outf)
    inf.close()
    for i in xrange(n + 1):
        outf.write('\n')
        write_records(outf, a)

    outf.close()

if __name__ == '__main__':
    parser = ArgumentParser(description='PMML data generator')
    parser.add_argument('-i', metavar='<input file>', default=None,
                        type=str, dest='infile', help='input PMML file', required=True)
    parser.add_argument('-o', metavar='<output file>', default=None,
                        type=str, dest='outfile', help='output XML file', required=True)
    parser.add_argument('-n', metavar='<records number>', default=100,
                        type=int, dest='n', help='how many random records to generate',
                        required=False)
    parser.add_argument('-f', metavar='<output format>', default='csv',
                        type=str, dest='format', help='output format (only csv yet supported)',
                        required=False)
    parser.add_argument('-v', '--version', action='version',
                        version='0.1', help="prints the current program version")

    args = parser.parse_args()
    run_it(args.infile, args.outfile, args.n)
