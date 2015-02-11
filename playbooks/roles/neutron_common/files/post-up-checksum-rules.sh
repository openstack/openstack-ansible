#!/usr/bin/env bash
# Copyright 2014, Rackspace US, Inc.
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

# NOTICE:
#   This script is purpose built to resolve an issue within neutron
#   where packet checksums are being dropped.
#   Launchpad issue:
#     https://bugs.launchpad.net/bugs/1244589
#
#   Open review:
#     https://review.openstack.org/#/c/148718/
#
# TODO(cloudnull) remove this script once the bug is fixed.


# Iptables path, used for ipv4 firewall.
IPTABLES=$(which iptables)
if [ ! -z "${IPTABLES}" ];then
    if [ ! "$(${IPTABLES} -t mangle -nL | awk '$4 == "0.0.0.0/0" && $5 == "0.0.0.0/0" && $9 == "fill"')" ];then
        ${IPTABLES} -A POSTROUTING \
                    -t mangle \
                    -p udp \
                    --dport 68 \
                    -j CHECKSUM \
                    --checksum-fill
    fi
fi

# Ip6tables path, used for ipv6 firewall.
IP6TABLES=$(which ip6tables)
if [ ! -z "${IP6TABLES}" ];then
    if [ ! "$(${IP6TABLES} -t mangle -nL | awk '$3 == "::/0" && $4 == "::/0" && $8 == "fill"')" ];then
        ${IP6TABLES} -A POSTROUTING \
                     -t mangle \
                     -p udp \
                     --dport 68 \
                     -j CHECKSUM \
                     --checksum-fill
    fi
fi
