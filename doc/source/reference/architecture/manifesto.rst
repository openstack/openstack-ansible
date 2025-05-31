OpenStack-Ansible Manifesto
===========================

Project scope
~~~~~~~~~~~~~

This will be a '**Batteries included**' project. Which means deployer
can expect that deploying from any of the named feature branches or tags should
provide an OpenStack cloud built for production which will be
available at the successful completion of the deployment.

However, this project solely focuses on the deployment of OpenStack and its
requirements.

This project does **not** PXE boot hosts. Host setup and lifecycle management
is left to the deployer. This project also requires that bridges are setup
within the hosts to allow the containers to attach to a local bridge for
network access.
See also the :ref:`container-networking`.

Ansible Usage
~~~~~~~~~~~~~

Ansible provides an automation platform to simplify system and application
deployment. Ansible manages systems by using Secure Shell (SSH)
instead of unique protocols that require remote daemons or agents.

Ansible uses playbooks written in the YAML language for orchestration.
For more information, see `Ansible playbooks <https://docs.ansible.com/ansible/latest/user_guide/playbooks_intro.html>`_.

Ansible is a simple yet powerful orchestration tool that is ideally
equipped for deploying OpenStack-powered clouds. The declarative nature of
Ansible allows the deployer to turn an entire deployment into a rather
simple set of instructions.

Roles within the OpenStack-Ansible umbrella are built using Ansible
best practices and contain namespaced variables that are *human*
understandable. All roles are independant of each other and testable
separately.

All roles are built as Galaxy compatible roles even when the given role is
not intended for standalone use. While the project will offer a lot of
built-in roles the deployer will be able to pull down or override roles
with external ones using the built-in Ansible capabilities.
This allows extreme flexibility for deployers.

Source based deployments
~~~~~~~~~~~~~~~~~~~~~~~~

When the OpenStack-Ansible project was created, it was required
to provide a system able to override any OpenStack upstream
source code.

This means that OpenStack services and their python
dependencies are built and installed from source
code as found within the OpenStack Git repositories by default,
but allow deployers to point to their own repositories.

This also allows developers to point to their own code for
their work.

A source based deployment, for Python-built parts of OpenStack,
makes sense when dealing with scale and wanting consistency
over long periods of time. A deployer should have the ability
to deploy the same OpenStack release on every node throughout
the life cycle of the cloud, even when some components are
end of life. By providing a repository of the sources, the
deployment can be re-created even years after the initial
deployment, assuming the underlying operating systems and
packages stay the same.

This means that there will never be a time where OpenStack
specific packages, as provided by the distributions, are
being used for OpenStack services. Third party repositories
like *CloudArchive* and or *RDO* may still be required within
a given deployment but only as a means to meet application
dependencies.

Containerized deployments
~~~~~~~~~~~~~~~~~~~~~~~~~

This project introduces containers as a means to abstract services from
one another.

The use of containers allows for additional abstractions of entire
application stacks to be run all within the same physical host machines.

The "containerized" applications are sometimes grouped within a single
container where it makes sense, or distributed in multiple containers
based on application and or architectural needs.

The default container architecture has been built in such a way to allow
for scalability and highly available deployments.

The simple nature of machine containers allows the deployer to treat
containers as physical machines. The same concepts apply for machine
containers and physical machines: This will allow deployers to use
existing operational tool sets to troubleshoot issues within a deployment
and the ability to revert an application or service within inventory
to a known working state without having to re-kick a physical host.

Not all services are containerized: some don't make sense to run
within a container. Logic needs to be applied in regards on how services
are containerized. If their requirements can't be met due to system
limitations, (kernel, application maturity, etc...), then the service
is not set to run within a container.

Example of un-containerized services:

* Nova compute (for direct access to virtualization devices)
* Swift storage (for direct access to drive)

The containers are not a mean of securing a system.
The containers were not chosen for any eventual security safe
guards. The machine containers were chosen because of their
practicality with regard to providing a more uniform OpenStack
deployment. Even if the abstractions that the containers provides
do improve overall deployment security these potential benefits
are not the intention of the containerization of services.
