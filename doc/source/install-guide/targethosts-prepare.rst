`Home <index.html>`_ OpenStack-Ansible Installation Guide

Preparing the target hosts
--------------------------

All target hosts will need a properly configured operating system as well as
some additional configurations that are noted in the following sections.

Installing the operating system
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Install the Ubuntu Server 14.04 (Trusty Tahr) LTS 64-bit operating
system on the target host with at least one network interface configured
to access the Internet or suitable local repositories.

On target hosts without local (console) access, We recommend
adding the Secure Shell (SSH) server packages to the installation.

We also recommend setting your locale to en_US.UTF-8. Other locales may
work, but they are not tested or supported.

Configuring the operating system
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Upgrade system packages, check the kernel version, install additional
software packages, and configure NTP.

#. Upgrade system packages and kernel:

   .. code-block:: shell-session

       # apt-get dist-upgrade

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

#. Reboot the host to activate the changes and use new kernel.

Deploying SSH keys
~~~~~~~~~~~~~~~~~~

Ansible uses Secure Shell (SSH) for connectivity between the deployment
and target hosts.

#. Copy the contents of the public key file on the deployment host to
   the ``/root/.ssh/authorized_keys`` file on each target host.

#. Test public key authentication from the deployment host to each
   target host. SSH should provide a shell without asking for a
   password.

For more information on how to generate an SSH keypair as well as best
practices, refer to `GitHub's documentation on generating SSH keys`_.

.. _GitHub's documentation on generating SSH keys: https://help.github.com/articles/generating-ssh-keys/

Configuring LVM
~~~~~~~~~~~~~~~

`Logical Volume Manager (LVM)`_ allows a single device to be split into multiple
logical volumes which appear as a physical storage device to the operating
system. The Block Storage (cinder) service as well as the LXC containers that
run the OpenStack infrastructure can optionally use LVM for their data storage.

.. note:: OpenStack-Ansible automatically configures LVM on the nodes, and
   overrides any existing LVM configuration. If you had a customized LVM
   configuration, edit the generated configuration file as needed.

#. To use the optional Block Storage (cinder) service, create an LVM
   volume group named *cinder-volumes* on the Block Storage host. A
   metadata size of 2048 must be specified during physical volume
   creation. For example:

   .. code-block:: shell-session

       # pvcreate --metadatasize 2048 physical_volume_device_path
       # vgcreate cinder-volumes physical_volume_device_path

#. Optionally, create an LVM volume group named *lxc* for container file
   systems. If the lxc volume group does not exist, containers will be
   automatically installed into the file system under */var/lib/lxc* by
   default.

.. _Logical Volume Manager (LVM): https://en.wikipedia.org/wiki/Logical_Volume_Manager_(Linux)

--------------

.. include:: navigation.txt
