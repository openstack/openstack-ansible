.. _code_rules:

==========
Code rules
==========

Project repositories
====================

The OpenStack-Ansible project has different kinds of git repositories,
each of them with specific use cases, and different sets of practices.

.. list-table::
   :header-rows: 1

   * - Repository type or name
     - Code location
     - Repository purpose
   * - | **OpenStack-Ansible**
       | Also called *integrated repository*
     - * https://opendev.org/openstack/openstack-ansible
     - Our main repository, used by deployers.
       Uses the other repositories.
   * - | The **OpenStack-Ansible roles** repositories
     - * https://opendev.org/openstack/openstack-ansible-os_nova
       * https://opendev.org/openstack/openstack-ansible-os_glance
       * https://opendev.org/openstack/ansible-role-systemd_mount
       * https://opendev.org/openstack/ansible-config_template
       * https://opendev.org/openstack/ansible-hardening
       * ...
     - Each role is in charge of deploying **exactly one**
       component of an OpenStack-Ansible deployment.
   * - | The **specs** repository
     - * https://opendev.org/openstack/openstack-ansible-specs
     - This repository contains all the information concerning
       large bodies of work done in OpenStack-Ansible,
       split by cycle.
   * - | The **ops** repository
     - * https://opendev.org/openstack/openstack-ansible-ops
     - This repository is an incubator for new projects, each project
       solving a particular operational problem. Each project has its
       own folder in this repository.
   * - | External repositories
     - * https://github.com/ceph/ceph-ansible
       * https://github.com/logan2211/ansible-resolvconf
       * https://github.com/evrardjp/ansible-keepalived
       * ...
     - OpenStack-Ansible is not re-inventing the wheel, and tries to
       reuse as much as possible existing roles. A bugfix for one of
       those repositories must be handled to these repositories'
       maintainers.

.. _codeguidelines:

General Guidelines for Submitting Code
======================================

* Write good commit messages. We follow the OpenStack
  "`Git Commit Good Practice`_" guide. if you have any questions regarding how
  to write good commit messages please review the upstream OpenStack
  documentation.
* Changes to the project should be submitted for review via the Gerrit tool,
  following the `workflow documented here`_.
* Pull requests submitted through GitHub will be ignored and closed without
  regard.
* Patches should be focused on solving one problem at a time. If the review is
  overly complex or generally large the initial commit will receive a "**-2**"
  and the contributor will be asked to split the patch up across multiple
  reviews. In the case of complex feature additions the design and
  implementation of the feature should be done in such a way that it can be
  submitted in multiple patches using dependencies. Using dependent changes
  should always aim to result in a working build throughout the dependency
  chain. Documentation is available for `advanced gerrit usage`_ too.
* All patch sets should adhere to the :ref:`Ansible Style Guide` listed here as
  well as adhere to the `Ansible playbooks`_ when possible.
* All changes should be clearly listed in the commit message, with an
  associated bug id/blueprint along with any extra information where
  applicable.
* Refactoring work should never include additional "rider" features. Features
  that may pertain to something that was re-factored should be raised as an
  issue and submitted in prior or subsequent patches.
* New features, breaking changes and other patches of note must include a
  release note generated using `the reno tool`_. Please see the
  :ref:`Documentation and Release Note Guidelines<documentation>`
  for more information.
* All patches including code, documentation and release notes should be built
  and tested locally with the appropriate test suite before submitting for
  review. See :ref:`Development and Testing<devel_and_testing>`
  for more information.

.. _Git Commit Good Practice: https://wiki.openstack.org/wiki/GitCommitMessages
.. _workflow documented here: https://docs.opendev.org/opendev/infra-manual/latest/developers.html#development-workflow
.. _advanced gerrit usage: https://docs.openstack.org/contributors/code-and-documentation/using-gerrit.html
.. _Ansible playbooks: https://docs.ansible.com/ansible/latest/playbook_guide/playbooks_intro.html
.. _the reno tool: https://docs.openstack.org/reno/latest/

.. _documentation:

Documentation and Release Note Guidelines
=========================================

Documentation is a critical part of ensuring that the deployers of
OpenStack-Ansible are appropriately informed about:

* How to use the project's tooling effectively to deploy OpenStack.
* How to implement the right configuration to meet the needs of their specific
  use-case.
* Changes in the project over time which may affect an existing deployment.

To meet these needs developers must submit
:ref:`code comments<codecomments>`, documentation (see also the
:ref:`documentation locations section<docslocations>`) and
:ref:`release notes<reno>` with any code submissions.

