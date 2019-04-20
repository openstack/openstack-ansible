.. _contributing:

======================
Contributor Guidelines
======================

Before submitting code
======================

Before jumping ahead and working on code, a series of steps should
be taken:

* Is there a bug for it? Can your track if someone else has seen
  the same bug?
* Are you sure nobody is working on this problem at the moment?
  Could there be a review pending fixing the same issue?
* Have you checked if your issue/feature request
  hasn't been solved in another branch?

If you're willing to submit code, please remember the following rules:

* All code should match our
  :ref:`codeguidelines`.
* All code requires to go through our :ref:`reviews`.
* Documentation should be provided with the
  code directly. See also :ref:`documentation`.
* Fixing bugs and increasing test coverage have priority to new features.
  See also the section :ref:`bugfixing`.
* New features are following a process, explained in the section
  :ref:`newfeatures`.
  New features are less likely to be :ref:`backported<backport>`
  to previous branches.

.. _reviews:

Review process
==============

Any new code will be reviewed before merging into our repositories.

We follow openstack guidelines for the `code reviewing <https://docs.openstack.org/project-team-guide/review-the-openstack-way.html>`_ process.

Please be aware that any patch can be refused by the community if they
don't match the :ref:`codeguidelines`.

.. _bugfixing:

Working on bug fixes
====================

Any bug fix should have, in its commit message:

  Closes-Bug: #bugnumber

or

  Related-Bug: #bugnumber

where #bugnumber refers to a Launchpad issue.

See also the `working on bugs`_ section of the openstack documentation.

.. _working on bugs: https://docs.openstack.org/infra/manual/developers.html#working-on-bugs

.. _newfeatures:

Working on new features
=======================

If you would like to contribute towards a role to introduce an OpenStack
or infrastructure service, or to improve an existing role, the
OpenStack-Ansible project would welcome that contribution and your assistance
in maintaining it.

Here are a few rules to get started:

* All large feature additions/deletions should be accompanied by a
  blueprint/spec. e.g. adding additional active agents to neutron,
  developing a new service role, etc... See also
  :ref:`specs`.
* Before creating blueprint/spec an associated 'Wishlist Bug' can be raised on
  launchpad. This issue will be triaged and a determination will be made on
  how large the change is and whether or not the change warrants a
  blueprint/spec. Both features and bug fixes may require the creation of a
  blueprint/spec. This requirement will be voted on by core reviewers and will
  be based on the size and impact of the change.
* All blueprints/specs should be voted on and approved by core reviewers
  before any associated code will be merged. For more information on
  blueprints/specs please review the OpenStack documentation regarding
  `Working on Specifications and Blueprints`_ and our own
  :ref:`specs`.
* Once the blueprint work is completed the author(s) can request a backport
  of the blueprint work into a stable branch. Each backport will be evaluated
  on a case by case basis with cautious consideration based on how the
  backport affects any existing deployments. See the
  :ref:`backport` section for more information.
* Any new OpenStack services implemented which have `Tempest`_ tests
  available must be implemented along with suitable functional tests enabled
  as part of the feature development in order to ensure that any changes
  to the code base do not break the service functionality.
* Feature additions must include documentation which provides reference to
  OpenStack documentation about what the feature is and how it works. The
  documentation should then describe how it is implemented in
  OpenStack-Ansible and what configuration options there are.
  See also the :ref:`documentation` section.

.. _Working on Specifications and Blueprints: https://docs.openstack.org/infra/manual/developers.html#working-on-specifications-and-blueprints
.. _Tempest: https://docs.openstack.org/developer/tempest/


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

   * Implement **developer_mode** to build from a git source into
     a Python virtual environment.
   * Deploy the applicable configuration files in the right places.
   * Ensure that the service starts.

   The convergence may involve consuming other OpenStack-Ansible roles
   (For example: **galera_server, galera_client, rabbitmq_server**)
   in order to ensure that the appropriate infrastructure is in place.
   Re-using existing roles in OpenStack-Ansible or Ansible Galaxy is
   strongly encouraged.
#. Once the initial convergence is working and the services are running,
   the role development should focus on implementing some level of
   functional testing. See also :ref:`tempest-testing`.
#. Test the role on a new machine, using our provided scripts.
#. Submit your role for review.
#. If required, ask the OpenStack-Ansible PTL to import the github
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
#. The :ref:`bug_triage` will classify if this new feature requires
   a spec or not.
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

.. _Submitting a change to a branch for review: http://www.mediawiki.org/wiki/Gerrit/Advanced_usage#Submitting_a_change_to_a_branch_for_review_.28.22backporting.22.29
.. _OpenStack Guidelines for stable branches: https://docs.openstack.org/project-team-guide/stable-branches.html
