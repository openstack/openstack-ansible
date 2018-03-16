Using overrides
===============

user_*.yml files
~~~~~~~~~~~~~~~~

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

Ordering and precedence
~~~~~~~~~~~~~~~~~~~~~~~

``user_*.yml`` files contain YAML variables which are applied as extra-vars
when executing ``openstack-ansible`` to run playbooks. They will be sourced
in alphanumeric order by ``openstack-ansible``. If duplicate variables occur
in the ``user_*.yml`` files, the variable in the last file read will take
precedence.

Adding extra python packages into the environment
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The system will allow you to install and build any package that is a python
installable. The repository infrastructure will look for and create any
git based or PyPi installable package. When the package is built the repo-build
role will create the sources as Python wheels to extend the base system and
requirements.

While the packages pre-built in the repository-infrastructure are
comprehensive, it may be needed to change the source locations and versions of
packages to suit different deployment needs. Adding additional repositories as
overrides is as simple as listing entries within the variable file of your
choice. Any ``user_.*.yml`` file within the "/etc/openstack_deployment"
directory will work to facilitate the addition of a new packages.


.. code-block:: yaml

    swift_git_repo: https://private-git.example.org/example-org/swift
    swift_git_install_branch: master


Additional lists of python packages can also be overridden using a
``user_.*.yml`` variable file.

.. code-block:: yaml

    swift_requires_pip_packages:
      - virtualenv
      - python-keystoneclient
      - NEW-SPECIAL-PACKAGE


Once the variables are set call the play ``repo-build.yml`` to build all of the
wheels within the repository infrastructure. When ready run the target plays to
deploy your overridden source code.

Setting overrides in configuration files
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

All of the services that use YAML, JSON, or INI for configuration can receive
overrides through the use of a Ansible action plugin named ``config_template``.
The configuration template engine allows a deployer to use a simple dictionary
to modify or add items into configuration files at run time that may not have a
preset template option. All OpenStack-Ansible roles allow for this
functionality where applicable. Files available to receive overrides can be
seen in the ``defaults/main.yml`` file as standard empty dictionaries (hashes).

Practical guidance for using this feature is available in the
:deploy_guide:`Deployment Guide <app-advanced-config-override.html>`.

This module has been `rejected for inclusion`_ into Ansible Core.

.. _rejected for inclusion: https://github.com/ansible/ansible/pull/12555


config_template documentation
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

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
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: yaml

   - name: Run config template ini
     config_template:
       src: test.ini.j2
       dest: /tmp/test.ini
       config_overrides: "{{ test_overrides }}"
       config_type: ini


Example overrides dictionary (hash)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: yaml

   test_overrides:
     DEFAULT:
       new_item: 12345


Original template file ``test.ini.j2``
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: ini

   [DEFAULT]
   value1 = abc
   value2 = 123


Rendered on disk file ``/tmp/test.ini``
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: ini

   [DEFAULT]
   value1 = abc
   value2 = 123
   new_item = 12345


In this task the ``test.ini.j2`` file is a template which will be rendered and
written to disk at ``/tmp/test.ini``. The **config_overrides** entry is a
dictionary (hash) which allows a deployer to set arbitrary data as overrides to
be written into the configuration file at run time. The **config_type** entry
specifies the type of configuration file the module will be interacting with;
available options are "yaml", "json", and "ini".


Discovering available overrides
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

All of these options can be specified in any way that suits your deployment.
In terms of ease of use and flexibility it's recommended that you define your
overrides in a user variable file such as
``/etc/openstack_deploy/user_variables.yml``.

The list of overrides available may be found by executing:

.. code-block:: bash

    find . -name "main.yml" -exec grep '_.*_overrides:' {} \; \
        | grep -v "^#" \
        | sort -u
