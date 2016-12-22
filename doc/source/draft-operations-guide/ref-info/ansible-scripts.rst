==========================================
Finding Ansible scripts after installation
==========================================

All scripts used to install OpenStack with Ansible can be viewed from
the repository on GitHub, and on the local infrastructure server.

The repository containing the scripts and playbooks is located at
https://github.com/openstack/openstack-ansible.

To access the scripts and playbooks on the local ``infra01`` server,
follow these steps.

#. Log into the ``infra01`` server.

#. Change to the ``/opt/rpc-openstack/openstack-ansible`` directory.

#. The ``scripts`` directory contains scripts used in the installation.
   Generally, directories and subdirectories under ``rpcd``
   contain files related to RPCO. For example, the
   ``rpcd/playbooks`` directory contains the RPCO playbooks.
