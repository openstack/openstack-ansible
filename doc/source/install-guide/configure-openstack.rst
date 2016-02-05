`Home <index.html>`_ OpenStack-Ansible Installation Guide

Overriding OpenStack Configuration Defaults
-------------------------------------------

OpenStack has many configuration options available in configuration files
which take the form of ``.conf`` files (in a standard ``INI`` file format),
policy files (in a standard ``JSON`` format) and also in ``YAML`` files (only
in the Ceilometer project at this time).

OpenStack-Ansible provides the facility to include any options referenced in
the `OpenStack Configuration Reference`_ through the use of a simple set of
configuration entries in ``/etc/openstack_deploy/user_variables.yml``.

This section provides guidance for how to make use of this facility. Further
guidance is available in the Developer Documentation in the section titled
`Setting overrides in configuration files`_.

.. _OpenStack Configuration Reference: http://docs.openstack.org/draft/config-reference/
.. _Setting overrides in configuration files: ../developer-docs/extending.html#setting-overrides-in-configuration-files

Overriding .conf files
~~~~~~~~~~~~~~~~~~~~~~

The most common use-case for implementing overrides are for the
``<service>.conf`` files (eg: ``nova.conf``). These files use a standard
``INI`` file format.

As an example, if a deployer wishes to add the following parameters
to ``nova.conf``:

.. code-block:: ini

    [DEFAULT]
    remove_unused_original_minimum_age_seconds = 43200

    [libvirt]
    cpu_mode = host-model
    disk_cachemodes = file=directsync,block=none

    [database]
    idle_timeout = 300
    max_pool_size = 10

This would be accomplished through the use of the following configuration
entry in ``/etc/openstack_deploy/user_variables.yml``:

.. code-block:: yaml

    nova_nova_conf_overrides:
      DEFAULT:
        remove_unused_original_minimum_age_seconds: 43200
      libvirt:
        cpu_mode: host-model
        disk_cachemodes: file=directsync,block=none
      database:
        idle_timeout: 300
        max_pool_size: 10

Overrides may also be applied on a per host basis with the following
configuration in ``/etc/openstack_deploy/openstack_user_config.yml``:

.. code-block:: yaml

      compute_hosts:
        900089-compute001:
          ip: 192.0.2.10
          host_vars:
            nova_nova_conf_overrides:
              DEFAULT:
                remove_unused_original_minimum_age_seconds: 43200
              libvirt:
                cpu_mode: host-model
                disk_cachemodes: file=directsync,block=none
              database:
                idle_timeout: 300
                max_pool_size: 10

This method may be used for any INI file format for all OpenStack projects
deployed in OpenStack-Ansible.

To assist deployers in finding the appropriate variable name to use for
overrides, the general format for the variable name is:
``<service>_<filename>_<file extension>_overrides``.

Overriding .json files
~~~~~~~~~~~~~~~~~~~~~~

Deployers may wish to adjust the default policies applied by services in order
to implement access controls which are different to the norm. Policy files
are in a JSON format.

As an example, the deployer wishes to add the following policy in
Keystone's ``policy.json``:

.. code-block:: json

    {
        "identity:foo": "rule:admin_required",
        "identity:bar": "rule:admin_required"
    }

This would be accomplished through the use of the following configuration
entry in ``/etc/openstack_deploy/user_variables.yml``:

.. code-block:: yaml

    keystone_policy_overrides:
      identity:foo: "rule:admin_required"
      identity:bar: "rule:admin_required"

This method may be used for any JSON file format for all OpenStack projects
deployed in OpenStack-Ansible.

To assist deployers in finding the appropriate variable name to use for
overrides, the general format for the variable name is
``<service>_policy_overrides``.

Currently Available Overrides
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

For convenience, this is a (possibly incomplete) list of overrides available:

Galera:
    * galera_client_my_cnf_overrides
    * galera_my_cnf_overrides
    * galera_cluster_cnf_overrides
    * galera_debian_cnf_overrides

Ceilometer:
    * ceilometer_policy_overrides
    * ceilometer_ceilometer_conf_overrides
    * ceilometer_api_paste_ini_overrides
    * ceilometer_event_definitions_yaml_overrides
    * ceilometer_event_pipeline_yaml_overrides
    * ceilometer_pipeline_yaml_overrides

Cinder:
    * cinder_policy_overrides
    * cinder_rootwrap_conf_overrides
    * cinder_api_paste_ini_overrides
    * cinder_cinder_conf_overrides

Glance:
    * glance_glance_api_paste_ini_overrides
    * glance_glance_api_conf_overrides
    * glance_glance_cache_conf_overrides
    * glance_glance_manage_conf_overrides
    * glance_glance_registry_paste_ini_overrides
    * glance_glance_registry_conf_overrides
    * glance_glance_scrubber_conf_overrides
    * glance_glance_scheme_json_overrides
    * glance_policy_overrides

Heat:
    * heat_heat_conf_overrides
    * heat_api_paste_ini_overrides
    * heat_default_yaml_overrides
    * heat_aws_cloudwatch_alarm_yaml_overrides
    * heat_aws_rds_dbinstance_yaml_overrides
    * heat_policy_overrides

Keystone:
    * keystone_keystone_conf_overrides
    * keystone_keystone_default_conf_overrides
    * keystone_keystone_paste_ini_overrides
    * keystone_policy_overrides

Neutron:
    * neutron_neutron_conf_overrides
    * neutron_ml2_conf_ini_overrides
    * neutron_dhcp_agent_ini_overrides
    * neutron_api_paste_ini_overrides
    * neutron_rootwrap_conf_overrides
    * neutron_policy_overrides
    * neutron_dnsmasq_neutron_conf_overrides
    * neutron_l3_agent_ini_overrides
    * neutron_metadata_agent_ini_overrides
    * neutron_metering_agent_ini_overrides

Nova:
    * nova_nova_conf_overrides
    * nova_rootwrap_conf_overrides
    * nova_api_paste_ini_overrides
    * nova_policy_overrides

Swift:
    * swift_swift_conf_overrides
    * swift_swift_dispersion_conf_overrides
    * swift_proxy_server_conf_overrides
    * swift_account_server_conf_overrides
    * swift_account_server_replicator_conf_overrides
    * swift_container_server_conf_overrides
    * swift_container_server_replicator_conf_overrides
    * swift_object_server_conf_overrides
    * swift_object_server_replicator_conf_overrides

Tempest:
    * tempest_tempest_conf_overrides

pip:
    * pip_global_conf_overrides

--------------

.. include:: navigation.txt
