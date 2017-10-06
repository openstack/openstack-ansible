==================================
Contributing to Roles and Services
==================================

If you would like to contribute towards a role to introduce an OpenStack
or infrastructure service, or to improve an existing role, the
OpenStack-Ansible project would welcome that contribution and your assistance
in maintaining it.

Recommended procedure to develop a role
---------------------------------------

#. Deploy OpenStack-Ansible (possibly using
   `an AIO`_
   deploy) so that you have the rest of an OpenStack cluster to integrate with
   in your testing.
#. Deploy your service on another VM, or possibly directly on the AIO host, by
   hand. Configure the service to coordinate with the OpenStack cluster
   appropriately. When all the related systems are communicating with each
   other you can use the resulting configuration as a reference later.
#. Develop a role for your service. A recommended process is detailed below.

.. _an AIO: quickstart-aio.html

Writing a new role
------------------

Here are the steps to write the role:

#. You can review roles which may be currently in development by checking our
   `specs repository`_ and `unmerged specs`_ on review.openstack.org. If you
   do not find a spec for the role, propose a blueprint/spec `(see also the
   spec template)`_ outlining the new Role. By proposing a draft spec you can
   help the OpenStack-Ansible community keep track of what roles are being
   developed and perhaps connect you with others who may be interested and
   able to help you in the process.
#. Create a source repository (e.g. on Github) to start your work on the Role.
#. Generate the reference directory structure for an Ansible role which is
   the necessary subset of the documented `Best Practice`_. You might use
   Ansible Galaxy tools to do this for you (e.g. ``ansible-galaxy init``).
   You may additionally want to include directories such as ``docs`` and
   ``examples`` and ``tests`` for your role.
#. Generate a meta/main.yml right away. This file is important to Ansible to
   ensure your dependent roles are installed and available and provides others
   with the information they will need to understand the purpose of your role.

#. Develop task files for each of the install stages in turn, creating any
   handlers and templates as needed. Ensure that you notify handlers after any
   task which impacts the way the service would run (such as configuration
   file modifications). Also take care that file ownership and permissions are
   appropriate.

   .. HINT:: Fill in variable defaults, libraries, and prerequisites as you
      discover a need for them. You can also develop documentation for your
      role at the same time.

#. Add tests to the role.
#. Ensuring the role matches OpenStack-Ansible's latest standards.
#. Deploying the role on an AIO.

Writing tasks in a role
^^^^^^^^^^^^^^^^^^^^^^^

Most OpenStack services will follow a common series of stages to install or
update a service deployment. This is apparent when you review `tasks/main.yml`
for existing roles.

#. pre-install: prepare the service user group and filesystem directory paths
   on the host or container
#. install: install system packages, prepare the (optional) service virtual
   environment, install service and requirements (into a virtual environment)
#. post-install: apply all configuration files
#. service add: register the service (each of: service type, service project,
   service user, and endpoints) within Keystone's service catalog.
#. service setup: install a service-startup script (init, upstart, systemd,
   etc.) so that the service will start up when the container or host next
   starts.
#. service init/startup: signal to the host or container to start the services,
   make sure the service runs on boot.

There may be other specialized steps required by some services but most of the
roles will perform all of these at a minimum. Begin by reviewing a role for a
service that has something in common with your service and think about how you
can fit most of the common service setup and configuration steps into that
model.

.. HINT:: Following the patterns you find in other roles can help ensure your role
   is easier to use and maintain.

.. _(see also the spec template): https://git.openstack.org/cgit/openstack/openstack-ansible-specs/tree/specs/templates/template.rst
.. _specs repository: https://git.openstack.org/cgit/openstack/openstack-ansible-specs
.. _unmerged specs: https://review.openstack.org/#/q/status:+open+project:openstack/openstack-ansible-specs
.. _Best Practice: https://docs.ansible.com/ansible/playbooks_best_practices.html#directory-layout

Keep in mind a role candidate for inclusion should respect our
`Ansible Style Guide`_.

