`Home <index.html>`_ OpenStack-Ansible Installation Guide

Installation requirements
-------------------------

Deployment host:

-  Required items:

   -  Ubuntu 14.04 LTS (Trusty Tahr) or compatible operating system that
      meets all other requirements.

   -  Secure Shell (SSH) client supporting public key authentication.

   -  Synchronized network time (NTP) client.

   -  Python 2.7 or later.

Target hosts:

-  Required items:

   -  Ubuntu Server 14.04 LTS (Trusty Tahr) 64-bit operating system,
      with Linux kernel version ``3.13.0-34-generic`` or later.

   -  SSH server supporting public key authentication.

   -  Synchronized NTP client.

-  Optional items:

   -  For hosts providing Block Storage (cinder) service volumes, a
      Logical Volume Manager (LVM) volume group named *cinder-volumes*.

   -  LVM volume group named *lxc* to store container file systems. If
      the lxc volume group does not exist, containers will be
      automatically installed in the root file system of the host.

      By default, ansible creates a 5 GB logical volume. Plan storage
      accordingly to support the quantity of containers on each target
      host.

--------------

.. include:: navigation.txt
