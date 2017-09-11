======================
Contributor Guidelines
======================

Reporting Bugs
~~~~~~~~~~~~~~

Bugs should be filed on `Bug Launchpad`_ for OpenStack-Ansible.

When submitting a bug, or working on a bug, please ensure the following
criteria are met:

* The description clearly states or describes the original problem or root
  cause of the problem.
* Include historical information on how the problem was identified.
* Any relevant logs are included.
* If the issue is a bug that needs fixing in a branch other than master,
  please note the associated branch within the launchpad issue.
* The provided information should be totally self-contained. External access
  to web services/sites should not be needed.
* Steps to reproduce the problem if possible.

Tags
----
If it's a bug that needs fixing in a branch in addition to master, add a
'\<release\>-backport-potential' tag (e.g. ``liberty-backport-potential``).
There are predefined tags that will auto-complete.

Status
------
Please leave the **status** of an issue alone until someone confirms it or
a member of the bugs team triages it. While waiting for the issue to be
confirmed or triaged the status should remain as **New**.

Importance
----------
Should only be touched if it is a Blocker/Gating issue. If it is, please
set to **High**, and only use **Critical** if you have found a bug that
can take down whole infrastructures. Once the importance has been changed
the status should be changed to *Triaged* by someone other than the bug
creator.

The triaging process is explained on the `bug triage documentation`_ page.

.. _Bug Launchpad: https://bugs.launchpad.net/openstack-ansible
.. _bug triage documentation: bug-triage.html

General Guidelines for Submitting Code
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

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
* All patch sets should adhere to the `Ansible Style Guide`_ listed here as
  well as adhere to the `Ansible best practices`_ when possible.
* All changes should be clearly listed in the commit message, with an
  associated bug id/blueprint along with any extra information where
  applicable.
* Refactoring work should never include additional "rider" features. Features
  that may pertain to something that was re-factored should be raised as an
  issue and submitted in prior or subsequent patches.
* New features, breaking changes and other patches of note must include a
  release note generated using `the reno tool`_. Please see the
  `Documentation and Release Note Guidelines`_ for more information.
* All patches including code, documentation and release notes should be built
  and tested locally with the appropriate test suite before submitting for
  review. See `Development and Testing`_ for more information.

.. _Git Commit Good Practice: https://wiki.openstack.org/wiki/GitCommitMessages
.. _workflow documented here: https://docs.openstack.org/infra/manual/developers.html#development-workflow
.. _advanced gerrit usage: http://www.mediawiki.org/wiki/Gerrit/Advanced_usage
.. _Ansible best practices: http://docs.ansible.com/playbooks_best_practices.html
.. _the reno tool: https://docs.openstack.org/developer/reno/usage.html
.. _Development and Testing: scripts.html#development-and-testing

Working on Features
~~~~~~~~~~~~~~~~~~~

* All feature additions/deletions should be accompanied by a blueprint/spec.
  e.g. adding additional active agents to neutron, developing a new service
  role, etc...
* Before creating blueprint/spec an associated 'Wishlist Bug' can be raised on
  launchpad. This issue will be triaged and a determination will be made on
  how large the change is and whether or not the change warrants a
  blueprint/spec. Both features and bug fixes may require the creation of a
  blueprint/spec. This requirement will be voted on by core reviewers and will
  be based on the size and impact of the change.
* All blueprints/specs should be voted on and approved by core reviewers
  before any associated code will be merged. For more information on
  blueprints/specs please review the OpenStack documentation regarding
  `Working on Specifications and Blueprints`_.
* Once the blueprint work is completed the author(s) can request a backport
  of the blueprint work into a stable branch. Each backport will be evaluated
  on a case by case basis with cautious consideration based on how the
  backport affects any existing deployments. See the `Backporting`_ section
  for more information.
* Any new OpenStack services implemented which have `Tempest`_ tests
  available must be implemented along with suitable functional tests enabled
  as part of the feature development in order to ensure that any changes
  to the code base do not break the service functionality.
* Feature additions must include documentation which provides reference to
  OpenStack documentation about what the feature is and how it works. The
  documentation should then describe how it is implemented in
  OpenStack-Ansible and what configuration options there are.

