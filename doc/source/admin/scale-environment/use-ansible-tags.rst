.. _ansible-tags:

==================
Using Ansible tags
==================

In Ansible, a tag is a label you can assign to tasks, allowing you to run
only the tasks you need instead of the whole playbook. This is especially
handy in large playbooks — for example, if you have 20–30 tasks but just
need to restart a service or make some changes in configuration, you can tag
those tasks and run them individually.

The following tags are available in OpenStack Ansible:

- ``common-mq``
- ``common-service``
- ``common-db``
- ``pki``
- ``post-install``
- ``haproxy-service-config``
- ``ceph``
- ``uwsgi``
- ``systemd-service``
- ``<service>-install``
- ``<service>-config``

common-mq
---------

Handles tasks for setting up and configuring RabbitMQ. Use this tag when
you need to reconfigure virtual hosts, users, or their privileges without
affecting the rest of the deployment.

Example:

.. code-block:: shell-session

   # openstack-ansible openstack.osa.nova --tags common-mq

common-service
--------------

Manages service configuration inside Keystone, such as service
catalog entries, service user existence, and user privileges.

Example:

.. code-block:: shell-session

   # openstack-ansible openstack.osa.nova --tags common-service,post-install

common-db
---------

Creates and configures databases, including user creation,
and permission assignments. Run this tag if database credential or permissions
need to be refreshed or corrected.

Example:

.. code-block:: shell-session

   # openstack-ansible openstack.osa.neutron --tags common-db

pki
---

Manages certificates and public key infrastructure.
Use it when renewing, replacing, or troubleshooting SSL/TLS certificates.

Example:

.. code-block:: shell-session

   # openstack-ansible openstack.osa.setup_infrastructure -e pki_regen_cert=true --tags pki

post-install
------------

Runs tasks after the main installation and configuration are complete.
This tag is used for final adjustments, applying changes in configuration
files, and validation checks. Run this tag when you’ve made changes that
require only applying updated configuration.

Example:

.. code-block:: shell-session

   # openstack-ansible openstack.osa.cinder --tags post-install

haproxy-service-config
----------------------

Configures HAProxy for routing traffic between services.
Use this tag if HAProxy settings change or a new service backend is added.

Example:

.. code-block:: shell-session

   # openstack-ansible haproxy-install.yml --tags haproxy-service-config

ceph
----

Deploys and configures Ceph clients and related components. Use this tag
for tasks such as adding new monitors or upgrading Ceph clients to a
different version, as well as other Ceph-related configuration updates.

Example:

.. code-block:: shell-session

   # openstack-ansible ceph-install.yml --tags ceph

uwsgi
-----

Sets up and configures uWSGI processes.
Useful when adjusting process counts, sockets, or performance tuning.

Example:

.. code-block:: shell-session

   # openstack-ansible openstack.osa.setup_openstack --tags uwsgi

systemd-service
---------------

Manages systemd unit components, ensuring they are configured as expected
and allowing overrides to be applied. Use this tag when you need to adjust
unit files or restart services in a controlled way.

Example:

.. code-block:: shell-session

   # openstack-ansible openstack.osa.designate --tags systemd-service

<service>-install
-----------------

Installs a specific OpenStack service (replace ``<service>`` with the
service name).
A tag including the word ``install`` handles only software installation
tasks — it deploys the necessary packages and binaries on the target host.
Use this tag when you only need to install or reinstall service software without
changing its configuration or running it.

Example:

.. code-block:: shell-session

   # openstack-ansible openstack.osa.designate --tags designate-install

<service>-config
----------------

Configures a specific OpenStack service (replace <service> with the service
name). This tag applies configuration files, directories, and service-specific
settings. It usually covers a broad set of tasks beyond post-install, and may
include systemd-service, pki, common-mq or common-db service tags.
Run this tag when applying updated configurations to a service that is
already installed.

Example:

.. code-block:: shell-session

   # openstack-ansible openstack.osa.cinder --tags cinder-config
