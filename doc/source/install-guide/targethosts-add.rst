`Home <index.html>`_ OpenStack-Ansible Installation Guide

Configuring the operating system
--------------------------------

Check the kernel version, install additional software packages, and
configure NTP.

#. Check the kernel version. It should be ``3.13.0-34-generic`` or
   later.

#. Install additional software packages if not already installed during
   operating system installation:

   .. code-block:: shell-session

       # apt-get install bridge-utils debootstrap ifenslave ifenslave-2.6 \
         lsof lvm2 ntp ntpdate openssh-server sudo tcpdump vlan

#. Add the appropriate kernel modules to the ``/etc/modules`` file to
   enable VLAN and bond interfaces:

   .. code-block:: shell-session

      # echo 'bonding' >> /etc/modules
      # echo '8021q' >> /etc/modules

#. Configure NTP to synchronize with a suitable time source.

#. Reboot the host to activate the changes.

--------------

.. include:: navigation.txt
