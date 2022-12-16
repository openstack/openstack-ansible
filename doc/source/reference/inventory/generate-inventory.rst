Generating the Inventory
========================

The script that creates the inventory is located at
``inventory/dynamic_inventory.py`` and installed into the ansible-runtime
virtualenv as ``openstack-ansible-inventory``.

This section explains how ansible runs the inventory, and how
you can run it manually to see its behavior.

Executing the dynamic_inventory.py script manually
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

When running an Ansible command (such as ``ansible``, ``ansible-playbook`` or
``openstack-ansible``) Ansible automatically executes the
``dynamic_inventory.py`` script
and use its output as inventory.

Run the following command:

.. code-block:: bash

    # from the root folder of cloned OpenStack-Ansible repository
    inventory/dynamic_inventory.py --config /etc/openstack_deploy/

Dynamic inventory script is also installed inside virtualenv as a script. So
alternatively you can run following:

.. code-block:: bash

    source /opt/ansible-runtime/bin/activate
    openstack-ansible-inventory --config /etc/openstack_deploy/

This invocation is useful when testing changes to the dynamic inventory script.

Inputs
~~~~~~

The ``dynamic_inventory.py`` takes the ``--config`` argument for the directory
holding configuration from which to create the inventory. If not specified,
the default is ``/etc/openstack_deploy/``.

In addition to this argument, the base environment skeleton is provided in the
``inventory/env.d`` directory of the OpenStack-Ansible codebase.

Should an ``env.d`` directory be found in the directory specified by
``--config``, its contents will be added to the base environment, overriding
any previous contents in the event of conflicts.

.. note::

   In all versions prior to |previous_release_formal_name|, this argument was ``--file``.

The following file must be present in the configuration directory:

* ``openstack_user_config.yml``

Additionally, the configuration or environment could be spread between two
additional sub-directories:

* ``conf.d``
* ``env.d`` (for environment customization)

The dynamic inventory script does the following:

* Generates the names of each container that runs a service
* Creates container and IP address mappings
* Assigns containers to physical hosts

As an example, consider the following excerpt from
``openstack_user_config.yml``:

.. code-block :: yaml

    identity_hosts:
      infra01:
        ip: 10.0.0.10
      infra02:
        ip: 10.0.0.11
      infra03:
        ip: 10.0.0.12

The ``identity_hosts`` dictionary defines an Ansible inventory group named
``identity_hosts`` containing the three infra hosts. The configuration file
``inventory/env.d/keystone.yml`` defines additional Ansible
inventory groups for the containers that are deployed onto the three hosts
named with the prefix *infra*.

Note that any services marked with ``is_metal: true`` will run on the allocated
physical host and not in a container. For an example of ``is_metal: true``
being used refer to ``inventory/env.d/cinder.yml`` in the
``container_skel`` section.

For more details, see :ref:`configuring-inventory`.

Outputs
~~~~~~~

Once executed, the script will output an ``openstack_inventory.json`` file into
the directory specified with the ``--config`` argument. This is used as the
source of truth for repeated runs.

.. warning::

    The ``openstack_inventory.json`` file is the source of truth for the
    environment. Deleting this in a production environment means that the UUID
    portion of container names will be regenerated, which then results in new
    containers being created. Containers generated under the previous version
    will no longer be recognized by Ansible, even if reachable via SSH.

The same JSON structure is printed to stdout, which is consumed by Ansible as
the inventory for the playbooks.

Checking inventory configuration for errors
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Using the ``--check`` flag when running ``dynamic_inventory.py`` will run the
inventory build process and look for known errors, but not write any files to
disk.

If any groups defined in the ``openstack_user_config.yml`` or ``conf.d`` files
are not found in the environment, a warning will be raised.

This check does not do YAML syntax validation, though it will fail if there
are unparseable errors.

Writing debug logs
~~~~~~~~~~~~~~~~~~~

The ``--debug/-d`` parameter allows writing of a detailed log file for
debugging the inventory script's behavior. The output is written to
``inventory.log`` in the current working directory.

The ``inventory.log`` file is appended to, not overwritten.

Like ``--check``, this flag is not invoked when running from ansible.


Running with tox
~~~~~~~~~~~~~~~~

In some cases you might want to generate inventory on operator local machines
after altering openstack_user_config.yml or env.d/conf.d files. Given that
you already have ``openstack_deploy`` directory on such machine, you can create
tox.ini file in that directory with following content:

.. code-block::

  [tox]
  envlist = generate_inventory

  [testenv]
  skip_install = True
  usedevelop = True
  allowlist_externals =
      bash

  [testenv:generate_inventory]
  basepython = python3
  deps = -rhttps://opendev.org/openstack/openstack-ansible/raw/branch/master/requirements.txt
  install_command =
      pip install -c https://releases.openstack.org/constraints/upper/master {packages} -e git+https://opendev.org/openstack/openstack-ansible@master\#egg=openstack-ansible
  commands =
      openstack-ansible-inventory --config {toxinidir}/openstack_deploy

Then you can run a command to generate inventory using tox:

.. code-block:: bash

  tox -e generate_inventory

As a result you will get your openstack_user_config.json updated. You can use
this method also to verify validity of the inventory.
