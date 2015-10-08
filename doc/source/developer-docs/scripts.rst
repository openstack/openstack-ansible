`Home <index.html>`_ OpenStack-Ansible Developer Documentation

Included Scripts
================

The repository contains several helper scripts to manage gate jobs,
install base requirements, and update repository information. Execute
these scripts from the root of the respository clone. For example:

.. code:: bash

   $ scripts/<script_name>.sh

Bootstrapping
^^^^^^^^^^^^^

bootstrap-aio.sh
----------------

The ``bootstrap-aio.sh`` script prepares a host for an *all-in-one* (AIO)
deployment for the purposes of development and gating. Create the necessary
partitions, directories, and configurations. Configurable via environment
variables to work with Jenkins.

bootstrap-ansible.sh
--------------------

The ``bootstrap-ansible.sh`` script installs Ansible including core and extras
module repositories and Galaxy roles.

Configurable environment variables:

* ``ANSIBLE_GIT_RELEASE`` - Version of Ansible to install.
* ``ANSIBLE_ROLE_FILE`` - Galaxy roles to install. Defaults to
  contents of ``ansible-role-requirements.yml`` file.

The script also creates the ``openstack-ansible`` wrapper tool that provides
the variable files to match ``/etc/openstack_deploy/user_*.yml`` as
arguments to ``ansible-playbook`` as a convenience.

Development and Testing
^^^^^^^^^^^^^^^^^^^^^^^

run-playbooks.sh
----------------

The ``run-playbooks`` script is designed to be executed in development and
test environments and is also used for automated testing. It executes actions
which are definitely **not** suitable for production environments and must
therefore **not** be used for that purpose.

In order to scope the playbook execution there are several ``DEPLOY_``
environment variables available near the top of the script. These are used
by simply exporting an override before executing the script. For example,
to skip the execution of the Ceilometer playbook, execute:

.. code-block:: bash

    export DEPLOY_CEILOMETER='no'

The default MaxSessions setting for the OpenSSH Daemon is 10. Each Ansible
fork makes use of a Session. By default Ansible sets the number of forks to 5,
but the ``run-playbooks.sh`` script sets the number of forks used based on the
number of CPU's on the deployment host up to a maximum of 10.

If a developer wishes to increase the number of forks used when using this
script, override the FORKS environment variable. For example:

.. code-block:: bash

    export FORKS=20

run-tempest.sh
--------------

The ``run-tempest.sh`` script runs Tempest tests from the first utility
container. This is primarily used for automated gate testing, but may also be
used through manual execution.

Configurable environment variables:

* ``TEMPEST_SCRIPT_PARAMETERS`` - Defines tests to run. Values are passed to
  ``openstack_tempest_gate.sh`` script, defined in the ``os_tempest`` role.
  Defaults to ``scenario heat_api cinder_backup``.

PEP8
----

Python coding conventions are tested using `PEP8`_, with the following
convention exceptions:

* F403 - 'from ansible.module_utils.basic import \*'
* H303 - No wildcard imports

Testing may be done locally by executing:

.. code-block:: bash

    tox -e pep8

.. PEP8: https://www.python.org/dev/peps/pep-0008/

Bashate
-------

Bash coding conventions are tested using `Bashate`_, with the following
convention exceptions:

* E003: Indent not multiple of 4 (we prefer to use multiples of 2)

Testing may be done locally by executing:

.. code-block:: bash

    tox -e bashate

.. Bashate: https://github.com/openstack-dev/bashate

Documentation
-------------

Documentation is developed in `reStructureText`_ (RST) and compiled into
HTML using Sphinx.

Documentation may be built locally by executing:

.. code-block:: bash

    tox -e docs

.. reStructureText: http://docutils.sourceforge.net/rst.html

Gating
^^^^^^

gate-check-commit.sh
--------------------

The ``gate-check-commit.sh`` script executes a suite of tests necessary for
each commit to the repository. By default, the script runs the bootstrap
scripts, builds an *all-in-one* deployment of OSA, and runs various Tempest
tests on it.

Configurable environment variables:

* ``BOOTSTRAP_AIO`` - Boolean (yes/no) to run AIO bootstrap script. Defaults
  to ``yes``.
* ``BOOTSTRAP_ANSIBLE`` - Boolean (yes/no) to run Ansible bootstrip script.
  Defaults to ``yes``.
* ``RUN_TEMPEST`` - Boolean (yes/no) to run Tempest tests. Defaults to
  ``yes``.

gate-check-docs.sh
------------------

The ``gate-check-docs.sh`` script invokes Sphinx to build the HTML
documentation from RST source.

gate-check-lint.sh
------------------

The ``gate-check-lint.sh`` script executes a suite of tests necessary for each
commit to the repository to verify correct YAML and Python syntax.

All files that begin with a Python shebang pass through *flake8* which ignores
the following rules due to Ansible conventions:

 * F403 - 'from ansible.module_utils.basic import \*'
 * H303 - No wildcard imports

Ansible playbooks pass through ``ansible-playbook --syntax-check``
and ``ansible-lint``.

--------------

.. include:: navigation.txt