.. _Ansible Style Guide: contribute.html#ansible-style-guide

Adding tests to a role
^^^^^^^^^^^^^^^^^^^^^^

Each of the role tests is in its tests/ folder.

This folder contains at least the following files:

#. ``test.yml`` ("super" playbook acting as test router to sub-playbooks)
#. ``<role name>-overrides.yml``. This var file is automatically loaded
   by our shell script in our `tests repository`_.
#. ``inventory``. A static inventory for role testing.
   It's possible some roles have multiple inventories. See for example the
   neutron role with its ``lxb_inventory``, ``calico_inventory``.
#. ``group_vars`` and ``host_vars``. These folders will hold override the
   necessary files for testing. For example, this is where you override
   the IP addresses, IP ranges, and ansible connection details.
#. ``ansible-role-requirements.yml``. This should be fairly straightforward:
   this file contains all the roles to clone before running your role.
   The roles' relative playbooks will have to be listed in the ``test.yml``
   file. However, keep in mind to NOT re-invent the wheel. For example,
   if your role needs keystone, you don't need to create your own keystone
   install playbook, because we have a generic keystone install playbook
   in the `tests repository`.

.. _tests repository: https://git.openstack.org/cgit/openstack/openstack-ansible-tests

Ensuring the role matches OpenStack-Ansible's standards
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

#. To facilitate the development and tests implemented across all
   OpenStack-Ansible roles, a base set of folders and files need to be
   implemented. A base set of configuration and test facilitation scripts must
   include at least the following:

   * ``tox.ini``:
     The lint testing, documentation build, release note build and
     functional build execution process for the role's gate tests are all
     defined in this file.
   * ``test-requirements.txt``:
     The Python requirements that must be installed when executing the
     tests.
   * ``bindep.txt``:
     The binary requirements that must be installed on the host the tests
     are executed on for the Python requirements and the tox execution to
     work. This must be copied from the
     ``openstack-ansible-tests`` repository and will be automatically
     be overriden by our proposal bot should any change happen.
   * ``setup.cfg`` and ``setup.py``:
     Information about the repository used when building artifacts.
   * ``run_tests.sh``:
     A script for developers to execute all standard tests on a
     suitable host. This must be copied from the
     ``openstack-ansible-tests`` repository and will be automatically
     be overriden by our proposal bot should any change happen.
   * ``Vagrantfile``:
     A configuration file to allow a developer to easily create a
     test virtual machine using `Vagrant`_. This must automatically execute
     ``run_tests.sh``. This must be copied from the
     ``openstack-ansible-tests`` repository and will be automatically
     be overriden by our proposal bot should any change happen.
   * ``README.rst``, ``LICENSE``, ``CONTRIBUTING.rst``:
     A set of standard files whose content is self-explanatory.
   * ``.gitignore``:
     A standard git configuration file for the repository which should be
     pretty uniform across all the repositories. This must be copied from the
     ``openstack-ansible-tests`` repository and will be automatically
     be overriden by our proposal bot should any change happen.
   * ``.gitreview``:
     A standard file configured for the project to inform the ``git-review``
     plugin where to find the upstream gerrit remote for the repository.
   * ``tests/tests-repo-clone.sh`` needs to be copied from the
     ``openstack-ansible-tests`` repository.

   Please have a look at a role like os_cinder, os_keystone, or os_neutron
   for latest files.

#. The role development should initially be focused on implementing a set of
   tasks and a test playbook which converge. The convergence must:

   * Implement ``developer_mode`` to build from a git source into a Python
     virtual environment.
   * Deploy the applicable configuration files in the right places.
   * Ensure that the service starts.

   The convergence may involve consuming other OpenStack-Ansible roles (For
   example: ``galera_server``, ``galera_client``, ``rabbitmq_server``) in
   order to ensure that the appropriate infrastructure is in place. Re-using
   existing roles in OpenStack-Ansible or Ansible Galaxy is strongly
   encouraged.

