Upgrade Playbooks
=================

This section describes the playbooks that are used in the upgrade process in
further detail.

Within the main :file:`scripts` directory there is an :file:`upgrade-utilities`
directory, which contains an additional playbooks directory. These playbooks
facilitate the upgrade process.

.. _config-change-playbook:

``deploy-config-changes.yml``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This playbook backs up the ``/etc/openstack_deploy`` directory before
changing the configuration.

``/etc/openstack_deploy`` copies once to ``/etc/openstack_deploy.MITAKA``.

.. _user-secrets-playbook:

``user-secrets-adjustment.yml``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This playbook ensures that the user secrets file is updated based on the example
file in the main repository, making it possible to guarantee all secrets move
into the upgraded environment and generate appropriately.
This adds only new secrets, such as those necessary for new services or new settings
added to existing services. Values set previously are not changed.

.. _setup-infra-playbook:

``repo-server-pip-conf-removal.yml``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The presence of ``pip.conf`` locks down all Python installations to packages on the
repo server. If ``pip.conf`` exists on the repo server, it creates a circular
dependency, causing build failures.

.. _repo-server-pip-conf-removal:

``setup-infrastructure.yml``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The ``playbooks`` directory contains the ``setup-infrastructure.yml`` playbook.
The ``run-upgrade.sh`` script calls ``setup-insfrastructure.yml`` with specific
arguments to upgrade MariaDB and RabbitMQ.

For example, to run an upgrade for both components at once, run the following commands:

.. code-block:: console

    # openstack-ansible setup-infrastructure.yml -e 'rabbitmq_upgrade=true' \
    # -e 'galera_upgrade=true'

The ``rabbitmq_upgrade`` variable tells the ``rabbitmq_server`` role to
upgrade RabbitMQ.

.. note::
    The RabbitMQ server role installs patch releases automatically,
    regardless of the value of ``rabbitmq_upgrade``. This variable only
    controls upgrading the major or minor versions.

    Upgrading RabbitMQ in the Mitaka release is optional. The
    ``run-upgrade.sh`` script does not automatically upgrade it. To upgrade RabbitMQ,
    insert the ``rabbitmq_upgrade: true``
    line into a file, such as: ``/etc/openstack_deploy/user_variables.yml``.

The ``galera_upgrade`` variable tells the ``galera_server`` role to remove the
current version of MariaDB and Galera and upgrade to the 10.x series.

.. _setup-infra-playbook:

--------------

.. include:: navigation.txt
