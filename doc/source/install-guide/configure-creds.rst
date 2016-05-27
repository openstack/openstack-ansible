`Home <index.html>`_ OpenStack-Ansible Installation Guide

Configuring service credentials
===============================

Configure credentials for each service in the
``/etc/openstack_deploy/*_secrets.yml`` files. Consider using `Ansible
Vault <http://docs.ansible.com/playbooks_vault.html>`_ to increase
security by encrypting any files containing credentials.

Adjust permissions on these files to restrict access by non-privileged
users.

Note that the following options configure passwords for the web
interfaces:

-  ``keystone_auth_admin_password`` configures the ``admin`` tenant
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

--------------

.. include:: navigation.txt
