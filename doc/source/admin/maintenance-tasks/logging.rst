Logging Services in OpenStack-Ansible
=====================================

Since the Train release, OpenStack-Ansible services have been configured to save
logs in ``systemd-journald`` instead of traditional log files. Journald logs from
containers are passed through to the physical host, so you can read and manipulate
all service logs directly from the metal hosts using tools like ``journalctl``.

``systemd-journald`` integrates well with a wide range of log collectors and
forwarders, including ``rsyslog``. However, while ``rsyslog`` stores data as
plain text (making it harder to index and search efficiently), journald uses a
structured format that allows logs to be queried and processed much more
efficiently by modern log analysis tools.

Log Locations
~~~~~~~~~~~~~

All container journals are accessible on the host under:

.. code-block:: console

   /var/log/journal/

This allows you to access and filter all service logs directly on the host using
tools such as journalctl. This also allows log collectors running
on the host to more seamlessly pick up and process journald log streams coming
from all service containers.

.. note::

   Due to the adoption of ``systemd-journald`` as the primary logging backend,
   the traditional mapping of ``/openstack/log/`` to ``/var/log/$SERVICE``
   inside the container is no longer present. Logs should be accessed directly
   through journald tools such as ``journalctl`` or by examining the
   ``/var/log/journal/`` directories on the host.

Configuring journald
~~~~~~~~~~~~~~~~~~~~

The ``openstack_hosts`` role allows control over the behavior of
``systemd-journald`` on the host. There are following variable to configure journald
settings:

#. **Persistent journal storage**

   By default, systemd journals are kept in memory and discarded after a reboot.
   OpenStack-Ansible sets the variable ``openstack_host_keep_journals: true`` by default,
   which persists journals across reboots. You can explicitly configure it in
   your ``user_variables.yml`` if needed:

   .. code-block:: yaml

      openstack_host_keep_journals: true

   This ensures that logs remain available for troubleshooting even
   after host restarts.

#. **Custom journald configuration**

   You can supply arbitrary journald configuration options by defining a mapping
   in ``openstack_hosts_journald_config`` in your ``user_variables.yml``.
   For example:

   .. code-block:: yaml

      openstack_hosts_journald_config:
        SystemMaxUse: 20G
        MaxRetentionSec: 7day

   This example limits journald's maximum disk usage to 20 GB and retains logs
   for 7 days.

After adjusting any journald-related variables, you can apply the changes by
re-running the ``openstack_hosts_setup`` role:

.. code-block:: bash

   openstack-ansible openstack.osa.openstack_hosts_setup

You can also check out our ELK role from
`OPS repository <https://opendev.org/openstack/openstack-ansible-ops/src/branch/master/elk_metrics_7x>`_
for a ready-to-use ELK stack deployment and metrics collection.
