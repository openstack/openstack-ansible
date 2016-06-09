`Home <index.html>`_ OpenStack-Ansible Installation Guide

Chapter 2. Deployment host
==========================

**Figure 2.1. Installation work flow**

.. image:: figures/workflow-deploymenthost.png

The OSA installation process recommends one deployment host. The
deployment host contains Ansible and orchestrates the OpenStack-Ansible
installation on the target hosts. We recommend using separate deployment and
target hosts. You could alternatively use one of the target hosts, preferably
one of the infrastructure variants, as the deployment host. To use a
deployment host as a target host, follow the steps in `Chapter 3, Target
hosts <targethosts.html>`_ on the deployment host.

Installing the operating system
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Install the `Ubuntu Server 14.04 (Trusty Tahr) LTS 64-bit
<http://releases.ubuntu.com/14.04/>`_ operating system on the
deployment host. Configure at least one network interface to
access the Internet or suitable local repositories.

Configuring the operating system
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Install additional software packages and configure NTP.

#. Install additional software packages if not already installed
   during operating system installation:

   .. code-block:: shell-session

       # apt-get install aptitude build-essential git ntp ntpdate \
         openssh-server python-dev sudo

#. Configure NTP to synchronize with a suitable time source.

Configuring the network
~~~~~~~~~~~~~~~~~~~~~~~

Ansible deployments fail if the deployment server is unable to SSH to the containers.
Configure the deployment host to be on the same network designated for container management.
This configuration reduces the rate of failure due to connectivity issues.

The following network information is used as an example:

  Container management: 172.29.236.0/22 (VLAN 10)

Select an IP from this range to assign to the deployment host.

Installing source and dependencies
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Install the source and dependencies for the deployment host.

#. Clone the OSA repository into the ``/opt/openstack-ansible``
   directory:

   .. code-block:: shell-session

       # git clone -b TAG https://github.com/openstack/openstack-ansible.git /opt/openstack-ansible

   Replace ``TAG`` with the current stable release tag.

#. Change to the ``/opt/openstack-ansible`` directory, and run the
   Ansible bootstrap script:

   .. code-block:: shell-session

       # scripts/bootstrap-ansible.sh

Configuring Secure Shell (SSH) keys
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Ansible uses Secure Shell (SSH) with public key authentication for
connectivity between the deployment and target hosts. To reduce user
interaction during Ansible operations, do not include pass phrases with
key pairs. However, if a pass phrase is required, consider using the
``ssh-agent`` and ``ssh-add`` commands to temporarily store the
pass phrase before performing Ansible operations.

--------------

.. include:: navigation.txt
