.. _reference_release:

========
Releases
========

What is the OpenStack-Ansible release model?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

OpenStack-Ansible uses the 'cycle-trailing' release model as specified
in the OpenStack `release model reference`_.

.. _release model reference: https://releases.openstack.org/reference/release_models.html

How are release tags decided?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

In order to ensure a common understanding of what release versions mean, we
use `Semantic Versioning 2.0.0`_ for versioning as a basis. The exception to
the rule is for milestone releases during a development cycle, where releases
are tagged ``<MAJOR>.0.0.0b<MILESTONE>`` where ``<MAJOR>`` is the next major
release number, and ``<MILESTONE>`` is the milestone number.

The OpenStack series names are alphabetical, with each letter matched to a
number (e.g., Austin = 1, Bexar = 2, Newton = 14, Pike = 16, etc.).
OpenStack-Ansible adopted the same ``<MAJOR>`` release numbering
as the Nova project to match the overall OpenStack series version numbering.

.. _Semantic Versioning 2.0.0: https://semver.org

How frequently does OpenStack-Ansible release?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Major releases are done every six months according to the `OpenStack release
schedule`_. Each major release is consistent with an OpenStack series.

Minor/patch releases are requested for stable branches on the second and last
Friday of every month. The releases are typically completed within a few days
of the request.

.. _OpenStack release schedule: https://releases.openstack.org

What version of OpenStack is deployed by OpenStack-Ansible?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

For each OpenStack-Ansible release, the OpenStack version that is
deployed is set to a specific OpenStack `git SHA-1 hash`_ (SHA).
These are updated after every OpenStack-Ansible release.
The intent is to ensure that OpenStack-Ansible users are able to
enjoy an updated OpenStack environment with smaller increments of
change than the typical upstream service releases allow for as they are
usually very infrequent.

This does mean that a stable OpenStack-Ansible deployment will
include a version of a service (e.g.: nova-17.0.3dev4) which does not
match a tag exactly as you may expect (e.g.: nova-17.0.3).

If you wish to change the SHA to a specific SHA/tag/branch, or wish to use
your own fork of an OpenStack service, please see the section titled
:ref:`override_openstack_sources` in the user guide.

.. _git SHA-1 hash: https://git-scm.com/book/en/v2/Git-Internals-Git-Objects

When does a patch to an OpenStack-Ansible role get into a release?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

For each OpenStack-Ansible release, the Ansible roles that form that
release are set to a specific `git SHA-1 hash`_ (SHA). These are updated
after every OpenStack-Ansible release.

OpenStack-Ansible frequently does proactive bugfix backports.
In order to reduce the risk of these backports introducing any
destabilization, OpenStack-Ansible implements a 'soak' period for any
patches implemented in the stable branches for roles, but also
provides for circumventing this in exceptional circumstances.

A patch merged into a role is immediately tested by other role tests,
ensuring that any major breaking change is caught. Once a minor/patch release
is requested, the integrated build receives a 'SHA bump' patch to update the
integrated build to using the latest available roles including that new patch.
This new set is available for testing to anyone wanting to use the head of the
stable branch, and is tested in periodic tests until the next release. In
total, that means that the cycle time for a patch from merge to release is
anywhere from two weeks to one month.

If there is a requirement to rush a role patch into the next release, then
anyone may propose a change to the ``ansible-role-requirements.yml`` file
in the ``openstack/openstack-ansible`` repository with the appropriate
justification.

We believe that this approach brings a balance of both reasonable stability,
while still being able to do pro-active backports.

The only exception to this process is for the ``master`` branch, which
intentionally consumes the ``master`` branch from all roles between releases
so that any changes are immediately integration tested.
