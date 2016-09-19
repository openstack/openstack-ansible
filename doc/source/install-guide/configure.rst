.. _configure:

====================
Configure deployment
====================

.. toctree::
   :maxdepth: 2

   configure-user-config-examples.rst

.. figure:: figures/installation-workflow-configure-deployment.png
   :width: 100%

Ansible references a handful of files containing mandatory and optional
configuration directives. Modify these files to define the
target environment before running the Ansible playbooks. Configuration
tasks include:

* Target host networking to define bridge interfaces and
  networks.
* A list of target hosts on which to install the software.
* Virtual and physical network relationships for OpenStack
  Networking (neutron).
* Passwords for all services.

Initial environment configuration
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
OpenStack-Ansible depends on various files that are used to build an inventory
for Ansible. Start by getting those files into the correct places:

#. Copy the contents of the
   ``/opt/openstack-ansible/etc/openstack_deploy`` directory to the
   ``/etc/openstack_deploy`` directory.

.. note::

    As of |current_release_formal_name|, the ``env.d`` directory has been
    moved from this source directory to ``playbooks/inventory/``.

#. Change to the ``/etc/openstack_deploy`` directory.

#. Copy the ``openstack_user_config.yml.example`` file to
   ``/etc/openstack_deploy/openstack_user_config.yml``.

You can review the ``openstack_user_config.yml`` file and make changes
to the deployment of your OpenStack environment.

.. note::

   The file is heavily commented with details about the various options.

Configuration in ``openstack_user_config.yml`` defines which hosts
will run the containers and services deployed by OpenStack-Ansible. For
example, hosts listed in the ``shared-infra_hosts`` run containers for many of
the shared services that your OpenStack environment requires. Some of these
services include databases, memcached, and RabbitMQ. There are several other
host types that contain other types of containers and all of these are listed
in ``openstack_user_config.yml``.

For details about how the inventory is generated from the environment
configuration, see :ref:`developer-inventory`.

Configuring service credentials
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Configure credentials for each service in the
``/etc/openstack_deploy/*_secrets.yml`` files. Consider using `Ansible
Vault <http://docs.ansible.com/playbooks_vault.html>`_ to increase
security by encrypting any files containing credentials.

Adjust permissions on these files to restrict access by non-privileged
users.

.. note::

   The following options configure passwords for the web interfaces.

* ``keystone_auth_admin_password`` configures the ``admin`` tenant
   password for both the OpenStack API and dashboard access.

.. note::

   We recommend using the ``pw-token-gen.py`` script to generate random
   values for the variables in each file that contains service credentials:

   .. code-block:: shell-session

      # cd /opt/openstack-ansible/scripts
      # python pw-token-gen.py --file /etc/openstack_deploy/user_secrets.yml

To regenerate existing passwords, add the ``--regen`` flag.

.. warning::

   The playbooks do not currently manage changing passwords in an existing
   environment. Changing passwords and re-running the playbooks will fail
   and may break your OpenStack environment.
