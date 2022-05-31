Configuring the operating system
================================

This section describes the installation and configuration of operating
systems for the target hosts, as well as deploying SSH keys and
configuring storage.

Installing the operating system
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Install one of the following supported operating systems on the
target host:

* Ubuntu server 18.04 (Bionic Beaver) LTS 64-bit
* Ubuntu server 20.04 (Focal Fossa) LTS 64-bit
* Debian 10 64-bit
* Debian 11 64-bit
* Centos 8 64-bit

Configure at least one network interface to access the Internet or
suitable local repositories.

We recommend adding the Secure Shell (SSH) server packages to the
installation on target hosts that do not have local (console) access.

.. note::

   We also recommend setting your locale to `en_US.UTF-8`. Other locales might
   work, but they are not tested or supported.


Configure Debian
~~~~~~~~~~~~~~~~

#. Update package source lists

   .. code-block:: shell-session

       # apt update

#. Upgrade the system packages and kernel:

   .. code-block:: shell-session

       # apt dist-upgrade

#. Install additional software packages:

   .. code-block:: shell-session

       # apt install bridge-utils debootstrap ifenslave ifenslave-2.6 \
         lsof lvm2 openssh-server sudo tcpdump vlan python3

#. Reboot the host to activate the changes and use the new kernel.


Configure Ubuntu
~~~~~~~~~~~~~~~~

#. Update package source lists

   .. code-block:: shell-session

       # apt update

#. Upgrade the system packages and kernel:

   .. code-block:: shell-session

       # apt dist-upgrade

#. Install additional software packages:

   .. code-block:: shell-session

       # apt install bridge-utils debootstrap openssh-server \
         tcpdump vlan python3

#. Install the kernel extra package if you have one for your kernel version \

   .. code-block:: shell-session

       # apt install linux-modules-extra-$(uname -r)

#. Reboot the host to activate the changes and use the new kernel.


Configure CentOS
~~~~~~~~~~~~~~~~

#. Upgrade the system packages and kernel:

   .. code-block:: shell-session

       # dnf upgrade

#. Disable SELinux. Edit ``/etc/sysconfig/selinux``, make sure that
   ``SELINUX=enforcing`` is changed to ``SELINUX=disabled``.

   .. note::

      SELinux enabled is not currently supported in OpenStack-Ansible
      for CentOS/RHEL due to a lack of maintainers for the feature.


#. Install additional software packages:

   .. code-block:: shell-session

       # dnf install iputils lsof openssh-server\
         sudo tcpdump python3


#. (Optional) Reduce the kernel log level by changing the printk
   value in your sysctls:

   .. code-block:: shell-session

      # echo "kernel.printk='4 1 7 4'" >> /etc/sysctl.conf


#. Reboot the host to activate the changes and use the new kernel.


Configure SSH keys
==================

Ansible uses SSH to connect the deployment host and target hosts.

#. Copy the contents of the public key file on the deployment host to
   the ``/root/.ssh/authorized_keys`` file on each target host.

#. Test public key authentication from the deployment host to each target
   host by using SSH to connect to the target host from the deployment host.
   If you can connect and get the shell without authenticating, it
   is working. SSH provides a shell without asking for a
   password.

For more information about how to generate an SSH key pair, as well as best
practices, see `GitHub's documentation about generating SSH keys`_.

.. _GitHub's documentation about generating SSH keys: https://help.github.com/articles/generating-ssh-keys/

.. important::

   OpenStack-Ansible deployments require the presence of a
   ``/root/.ssh/id_rsa.pub`` file on the deployment host.
   The contents of this file is inserted into an
   ``authorized_keys`` file for the containers, which is a
   necessary step for the Ansible playbooks. You can
   override this behavior by setting the
   ``lxc_container_ssh_key`` variable to the public key for
   the container.

Configuring the storage
=======================

`Logical Volume Manager (LVM)`_ enables a single device to be split into
multiple logical volumes that appear as a physical storage device to the
operating system. The Block Storage (cinder) service, and LXC containers
that optionally run the OpenStack infrastructure,
can optionally use LVM for their data storage.

.. note::

   OpenStack-Ansible automatically configures LVM on the nodes, and
   overrides any existing LVM configuration. If you had a customized LVM
   configuration, edit the generated configuration file as needed.

#. To use the optional Block Storage (cinder) service, create an LVM
   volume group named ``cinder-volumes`` on the storage host. Specify a metadata
   size of 2048 when creating the physical volume. For example:

   .. code-block:: shell-session

       # pvcreate --metadatasize 2048 physical_volume_device_path
       # vgcreate cinder-volumes physical_volume_device_path

#. Optionally, create an LVM volume group named ``lxc`` for container file
   systems and set ``lxc_container_backing_store: lvm`` in user_variables.yml
   if you want to use LXC with LVM. If the ``lxc`` volume group does not
   exist, containers are automatically installed on the file system under
   ``/var/lib/lxc`` by default.

.. _Logical Volume Manager (LVM): https://en.wikipedia.org/wiki/Logical_Volume_Manager_(Linux)
