================
Included Scripts
================

The repository contains several helper scripts to manage gate jobs,
install base requirements, and update repository information. Execute
these scripts from the root of the repository clone. For example:

.. code:: bash

   $ scripts/<script_name>.sh

Bootstrapping
^^^^^^^^^^^^^

bootstrap-ansible.sh
--------------------

The ``bootstrap-ansible.sh`` script installs Ansible, including the `core`_ and
`extras`_ module repositories and Galaxy roles.

While there are several configurable environment variables which this script
uses, the following are commonly used:

* ``ANSIBLE_PACKAGE`` - The version of Ansible to install.

For example:

.. code:: bash

   $ export ANSIBLE_PACKAGE="ansible==2.1.0"

Installing directly from git is also supported. For example, from the tip of
Ansible development branch:

.. code:: bash

   $ export ANSIBLE_PACKAGE="git+https://github.com/ansible/ansible@devel#egg=ansible"

* ``ANSIBLE_ROLE_FILE`` - The location of a YAML file which ansible-galaxy can
  consume which specifies which roles to download and install. The default
  value for this is ``ansible-role-requirements.yml``.

The script also creates the ``openstack-ansible`` wrapper tool that provides
the variable files to match ``/etc/openstack_deploy/user_*.yml`` as
arguments to ``ansible-playbook`` as a convenience.

.. _core: https://github.com/ansible/ansible-modules-core
.. _extras: https://github.com/ansible/ansible-modules-extras

bootstrap-aio.sh
----------------

The ``bootstrap-aio.sh`` script prepares a host for an `All-In-One`_ (AIO)
deployment for the purposes of development and gating. The script creates the
necessary partitions, directories, and configurations. The script can be
configured using environment variables - more details are provided on the
`All-In-One`_ page.

.. _All-In-One: quickstart-aio.html

Development and Testing
^^^^^^^^^^^^^^^^^^^^^^^

Lint Tests
----------

Python coding conventions are tested using `PEP8`_, with the following
convention exceptions:

* F403 - 'from ansible.module_utils.basic import \*'

Testing may be done locally by executing:

.. code-block:: bash

    tox -e pep8

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

    tox -e bashate

Ansible is lint tested using `ansible-lint`_.

Testing may be done locally by executing:

.. code-block:: bash

    tox -e ansible-lint

Ansible playbook syntax is tested using ansible-playbook.

Testing may be done locally by executing:

.. code-block:: bash

    tox -e ansible-syntax

A consolidated set of all lint tests may be done locally by executing:

.. code-block:: bash

    tox -e linters

.. _PEP8: https://www.python.org/dev/peps/pep-0008/
.. _Bashate: https://git.openstack.org/cgit/openstack-dev/bashate
.. _ansible-lint: https://github.com/willthames/ansible-lint

Documentation Build
-------------------

Documentation is developed in reStructuredText_ (RST) and compiled into
HTML using Sphinx.

Documentation may be built locally by executing:

.. code-block:: bash

    tox -e docs
    tox -e deploy-guide

.. _reStructuredText: http://docutils.sourceforge.net/rst.html

Release Notes Build
-------------------

Release notes are generated using the `the reno tool`_ and compiled into
HTML using Sphinx.

Release notes may be built locally by executing:

.. code-block:: bash

    tox -e releasenotes

.. _the reno tool: https://docs.openstack.org/developer/reno/usage.html

.. note::

   The ``releasenotes`` build argument only tests committed changes.
   Ensure your local changes are committed before running the
   ``releasenotes`` build.

Gating
^^^^^^

Every commit to the OpenStack-Ansible integrated build is verified by
OpenStack-CI through the following jobs:

* ``gate-openstack-ansible-releasenotes``: This job executes the
  `Release Notes Build`_.

* ``gate-openstack-ansible-docs-ubuntu-xenial``: This job executes the
  `Documentation Build`_.

* ``gate-openstack-ansible-linters-ubuntu-xenial``: This job executes
  the `Lint Tests`_.

* ``gate-openstack-ansible-openstack-ansible-aio-ubuntu-xenial``: where
  ``aio`` is the scenario, ``ubuntu`` is the distribution, and ``xenial``
  is the version of the distribution.

  The same test is executed against multiple distribution versions, and
  may be executed against multiple distributions and multiple scenarios
  too.

  This job executes the ``gate-check-commit.sh`` script which executes a
  convergence test and then a functional test.

  The convergence test is the execution of an AIO build which aims to test
  the primary code path for a functional environment. The functional test
  then executes OpenStack's Tempest testing suite to verify that the
  environment that has deployed successfully actually works.

  While this script is primarily developed and maintained for use in
  OpenStack-CI, it can be used in other environments.

Dependency Updates
^^^^^^^^^^^^^^^^^^

The dependencies for OpenStack-Ansible are updated approximately every two
weeks through the use of ``scripts/sources-branch-updater.sh``. This script
updates all pinned SHA's for OpenStack services, OpenStack-Ansible roles,
and other python dependencies which are not handled by the OpenStack global
requirements management process. This script also updates the statically
held templates/files in each role to ensure that they are always up to date.
Finally, it also does a minor version increment of the value for
``openstack_release``.

The update script is used as follows:

.. parsed-literal::

   # change directory to the openstack-ansible checkout
   cd ~/code/openstack-ansible

   # ensure that the correct branch is checked out
   git checkout |current_release_git_branch_name|

   # ensure that the branch is up to date
   git pull

   # create the local branch for the update
   git checkout -b sha-update

   # execute the script for all openstack services
   ./scripts/sources-branch-updater.sh -b |current_release_git_branch_name| -o |current_release_git_branch_name|

   # execute the script for gnocchi
   ./scripts/sources-branch-updater.sh -s playbooks/defaults/repo_packages/gnocchi.yml -b |current_release_gnocchi_git_branch_name| -o |current_release_git_branch_name|

   # the console code should only be updated when necessary for a security fix, or for the OSA master branch
   ./scripts/sources-branch-updater.sh -s playbooks/defaults/repo_packages/nova_consoles.yml -b master

   # the testing repositories should not be updated for stable branches as the new tests
   # or other changes introduced may not work for older branches
   ./scripts/sources-branch-updater.sh -s playbooks/defaults/repo_packages/openstack_testing.yml -b master

   # commit the changes
   new_version=$(awk '/^openstack_release/ {print $2}' inventory/group_vars/all/all.yml)
   git add --all
   git commit -a -m "Update all SHAs for ${new_version}" \
   -m "This patch updates all the roles to the latest available stable
   SHA's, copies the release notes from the updated roles into the
   integrated repo, updates all the OpenStack Service SHA's, and
   updates the appropriate python requirements pins.

   # push the changes up to gerrit
   git review

