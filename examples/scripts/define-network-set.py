#!/usr/bin/env python3
###
# (C) Copyright 2014 Hewlett-Packard Development Company, L.P.
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
###
import sys
if sys.version_info < (3, 2):
    raise Exception('Must use Python 3.2 or later')

import hpOneView as hpov
from pprint import pprint


def acceptEULA(con):
    # See if we need to accept the EULA before we try to log in
    con.get_eula_status()
    try:
        if con.get_eula_status() is True:
            print('EULA display needed')
            con.set_eula('no')
    except Exception as e:
        print('EXCEPTION:')
        print(e)


def login(con, credential):
    # Login with givin credentials
    try:
        con.login(credential)
    except:
        print('Login failed')


def addnetset(net, name, networks, minbw, maxbw):

    nset = []
    pprint(networks)
    sys.exit()

    maxbw = int(maxbw * 1000)
    minbw = int(minbw * 1000)
    bandDict = hpov.common.make_bw_dict(maxbw, minbw)

    print('Creating Network Set: ', name)
    if networks:
        enets = net.get_enet_networks()
        for enet in enets:
            if enet['name'] in networks:
                print('  Adding Network: ', enet['name'])
                nset.append(enet['uri'])

    nset = net.create_networkset(name, nets=nset, bw=bandDict)
    pprint(nset)


def main():
    parser = argparse.ArgumentParser(add_help=True, description='Usage')
    parser.add_argument('-a', '--appliance', dest='host', required=True,
                        help='HP OneView Appliance hostname or IP')
    parser.add_argument('-u', '--user', dest='user', required=False,
                        default='Administrator', help='HP OneView Username')
    parser.add_argument('-p', '--pass', dest='passwd', required=False,
                        help='HP OneView Password')
    parser.add_argument('-c', '--certificate', dest='cert', required=False,
                        help='Trusted SSL Certificate Bundle in PEM '
                        '(Base64 Encoded DER) Format')
    parser.add_argument('-r', '--proxy', dest='proxy', required=False,
                        help='Proxy (host:port format')
    parser.add_argument('-n', dest='network_set_name', required=True,
                        help='Name of the network set')
    parser.add_argument('-t', dest='list_of_networks', required=False,
                        nargs='+', help='List of network names to add to the '
                        'network set, seperated by spaces. I.E. -t "Net One" '
                        '"Net Two" "Net Three"')
    parser.add_argument('-b', dest='prefered_bandwidth', type=float,
                        required=False, default=2.5, help='Typical '
                        'bandwidth between .1  and 20 Gb/s')
    parser.add_argument('-m', dest='max_bandwidth', type=float, required=False,
                        default=10, help='Maximum bandwidth between .1 and '
                        '20 Gb/s')

    args = parser.parse_args()
    credential = {'userName': args.user, 'password': args.passwd}

    con = hpov.connection(args.host)
    net = hpov.networking(con)

    if args.proxy:
        con.set_proxy(args.proxy.split(':')[0], args.proxy.split(':')[1])
    if args.cert:
        con.set_trusted_ssl_bundle(args.cert)

    login(con, credential)
    acceptEULA(con)

    if args.prefered_bandwidth < .1 or args.prefered_bandwidth > 20:
        print('Error, prefered bandwidth must be between .1 and 20 Gb/s')
        sys.exit()
    if args.max_bandwidth < .1 or args.max_bandwidth > 20:
        print('Error, max bandwidth must be between .1 and 20 Gb/s')
        sys.exit()
    if args.prefered_bandwidth > args.max_bandwidth:
        print('Error, prefered bandwidth must be less than or equal '
              'to the maximum bandwidth')
        sys.exit()

    addnetset(net, args.network_set_name, args.list_of_networks,
              args.prefered_bandwidth, args.max_bandwidth)

if __name__ == '__main__':
    import sys
    import argparse
    sys.exit(main())

# vim:set shiftwidth=4 tabstop=4 expandtab textwidth=79:
