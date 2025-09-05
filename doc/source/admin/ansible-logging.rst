Ansible Logging Guide
=====================

OpenStack-Ansible provides flexible options for collecting and analyzing
Ansible execution logs. Operators can use the default logging configuration,
or integrate with `ARA Records Ansible <https://ara.recordsansible.org/>`_ for advanced reporting.

Default Log File
----------------

By default, OpenStack-Ansible stores all playbook logs in:

.. code-block:: shell-session

   /openstack/log/ansible-logging/ansible.log

This location is defined by the ``ANSIBLE_LOG_PATH`` environment variable.

To change the path, override it in the deployment configuration file:

.. code-block:: shell-session

   /etc/openstack_deploy/user.rc

ARA Integration
---------------

For richer reporting, OpenStack-Ansible can be integrated with **ARA (Ansible Run Analysis)**.

During the bootstrap process, set the following variable:

.. code-block:: shell-session

   export SETUP_ARA=true
   ./bootstrap-ansible.sh

This installs the ARA client and configures it as an Ansible callback.

The client requires an ARA server to store data. The server is not included in
OpenStack-Ansible and must be deployed by the operator. The recommended method
is to use the ``recordsansible.ara`` collection.

On the deployment host, configure the client with:

.. code-block:: shell-session

   export ARA_API_CLIENT=http
   export ARA_API_SERVER=https://ara.example.com
   export ARA_API_INSECURE=False
   export ARA_API_USERNAME=ara
   export ARA_API_PASSWORD=

If you prefer not to run an ARA server, you can still generate local reports:

.. code-block:: bash

   export ARA_REPORT_TYPE=html

Each playbook run will then produce an HTML report stored on the deploy host.
