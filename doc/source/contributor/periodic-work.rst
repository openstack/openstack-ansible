.. _periodicwork:

=============
Periodic Work
=============

Releasing
=========

Our release schedule for stable branches is around every two weeks:

* We request an OpenStack release on the second Friday of the month
* We request an OpenStack release on the last Friday of the month

The releases take generally a few days to get "tagged" and be publicly
available.

Dependency Updates
------------------

The dependencies for OpenStack-Ansible are updated
through the use of ``scripts/sources-branch-updater.sh``. This script
updates all pinned SHA's for OpenStack services, OpenStack-Ansible roles,
and other python dependencies which are not handled by the OpenStack global
requirements management process. This script also updates the statically
held templates/files in each role to ensure that they are always up to date.
Finally, it also increments the patch version of the
``openstack_release`` variable.

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


Development cycle checklist
===========================

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

  * Check outstanding reviews and move to merge or abandon them if no longer
    valid.

* By milestone 3:

  * Implement features

* After milestone 3:

  * Feature freeze, bug fixes, and testing improvements

* After official project release, before official OpenStack-Ansible release:

  * Bump RDO, Ubuntu Cloud Archive and openSUSE OBS OpenStack Cloud
    repositories if they are ready on time.
