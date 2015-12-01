`Home <index.html>`_ OpenStack-Ansible Developer Documentation

Quick Start
===========

All-in-one (AIO) builds are a great way to perform an OpenStack-Ansible build
for:

* a development environment
* an overview of how all of the OpenStack services fit together
* a simple lab deployment

Although AIO builds aren't recommended for large production deployments,
they're great for smaller proof-of-concept deployments.

Absolute minimum server resources (currently used for gate checks):

* 8 vCPU's
* 50GB disk space
* 8GB RAM

Recommended server resources:

* CPU/motherboard that supports `hardware-assisted virtualization`_
* 8 CPU Cores
* 80GB disk space
* 16GB RAM

It's `possible` to perform AIO builds within a virtual machine but your
virtual machines will perform poorly.

.. _hardware-assisted virtualization: https://en.wikipedia.org/wiki/Hardware-assisted_virtualization

Running an AIO build in one step
--------------------------------

For a one-step build, there is a `convenient script`_ within the
Openstack-Ansible repository that will run a AIO build with defaults:

.. _convenient script: https://raw.githubusercontent.com/openstack/openstack-ansible/kilo/scripts/run-aio-build.sh

   .. code-block:: bash

    curl https://raw.githubusercontent.com/openstack/openstack-ansible/kilo/scripts/run-aio-build.sh | sudo bash

It's advised to run this build within a terminal muxer, like tmux or screen,
so that you don't lose your progress if you're disconnected from your terminal
session.

Running a customized AIO build
------------------------------

There are four main steps for running a customized AIO build:

* Configuration *(this step is optional)*
* Install and bootstrap Ansible
* Initial host bootstrap
* Run playbooks

Start by cloning the openstack-ansible repository and changing into the
repository root directory:

   .. code-block:: bash

       $ git clone https://github.com/openstack/openstack-ansible \
           /opt/openstack-ansible
       $ cd /opt/openstack-ansible

Next switch the applicable branch/tag you wish to deploy from. Note that
deploying from the head of a branch may result in an unstable build due to
changes in flight and upstream OpenStack changes. For a test (ie not a
development) build it is usually best to checkout the latest tagged version.

   .. code-block:: bash

       $ # List all existing tags.
       $ git tag -l

       $ # Checkout the latest tag from the previous command.
       $ git checkout 11.2.5

By default the scripts deploy all OpenStack services with sensible defaults
for the purpose of a gate check, development or testing system.

Review the ``tests/roles/bootstrap-host/defaults/main.yml`` file to see
various configuration options.  Deployers have the option to change how the
host is bootstrapped. This is useful when you wish the AIO to make use of
a secondary data disk, or when using this role to bootstrap a multi-node
development environment.

The bootstrap script is pre-set to pass the environment variable
``BOOTSTRAP_OPTS`` as an additional option to the bootstrap process. For
example, if you wish to set the bootstrap to re-partition a specific
secondary storage device (/dev/sdb), which will erase all of the data on the
device, then execute:

  .. code-block:: bash

      $ export BOOTSTRAP_OPTS="bootstrap_host_data_disk_device=sdb"

Additional options may be implemented by simply concatenating them with
a space between each set of options, for example:

  .. code-block:: bash

      $ export BOOTSTRAP_OPTS="bootstrap_host_data_disk_device=sdb"
      $ export BOOTSTRAP_OPTS="${BOOTSTRAP_OPTS} bootstrap_host_ubuntu_repo=http://mymirror.example.com/ubuntu"

The next step is to bootstrap Ansible and the Ansible roles for the
development environment.  Deployers can customize roles by adding variables to
override the defaults in each role (see :ref:`adding-galaxy-roles`).  Run the
following to bootstrap Ansible:

   .. code-block:: bash

       $ scripts/bootstrap-ansible.sh

In order for all the services to run, the host must be prepared with the
appropriate disks, packages, network configuration and a base configuration
for the OpenStack Deployment. This preparation is completed by executing:

   .. code-block:: bash

       $ scripts/bootstrap-aio.sh

If you wish to add any additional configuration entries for the OpenStack
configuration then this can be done now by editing
``/etc/openstack_deploy/user_variables.yml``. Please see the `Install Guide`_
for more details.

