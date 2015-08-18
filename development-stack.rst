OpenStack Ansible Deployment
############################
:date: 2015-02-02 22:00
:tags: lxc, openstack, cloud, ansible
:category: \*nix


Building a development stack
----------------------------

To deploy an *all-in-one* (AIO) environment for testing or contributing to
this project, use the scripts in the ``scripts`` directory. You must run these
scripts from the repository top-level directory. For example:

.. code-block:: console

   $ git clone https://github.com/stackforge/os-ansible-deployment \
     /opt/os-ansible-deployment
   $ cd /opt/os-ansible-deployment
   $ scripts/bootstrap-aio.sh

Requirements
^^^^^^^^^^^^

* Quad-core processor capable of running KVM
* 8 GB of RAM
* 60 GB of storage

  .. note::

     By default, the deployment scripts use the file system on "/" for
     containers. Optionally, the deployment scripts can use LVM for
     containers. To use LVM, create the ``lvm`` volume group. Each
     container uses a logical volume that requires **5 GB** of available
     storage in the volume group.

If deploying on a Rackspace public cloud server, use the *general1-8* or
larger flavor. Optionally, you can use the Orchestration template
``osad-aio-heat-template.yml`` to launch a cloud server and deploy an AIO
environment on it.

These requirements may seem excessive; however, the default AIO deployment
builds a roughly 35-node environment that closely matches the reference
architecture. For example, components such as RabbitMQ, MariaDB with Galera,
source repository, and Identity service all use multiple containers to
simulate clustering.

Finally, the AIO deployment uses HAProxy for testing purposes only. Please
do not use this HAProxy configuration for production purposes because it
does not provide any redundancy.

.. note::

   Never deploy an AIO environment on a host that you cannot risk breaking
   or destroying.

Procedure
^^^^^^^^^

To deploy an AIO environment, complete these steps:

#. Clone the repository:

   .. code-block:: console

      $ git clone https://github.com/stackforge/os-ansible-deployment \
        /opt/os-ansible-deployment

#. Change to the repository top-level directory:

   .. code-block:: console

      $ cd /opt/os-ansible-deployment

#. By default, the repository uses the *master* branch. Optionally, you can
   check out a different branch. For example, to check out the Kilo branch:

   .. code-block:: console

      $ git checkout kilo

#. By default, the scripts deploy all OpenStack services. Optionally, you can
   disable one or more services using environment variables. See the
   ``DEPLOY_*`` variables in the ``run-playbooks.sh`` script for details. For
   example, to disable the Telemetry service:

   .. code-block:: console

      $ export DEPLOY_CEILOMETER="no"

   .. note::

      The scripts still build containers for any service that you disable, but
      do not deploy the service.

#. Prepare the host:

   .. code-block:: console

      $ scripts/bootstrap-aio.sh

   .. note::

      This script configures the host operating system and supplies values for
      mandatory options in configuration files in the
      ``/etc/openstack_deploy`` directory.

#. Install the necessary Ansible components:

   .. code-block:: console

      $ scripts/bootstrap-ansible.sh

   .. note::

      Only run this script once.

#. Run the Ansible playbooks to deploy the environment:

   .. code-block:: console

      $ scripts/run-playbooks.sh

   .. note::

      You can run this script multiple times.

   Optionally, you can run individual playbooks. For example, to deploy the
   Identity service:

   .. code-block:: console

      $ cd /opt/os-ansible-deployment/playbooks
      $ openstack-ansible os-keystone-install.yml

Rebuilding the stack
^^^^^^^^^^^^^^^^^^^^

Once you have completed your testing and or dev work if you'd like to tear down the stack and restart from a new build there is a play that will assist you in doing just that. Simply change to your playbooks directory and execute the ``lxc-containers-destroy.yml`` play.

Example:

.. code-block:: bash

  # Move to the playbooks directory.
  cd /opt/os-ansible-deployment/playbooks

  # Destroy all of the running containers.
  openstack-ansible lxc-containers-destroy.yml

  # On the host stop all of the services that run locally and not within a container.
  for i in $(ls /etc/init | grep -e nova -e swift -e neutron | awk -F'.' '{print $1}'); do service $i stop; done

  # Uninstall the core services that were installed.
  for i in $(pip freeze | grep -e nova -e neutron -e keystone -e swift); do pip uninstall -y $i; done

  # Remove crusty directories.
  rm -rf /openstack /etc/neutron /etc/nova /etc/swift /var/log/neutron /var/log/nova /var/log/swift


Using the teardown script:
  The ``teardown.sh`` script that will destroy everything known within an environment. You should be aware that this script will destroy whole environments and should be used **WITH CAUTION**.

This script will destroy all of your running containers and remove items within the ``/openstack`` directory for the container. After the completion of this play you can rerun the ``run-playbooks.sh`` or you can run the plays manually to rebuild the stack.

Notice
^^^^^^

The system uses a number of variables. You should look a the scripts for a full explanation and description of all of the available variables that you can set. At a minimum you should be aware of the default public interface variable as you may be kicking on a box that does not have an ``eth0`` interface. To set the default public interface run the following.

.. code-block:: bash

    export PUBLIC_INTERFACE="<<REPLACE WITH THE NAME OF THE INTERFACE>>" # This is only required if you dont have eth0


Diagram of stack
^^^^^^^^^^^^^^^^

Here is a basic diagram that attempts to illustrate what the AIO installation job is doing. **NOTICE** This diagram is not to scale and is not even 100% accurate, this diagram was built for informational purposes only and should **ONLY** be used as such.


Diagram::

    ====== ASCII Diagram for AIO infrastructure ======

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


    ====== ASCII Diagram for AIO infrastructure ======