#. The role *must* support Ubuntu 16.04 LTS. It should
   ideally also support CentOS 7 and openSUSE 42.X but this is not required
   at this time. The patterns to achieve this include:

   * The separation of platform specific variables into role vars files.
   * The detection and handling of different init systems (init.d, SystemD).
   * The detection and handling of different package managers (apt, yum).
   * The detection and handling of different network configuration methods.

   There are several examples of these patterns implemented across many of
   the OpenStack-Ansible roles. Developers are advised to inspect the
   established patterns and either implement or improve upon them.

#. The role implementation should be done in such a way that it is agnostic
   with regards to whether it is implemented in a container, or on a
   physical host. The test infrastructure may make use of LXC containers for
   the separation of services, but if a role is used by a playbook that
   targets a host, it must work regardless of whether that host is a
   container, a virtual server, or a physical server. The use of LXC
   containers for role tests is not required but it may be useful in order
   to simulate a multi-node build out as part of the testing infrastructure.

#. Any secrets (For example: passwords) should not be provided with default
   values in the tasks, role vars, or role defaults. The tasks should be
   implemented in such a way that any secrets required, but not provided,
   should result in the task execution failure. It is important for a
   secure-by-default implementation to ensure that an environment is not
   vulnerable due to the production use of default secrets. Deployers
   must be forced to properly provide their own secret variable values.

#. Once the initial convergence is working and the services are running,
   the role development should focus on implementing some level of
   functional testing. Ideally, the functional tests for an OpenStack role
   should make use of Tempest to execute the functional tests. The ideal
   tests to execute are scenario tests as they test the functions that
   the service is expected to do in a production deployment. In the absence
   of any scenario tests for the service a fallback option is to implement
   the smoke tests instead.

#. The role must include documentation. The `Documentation and Release Note
   Guidelines`_ provide specific guidelines with regards to style and
   conventions. The documentation must include a description of the
   mandatory infrastructure (For example: a database and a message queue are
   required), variables (For example: the database name and credentials) and
   group names (For example: The role expects a group named ``foo_all`` to
   be present and it expects the host to be a member of it) for the role's
   execution to succeed.

   .. _Documentation and Release Note Guidelines: contribute.html#documentation-and-release-note-guidelines
   .. _Vagrant: https://www.vagrantup.com/

Deploying the role
^^^^^^^^^^^^^^^^^^

#. Include your role on the deploy host. See also `Adding Galaxy roles`_.
#. Perform any other host preparation (such as the tasks performed by the
   ``bootstrap-aio.yml`` playbook). This includes any preparation tasks that
   are particular to your service.
#. Generate files to include your service in the Ansible inventory
   using `env.d`_ and `conf.d`_ files for use on your deploy host.

   .. HINT:: You can follow examples from other roles, making the appropriate
      modifications being sure that group labels in ``env.d`` and ``conf.d``
      files are consistent.

   .. HINT:: A description of how these work can be
     found in :deploy_guide:`Appendix C <app-custom-layouts.html>`
     of the Deployment Guide.

#. Generate secrets, if any, as described in the :deploy_guide:`Configure
   Service Credentials <configure.html#configuring-service-credentials>`.
   You can append your keys to an existing ``user_secrets.yml`` file or add a
   new file to the ``openstack_deploy`` directory to contain them. Provide
   overrides for any other variables you will need at this time as well, either
   in ``user_variables.yml`` or another file. This is explained in more depth
   under `Extending OpenStack-Ansible`_.
   Any secrets required for the role to work must be noted in the
   ``etc/openstack_deploy/user_secrets.yml`` file for reuse by other users.

#. If your service is installed from source or relies on python packages which
   need to be installed from source, specify a repository for the source
   code of each requirement by adding a file to your deploy host under
   ``playbooks/defaults/repo_packages`` in the OpenStack-Ansible source
   repository and following the pattern of files currently in that directory.
   You could also simply add an entry to an existing file there. Be sure to
   run the ``repo-build.yml`` play later so that wheels for your packages will
   be included in the repository infrastructure.
