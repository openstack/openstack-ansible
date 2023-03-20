==============================
Multi-Architecture Deployments
==============================

OpenStack-Ansible supports deployments where either the control plane
or compute nodes may comprise of several different CPU architectures

Mixed CPU architectures for compute nodes
=========================================

OpenStack-Ansible supports having compute nodes of multiple architectures
deployed in the same environment.

Deployments consisting entirely of x86_64 or aarch64 nodes do not need any
special consideration and will work according to the normal OpenStack-Ansible
documentation.

A deployment with a mixture of architectures, or adding a new architecture
to an existing single architecure deployment requires some additional
steps to be taken by both the deployer and end users to ensure that the
behaviour is as desired.

Example - adding ``aarch64`` nodes to an ``x86_64`` deployment
--------------------------------------------------------------

1) Install the operating system onto all the new compute nodes.

2) Add the new compute nodes to ``openstack_user_config.yml``.

3) Ensure a host of each compute architecture is present in
   ``repo-infra_hosts`` in ``openstack_user_config.yml``.

   This host will build python wheels for it's own architecture which will
   speed up the deployment of many hosts. If you do not make a repository
   server for each architecture, ensure that measures are taken not to
   overload the opendev.org git servers, such as using local mirrors of
   all OpenStack service repos.

4) Run the OpenStack-Ansible playbooks to deploy the required services.

5) Add HW_ARCH_XXXX Trait to Every Compute Host in Openstack

   Although most CPU hardware traits such as instruction set extensions are
   detected and handled automatically in OpenStack, CPU architecture is not.
   It is necessary to manually add an architecture trait to the resource provider
   corresponding to every compute host. The required traits are:

   HW_ARCH_X86_64    for x86_64 Intel and AMD CPUs
   HW_ARCH_AARCH64   for aarch64 architecure CPUs

   (see: https://docs.openstack.org/os-traits/latest/reference/traits.html)

    .. code:: bash

      openstack resource provider list
      openstack resource provider trait list <uuid-of-compute-host>
      openstack resource provider trait set --trait <existing-trait-1> --trait <existing-trait-2> ... --trait HW_ARCH_xxxxx <uuid-of-compute-host>

    .. note::

      The trait set command replaces all existing traits with the set provided,
      so you must specify all existing traits as well as the new trait.

6) Configure Nova Scheduler to Check Architecture

   Two additional settings in /etc/nova/nova.conf in all Nova API instances:

   .. code:: yaml

     [scheduler]
     image_metadata_prefilter = True

     [filter_scheduler]
     image_properties_default_architecture = x86_64

   The ``image_metadata_prefilter`` setting forces the Nova scheduler to match
   the ``hw_architecture`` property on Glance images with the corresponding HW_ARCH_XXX
   trait on compute host resource providers. This ensures that images explicitly tagged
   with a target architecture get scheduled hosts with a matching architecture.

   The ``image_properties_default_architecture`` setting would apply in an existing
   ``x86_64`` architecture cloud where previously ``hw_architecture`` was not set on all
   Glance images. This avoids the need to retrospectively apply the property for all
   existing images which may be difficult as users may have their own tooling to
   create and upload images without applying the required property.

   .. warning::

     Undocumented Behaviour Alert!

     Note that the image metadata prefilter and ImagePropertiesFilter are different
     and unrelated steps in the process Nova scheduler uses to determine candidate
     compute hosts. This section explains how to use them together.

     The ``image_metadata_prefilter`` only looks at the HW_ARCH_XXX traits on compute hosts
     and finds hardware that matches the required architecture. This only happens
     when the ``hw_architecture`` property is present on an image, and only if the
     required traits are manually added to compute hosts.

     The ``image_properties_default_architecture`` is used by the ImagePropertiesFilter
     which examines all the architectures supported by QEMU on each compute host; this
     includes software emulations of non-native architectures.

     If the full QEMU suite is installed on a compute host, that host will offer to run
     all architectures supported by the available ``qemu-system-*`` binaries. In this
     situation images without the ``hw_architecture`` property could be scheduled to a
     non native architecture host and emulated.

7) Disable QEMU Emulation

   .. note::

     This step applies particularly to existing ``x86_64`` environments when new
     ``aarch64`` compute nodes are added and it cannot be assumed that the
     ``hw_architecure`` property is applied to all Glance images as the operator
     may not be in control of all image uploads.

   To avoid unwanted QEMU emulation of non native architectures it is necessary to
   ensure that only the native ``qemu-system-*`` binary is present on all compute
   nodes. The simplest way to do this for existing deployments is to use the system
   package manager to ensure that the unwanted binaries are removed.

   OpenStack-Ansible releases including 2023.1 and later will only install the native
   architecture `qemu-system-*`` binary so this step should not be required on newer
   releases.

8) Upload images to Glance

   * Ideally the ``hw_architecture`` property is set for all uploaded images. It is
     mandatory to set this property for all architectures that do not match
     ``image_properties_default_architecture``

   * It is recommended to set the property ``hw_firmware_type='uefi'`` for any images
     which require UEFI boot, even when this implicit with the ``aarch64`` architecture.
     This is to avoid issues with NVRAM files in libvirt when deleting an instance.

Architecture emulation by Nova
==============================

Nova has the capability to allow emulation of one CPU architecture on a host
with a different native CPU architecure, see https://docs.openstack.org/nova/latest/admin/hw-emulation-architecture.html
for more details.

This OpenStack-Ansible documentation currently assumes that a deployer wishes to
run images on a compute host with a native CPU architecure, and does not give an
example configuration involving emulation.