Finally, run the playbooks by executing:

   .. code-block:: bash

       $ scripts/run-playbooks.sh

The installation process will take a while to complete, but here are some
general estimates:

* Bare metal systems with SSD storage: ~ 30-50 minutes
* Virtual machines with SSD storage: ~ 45-60 minutes
* Systems with traditional hard disks: ~ 90-120 minutes

Once the playbooks have fully executed, you may experiment with various
settings changes in ``/etc/openstack_deploy/user_variable.yml`` and only
run individual playbooks. For example, to run the playbook for the
Keystone service, execute:

   .. code-block:: bash

       $ cd /opt/openstack-ansible/playbooks
       $ openstack-ansible os-keystone-install.yml

**Note:** The AIO bootstrap playbook will still build containers for services
that are not requested for deployment, but the service will not be deployed
in that container.

.. _Install Guide: ../install-guide/

Rebuilding the AIO
------------------
Sometimes it may be useful to destroy all the containers and rebuild the AIO.
While it is preferred that the AIO is entirely destroyed and rebuilt, this
isn't always practical. As such the following may be executed instead:

   .. code-block:: bash

       $ # Move to the playbooks directory.
       $ cd /opt/openstack-ansible/playbooks

       $ # Destroy all of the running containers.
       $ openstack-ansible lxc-containers-destroy.yml

       $ # On the host stop all of the services that run locally and not
       $ #  within a container.
       $ for i in \
              $(ls /etc/init \
                | grep -e "nova\|swift\|neutron" \
                | awk -F'.' '{print $1}'); do \
           service $i stop; \
         done

       $ # Uninstall the core services that were installed.
       $ for i in $(pip freeze | grep -e "nova\|neutron\|keystone\|swift"); do \
           pip uninstall -y $i; done

       $ # Remove crusty directories.
       $ rm -rf /openstack /etc/{neutron,nova,swift} \
                /var/log/{neutron,nova,swift}

There is a convenience script (``scripts/teardown.sh``) which will destroy
everything known within an environment. You should be aware that this script
will destroy whole environments and should be used WITH CAUTION.

After the teardown is complete, ``run-playbooks.sh`` may be executed again to
rebuild the AIO.

Quick AIO build on Rackspace Cloud
----------------------------------

You can automate the AIO build process with a virtual machine from the
Rackspace Cloud.

First, we will need a cloud-config file that will allow us to run the build as
soon as the instance starts.  Save this file as ``user_data.yml``:

   .. code-block:: yaml

    #cloud-config
    apt_mirror: http://mirror.rackspace.com/ubuntu/
    package_upgrade: true
    packages:
      - git-core
    runcmd:
      - export ANSIBLE_FORCE_COLOR=true
      - export PYTHONUNBUFFERED=1
      - export REPO=https://github.com/openstack/openstack-ansible
      - export BRANCH=kilo
      - git clone -b ${BRANCH} ${REPO} /opt/openstack-ansible
      - cd /opt/openstack-ansible && scripts/bootstrap-ansible.sh
      - cd /opt/openstack-ansible && scripts/bootstrap-aio.sh
      - cd /opt/openstack-ansible && scripts/run-playbooks.sh
    output: { all: '| tee -a /var/log/cloud-init-output.log' }

Feel free to customize the YAML file to meet your requirements.

We can pass this YAML file to nova and build a Cloud Server at Rackspace:

   .. code-block:: bash

    nova boot \
        --flavor general1-8 \
        --image 09de0a66-3156-48b4-90a5-1cf25a905207 \
        --key-name=public_key_name \
        --config-drive=true \
        --user-data user_data.yml
        --poll
        openstack-ansible-aio-build

Be sure to replace ``public_key_name`` with the name of the public key that
you prefer to use with your instance.  Within a minute or so, your instance
should be running and the OpenStack-Ansible installation will be in progress.

To follow along with the progress, ssh to your running instance and execute:

   .. code-block:: bash

    tail -F /var/log/cloud-init-output.log

Reference Diagram for the AIO Build
-----------------------------------

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
      |                          (BR-Interfaces)<-------                |
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
      |        [ Ceilometer api ]<-------|->|  |                        |
      |        [ Ceilometer collector ]<-|->|  |                        |
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

--------------

.. include:: navigation.txt
