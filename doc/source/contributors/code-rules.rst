.. _code_rules:

==========
Code rules
==========

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
  well as adhere to the `Ansible best practices`_ when possible.
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
.. _workflow documented here: https://docs.openstack.org/infra/manual/developers.html#development-workflow
.. _advanced gerrit usage: https://www.mediawiki.org/wiki/Gerrit/Advanced_usage
.. _Ansible best practices: https://docs.ansible.com/playbooks_best_practices.html
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

.. _specs:

Submitting a specification
==========================

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

* A tag including the word ``upgrade`` handles all the upgrade tasks.

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
* ``run_tests.sh``:
  A script for developers to execute all standard tests on a
  suitable host. This must be copied from the
  ``openstack-ansible-tests`` repository and will be automatically
  be overridden by our proposal bot should any change happen.
* ``Vagrantfile``:
  A configuration file to allow a developer to easily create a
  test virtual machine using `Vagrant`_. This must automatically execute
  ``run_tests.sh``. This must be copied from the
  ``openstack-ansible-tests`` repository and will be automatically
  be overridden by our proposal bot should any change happen.
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

.. _Vagrant: https://www.vagrantup.com/

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

See our :ref:`supported-distros` page.
