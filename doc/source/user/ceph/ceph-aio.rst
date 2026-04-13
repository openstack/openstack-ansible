.. _aio_ceph_deployment:

================================
All-in-One (AIO) Ceph Deployment
================================

OpenStack-Ansible provides a dedicated AIO Ceph scenario that deploys
OpenStack together with a minimal Ceph cluster on a single host.

.. important::

   The AIO Ceph scenario is intended for **testing and development only**.
   It must not be used in production environments. For production use,
   deploy a dedicated multi-node Ceph cluster.

This document describes how to enable the AIO Ceph scenario using the
standard AIO quickstart procedure.

For the regular AIO workflow, refer to `OpenStack-Ansible AIO Quickstart Guide <https://docs.openstack.org/openstack-ansible/latest/user/aio/quickstart.html>`_

Overview
========

The AIO Ceph scenario extends the default All-in-One deployment by adding
a minimal Ceph cluster to the same host. During bootstrap, Ceph services
are installed and configured automatically.

Ceph OSDs are backed by sparse files created locally on the AIO host.
This allows Ceph to operate without dedicated block devices, which makes
the scenario suitable for labs and CI environments.

Enabling the AIO Ceph Scenario
==============================

Prepare the host as described in the standard AIO quickstart guide.

Before running the AIO bootstrap script, set the scenario variable to enable
the Ceph-enabled layout:

.. code-block:: console

   export SCENARIO='aio_ceph'

Then start the bootstrap process:

.. code-block:: console

   scripts/bootstrap-aio.sh

Bootstrap Behavior
==================

During the bootstrap process, OpenStack-Ansible prepares the host,
creates the required containers, and deploys a minimal Ceph cluster.

As part of this process, three sparse files are automatically created.
These files are used as Ceph OSD backing devices and together form the
Ceph cluster on the single AIO node.

Because the OSDs are file-backed and all services run on a single host,
this configuration is strictly for functional testing.

Ceph Services and Object Storage
================================

The deployment includes Ceph MON, OSD, and MGR services, as well as
Ceph RADOS Gateway (RGW).

After bootstrap completes, RGW is configured to provide a
Swift-compatible object storage endpoint. This allows Ceph RADOS Gateway
to act as a replacement for Swift and to be used as the object storage
backend in the AIO environment.

Once configured, Object Storage will also be available to users through
both the Skyline and Horizon dashboards.

For more details about using Ceph as a Swift replacement, see:

`Using Ceph for Swift-compatible Object Storage <https://docs.openstack.org/openstack-ansible/latest/user/ceph/swift.html>`_

Verification
============

After running the OpenStack-Ansible playbooks, you can verify the Ceph
cluster status. Since Ceph services run inside LXC containers, the
command should be executed on the Ceph monitor container.

For example, you can use an Ansible ad-hoc command:

.. code-block:: console

   ansible -m command -a "ceph -s" ceph_mon[0]

A healthy cluster should report three OSDs up and the monitor in quorum.

For production deployments, use dedicated Ceph nodes with proper storage
devices, redundancy, and failure domain design, see :ref:`production-ceph-environment-config`.