.. _Working on Specifications and Blueprints: https://docs.openstack.org/infra/manual/developers.html#working-on-specifications-and-blueprints
.. _Tempest: https://docs.openstack.org/developer/tempest/

Backporting
~~~~~~~~~~~

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
  guidelines in `General Guidelines for Submitting Code`_.
* If a backport is a squashed set of cherry-picked commits, the original SHAs
  should be referenced in the commit message and the reason for squashing the
  commits should be clearly explained.
* When a cherry-pick is modified in any way, the changes made and the reasons
  for them must be explicitly expressed in the commit message.
* Refactoring work must not be backported to a "released" branch.
* Backport reviews should be done with due consideration to the effect of the
  patch on any existing environment deployed by OpenStack-Ansible. The general
  `OpenStack Guidelines for stable branches`_ can be used as a reference.

.. _Submitting a change to a branch for review: http://www.mediawiki.org/wiki/Gerrit/Advanced_usage#Submitting_a_change_to_a_branch_for_review_.28.22backporting.22.29
.. _OpenStack Guidelines for stable branches: https://docs.openstack.org/project-team-guide/stable-branches.html

Documentation and Release Note Guidelines
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Documentation is a critical part of ensuring that the deployers of
OpenStack-Ansible are appropriately informed about:

* How to use the project's tooling effectively to deploy OpenStack.
* How to implement the right configuration to meet the needs of their specific
  use-case.
* Changes in the project over time which may affect an existing deployment.

To meet these needs developers must submit code comments, documentation and
release notes with any code submissions. All forms of documentation should
comply with the guidelines provided in the `OpenStack Documentation Contributor
Guide`_, with particular reference to the following sections:

* Writing style
* RST formatting conventions

.. _OpenStack Documentation Contributor Guide: https://docs.openstack.org/contributor-guide/

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

Documentation
-------------

OpenStack-Ansible has multiple forms of documentation with different intent.

.. note::

   The statements below regarding the Install Guide and Role Documentation are
   statements of intent. The work to fulfill the intent is ongoing. Any new
   documentation submissions should try to help this intent where possible.

The `Deployment Guide <https://docs.openstack.org/project-deploy-guide/openstack-ansible>`_
intends to help deployers deploy OpenStack-Ansible for the first time.

The role documentation (for example, the `keystone role documentation`_)
intends to explain all the options available for the role and how to implement
more advanced requirements. To reduce duplication, the role documentation
directly includes the role's default variables file which includes the
comments explaining the purpose of the variables. The long hand documentation
for the roles should focus less on explaining variables and more on explaining
how to implement advanced use cases.

Where possible the documentation in OpenStack-Ansible should steer clear of
trying to explain OpenStack concepts. Those explanations belong in the
OpenStack Manuals or service documentation and OpenStack-Ansible documentation
should link to those documents when available, rather than duplicate their
content.

.. _keystone role documentation: https://docs.openstack.org/developer/openstack-ansible-os_keystone/

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

Ansible Style Guide
~~~~~~~~~~~~~~~~~~~

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

Development cycle checklist
~~~~~~~~~~~~~~~~~~~~~~~~~~~

On top of the normal cycle goals, a contributor can help the OpenStack-Ansible
development team by performing one of the following recurring tasks:

* By milestone 1:

  * Community goal acknowledgement.

* By milestone 2:

  * Handle deprecations from upstream project's previous cycle.

  * Handle OpenStack-Ansible roles deprecations from the previous cycle.

  * Refresh static elements in roles. For example, update a specific version of
    the software packages.

  * Bump ``ceph_stable_release`` to latest Ceph LTS release in the integrated
    OpenStack-Ansible repo, and inside the ``ceph_client`` role defaults.

  * Check and bump galera versions if required.

  * Check and bump rabbitmq versions if required.

* By milestone 3:

  * Implement features

* After milestone 3:

  * Feature freeze, bug fixes, and testing improvements

* After official project release, before official OpenStack-Ansible release:

  * Bump RDO, Ubuntu Cloud Archive and openSUSE OBS OpenStack Cloud
    repositories if they are ready on time.
