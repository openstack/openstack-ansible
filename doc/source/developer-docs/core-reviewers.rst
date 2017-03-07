==============
Core Reviewers
==============

General Responsibilities
------------------------

The `OpenStack-Ansible Core Reviewer Team`_ is responsible for many aspects of
the OpenStack-Ansible project. These include, but are not limited to:

* Mentor community contributors in solution design, testing, and the review
  process
* Actively reviewing patch submissions, considering whether the patch:
  - is functional
  - fits the use-cases and vision of the project
  - is complete in terms of testing, documentation, and release notes
  - takes into consideration upgrade concerns from previous versions
* Assist in bug triage and delivery of bug fixes
* Curating the gate and triaging failures
* Maintaining accurate, complete, and relevant documentation
* Ensuring the level of testing is adequate and remains relevant as features
  are added
* Answering questions and participating in mailing list discussions
* Interfacing with other OpenStack teams

In essence, core reviewers share the following common ideals:

* They share responsibility in the project’s success in its `mission`_.
* They value a healthy, vibrant, and active developer and user community.
* They have made a long-term, recurring time investment to improve the
  project.
* They spend their time doing what needs to be done to ensure the project's
  success, not necessarily what is the most interesting or fun.
* A core reviewer’s responsibility doesn’t end with merging code.

.. _OpenStack-Ansible Core Reviewer Team: https://review.openstack.org/#/admin/groups/490,members
.. _mission: https://governance.openstack.org/reference/projects/openstackansible.html#mission

Core Reviewer Expectations
--------------------------

Members of the core reviewer team are expected to:

* Attend and participate in the weekly IRC meetings
* Monitor and participate in-channel at #openstack-ansible
* Monitor and participate in OpenStack-Ansible discussions on the mailing list
* Participate in related design summit sessions at the OpenStack Summits
* Review patch submissions actively and consistently

Please note in-person attendance at design summits, mid-cycles, and other code
sprints is not a requirement to be a core reviewer. The team will do its best
to facilitate virtual attendance at all events. Travel is not to be taken
lightly, and we realize the costs involved for those who attend these events.

Code Merge Responsibilities
---------------------------

While everyone is encouraged to review changes, members of the core reviewer
team have the ability to +2/-2 and +W changes to these repositories. This is
an extra level of responsibility not to be taken lightly. Correctly merging
code requires not only understanding the code itself, but also how the code
affects things like documentation, testing, upgrade impacts and interactions
with other projects. It also means you pay attention to release milestones and
understand if a patch you are merging is marked for the release, especially
critical during the feature freeze.
