Ansible OpenStack Networking
============================
:date: 2020-10-21
:tags: openstack, cloud, ansible, networking, bond, netplan
:category: \*nix
:author Per Abildgaard Toft <per@minfejl.dk>

This directory contains an example network configuration for Netplan which is the new network
manager in Ubuntu. The files shoule be copied to /etc/netplan/ and applied with `netplan apply`.
These files should cover most cases in terms of host setup though should **NEVER** be taken
literally. These files should only serve as an example and **WILL** need to be edited to fit your
unique network needs.

On-line Resources:
  * Netplan: https://netplan.io/examples/
