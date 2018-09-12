.. _quickstart-aio:

===============
Quickstart: AIO
===============

All-in-one (AIO) builds are a great way to perform an OpenStack-Ansible build
for:

* a development environment
* an overview of how all of the OpenStack services fit together
* a simple lab deployment

Although AIO builds aren't recommended for large production deployments,
they're great for smaller proof-of-concept deployments.

Absolute minimum server resources (currently used for gate checks):

* 8 vCPU's
* 50GB free disk space on the root partition
* 8GB RAM

Recommended server resources:

* CPU/motherboard that supports `hardware-assisted virtualization`_
* 8 CPU Cores
* 80GB free disk space on the root partition, or 60GB+ on a blank
  secondary disk. Using a secondary disk requires the use of the
  ``bootstrap_host_data_disk_device`` parameter. Please see
  `Building an AIO`_ for more details.
* 16GB RAM

It's `possible` to perform AIO builds within a virtual machine for
demonstration and evaluation, but your virtual machines will perform poorly.
For production workloads, multiple nodes for specific roles are recommended.

.. _hardware-assisted virtualization: https://en.wikipedia.org/wiki/Hardware-assisted_virtualization


Building an AIO
---------------

There are three steps to running an AIO build, with an optional first step
should you need to customize your build:

* Configuration *(this step is optional)*
* Install and bootstrap Ansible
* Initial host bootstrap
* Run playbooks

When building an AIO on a new server, it is recommended that all
system packages are upgraded and then reboot into the new kernel:

.. note:: Execute the following commands and scripts as the root user.

.. code-block:: shell-session

   ## Ubuntu
   # apt-get dist-upgrade
   # reboot

.. code-block:: shell-session

   ## CentOS
   # yum upgrade
   # yum install git
   # reboot

.. code-block:: shell-session

   ## openSUSE
   # zypper up
   # zypper in git-core
   # reboot

.. note::

   If you are installing with limited connectivity, please review
   the *Installing with limited connectivity* appendix in the
   :deploy_guide:`Deployment Guide <index.html>` before proceeding.

Start by cloning the OpenStack-Ansible repository and changing into the
repository root directory:

.. code-block:: shell-session

   # git clone https://git.openstack.org/openstack/openstack-ansible \
       /opt/openstack-ansible
   # cd /opt/openstack-ansible

Next switch the applicable branch/tag to be deployed from. Note that
deploying from the head of a branch may result in an unstable build due to
changes in flight and upstream OpenStack changes. For a test (for example,
not a development) build it is usually best to checkout the latest tagged
version.

.. parsed-literal::

   # # List all existing tags.
   # git tag -l

   # # Checkout the stable branch and find just the latest tag
   # git checkout |current_release_git_branch_name|
   # git describe --abbrev=0 --tags

   # # Checkout the latest tag from either method of retrieving the tag.
   # git checkout |latest_tag|

.. note::
   The |current_release_formal_name| release is only compatible with Ubuntu
   16.04 (Xenial Xerus), Centos 7 and openSUSE Leap 42.X.

By default the scripts deploy all OpenStack services with sensible defaults
for the purpose of a gate check, development or testing system.

Review the `bootstrap-host role defaults`_ file to see
various configuration options. Deployers have the option to change how the
host is bootstrapped. This is useful when you wish the AIO to make use of
a secondary data disk, or when using this role to bootstrap a multi-node
development environment.

.. _bootstrap-host role defaults: https://git.openstack.org/cgit/openstack/openstack-ansible/tree/tests/roles/bootstrap-host/defaults/main.yml?h=stable/rocky

The bootstrap script is pre-set to pass the environment variable
``BOOTSTRAP_OPTS`` as an additional option to the bootstrap process. For
example, if you wish to set the bootstrap to re-partition a specific
secondary storage device (``/dev/sdb``), which will erase all of the data
on the device, then execute:

.. code-block:: shell-session

   # export BOOTSTRAP_OPTS="bootstrap_host_data_disk_device=sdb"

By default the filesystem type will be set to ext4, if you want another type
of filesystem to be used, just use something similar to the following:

.. code-block:: shell-session

   # export BOOTSTRAP_OPTS="bootstrap_host_data_disk_device=sdb bootstrap_host_data_disk_fs_type=xfs"

Additional options may be implemented by simply concatenating them with
a space between each set of options, for example:

.. code-block:: shell-session

   # export BOOTSTRAP_OPTS="bootstrap_host_data_disk_device=sdb"
   # export BOOTSTRAP_OPTS="${BOOTSTRAP_OPTS} bootstrap_host_ubuntu_repo=http://mymirror.example.com/ubuntu"

