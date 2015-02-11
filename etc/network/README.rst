Ansible OpenStack Networking
============================
:date: 2013-09-05 09:51
:tags: openstack, cloud, ansible, networking, bond, interfaces
:category: \*nix

This directory contains some base interface files that will allow you to see what 
the networking setup might be like in your environment. Three **basic** example 
configurations have been provided in the in ``interfaces.d`` directory.  These
files should cover most cases in terms of host setup though should **NEVER** be
taken literally.  These files should only serve as an example and **WILL** need to
be edited to fit your unique network needs. All provided files have different configurations
within them to suit very different use cases.  It should also be noted that UDEV rules may 
change your network setup between boxes and may require tweaking. If you have questions on 
how debian networking is built out please review the following documentation. 


On-line Resources:
  * Ubuntu Bonding: https://help.ubuntu.com/community/UbuntuBonding
  * Ubuntu Networking: https://help.ubuntu.com/14.04/serverguide/network-configuration.html
  * Debian Bonding: https://wiki.debian.org/Bonding
  * Debian Networking: https://wiki.debian.org/NetworkConfiguration
