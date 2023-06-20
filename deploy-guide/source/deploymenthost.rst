.. _deployment-host:

===========================
Prepare the deployment host
===========================

.. figure:: figures/installation-workflow-deploymenthost.png
   :width: 100%

When you install OpenStack in a production environment, we recommend using a
separate deployment host that contains Ansible and orchestrates the
OpenStack-Ansible (OSA) installation on the target hosts. In a test
environment, we recommend using one of the infrastructure target hosts as the
deployment host.

To use a target host as a deployment host, follow the steps in
:deploy_guide:`Prepare the target hosts <targethosts.html>` on
the deployment host.

Configuring the operating system
================================

Install the operating system
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Install one of the following supported operating systems on the deployment
hosts:

* `Ubuntu server 22.04 (Jammy Jellyfish) LTS 64-bit <http://releases.ubuntu.com/22.04/>`_
* `Debian 11 (Bullseye) LTS 64-bit <https://www.debian.org/distrib/>`_
* `Centos 9 Stream 64-bit <https://mirrors.centos.org/mirrorlist?path=/9-stream/BaseOS/x86_64/iso/>`_
* `Rocky Linux 9 64-bit <https://mirrors.rockylinux.org/mirrorlist?path=/pub/rocky/9.0/isos/>`_

Configure at least one network interface to access the Internet or suitable
local repositories.

Configure Ubuntu
~~~~~~~~~~~~~~~~

Install additional software packages and configure Network Time Protocol (NTP).
Before you begin, we recommend upgrading your system packages and kernel.

#. Update package source lists:

   .. code-block:: shell-session

       # apt update


#. Upgrade the system packages and kernel:

   .. code-block:: shell-session

       # apt dist-upgrade

#. Reboot the host.

#. Install additional software packages if they were not installed
   during the operating system installation:

   .. code-block:: shell-session

       # apt install build-essential git chrony openssh-server python3-dev sudo

#. Configure NTP to synchronize with a suitable time source.

Configure CentOS / Rocky
~~~~~~~~~~~~~~~~~~~~~~~~

Install additional software packages and configure Network Time Protocol (NTP).
Before you begin, we recommend upgrading your system packages and kernel.

#. Upgrade the system packages and kernel

   .. code-block:: shell-session

       # dnf upgrade

#. Reboot the host.

#. Install additional software packages if they were not installed
   during the operating system installation:

   .. parsed-literal::

       # dnf install git chrony openssh-server python3-devel sudo
       # dnf group install "Development Tools"

#. Configure NTP to synchronize with a suitable time source.

#. The ``firewalld`` service is enabled on most CentOS systems by default and
   its default ruleset prevents OpenStack components from communicating
   properly. Stop the ``firewalld`` service and mask it to prevent it from
   starting:

   .. code-block:: shell-session

       # systemctl stop firewalld
       # systemctl mask firewalld

.. note::

    There is `future work planned <https://bugs.launchpad.net/openstack-ansible/+bug/1657518>`_
    to create proper firewall rules for OpenStack services in OpenStack-Ansible
    deployments. Until that work is complete, deployers must maintain their
    own firewall rulesets or disable the firewall entirely.


Configure SSH keys
==================

Ansible uses SSH with public key authentication to connect the
deployment host and target hosts. To reduce user
interaction during Ansible operations, do not include passphrases with
key pairs. However, if a passphrase is required, consider using the
``ssh-agent`` and ``ssh-add`` commands to temporarily store the
passphrase before performing Ansible operations.

Configure the network
=====================

Ansible deployments fail if the deployment server can't use Secure Shell (SSH)
to connect to the containers.

Configure the deployment host (where Ansible is executed) to be on
the same layer 2 network as the network designated for container management. By
default, this is the ``br-mgmt`` network. This configuration reduces the rate
of failure caused by connectivity issues.

Select an IP address from the following example range to assign to the
deployment host:

.. code-block:: ini

   Container management: 172.29.236.0/22 (VLAN 10)

Install the source and dependencies
===================================

Install the source and dependencies for the deployment host.

.. note::

   If you are installing with limited connectivity, please review
   :dev_docs:`Installing with limited connectivity
   <user/limited-connectivity/index.html>`
   before proceeding.

#. Clone the latest stable release of the OpenStack-Ansible Git repository in
   the ``/opt/openstack-ansible`` directory:

   .. parsed-literal::

       # git clone -b |latest_tag| \https://opendev.org/openstack/openstack-ansible /opt/openstack-ansible

   If opendev.org can not be accessed to run git clone, github.com can be used
   as an alternative repo:

   .. parsed-literal::

       # git clone -b |latest_tag| \https://github.com/openstack/openstack-ansible.git /opt/openstack-ansible

#. Change to the ``/opt/openstack-ansible`` directory, and run the
   Ansible bootstrap script:

   .. code-block:: shell-session

       # scripts/bootstrap-ansible.sh


Configure Docker with Alpine
============================

It is an alternative realization of deploy host configuration which includes usage of the Docker
container as the deploy host.

This is also neither supported nor tested in CI, so you should use it at your own risk.

Before you begin, we recommend upgrading your Docker host system packages and kernel.

#. Prepare your OpenStack Ansible Dockerfile

   .. parsed-literal::

       FROM alpine
       RUN apk add --no-cache bash build-base git python3-dev openssh-client openssh-keygen sudo py3-virtualenv iptables libffi-dev openssl-dev linux-headers coreutils curl
       RUN git clone -b |latest_tag| \https://git.openstack.org/openstack/openstack-ansible /opt/openstack-ansible
       WORKDIR /opt/openstack-ansible
       RUN /opt/openstack-ansible/scripts/bootstrap-ansible.sh
       ENTRYPOINT ["bash"]

#. Build and run your deploy host container

   .. parsed-literal::

       # docker build . -t openstack-ansible:|latest_tag|
       # docker run -dit --name osa-deploy openstack-ansible:|latest_tag|
       # docker exec -it osa-deploy bash

#. Configure NTP to synchronize with a suitable time source on the Docker host.
