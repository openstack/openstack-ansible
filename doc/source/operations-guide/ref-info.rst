=====================
Reference information
=====================

This is a draft reference information page for the proposed OpenStack-Ansible
operations guide.

Linux Container commands
~~~~~~~~~~~~~~~~~~~~~~~~

The following are some useful commands to manage LXC:

-  List containers and summary information such as operational state and
   network configuration:

   .. code-block:: shell-session

       # lxc-ls --fancy

-  Show container details including operational state, resource
   utilization, and ``veth`` pairs:

   .. code-block:: shell-session

       # lxc-info --name container_name

-  Start a container:

   .. code-block:: shell-session

       # lxc-start --name container_name

-  Attach to a container:

   .. code-block:: shell-session

       # lxc-attach --name container_name

-  Stop a container:

   .. code-block:: shell-session

       # lxc-stop --name container_name

Finding Ansible scripts after installation
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

All scripts used to install OpenStack with Ansible can be viewed from
the repository on GitHub, and on the deployment host.

The repository containing the scripts and playbooks is located at
https://github.com/openstack/openstack-ansible.

To access the scripts and playbooks on your deployment host,
follow these steps.

#. Log into your deployment host.

#. Change to the ``/opt/openstack-ansible`` directory.

#. The ``scripts`` directory contains scripts used in the installation.
