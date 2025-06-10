.. _user-overrides:

Overriding default configuration
================================

Variable precedence
~~~~~~~~~~~~~~~~~~~

Role defaults
-------------

Every role has a file, ``defaults/main.yml`` which holds the
usual variables overridable by a deployer, like a regular Ansible
role. This defaults are the closest possible to OpenStack standards.

They can be overridden at multiple levels.

Group vars and host vars
------------------------

OpenStack-Ansible provides safe defaults for deployers in its
group_vars folder. They take care of the wiring between different
roles, like for example storing information on how to reach
RabbitMQ from nova role.

You can override the existing group vars (and host vars) by creating
your own folder in ``/etc/openstack_deploy/group_vars`` (and
``/etc/openstack_deploy/host_vars`` respectively).

If you want to change the location of the override folder, you
can adapt your ``user.rc`` file (see details in :ref:`defining_environment_variables_for_deployment`),
or export
``GROUP_VARS_PATH`` and ``HOST_VARS_PATH`` during your shell session.

Role vars
---------

Every role makes use of additional variables in ``vars/`` which take
precedence over group vars.

These variables are typically internal to the role and are not
designed to be overridden. However, deployers may choose to override
them using extra-vars by placing the overrides into the user variables
file.

User variables
--------------

If you want to globally override variable, you can define
the variable you want to override in a
``/etc/openstack_deploy/user_*.yml`` file. It will apply on all hosts.

user_*.yml files in more details
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Files in ``/etc/openstack_deploy`` beginning with ``user_`` will be
automatically sourced in any ``openstack-ansible`` command. Alternatively,
the files can be sourced with the ``-e`` parameter of the ``ansible-playbook``
command.

``user_variables.yml`` and ``user_secrets.yml`` are used directly by
OpenStack-Ansible. Adding custom variables used by your own roles and
playbooks to these files is not recommended. Doing so will complicate your
upgrade path by making comparison of your existing files with later versions
of these files more arduous. Rather, recommended practice is to place your own
variables in files named following the ``user_*.yml`` pattern so they will be
sourced alongside those used exclusively by OpenStack-Ansible.

``user_*.yml`` files contain YAML variables which are applied as extra-vars
when executing ``openstack-ansible`` to run playbooks. They will be sourced
in alphanumeric order by ``openstack-ansible``. If duplicate variables occur
in the ``user_*.yml`` files, the variable in the last file read will take
precedence.

Setting overrides in configuration files with config_template
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

All of the services that use YAML, JSON, or INI for configuration can receive
overrides through the use of a Ansible action plugin named ``config_template``.
The configuration template engine allows a deployer to use a simple dictionary
to modify or add items into configuration files at run time that may not have a
preset template option. All OpenStack-Ansible roles allow for this
functionality where applicable. Files available to receive overrides can be
seen in the ``defaults/main.yml`` file as standard empty dictionaries (hashes).

This module was not accepted into Ansible Core (see `PR1`_ and `PR2`_), and
will never be.

.. _PR1: https://github.com/ansible/ansible/pull/12555
.. _PR2: https://github.com/ansible/ansible/pull/35453

config_template documentation
-----------------------------

These are the options available as found within the virtual module
documentation section.

.. code-block:: yaml

    module: config_template
    version_added: 1.9.2
    short_description: >
      Renders template files providing a create/update override interface
    description:
      - The module contains the template functionality with the ability to
        override items in config, in transit, through the use of a simple
        dictionary without having to write out various temp files on target
        machines. The module renders all of the potential jinja a user could
        provide in both the template file and in the override dictionary which
        is ideal for deployers who may have lots of different configs using a
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

Example task using the config_template module
---------------------------------------------

In this task the ``test.ini.j2`` file is a template which will be rendered and
written to disk at ``/tmp/test.ini``. The **config_overrides** entry is a
dictionary (hash) which allows a deployer to set arbitrary data as overrides to
be written into the configuration file at run time. The **config_type** entry
specifies the type of configuration file the module will be interacting with;
available options are "yaml", "json", and "ini".

.. code-block:: yaml

   - name: Run config template ini
     config_template:
       src: test.ini.j2
       dest: /tmp/test.ini
       config_overrides: "{{ test_overrides }}"
       config_type: ini

Here is an example override dictionary (hash):

.. code-block:: yaml

   test_overrides:
     DEFAULT:
       new_item: 12345

And here is the template file:

.. code-block:: ini

   [DEFAULT]
   value1 = abc
   value2 = 123

The rendered file on disk, namely ``/tmp/test.ini`` looks like
this:

.. code-block:: ini

   [DEFAULT]
   value1 = abc
   value2 = 123
   new_item = 12345

Discovering available overrides
-------------------------------

All of these options can be specified in any way that suits your deployment.
In terms of ease of use and flexibility it's recommended that you define your
overrides in a user variable file such as
``/etc/openstack_deploy/user_variables.yml``.

The list of overrides available may be found by executing:

.. code-block:: bash

    ls /etc/ansible/roles/*/defaults/main.yml -1 \
        | xargs -I {} grep '_.*_overrides:' {} \
        | egrep -v "^#|^\s" \
        | sort -u

.. note::

   Possible additional overrides can be found in the "Tunable Section"
   of each role's ``main.yml`` file, such as
   ``/etc/ansible/roles/role_name/defaults/main.yml``.

Overriding OpenStack configuration defaults
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

OpenStack has many configuration options available in ``.conf`` files
(in a standard ``INI`` file format),
policy files (in a standard ``JSON`` format) and ``YAML`` files, and
can therefore use the ``config_template`` module described above.

OpenStack-Ansible enables you to reference any options in the
`OpenStack Configuration Reference`_ through the use of a simple set of
configuration entries in the ``/etc/openstack_deploy/user_variables.yml``.

.. _OpenStack Configuration Reference: https://docs.openstack.org/latest/configuration/

Overriding .conf files
----------------------

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

The same way you can apply overrides to the uwsgi services. For example:

.. code-block:: yaml

    nova_api_os_compute_uwsgi_ini_overrides:
      uwsgi:
        limit: 1024

.. note::

  Some roles, like uwsgi, are used for lot of roles, and have "special" overrides,
  (like `uwsgi_ini_overrides`) which can be defined to impact all services which
  are using uwsgi. These variables are "special" as they will have precedence over
  role defined `*_uwsgi_ini_overrides`.

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
----------------------

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
---------------------

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

Overriding OpenStack upper constraints
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Each OpenStack release uses an ``upper-constraints.txt`` file to define the
maximum permitted version of each Python package. In some cases it may be
necessary to override this file, for example when your local deployment needs
to take advantage of a bug fix. Care should be taken when modifying this file
as OpenStack services may not have been tested against more recent package
versions.

To override the upper constraints for a deployment, clone the OpenStack
requirements git repository, either storing it as a fork at a URL of your
choice, or within the local filesystem of the host you are using to deploy
OpenStack Ansible from. Once cloned, switch to the branch which matches the
name of your deployed OpenStack version, and modify the upper constraints as
required.

Next, edit your ``/etc/openstack_deploy/user_variables.yml`` file to indicate
the path to the requirements git repository, and the git hash of the commit
containing your changes using the ``requirements_git_repo`` and
``requirements_git_install_branch`` variables. When using the local
filesystem, the ``requirements_git_repo`` should start with ``file://``.

Finally, run the ``repo-install.yml`` playbook to upload these modified
constraints to your repo host(s).