You may wish to change the role fetch mode. Options are ``galaxy`` and
``git-clone``. The default for this option is ``galaxy``.

options:
  :galaxy: Resolve all role dependencies using the ``ansible-galaxy`` resolver
  :git-clone: Clone all of the role dependencies using native git

Notes:
  When doing role development it may be useful to set
  ``ANSIBLE_ROLE_FETCH_MODE`` to ``git-clone``. This will provide you the
  ability to develop roles within the environment by modifying, patching, or
  committing changes using an intact git tree while the ``galaxy`` option
  scrubs the ``.git`` directory when it resolves a dependency.

.. code-block:: bash

   $ export ANSIBLE_ROLE_FETCH_MODE=git-clone

The next step is to bootstrap Ansible and the Ansible roles for the
development environment.  Deployers can customize roles by adding variables to
override the defaults in each role (see :ref:`user-overrides`).  Run the
following to bootstrap Ansible:

.. code-block:: shell-session

   # scripts/bootstrap-ansible.sh

Notes:
  You might encounter an error while running the Ansible bootstrap script
  when building some of the Python extensions (like pycrypto) which says:

  .. code-block:: shell-session

     configure: error: cannot run C compiled programs.

  The reason of this failure might be resulting from a noexec mount flag
  used for the filesystem associated with /tmp which you can check by
  running the following command:

  .. code-block:: shell-session

     # mount | grep $(df /tmp | tail -n +2 | awk '{print $1}') | grep noexec

  If this is the case you can specify an alternate path which does not
  have this mount option set:

  .. code-block:: shell-session

     # TMPDIR=/var/tmp scripts/bootstrap-ansible.sh

In order for all the services to run, the host must be prepared with the
appropriate disks partitioning, packages, network configuration and
configurations for the OpenStack Deployment.

For the default AIO scenario, this preparation
is completed by executing:

.. code-block:: shell-session

   # scripts/bootstrap-aio.sh

If you wish to use a different scenario, for example, the Ceph scenario,
execute the following:

.. code-block:: shell-session

   # export SCENARIO='ceph'
   # scripts/bootstrap-aio.sh

**Tested Scenarios**

.. raw:: html
   :file: scenario-table-gen.html


To add OpenStack Services over and above the `bootstrap-aio default services`_
for the applicable scenario, copy the ``conf.d`` files with the ``.aio`` file
extension into ``/etc/openstack_deploy`` and rename then to ``.yml`` files.
For example, in order to enable the OpenStack Telemetry services, execute the
following:

.. code-block:: shell-session

   # cd /opt/openstack-ansible/
   # cp etc/openstack_deploy/conf.d/{aodh,gnocchi,ceilometer}.yml.aio /etc/openstack_deploy/conf.d/
   # for f in $(ls -1 /etc/openstack_deploy/conf.d/*.aio); do mv -v ${f} ${f%.*}; done

To add any global overrides, over and above the defaults for the applicable
scenario, edit  ``/etc/openstack_deploy/user_variables.yml``. See the
:deploy_guide:`Deployment Guide <index.html>` for more details.

Finally, run the playbooks by executing:

.. code-block:: shell-session

   # cd /opt/openstack-ansible/playbooks
   # openstack-ansible setup-hosts.yml
   # openstack-ansible setup-infrastructure.yml
   # openstack-ansible setup-openstack.yml

The installation process will take a while to complete, but here are some
general estimates:

* Bare metal systems with SSD storage: ~ 30-50 minutes
* Virtual machines with SSD storage: ~ 45-60 minutes
* Systems with traditional hard disks: ~ 90-120 minutes

Once the playbooks have fully executed, it is possible to experiment with
various settings changes in ``/etc/openstack_deploy/user_variables.yml`` and
only run individual playbooks. For example, to run the playbook for the
Keystone service, execute:

.. code-block:: shell-session

   # cd /opt/openstack-ansible/playbooks
   # openstack-ansible os-keystone-install.yml

.. _bootstrap-aio default services: https://git.openstack.org/cgit/openstack/openstack-ansible/tree/tests/bootstrap-aio.yml

Rebooting an AIO
----------------

As the AIO includes all three cluster members of MariaDB/Galera, the cluster
has to be re-initialized after the host is rebooted.

This is done by executing the following:

.. code-block:: shell-session

   # cd /opt/openstack-ansible/playbooks
   # openstack-ansible -e galera_ignore_cluster_state=true galera-install.yml

