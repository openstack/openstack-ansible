OpenStack Ansible Deployment
############################
:tags: openstack, cloud, ansible
:category: \*nix

contributor guidelines
^^^^^^^^^^^^^^^^^^^^^^

Filing Bugs
-----------

Bugs should be filed on Launchpad, not GitHub: "https://bugs.launchpad.net/openstack-ansible".


When submitting a bug, or working on a bug, please ensure the following criteria are met:
    * The description clearly states or describes the original problem or root cause of the problem.
    * Include historical information on how the problem was identified.
    * Any relevant logs are included.
    * The provided information should be totally self-contained. External access to web services/sites should not be needed.
    * Steps to reproduce the problem if possible.


Submitting Code
---------------

Changes to the project should be submitted for review via the Gerrit tool, following
the workflow documented at: "http://docs.openstack.org/infra/manual/developers.html#development-workflow"

Pull requests submitted through GitHub will be ignored and closed without regard.


Extra
-----

Tags:
    If it's a bug that needs fixing in a branch in addition to Master, add a '\<release\>-backport-potential' tag (eg ``juno-backport-potential``).  There are predefined tags that will auto-complete.

Status:
    Please leave this alone, it should be New till someone triages the issue.

Importance:
    Should only be touched if it is a Blocker/Gating issue. If it is, please set to High, and only use Critical if you have found a bug that can take down whole infrastructures.


Style guide
-----------

When creating tasks and other roles for use in Ansible please create then using the YAML dictionary format.

Example YAML dictionary format:
    .. code-block:: yaml

        - name: The name of the tasks
          module_name:
            thing1: "some-stuff"
            thing2: "some-other-stuff"
          tags:
            - some-tag
            - some-other-tag


Example what **NOT** to do:
    .. code-block:: yaml

        - name: The name of the tasks
          module_name: thing1="some-stuff" thing2="some-other-stuff"
          tags: some-tag

    .. code-block:: yaml

        - name: The name of the tasks
          module_name: >
            thing1="some-stuff"
            thing2="some-other-stuff"
          tags: some-tag


Usage of the ">" and "|" operators should be limited to Ansible conditionals and command modules such as the ansible ``shell`` or ``command``.


Issues
------

When submitting an issue, or working on an issue please ensure the following criteria are met:
    * The description clearly states or describes the original problem or root cause of the problem.
    * Include historical information on how the problem was identified.
    * Any relevant logs are included.
    * If the issue is a bug that needs fixing in a branch other than Master, please note the associated branch within the launchpad issue.
    * The provided information should be totally self-contained. External access to web services/sites should not be needed.
    * Steps to reproduce the problem if possible.