All forms of documentation should comply with the guidelines provided
in the `OpenStack Documentation Contributor
Guide`_, with particular reference to the following sections:

* Writing style
* RST formatting conventions

.. _OpenStack Documentation Contributor Guide: https://docs.openstack.org/doc-contrib-guide/

.. _codecomments:

Code Comments
-------------

Code comments for variables should be used to explain the purpose of the
variable. This is particularly important for the role defaults file as the file
is included verbatim in the role's documentation. Where there is an optional
variable, the variable and an explanation of what it is used for should be
added to the defaults file.

Code comments for bash/python scripts should give guidance to the purpose of
the code. This is important to provide context for reviewers before the patch
has merged, and for later modifications to remind the contributors what the
purpose was and why it was done that way.

.. _docslocations:

Documentation locations
-----------------------

OpenStack-Ansible has multiple forms of documentation with different intent.

The :deploy_guide:`Deployment Guide <index.html>`
intends to help deployers deploy OpenStack-Ansible for the first time.

The :dev_docs:`User Guide <user/index.html>` intends to provide user
stories on how to do specific things with OpenStack-Ansible.

The :dev_docs:`Operations Guide <admin/index.html>` provide help
on how to manage and operate OpenStack-Ansible.

The in-depth technical information is located in the
:dev_docs:`OpenStack-Ansible Reference <reference/index.html>`.

The role documentation (for example, the `keystone role documentation`_)
intends to explain all the options available for the role and how to implement
more advanced requirements. To reduce duplication, the role documentation
directly includes the role's default variables file which includes the
comments explaining the purpose of the variables. The long hand documentation
for the roles should focus less on explaining variables and more on explaining
how to implement advanced use cases.

The role documentation must include a description of the mandatory
infrastructure (For example: a database and a message queue are required),
variables (For example: the database name and credentials) and group names
(For example: The role expects a group named ``foo_all`` to
be present and it expects the host to be a member of it) for the role's
execution to succeed.

Where possible the documentation in OpenStack-Ansible should steer clear of
trying to explain OpenStack concepts. Those explanations belong in the
OpenStack Manuals or service documentation and OpenStack-Ansible documentation
should link to those documents when available, rather than duplicate their
content.

.. _keystone role documentation: https://docs.openstack.org/openstack-ansible-os_keystone/

.. _reno:

Release Notes
-------------

Release notes are generated using `the reno tool`_. Release notes must be
written with the following guidelines in mind:

* Each list item must make sense to read without the context of the patch or
  the repository the patch is being submitted into. The reason for this is that
  all release notes are consolidated and presented in a long list without
  reference to the source patch or the context of the repository.
* Each note should be brief and to the point. Try to avoid multi-paragraph
  notes. For features the note should typically refer to documentation for more
  details. For bug fixes the note can refer to a registered bug for more
  details.

In most cases only the following sections should be used for new release notes
submitted with patches:

* ``features``: This should inform the deployer briefly about a new feature and
  should describe how to use it either by referencing the variables to set or
  by referring to documentation.
* ``issues``: This should inform the deployer about known issues. This may be
  used when fixing an issue and wanting to inform deployers about a workaround
  that can be used for versions prior to that which contains the patch that
  fixes the issue. Issue notes should specifically make mention of what
  versions of OpenStack-Ansible are affected by the issue.
* ``upgrade``: This should inform the deployer about changes which may affect
  them when upgrading from a previous major or minor version. Typically, these
  notes would describe changes to default variable values or variables that
  have been removed.
* ``deprecations``: If a variable has been deprecated (ideally using the
  deprecation filter), then it should be communicated through notes in this
  section. Note that if a variable has been removed entirely then it has not
  been deprecated and the removal should be noted in the ``upgrade`` section.

.. _backport:

Backporting
===========

* Backporting is defined as the act of reproducing a change from another
  branch. Unclean/squashed/modified cherry-picks and complete
  reimplementations are OK.
* Backporting is often done by using the same code (via cherry picking), but
  this is not always the case. This method is preferred when the cherry-pick
  provides a complete solution for the targeted problem.
* When cherry-picking a commit from one branch to another the commit message
  should be amended with any files that may have been in conflict while
  performing the cherry-pick operation. Additionally, cherry-pick commit
  messages should contain the original commit *SHA* near the bottom of the new
  commit message. This can be done with ``cherry-pick -x``. Here's more
  information on `Submitting a change to a branch for review`_.
* Every backport commit must still only solve one problem, as per the
  guidelines in :ref:`codeguidelines`.
