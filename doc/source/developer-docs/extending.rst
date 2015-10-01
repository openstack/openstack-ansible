Extending openstack-ansible
===========================

The openstack-ansible project provides a basic OpenStack environment, but
many deployers will wish to extend the environment based on their needs. This
could include installing extra services, changing package versions, or
overriding existing variables.

Using these extension points, deployers can provide a more 'opinionated'
installation of OpenStack that may include their own software.

Including openstack-ansible in your project
-------------------------------------------

Including the openstack-ansible repository within another project can be
done in several ways.

    1. A git submodule pointed to a released tag.
    2. A script to automatically perform a git checkout of
       openstack-ansible

When including openstack-ansible in a project, consider using a parallel
directory structure as shown in the `ansible.cfg files`_ section.

Also note that copying files into directories such as `env.d`_ or
`conf.d`_ should be handled via some sort of script within the extension
project.

ansible.cfg files
-----------------

You can create your own playbook, variable, and role structure while still
including the openstack-ansible roles and libaries by putting an
``ansible.cfg`` file in your ``playbooks`` directory.

The relevant options for Ansible 1.9 (included in openstack-ansible)
are as follows:

    ``library``
        This variable should point to
        ``openstack-ansible/playbooks/library``. Doing so allows roles and
        playbooks to access openstack-ansible's included Ansible modules.
    ``roles_path``
        This variable should point to
        ``openstack-ansible/playbooks/roles``. This allows Ansible to
        properly look up any openstack-ansible roles that extension roles
        may reference.
    ``inventory``
        This variable should point to
        ``openstack-ansible/playbooks/inventory``. With this setting,
        extensions have access to the same dynamic inventory that
        openstack-ansible uses.

Note that the paths to the ``openstack-ansible`` top level directory can be
relative in this file.

Consider this directory structure::

    my_project
    |
    |- custom_stuff
    |  |
    |  |- playbooks
    |- openstack-ansible
    |  |
    |  |- playbooks

The variables in ``my_project/custom_stuff/playbooks/ansible.cfg`` would use
``../openstack-ansible/playbooks/<directory>``.


env.d
-----

The openstack-ansible default environment, including container and host
group mappings, resides in ``/etc/openstack_deploy/openstack_environment.yml``.

The ``/etc/openstack_deploy/env.d`` directory sources all YAML files into the
deployed environment, allowing a deployer to define additional group mappings
without having to edit the ``openstack_environment.yml`` file, which is
controlled by the openstack-ansible project itself.

conf.d
------

Common OpenStack services and their configuration are defined by
openstack-ansible in the
``/etc/openstack_deploy/openstack_user_config.yml`` settings file.

Additional services should be defined with a YAML file in
``/etc/openstack_deploy/conf.d``, in order to manage file size.


user\_*.yml files
-----------------

Files in ``/etc/openstack_deploy`` beginning with ``user_`` will be automatically
sourced in any ``openstack-ansible`` command. Alternatively, the files can be
sourced with the ``-e`` parameter of the ``ansible-playbook`` command.

``user_variables.yml`` and ``user_secrets.yml`` are used directly by
openstack-ansible; adding custom values here is not recommended.

``user_extras_variables.yml`` and ``users_extras_secrets.yml`` are provided
and can contain deployer's custom values, but deployers can add any other
files they wish to include new configuration, or override existing.

Ordering and Precedence
+++++++++++++++++++++++

``user_*.yml`` variables are just YAML variable files. They will be sourced
in alphanumeric order by ``openstack-ansible``.

Adding Galaxy roles
-------------------

Any roles defined in ``openstack-ansible/ansible-role-requirements.yml``
will be installed by the
``openstack-ansible/scripts/bootstrap-ansible.sh`` script.


Setting overrides in configuration files
----------------------------------------

All of the services that use YAML, JSON, or INI for configuration can recieve
overrides through the use of a Ansible action plugin named ``config_template``.
The configuration template engine allows a deployer to use a simple dictionary
to modify or add items into configuration files at run time that may not have a
preset template option. All OpenStack-Ansible roles allow for this functionality
where applicable. Files available to receive overrides can be seen in the
``defaults/main.yml`` file as standard empty dictionaries (hashes).


Module documentation
++++++++++++++++++++

These are the options available as found within the virtual module documentation
section.

.. code-block:: yaml

    module: config_template
    version_added: 1.9.2
    short_description: >
      Renders template files providing a create/update override interface
    description:
      - The module contains the template functionality with the ability to
        override items in config, in transit, though the use of an simple
        dictionary without having to write out various temp files on target
        machines. The module renders all of the potential jinja a user could
        provide in both the template file and in the override dictionary which
        is ideal for deployers whom may have lots of different configs using a
        similar code base.
      - The module is an extension of the **copy** module and all of attributes
        that can be set there are available to be set here.
    options:
      src:
        description:
          - Path of a Jinja2 formatted template on the local server. This can
            be a relative or absolute path.
        required: true
        default: null
      dest:
        description:
          - Location to render the template to on the remote machine.
        required: true
        default: null
      config_overrides:
        description:
          - A dictionary used to update or override items within a configuration
            template. The dictionary data structure may be nested. If the target
            config file is an ini file the nested keys in the ``config_overrides``
            will be used as section headers.
      config_type:
        description:
          - A string value describing the target config type.
        choices:
          - ini
          - json
          - yaml


Example task using the "config_template" module
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: yaml

   - name: Run config template ini
     config_template:
       src: test.ini.j2
       dest: /tmp/test.ini
       config_overrides: {{ test_overrides }}
       config_type: ini


Example overrides dictionary(hash)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: yaml

   test_overrides:
     DEFAULT:
       new_item: 12345


Original template  file "test.ini.j2"
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: ini

   [DEFAULT]
   value1 = abc
   value2 = 123


Rendered on disk file "/tmp/test.ini"
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: ini

   [DEFAULT]
   value1 = abc
   value2 = 123
   new_item = 12345


In this task the ``test.ini.j2`` file is a template which will be rendered and
written to disk at ``/tmp/test.ini``. The **config_overrides** entry is a
dictionary(hash) which allows a deployer to set arbitrary data as overrides to
be written into the configuration file at run time. The **config_type** entry
specifies the type of configuration file the module will be interacting with;
available options are "yaml", "json", and "ini".


These are the current overrides available
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

All of these options can be specified in any way that suits your deployment.
In terms of ease of use and flexibility it's recommended that you define your
overrides in a user variable file such as
``/etc/openstack_deploy/user_variables.yml``.

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
