===========================================
Overriding OpenStack configuration defaults
===========================================

OpenStack has many configuration options available in ``.conf`` files
(in a standard ``INI`` file format),
policy files (in a standard ``JSON`` format) and ``YAML`` files.

.. note::

   ``YAML`` files are only in the ceilometer project at this time.

OpenStack-Ansible enables you to reference any options in the
`OpenStack Configuration Reference`_ through the use of a simple set of
configuration entries in the ``/etc/openstack_deploy/user_variables.yml``.

This section describes how to use the configuration entries in the
``/etc/openstack_deploy/user_variables.yml`` file to override default
configuration settings. For more information, see the
:dev_docs:`Setting overrides in configuration files
<extending.html#setting-overrides-in-configuration-files>` section in the
developer documentation.

.. _OpenStack Configuration Reference: http://docs.openstack.org/draft/config-reference/

Overriding .conf files
~~~~~~~~~~~~~~~~~~~~~~

Most often, overrides are implemented for the ``<service>.conf`` files
(for example, ``nova.conf``). These files use a standard INI file format.

For example, you might want to add the following parameters to the
``nova.conf`` file:

.. code-block:: ini

    [DEFAULT]
    remove_unused_original_minimum_age_seconds = 43200

    [libvirt]
    cpu_mode = host-model
    disk_cachemodes = file=directsync,block=none

    [database]
    idle_timeout = 300
    max_pool_size = 10

To do this, you use the following configuration entry in the
``/etc/openstack_deploy/user_variables.yml`` file:

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

.. note::

   The general format for the variable names used for overrides is
   ``<service>_<filename>_<file extension>_overrides``. For example, the variable
   name used in these examples to add parameters to the ``nova.conf`` file is
   ``nova_nova_conf_overrides``.

You can also apply overrides on a per-host basis with the following
configuration in the ``/etc/openstack_deploy/openstack_user_config.yml``
file:

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

Use this method for any files with the ``INI`` format for in OpenStack projects
deployed in OpenStack-Ansible.

Overriding .json files
~~~~~~~~~~~~~~~~~~~~~~

To implement access controls that are different from the ones in a standard
OpenStack environment, you can adjust the default policies applied by services.
Policy files are in a ``JSON`` format.

For example, you might want to add the following policy in the ``policy.json``
file for the Identity service (keystone):

.. code-block:: json

    {
        "identity:foo": "rule:admin_required",
        "identity:bar": "rule:admin_required"
    }

To do this, you use the following configuration entry in the
``/etc/openstack_deploy/user_variables.yml`` file:

.. code-block:: yaml

    keystone_policy_overrides:
      identity:foo: "rule:admin_required"
      identity:bar: "rule:admin_required"

.. note::

   The general format for the variable names used for overrides is
   ``<service>_policy_overrides``. For example, the variable name used in this
   example to add a policy to the Identity service (keystone) ``policy.json`` file
   is ``keystone_policy_overrides``.

Use this method for any files with the ``JSON`` format in OpenStack projects
deployed in OpenStack-Ansible.

To assist you in finding the appropriate variable name to use for
overrides, the general format for the variable name is
``<service>_policy_overrides``.

Overriding .yml files
~~~~~~~~~~~~~~~~~~~~~

You can override ``.yml`` file values by supplying replacement YAML content.

.. note::

   All default YAML file content is completely overwritten by the overrides,
   so the entire YAML source (both the existing content and your changes)
   must be provided.

For example, you might want to define a meter exclusion for all hardware
items in the default content of the ``pipeline.yml`` file for the
Telemetry service (ceilometer):

.. code-block:: yaml

    sources:
        - name: meter_source
        interval: 600
        meters:
            - "!hardware.*"
        sinks:
            - meter_sink
        - name: foo_source
        value: foo

To do this, you use the following configuration entry in the
``/etc/openstack_deploy/user_variables.yml`` file:

.. code-block:: yaml

    ceilometer_pipeline_yaml_overrides:
      sources:
          - name: meter_source
          interval: 600
          meters:
              - "!hardware.*"
          sinks:
              - meter_sink
          - name: source_foo
          value: foo

.. note::

   The general format for the variable names used for overrides is
   ``<service>_<filename>_<file extension>_overrides``. For example, the variable
   name used in this example to define a meter exclusion in the ``pipeline.yml`` file
   for the Telemetry service (ceilometer) is ``ceilometer_pipeline_yaml_overrides``.

Currently available overrides
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The following override variables are available.

Galera:
    * galera_client_my_cnf_overrides
    * galera_my_cnf_overrides
    * galera_cluster_cnf_overrides
    * galera_debian_cnf_overrides

Telemetry service (ceilometer):
    * ceilometer_policy_overrides
    * ceilometer_ceilometer_conf_overrides
    * ceilometer_event_definitions_yaml_overrides
    * ceilometer_event_pipeline_yaml_overrides
    * ceilometer_pipeline_yaml_overrides

Block Storage (cinder):
    * cinder_policy_overrides
    * cinder_rootwrap_conf_overrides
    * cinder_api_paste_ini_overrides
    * cinder_cinder_conf_overrides

Image service (glance):
    * glance_glance_api_paste_ini_overrides
    * glance_glance_api_conf_overrides
    * glance_glance_cache_conf_overrides
    * glance_glance_manage_conf_overrides
    * glance_glance_registry_paste_ini_overrides
    * glance_glance_registry_conf_overrides
    * glance_glance_scrubber_conf_overrides
    * glance_glance_scheme_json_overrides
    * glance_policy_overrides

Orchestration service (heat):
    * heat_heat_conf_overrides
    * heat_api_paste_ini_overrides
    * heat_default_yaml_overrides
    * heat_aws_cloudwatch_alarm_yaml_overrides
    * heat_aws_rds_dbinstance_yaml_overrides
    * heat_policy_overrides

Identity service (keystone):
    * keystone_keystone_conf_overrides
    * keystone_keystone_default_conf_overrides
    * keystone_keystone_paste_ini_overrides
    * keystone_policy_overrides

Networking service (neutron):
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

Compute service (nova):
    * nova_nova_conf_overrides
    * nova_rootwrap_conf_overrides
    * nova_api_paste_ini_overrides
    * nova_policy_overrides

Object Storage service (swift):
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

  .. note::

     Possible additional overrides can be found in the "Tunable Section"
     of each role's ``main.yml`` file, such as
     ``/etc/ansible/roles/role_name/defaults/main.yml``.
