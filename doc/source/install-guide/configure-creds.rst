`Home <index.html>`__ OpenStack Ansible Installation Guide

Configuring service credentials
-------------------------------

Configure credentials for each service in the
``/etc/openstack_deploy/*_secrets.yml`` files. Consider using `Ansible
Vault <http://docs.ansible.com/playbooks_vault.html>`__ to increase
security by encrypting any files containing credentials.

Adjust permissions on these files to restrict access by non-privileged
users.

Note that the following options configure passwords for the web
interfaces:

-  ``keystone_auth_admin_password`` configures the ``admin`` tenant
   password for both the OpenStack API and dashboard access.

-  ``kibana_password`` configures the password for Kibana web interface
   access.

Recommended: Use the ``pw-token-gen.py`` script to generate random
values for the variables in each file that contains service credentials:

.. code-block:: bash

    $ cd /opt/openstack-ansible/scripts
    $ python pw-token-gen.py --file /etc/openstack_deploy/user_secrets.yml
        

To regenerate existing passwords, add the ``--regen`` flag.

--------------

.. include:: navigation.txt
