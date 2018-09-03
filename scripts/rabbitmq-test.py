#!/usr/bin/env python
#
# Copyright 2017, Rackspace US, Inc.
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
#
# (c) 2017, Jean-Philippe Evrard <jean-philippe.evrard@rackspace.co.uk>
#
"""Tests rabbitmq with our hardcoded test credentials"""

import argparse
import sys
try:
    import pika
except Exception:
    sys.exit("Can't import pika")


def rabbitmq_connect(ip=None):
    """Connects to ip using standard port and credentials."""
    credentials = pika.credentials.PlainCredentials('testguest', 'secrete')
    parameters = pika.ConnectionParameters(
        host=ip, virtual_host='/testvhost', credentials=credentials)
    try:
        connection = pika.BlockingConnection(parameters)
        connection.channel()
    except Exception:
        sys.exit("Can't connect to %s" % ip)
    else:
        print("Connected.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("ip", help="The IP to connect to")
    args = parser.parse_args()
    rabbitmq_connect(args.ip)
