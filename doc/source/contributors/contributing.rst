============================
So You Want to Contribute...
============================

* For contributing code and documentation, you must follow the
  OpenStack practices. Nothing special is required for OpenStack-Ansible.
  See also the `OpenStack developers getting started page`_
  and our :ref:`code rules <code_rules>` before hacking.

* For helping on or submitting bugs, you must have an account on
  Ubuntu Launchpad.
  All our repositories share the same `Launchpad project`_.
  Please check our :ref:`bug report <bug_reporting>` and
  :ref:`bug triage <bug_triage>` processes.
  Easy to fix bugs are marked with the tag *low hanging fruit*, and
  should be the target of first time contributors.

* For sharing your user experience, stories, and helping other users,
  please join us in our :ref:`IRC channel <irc>`.

* The OpenStack-Ansible project has recurring tasks that need
  attention, like releasing, or other code duties.
  See our page :ref:`Periodic work <periodicwork>`.

Below will cover the more project specific information you need to get started
with OpenStack-Ansible.

.. _OpenStack developers getting started page: https://docs.openstack.org/infra/manual/developers.html#getting-started
.. _Launchpad project: https://bugs.launchpad.net/openstack-ansible

Communication
~~~~~~~~~~~~~

.. _irc:

IRC channel
^^^^^^^^^^^

The OpenStack-Ansible community communicates in the ``#openstack-ansible`` IRC
channel hosted on `OFTC <https://www.oftc.net/>` network. This channel is logged, and its
logs are published on https://meetings.opendev.org/irclogs/%23openstack-ansible/

Weekly meetings are held in our IRC channel. The schedule and
logs can be found on
https://meetings.opendev.org/%23OpenStack_Ansible_Deployment_Meeting

The agenda for the next meeting can be found on our
`Meetings wiki page <https://wiki.openstack.org/wiki/Meetings/openstack-ansible>`_.

Matrix bridge
^^^^^^^^^^^^^

Matrix maintains a bridge connection to the OFTC IRC server. So you can use
an `Element <https://element.io/>`_ or any other client compatible with Matrix
protocol, to connect with the team.

To join the channel with Matrix, you will need to enter the room
`#_oftc_#openstack-ansible:matrix.org <https://matrix.to/#/!eHBScvBFekcFIYVcYz:matrix.org>`_.


Mailing lists
^^^^^^^^^^^^^

Members of the OpenStack-Ansible community should monitor the
**OpenStack-discuss** `mailing lists`_.

.. _mailing lists: https://lists.openstack.org/mailman3/lists/openstack-discuss.lists.openstack.org/

All our communications should be prefixed with **[openstack-ansible]**.

Contacting the Core Team
^^^^^^^^^^^^^^^^^^^^^^^^

All of our core team is available through IRC and present in ``#openstack-ansible``
channel on OFTC. The list of the current members of the OpenStack-Ansible Team
might be found on `gerrit`_.

.. _gerrit: https://review.opendev.org/#/admin/groups/490,members


New Feature Planning
~~~~~~~~~~~~~~~~~~~~

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
* Feel free to reach the Core Team via Mailing List or IRC to double-check
  details or ask question regarding a feature at any step. It can save you
  time and avoid unnecessary confusion in the future.

Please check :ref:`newfeatures` section for more detailed process.

.. _Working on Specifications and Blueprints: https://docs.openstack.org/infra/manual/developers.html#working-on-specifications-and-blueprints
.. _Tempest: https://docs.openstack.org/tempest/


Bug Tracking
~~~~~~~~~~~~

We track our tasks and bugs in Launchpad

   https://bugs.launchpad.net/openstack-ansible

If you're looking for some smaller, easier work item to pick up and get started
on, search for the *low-hanging-fruit* tag.


Reporting a Bug
^^^^^^^^^^^^^^^

You found an issue and want to make sure we are aware of it? You can do so on
`Launchpad
<https://bugs.launchpad.net/openstack-ansible>`_.

Also you may find more detailed information about how to work with bugs
on the page :dev_docs:`Bug Handling <contributors/bugs.html>`.

.. _bugfixing:

Working on bug fixes
^^^^^^^^^^^^^^^^^^^^

Any bug fix should have, in its commit message:

  Closes-Bug: #bugnumber

or

  Related-Bug: #bugnumber

where #bugnumber refers to a Launchpad issue.

See also the `working on bugs`_ section of the openstack documentation.

.. _working on bugs: https://docs.openstack.org/infra/manual/developers.html#working-on-bugs


.. _reviews:

Getting Your Patch Merged
~~~~~~~~~~~~~~~~~~~~~~~~~

Any new code will be reviewed by the project Core Team
before merging into our repositories.

We follow OpenStack guidelines for the `code reviewing <https://docs.openstack.org/project-team-guide/review-the-openstack-way.html>`_ process.

Please be aware that any patch can be refused by the community if they
don't match the :ref:`codeguidelines`.

Project Team Lead Duties
~~~~~~~~~~~~~~~~~~~~~~~~

All common PTL duties are enumerated in the `PTL guide
<https://docs.openstack.org/project-team-guide/ptl.html>`_.

All Core reviewer duties are described on the page
:dev_docs:`Core Reviewers <contributors/core-reviewers.html>`.
