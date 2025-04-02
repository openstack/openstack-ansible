.. _tests:

=======
Testing
=======

Adding tests to a new role
==========================

Each of the role tests is in its tests/ folder.

This folder contains at least the following files:

* ``test.yml`` ("super" playbook acting as test router to sub-playbooks)
* ``<role name>-overrides.yml``. This var file is automatically loaded
  by our shell script in our `tests repository`_.
* ``inventory``. A static inventory for role testing.
  It's possible some roles have multiple inventories. See for example the
  neutron role with its ``ovs_inventory``.
* ``group_vars`` and ``host_vars``. These folders will hold override the
  necessary files for testing. For example, this is where you override
  the IP addresses, IP ranges, and ansible connection details.
* ``ansible-role-requirements.yml``. This should be fairly straightforward:
  this file contains all the roles to clone before running your role.
  The roles' relative playbooks will have to be listed in the ``test.yml``
  file. However, keep in mind to NOT re-invent the wheel. For example,
  if your role needs keystone, you don't need to create your own keystone
  install playbook, because we have a generic keystone install playbook
  in the `tests repository`.
* Only add a ``zuul.d`` folder when your role is imported into the
  openstack-ansible namespace.

.. _tests repository: https://opendev.org/openstack/openstack-ansible-tests

Extending tests of an existing role
===================================

#. Modify the tox.ini to add your new scenario. If required, you can
   override the inventory, and/or the variable files.
#. Add a new non-voting job in ``zuul.d/jobs.yaml``, and wire it in
   the project tests file ``zuul.d/project.yaml``.

.. _tempest-testing:

Improve testing with tempest
============================

Once the initial convergence is working and the services are running,
the role development should focus on implementing some level of
functional testing.

Ideally, the functional tests for an OpenStack role
should make use of Tempest to execute the functional tests. The ideal
tests to execute are scenario tests as they test the functions that
the service is expected to do in a production deployment. In the absence
of any scenario tests for the service a fallback option is to implement
the smoke tests instead.

If no tempest is provided, some other functional testing should be done.
For APIs, you can probably check the HTTP response codes, with
specially crafted requests.

.. _devel_and_testing:

Running tests locally
=====================

Linting
-------

Python coding conventions are tested using `PEP8`_, with the following
convention exceptions:

* F403 - 'from ansible.module_utils.basic import \*'

Testing may be done locally by executing:

.. code-block:: bash

    ./run_tests.sh pep8

Bash coding conventions are tested using `Bashate`_, with the following
convention exceptions:

* E003: Indent not multiple of 4. We prefer to use multiples of 2 instead.
* E006: Line longer than 79 columns. As many scripts are deployed as templates
        and use jinja templating, this is very difficult to achieve. It is
        still considered a preference and should be a goal to improve
        readability, within reason.
* E040: Syntax error determined using `bash -n`. As many scripts are deployed
        as templates and use jinja templating, this will often fail. This
        test is reasonably safely ignored as the syntax error will be
        identified when executing the resulting script.

Testing may be done locally by executing:

.. code-block:: bash

    ./run_tests.sh bashate

Ansible is lint tested using `ansible-lint`_.

Testing may be done locally by executing:

.. code-block:: bash

    ./run_tests.sh ansible-lint

Ansible playbook syntax is tested using ansible-playbook.

Testing may be done locally by executing:

.. code-block:: bash

    ./run_tests.sh ansible-syntax

A consolidated set of all lint tests may be done locally by executing:

.. code-block:: bash

    ./run_tests.sh linters

.. _PEP8: https://www.python.org/dev/peps/pep-0008/
.. _Bashate: https://opendev.org/openstack/bashate
.. _ansible-lint: https://github.com/ansible/ansible-lint

Documentation building
----------------------

Documentation is developed in reStructuredText_ (RST) and compiled into
HTML using Sphinx.

Documentation may be built locally by executing:

.. code-block:: bash

    ./run_tests.sh docs

.. _reStructuredText: http://docutils.sourceforge.net/rst.html

The OpenStack-Ansible integrated repo also has an extra documentation
building process, to build the deployment guide.

This guide may be built locally by executing:

.. code-block:: bash

    ./run_tests.sh deploy-guide

Release notes building
----------------------

Release notes are generated using the `the reno tool`_ and compiled into
HTML using Sphinx.

Release notes may be built locally by executing:

.. code-block:: bash

    ./run_tests.sh releasenotes

.. _the reno tool: https://docs.openstack.org/reno/latest/

.. note::

   The ``releasenotes`` build argument only tests committed changes.
   Ensure your local changes are committed before running the
   ``releasenotes`` build.

Roles functional or scenario testing
------------------------------------

To run a functional test of the role, execute:

.. code-block:: bash

    ./run_tests.sh functional