* If a backport is a squashed set of cherry-picked commits, the original SHAs
  should be referenced in the commit message and the reason for squashing the
  commits should be clearly explained.
* When a cherry-pick is modified in any way, the changes made and the reasons
  for them must be explicitly expressed in the commit message.
* Refactoring work must not be backported to a "released" branch.
* Backport reviews should be done with due consideration to the effect of the
  patch on any existing environment deployed by OpenStack-Ansible. The general
  `OpenStack Guidelines for stable branches`_ can be used as a reference.

.. _Submitting a change to a branch for review: https://www.mediawiki.org/wiki/Gerrit/Advanced_usage#Submitting_a_change_to_a_branch_for_review_.28.22backporting.22.29
.. _OpenStack Guidelines for stable branches: https://docs.openstack.org/project-team-guide/stable-branches.html

.. _newfeatures:

Working on new features
=======================

.. _specs:

Submitting a specification
--------------------------

By proposing a draft spec you can help the OpenStack-Ansible
community keep track of what roles or large changes are being developed,
and perhaps connect you with others who may be interested and able
to help you in the process.

Our specifications repository follows the usual OpenStack and
OpenStack-Ansible guidelines for submitting code.

However, to help you in the writing of the specification, we have a
`specification template`_ that can be copied into the latest release
name folder. Rename and edit it for your needs.

.. _specification template: https://opendev.org/openstack/openstack-ansible-specs/src/specs/templates/template.rst

Example process to develop a new role
-------------------------------------

Here are the steps to write the role:

#. You can review roles which may be currently in development by checking our
   `specs repository`_ and `unmerged specs`_ on review.openstack.org. If you
   do not find a spec for the role, propose a blueprint/spec.
   See also :ref:`specs`.
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

#. Add tests to the role. See also our :ref:`tests` page.
#. Ensuring the role matches OpenStack-Ansible's latest standards.
   See also our :ref:`code_rules` page.
#. Ensure the role converges:

   * Deploy the applicable configuration files in the right places.
   * Ensure that the service starts.

   The convergence may involve consuming other OpenStack-Ansible roles
   (For example: **galera_server, python_venv_build, rabbitmq_server,
   systemd_service, openstack.osa.db_setup**)
   in order to ensure that the appropriate infrastructure is in place.
   Re-using existing roles in OpenStack-Ansible or Ansible Galaxy is
   strongly encouraged.
#. Once the initial convergence is working and the services are running,
   the role development should focus on implementing some level of
   functional testing. See also :ref:`tempest-testing`.
#. Test the role on a new machine, using our provided scripts.
#. Submit your role for review.
#. If required, ask the OpenStack-Ansible PTL to import the GitHub
   role into the openstack-ansible namespace (This can only be done
   early in the development cycle, and may be postponed to next
   cycle).
#. If necessary, work on the integration within the
   openstack-ansible integrated repository, and deploy
   the role on an AIO. See also :ref:`integrate-new-role-with-aio`.

.. _specs repository: https://opendev.org/openstack/openstack-ansible-specs
.. _unmerged specs: https://review.opendev.org/#/q/status:+open+project:openstack/openstack-ansible-specs
.. _Best Practice: https://docs.ansible.com/ansible/playbooks_best_practices.html#directory-layout


Example process for adding a feature to an existing role
--------------------------------------------------------

#. Search for in the `OpenStack-Ansible Launchpad project`_ for
   the feature request.
#. If no "Wishlist" item exist in Launchpad for your feature, create
   a bug for it. Don't hesitate to ask if a spec is required in
   the bug.
#. Work on the role files, following our :ref:`code_rules`.
#. Add an extra role test scenario, to ensure your code path is
   tested and working.
#. Test your new scenario with a new machine.
   See also the :ref:`devel_and_testing` page.
#. Submit your code for review, with its necessary documentation and
   release notes.

.. _OpenStack-Ansible Launchpad project: https://bugs.launchpad.net/openstack-ansible


Example process to incubate a new "ops" project
-----------------------------------------------

A new project in "openstack-ansible-ops" can be started at any time,
with no constraint like writing a specification, or creating a bug.

Instead, the new code has to be isolated on a separate folder of the
`openstack-ansible-ops repo`_.

.. _openstack-ansible-ops repo: https://opendev.org/openstack/openstack-ansible-ops

.. _Ansible Style Guide:

Ansible Style Guide
===================

YAML formatting
---------------

When creating tasks and other roles for use in Ansible please create them
using the YAML dictionary format.

Example YAML dictionary format:

