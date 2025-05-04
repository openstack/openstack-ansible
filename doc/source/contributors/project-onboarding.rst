==================
Project Onboarding
==================

This document should help you understand how to contribute to
OpenStack-Ansible.

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
       * https://github.com/willshersystems/ansible-sshd
       * https://github.com/evrardjp/ansible-keepalived
       * ...
     - OpenStack-Ansible is not re-inventing the wheel, and tries to
       reuse as much as possible existing roles. A bugfix for one of
       those repositories must be handled to these repositories'
       maintainers.

How to contribute on code or issues
===================================

* For contributing code and documentation, you must follow the
  OpenStack practices. Nothing special is required for OpenStack-Ansible.

  See also the `OpenStack developers getting started page`_.
  and our :ref:`contributor guidelines<contributing>` before hacking.

* For helping on or submitting bugs, you must have an account on
  ubuntu Launchpad.
  All our repositories share the same `Launchpad project`_.

  Please check our :ref:`bug report<bug_reporting>` and
  :ref:`bug triage<bug_triage>` processes.

  Easy to fix bugs are marked with the tag *low hanging fruit*, and
  should be the target of first time contributors.

* For sharing your user experience, stories, and helping other users,
  please join us in our :ref:`IRC channel<irc>`.

* The OpenStack-Ansible project has recurring tasks that need
  attention, like releasing, or other code duties.
  See our page :ref:`Periodic work<periodicwork>`.

.. _OpenStack developers getting started page: https://docs.openstack.org/infra/manual/developers.html#getting-started
.. _Launchpad project: https://bugs.launchpad.net/openstack-ansible

Community communication channels
================================

.. _irc:

IRC channel
^^^^^^^^^^^

.. warning::

  The OpenStack Community moved the IRC network from Freenode to OFTC on May 31,
  2021. All the current IRC channels used in The OpenStack community are registered in OFTC
  network too.

The OpenStack-Ansible community communicates a lot through IRC, in
the #openstack-ansible channel, on OFTC. This channel is
logged, and its logs are published on
https://meetings.opendev.org/irclogs/%23openstack-ansible/

Weekly meetings are held in our IRC channel. The schedule and
logs can be found on
https://meetings.opendev.org/%23OpenStack_Ansible_Deployment_Meeting

Next meeting agenda can be found on our
`Meetings wiki page <https://wiki.openstack.org/wiki/Meetings/openstack-ansible>`_.

Mailing lists
^^^^^^^^^^^^^

A member of the OpenStack-Ansible community should monitor the
**OpenStack-discuss** `mailing lists`_.

.. _mailing lists: https://lists.openstack.org/mailman3/lists/

All our communications should be prefixed with **[openstack-ansible]**.