#. Make any required adjustments to the load balancer configuration
   (e.g. modify ``playbooks/inventory/group_vars/all/haproxy.yml`` in the
   OpenStack-Ansible source repository on your deploy host) so that your
   service can be reached through a load balancer, if appropriate, and be sure
   to run the ``haproxy-install.yml`` play later so your changes will be
   applied. Please note, you can also use ``haproxy_extra_services`` variable
   if you don't want to provide your service as default for everyone.
#. Put together a service install playbook file for your role. This can also
   be modeled from any existing service playbook that has similar
   dependencies to your service (database, messaging, storage drivers,
   container mount points, etc.). A common place to keep playbook files in a
   Galaxy role is in an ``examples`` directory off the root of the role.
   If the playbook is meant for installing an OpenStack service, name it
   ``os-<service>-install.yml`` and target it at the appropriate
   group defined in the service ``env.d`` file.
   It is crucial that the implementation of the service is optional and
   that the deployer must opt-in to the deployment through the population
   of a host in the applicable host group. If the host group has no
   hosts, Ansible skips the playbook's tasks automatically.
#. Any variables needed by other roles to connect to the new role, or by the
   new role to connect to other roles, should be implemented in
   ``playbooks/inventory/group_vars``. The group vars are essentially the
   glue which playbooks use to ensure that all roles are given the
   appropriate information. When group vars are implemented it should be a
   minimum set to achieve the goal of integrating the new role into the
   integrated build.
#. Documentation must be added in the role to describe how to implement
   the new service in an integrated environement. This content must
   adhere to the `Documentation and Release Note Guidelines`_. Until the
   role has integrated functional testing implemented (see also the
   Role development maturity paragraph), the documentation
   must make it clear that the service inclusion in OpenStack-Ansible is
   experimental and is not fully tested by OpenStack-Ansible in an
   integrated build.
#. A feature release note must be added to announce the new service
   availability and to refer to the role documentation for further
   details. This content must adhere to the
   `Documentation and Release Note Guidelines`_.
#. It must be possible to execute a functional, integrated test which
   executes a deployment in the same way as a production environment. The
   test must execute a set of functional tests using Tempest. This is the
   required last step before a service can remove the experimental warning
   from the documentation.

.. HINT:: If you adhere to the pattern of isolating your role's extra
   deployment requirements (secrets and var files, HAProxy yml fragments,
   repo_package files, etc.) in their own files it makes it easy for you to
   automate these additional steps when testing your role.

.. _Adding Galaxy roles: extending.html#adding-galaxy-roles
.. _env.d: extending.html#env-d
.. _conf.d: extending.html#conf-d
.. _Extending OpenStack-Ansible: extending.html#user-yml-files

Role development maturity
-------------------------

A role may be fully mature, even if it is not integrated in the
``openstack-ansible`` repository.

A role can be in one of the four maturity levels:

* ``Complete``
* ``Incubated``
* ``Unmaintained``
* ``Retired``

Here are a series of rules that define maturity levels:

* A role can be retired at any time if it is not relevant anymore.
* A role can be ``Incubated`` for maximum 2 cycles.
* An ``Incubated`` role that passes functional testing will be upgraded
  to the ``Complete`` status, and cannot return in ``Incubated`` status.
* An ``Incubated`` role that didn't implement functional testing in
  the six month timeframe will become ``Unmaintained``.
* A role in ``Complete`` status can be downgraded to ``Unmaintained``.
  status, according to the maturity downgrade procedure.

Maturity downgrade procedure
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

If a role has failed periodics or gate test for two weeks, a bug
should be filed, and a message to the mailing list will be sent,
referencing the bug.

The next community meeting should discuss about role deprecation,
and if no contributor comes forward to fix the role, periodic
testing will be turned off, and the role will move to an
``unmaintained`` state.

Maturity Matrix
^^^^^^^^^^^^^^^

View the following role maturity table to see each role's status.

.. _role maturity table: role-maturity.html
