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

Install the operating system
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Install one of the following supported operating systems on the deployment
hosts:

* `Ubuntu server 16.04 (Xenial Xerus) LTS 64-bit <http://releases.ubuntu.com/16.04/>`_
* `Centos 7 64-bit <https://www.centos.org/download/>`_
* `openSUSE 42.X 64-bit <https://software.opensuse.org/distributions/leap>`_

Configure at least one network interface to access the Internet or suitable
local repositories.

Configure the operating system (Ubuntu)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Install additional software packages and configure Network Time Protocol (NTP).
Before you begin, we recommend upgrading your system packages and kernel.

#. Update package source lists:

   .. code-block:: shell-session

       # apt-get update


#. Upgrade the system packages and kernel:

   .. code-block:: shell-session

       # apt-get dist-upgrade

#. Reboot the host.

#. Install additional software packages if they were not installed
   during the operating system installation:

   .. code-block:: shell-session

       # apt-get install aptitude build-essential git ntp ntpdate \
         openssh-server python-dev sudo

#. Configure NTP to synchronize with a suitable time source.

Configure the operating system (CentOS)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Install additional software packages and configure Network Time Protocol (NTP).
Before you begin, we recommend upgrading your system packages and kernel.

#. Upgrade the system packages and kernel

   .. code-block:: shell-session

       # yum upgrade

#. Reboot the host.

#. Install additional software packages if they were not installed
   during the operating system installation:

   .. code-block:: shell-session

       # yum install https://rdoproject.org/repos/openstack-pike/rdo-release-pike.rpm
       # yum install git ntp ntpdate openssh-server python-devel \
         sudo '@Development Tools'

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

Configure the operating system (openSUSE)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Install additional software packages and configure Network Time Protocol (NTP).
Before you begin, we recommend upgrading your system packages and kernel.

#. Upgrade the system packages and kernel

   .. code-block:: shell-session

       # zypper up

#. Reboot the host.

#. Install additional software packages if they were not installed
   during the operating system installation:

   .. code-block:: shell-session

       # zypper ar http://download.opensuse.org/repositories/Cloud:/OpenStack:/Pike/openSUSE_Leap_42.3 OBS:Cloud:OpenStack:Pike
       # zypper install git-core ntp openssh python-devel \
         sudo gcc libffi-devel libopenssl-devel

#. Configure NTP to synchronize with a suitable time source.

Configure the network
~~~~~~~~~~~~~~~~~~~~~

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
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Install the source and dependencies for the deployment host.

.. note::

   If you are installing with limited connectivity, please review
   :ref:`limited-connectivity-appendix` before proceeding.

#. Clone the latest stable release of the OpenStack-Ansible Git repository in
   the ``/opt/openstack-ansible`` directory:

   .. parsed-literal::

       # git clone -b |latest_tag| https://git.openstack.org/openstack/openstack-ansible \\
         /opt/openstack-ansible

#. Change to the ``/opt/openstack-ansible`` directory, and run the
   Ansible bootstrap script:

   .. code-block:: shell-session

       # scripts/bootstrap-ansible.sh

Configure SSH keys
~~~~~~~~~~~~~~~~~~

Ansible uses SSH with public key authentication to connect the
deployment host and target hosts. To reduce user
interaction during Ansible operations, do not include passphrases with
key pairs. However, if a passphrase is required, consider using the
``ssh-agent`` and ``ssh-add`` commands to temporarily store the
passphrase before performing Ansible operations.