If this fails to get the database cluster back into a running state, then
please make use of the
:dev_docs:`Galera Cluster Recovery <admin/maintenance-tasks/galera.html>`
section in the operations guide.

Rebuilding an AIO
-----------------

Sometimes it may be useful to destroy all the containers and rebuild the AIO.
While it is preferred that the AIO is entirely destroyed and rebuilt, this
isn't always practical. As such the following may be executed instead:

.. code-block:: shell-session

   # # Move to the playbooks directory.
   # cd /opt/openstack-ansible/playbooks

   # # Destroy all of the running containers.
   # openstack-ansible lxc-containers-destroy.yml

   # # On the host stop all of the services that run locally and not
   # #  within a container.
   # for i in \
          $(ls /etc/init \
            | grep -e "nova\|swift\|neutron\|cinder" \
            | awk -F'.' '{print $1}'); do \
       service $i stop; \
     done

   # # Uninstall the core services that were installed.
   # for i in $(pip freeze | grep -e "nova\|neutron\|keystone\|swift\|cinder"); do \
       pip uninstall -y $i; done

   # # Remove crusty directories.
   # rm -rf /openstack /etc/{neutron,nova,swift,cinder} \
            /var/log/{neutron,nova,swift,cinder}

   # # Remove the pip configuration files on the host
   # rm -rf /root/.pip

   # # Remove the apt package manager proxy
   # rm /etc/apt/apt.conf.d/00apt-cacher-proxy

Should an existing AIO environment need to be reinstalled, the most efficient
method is to destroy the host operating system and start over. For this reason,
AIOs are best run inside of some form of virtual machine or cloud guest.

Reference Diagram for an AIO Build
----------------------------------

Here is a basic diagram that attempts to illustrate what the resulting AIO
deployment looks like.

This diagram is not to scale and is not even 100% accurate, this diagram was
built for informational purposes only and should **ONLY** be used as such.

.. code-block:: text

              ------->[ ETH0 == Public Network ]
              |
              V                        [  *   ] Socket Connections
    [ HOST MACHINE ]                   [ <>v^ ] Network Connections
      *       ^  *
      |       |  |-------------------------------------------------------
      |       |                                                         |
      |       |---------------->[ HAProxy ]                             |
      |                                 ^                               |
      |                                 |                               |
      |                                 V                               |
      |                          (BR-Interfaces)<------                 |
      |                                  ^     *      |                 |
      *-[ LXC ]*--*----------------------|-----|------|----|            |
      |           |                      |     |      |  | |            |
      |           |                      |     |      |  | |            |
      |           |                      |     |      |  | |            |
      |           |                      |     |      V  * |            |
      |           *                      |     |   [ Galera x3 ]        |
      |        [ Memcached ]<------------|     |           |            |
      *-------*[ Rsyslog ]<--------------|--|  |           *            |
      |        [ Repos Server x3 ]<------|  ---|-->[ RabbitMQ x3 ]      |
      |        [ Horizon x2 ]<-----------|  |  |                        |
      |        [ Nova api ec2 ]<---------|--|  |                        |
      |        [ Nova api os ]<----------|->|  |                        |
      |        [ Nova console ]<---------|  |  |                        |
      |        [ Nova Cert ]<------------|->|  |                        |
      |        [ Cinder api ]<-----------|->|  |                        |
      |        [ Glance api ]<-----------|->|  |                        |
      |        [ Heat apis ]<------------|->|  | [ Loop back devices ]*-*
      |        [ Heat engine ]<----------|->|  |    \        \          |
      | ------>[ Nova api metadata ]     |  |  |    { LVM }  { XFS x3 } |
      | |      [ Nova conductor ]<-------|  |  |       *         *      |
      | |----->[ Nova scheduler ]--------|->|  |       |         |      |
      | |      [ Keystone x3 ]<----------|->|  |       |         |      |
      | | |--->[ Neutron agents ]*-------|--|---------------------------*
      | | |    [ Neutron server ]<-------|->|          |         |      |
      | | | |->[ Swift proxy ]<-----------  |          |         |      |
      *-|-|-|-*[ Cinder volume ]*----------------------*         |      |
      | | | |                               |                    |      |
      | | | -----------------------------------------            |      |
      | | ----------------------------------------- |            |      |
      | |          -------------------------|     | |            |      |
      | |          |                              | |            |      |
      | |          V                              | |            *      |
      ---->[ Compute ]*[ Neutron linuxbridge ]<---| |->[ Swift storage ]-
