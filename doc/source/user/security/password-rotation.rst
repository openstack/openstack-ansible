Password Rotation
=================

.. warning::

   The playbooks do not guarantee password rotation with zero downtime in an
   existing environment. Downtime for the service is expected between
   password is reset on backend and services are restarted to apply new value.

All service passwords are defined and stored as Ansible variables in
OpenStack-Ansible.
This allows the operator to store passwords in an encrypted format using
`Ansible Vault <https://docs.ansible.com/ansible/latest/vault_guide/index.html>`_
or define them as a lookup to `SOPS <https://getsops.io/>`_ or `OpenBao <https://openbao.org/>`_

Typical password change processes include the following steps:

#. Define a new password in Ansible variables (or where defined lookup is pointing to).
#. Change password on an infrastructure backend (i.e. MariaDB, RabbitMQ, etc.).
#. Update service configuration file with the new password.
#. Restart the service to apply new configuration.

Due to the variety of methods which can be used for storing and defining
Ansible variables, we will leave the process of changing password definitions out
of scope of this article, and will focus solely on the process of applying
new passwords to the environment.


Applying new passwords to the service
-------------------------------------

A typical service has a set of passwords for authentication in "infra" backends,
which include, but not limited to:

* Keystone
* MariaDB
* RabbitMQ

As a service downtime is expected after a password is changed (which generally happens
at the very beginning of each role) until the service is restarted, it is important
to ensure that playbook will execute as fast as possible. For that, we will use a set
of specific tags and variables for each "backend" individually.

For following examples, we will take Nova as a sample service, as Nova may struggle
from playbook runtime the most due to amount of hosts which needs to be updated.

As a common technique, we will disable ``serial`` execution, which is enabled by
default, as the password for the backend will be reset during the runtime for
the first host, so rest will not be able to communicate normally regardless of
used ``serial``.

Another common thing among all sections below is usage of ``post-install`` tag.
It has been introduced in 2024.1 (Caracal) release and is applied only to
``<service>_post_install.yml`` tasks, where templating of config files is
happening.

Changing Keystone password for the service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

In order to trigger a password update in Keystone for the service, we
need to supply ``service_update_password`` variable.
To execute the rotation of the Keystone password for a service like Nova,
you will need to execute playbook like this:

.. code-block:: shell-session

    openstack-ansible openstack.osa.nova -e nova_conductor_serial=100% -e nova_compute_serial=100% \
        -e service_update_password=true --tags common-service,post-install

Changing MariaDB password for the service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

To execute the rotation of the MariaDB password for a service like Nova,
you will need to execute playbook like this:

.. code-block:: shell-session

    openstack-ansible openstack.osa.nova -e nova_conductor_serial=100% -e nova_compute_serial=100% \
        --tags common-db,post-install

Changing RabbitMQ password for the service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

To execute the rotation of the MariaDB password for a service like Nova,
you will need to execute playbook like this:

.. code-block:: shell-session

    openstack-ansible openstack.osa.nova -e nova_conductor_serial=100% -e nova_compute_serial=100% \
        --tags common-mq,post-install

Changing all passwords for the service at once
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

It is worth to mention, that operator can combine them together to perform
rotation of passwords for all backends at the same time. While it will increase
playbook runtime (and thus a downtime), it will still be more efficient when
all passwords need to be changed anyway.

To update all passwords mentioned in previous sections, we will simply
combine all used tags and variables:

.. code-block:: shell-session

    openstack-ansible openstack.osa.nova -e nova_conductor_serial=100% -e nova_compute_serial=100% \
        -e service_update_password=true --tags common-service,common-db,common-mq,post-install