.. _integrate-new-role-with-aio:

Testing a new role with an AIO
==============================

#. Include your role on the deploy host.
   See also :ref:`extend_osa_roles`.
#. Perform any other host preparation (such as the tasks performed by the
   ``bootstrap-aio.yml`` playbook). This includes any preparation tasks that
   are particular to your service.
#. Generate files to include your service in the Ansible inventory
   using ``env.d`` and ``conf.d`` files for use on your deploy host.

   .. HINT:: You can follow examples from other roles, making the appropriate
      modifications being sure that group labels in ``env.d`` and ``conf.d``
      files are consistent.

   .. HINT:: A description of how these work can be
     found in :ref:`inventory-confd` and :ref:`inventory-envd`.

#. Generate secrets, if any, as described in the :deploy_guide:`Configure
   Service Credentials <configure.html#configuring-service-credentials>`.
   You can append your keys to an existing ``user_secrets.yml`` file or add a
   new file to the ``openstack_deploy`` directory to contain them. Provide
   overrides for any other variables you will need at this time as well, either
   in ``user_variables.yml`` or another file.

   See also our :ref:`user-overrides` page.

   Any secrets required for the role to work must be noted in the
   ``etc/openstack_deploy/user_secrets.yml`` file for reuse by other users.

#. If your service is installed from source or relies on python packages which
   need to be installed from source, specify a repository for the source
   code of each requirement by adding a file to your deploy host under
   ``inventory/group_vars/<service_group>/source_git.yml`` in the
   OpenStack-Ansible source repository and following the pattern of files
   currently in that directory. You could also simply add an entry to an
   existing file there.

#. Make any required adjustments to the load balancer configuration
   (e.g. modify ``inventory/group_vars/all/haproxy.yml`` in the
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
   ``inventory/group_vars``. The group vars are essentially the
   glue which playbooks use to ensure that all roles are given the
   appropriate information. When group vars are implemented it should be a
   minimum set to achieve the goal of integrating the new role into the
   integrated build.

#. Documentation must be added in the role to describe how to implement
   the new service in an integrated environement. This content must
   adhere to the :ref:`documentation`. Until the
   role has integrated functional testing implemented (see also the
   Role development maturity paragraph), the documentation
   must make it clear that the service inclusion in OpenStack-Ansible is
   experimental and is not fully tested by OpenStack-Ansible in an
   integrated build. Alternatively, an user story can be created.

#. A feature release note must be added to announce the new service
   availability and to refer to the role documentation for further
   details. This content must adhere to the
   :ref:`documentation`.

#. It must be possible to execute a functional, integrated test which
   executes a deployment in the same way as a production environment. The
   test must execute a set of functional tests using Tempest. This is the
   required last step before a service can remove the experimental warning
   from the documentation.

.. HINT:: If you adhere to the pattern of isolating your role's extra
   deployment requirements (secrets and var files, HAProxy yml fragments,
   repo_package files, etc.) in their own files it makes it easy for you to
   automate these additional steps when testing your role.

Integrated repo functional or scenario testing
----------------------------------------------

To test the integrated repo, follow the
:deploy_guide:`Deployment Guide <index.html>`

Alternatively, you can check the :ref:`aio guide<quickstart-aio>`,
or even run the gate wrapper script,
named ``scripts/gate-check-commit.sh``, described below.

The OpenStack Infrastructure automated tests
============================================

There should be no difference between running tests in the openstack
infrastructure, versus running locally.

The tests in the openstack infrastructure are triggered by jobs
defined in each repo ``zuul.d`` folder.

See also the `zuul user guide`_.

However, for reliability purposes, a few variables are defined
to point to the OpenStack infra pypi and packages mirrors.

.. _zuul user guide: https://zuul-ci.org/docs/zuul/user/index.html

The integrated repo functional test is using the
``scripts/gate-check-commit.sh`` script, which receives arguments
from the zuul run playbook definition.

While this script is primarily developed and maintained for use in
OpenStack-CI, it can be used in other environments.

.. _role-maturity:

Role development maturity
=========================

A role may be fully mature, even if it is not integrated in the
``openstack-ansible`` repository. The maturity depends on its
testing levels.

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
----------------------------

If a role has failed periodics or gate test for two weeks, a bug
should be filed, and a message to the mailing list will be sent,
referencing the bug.

The next community meeting should discuss about role deprecation,
and if no contributor comes forward to fix the role, periodic
testing will be turned off, and the role will move to an
``unmaintained`` state.

.. _role-maturity-matrix:

Maturity Matrix
---------------

All of the OpenStack-Ansible roles do not have the same level of maturity and
testing.

Here is a dashboard of the current status of the roles:

.. raw:: html
   :file: role-maturity-matrix.html
