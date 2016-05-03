Upgrade Playbooks
=================

This section describes the playbooks that are used in the upgrade process in
further detail.

Within the main :file:`scripts` directory there is an :file:`upgrade-utilities`
directory, which contains an additional playbooks directory. These playbooks
facilitate the upgrade process.

.. _config-change-playbook:

deploy-config-changes.yml
-------------------------

This playbook will back up the ``/etc/openstack_deploy`` directory before
making the necessary changes to the configuration.

``/etc/openstack_deploy`` is copied once to ``/etc/openstack_deploy.NEWTON``.
The copy happens only once, so repeated runs are safe.

.. _user-secrets-playbook:

user-secrets-adjustment.yml
---------------------------

This playbook ensures that the user secrets file is updated based on the example
file in the main repository. This makes it possible to guarantee all secrets are
carried into the upgraded environment and appropriately generated. Only new
secrets are added, such as those necessary for new services or new settings
added to existing services. Previously set values will not be changed.

.. _setup-infra-playbook:

repo-server-pip-conf-removal.yml
--------------------------------

This playbook ensures the repository servers do not have the ``pip.conf`` in the
root ``pip`` directory locking down the python packages available to install. If
this file exists on the repository servers it will cause build failures.

.. _repo-server-pip-conf-removal:

setup-infrastructure.yml
------------------------

The ``setup-infrastructure.yml`` playbook is contained in the main
``playbooks`` directory, but is called by ``run-upgrade.sh`` with specific
arguments in order to upgrade infrastructure components such as MariaDB and
RabbitMQ.

For example, to run an upgrade for both components at once, run the following:

.. code-block:: console

    # openstack-ansible setup-infrastructure.yml -e 'rabbitmq_upgrade=true' \
    # -e 'galera_upgrade=true'

The ``rabbitmq_upgrade`` variable tells the ``rabbitmq_server`` role to
upgrade the running major/minor version of RabbitMQ.

.. note::
    The RabbitMQ server role will install patch releases automatically,
    regardless of the value of ``rabbitmq_upgrade``. This variable only
    controls upgrading the major or minor version.

    Upgrading RabbitMQ in the Newton release is optional. The
    ``run-upgrade.sh`` script will not automatically upgrade it. If a RabbitMQ
    upgrade using the script is desired, insert the ``rabbitmq_upgrade: true``
    line into a file such as ``/etc/openstack_deploy/user_variables.yml``.

The ``galera_upgrade`` variable tells the ``galera_server`` role to remove the
current version of MariaDB/Galera and upgrade to the 10.x series.

.. _setup-infra-playbook:

--------------

.. include:: navigation.txt