.. code-block:: yaml

   - name: The name of the tasks
      module_name:
        thing1: "some-stuff"
        thing2: "some-other-stuff"
      tags:
        - some-tag
        - some-other-tag


Example what **NOT** to do:

.. code-block:: yaml

    - name: The name of the tasks
      module_name: thing1="some-stuff" thing2="some-other-stuff"
      tags: some-tag

.. code-block:: yaml

    - name: The name of the tasks
      module_name: >
        thing1="some-stuff"
        thing2="some-other-stuff"
      tags: some-tag


Usage of the ">" and "|" operators should be limited to Ansible conditionals
and command modules such as the Ansible ``shell`` or ``command``.

Tags and tags conventions
-------------------------

.. note::

   If you want to learn more about how to use Ansible tags effectively,
   check out the :dev_docs:`Operations Guide <admin/index.html>`.

Tags are assigned based on the relevance of each individual item.
Higher level includes (for example in the ``tasks/main.yml``) need high
level tags. For example, ``*-config`` or ``*-install``.
Included tasks can have more detailed tags.

The following convention is used:

* A tag including the word ``install`` handles software installation tasks.
  Running a playbook with ``--tags <role>-install`` only deploys the
  necessary software on the target, and will not configure it to your
  needs or run any service.

* A tag including the word ``config`` prepares the configuration of the
  software (adapted to your needs), and all the components necessary
  to run the service(s) configured in the role. Running a playbook with
  ``--tags <role>-config`` is only possible if the target already ran
  the tags ``<role>-install``.

Variable files conventions
--------------------------

The variables files in a role are split in 3 locations:

#. The `defaults/main.yml` file
#. The `vars/main.yml` file
#. The `vars/<platform specific>.yml` file

The variables with lower priority should be in the `defaults/main.yml`.
This allows their overriding with group variables or host variables.
A good example for this are default database connection details, default
queues connection details, or debug mode.

In other words, `defaults/main.yml` contains variables that are meant to
be overridable by a deployer or a continuous integration system.
These variables should be limited as much as possible, to avoid
increasing the test matrix.

The `vars/main.yml` is always included. It contains generic
variables that aren't meant to be changed by a deployer. This includes
for example static information that aren't distribution specific (like
aggregation of role internal variables for example).

The `vars/<platform specific>.yml` is the place where distribution
specific content will be stored. For example, this file will hold
the package names, repositories urls and keys, file paths, service
names/init scripts.

Secrets
^^^^^^^

Any secrets (For example: passwords) should not be provided with default
values in the tasks, role vars, or role defaults. The tasks should be
implemented in such a way that any secrets required, but not provided,
should result in the task execution failure. It is important for a
secure-by-default implementation to ensure that an environment is not
vulnerable due to the production use of default secrets. Deployers
must be forced to properly provide their own secret variable values.

Task files conventions
----------------------

Most OpenStack services will follow a common series of stages to
install, configure, or update a service deployment. This is apparent
when you review `tasks/main.yml` for existing roles.

If developing a new role, please follow the conventions set by
existing roles.

Tests conventions
-----------------

The conventions for writing tests are described in the
:ref:`tests` page.

Other OpenStack-Ansible conventions
-----------------------------------

To facilitate the development and tests implemented across all
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
  be overridden by our proposal bot should any change happen.
* ``setup.cfg`` and ``setup.py``:
  Information about the repository used when building artifacts.
* ``README.rst``, ``LICENSE``, ``CONTRIBUTING.rst``:
  A set of standard files whose content is self-explanatory.
* ``.gitignore``:
  A standard git configuration file for the repository which should be
  pretty uniform across all the repositories. This must be copied from the
  ``openstack-ansible-tests`` repository and will be automatically
  be overridden by our proposal bot should any change happen.
* ``.gitreview``:
  A standard file configured for the project to inform the ``git-review``
  plugin where to find the upstream gerrit remote for the repository.
* ``docs/`` and ``releasenotes/`` folders need to be exist and be
  properly configured.

Please have a look at a role like os_cinder, os_keystone, or os_neutron
for latest files.

Container technology independence
---------------------------------

The role implementation should be done in such a way that it is agnostic
with regards to whether it is implemented in a container, or on a
physical host. The test infrastructure may make use of containers for
the separation of services, but if a role is used by a playbook that
targets a host, it must work regardless of whether that host is a
container, a virtual server, or a physical server. The use of
containers for role tests is not required but it may be useful in order
to simulate a multi-node build out as part of the testing infrastructure.

Minimum supported distributions
-------------------------------

See our :ref:`compatibility-matrix` page.
