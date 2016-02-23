`Home <index.html>`_ OpenStack-Ansible Installation Guide

Chapter 2. Deployment host
--------------------------

**Figure 2.1. Installation work flow**

.. image:: figures/workflow-deploymenthost.png

The OSA installation process recommends one deployment host. The
deployment host contains Ansible and orchestrates the OSA installation
on the target hosts. One of the target hosts, preferably one of the
infrastructure variants, can be used as the deployment host. To use a
deployment host as a target host, follow the steps in `Chapter 3,
*Target hosts* <targethosts.html>`_ on the deployment host. This guide
assumes separate deployment and target hosts.

Installing the operating system
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Install the `Ubuntu Server 14.04 (Trusty Tahr) LTS 64-bit
<http://releases.ubuntu.com/14.04/>`_ operating system on the
deployment host with at least one network interface configured to
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

Installing source and dependencies
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Install the source and dependencies for the deployment host.

#. Clone the OSA repository into the ``/opt/openstack-ansible``
   directory:

   .. code-block:: shell-session

       # git clone -b TAG https://github.com/openstack/openstack-ansible.git /opt/openstack-ansible

   Replace *``TAG``* with the current stable release tag.

#. Change to the ``/opt/openstack-ansible`` directory, and run the
   Ansible bootstrap script:

   .. code-block:: shell-session

       # scripts/bootstrap-ansible.sh

Configuring Secure Shell (SSH) keys
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Ansible uses Secure Shell (SSH) with public key authentication for
connectivity between the deployment and target hosts. To reduce user
interaction during Ansible operations, key pairs should not include
pass phrases. However, if a pass phrase is required, consider using the
**ssh-agent** and **ssh-add** commands to temporarily store the
pass phrase before performing Ansible operations.

--------------

.. include:: navigation.txt
