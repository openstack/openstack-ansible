###Contributor guidelines
**Filing Bugs**

Bugs should be filed on Launchpad, not GitHub:

   https://bugs.launchpad.net/openstack-ansible

When submitting a bug, or working on a bug, please ensure the following criteria are met:

* The description clearly states or describes the original problem or root cause of the problem.
* Include historical information on how the problem was identified.
* Any relevant logs are included.
* The provided information should be totally self-contained. External access to web services/sites should not be needed.
* Steps to reproduce the problem if possible.

**Submitting Code**

Changes to the project should be submitted for review via the Gerrit tool, following
the workflow documented at:

   http://docs.openstack.org/infra/manual/developers.html#development-workflow

Pull requests submitted through GitHub will be ignored.


**Extra**

***Tags***: If it's a bug that needs fixing in a branch in addition to Master, add a '\<release\>-backport-potential' tag (eg ```juno-backport-potential```).  There are predefined tags that will autocomplete  
***Status***: Please leave this alone, it should be New till someone triages the issue.  
***Importance***: Should only be touched if it is a Blocker/Gating issue. If it is, please set to High, and only use Critical if you have found a bug that can take down whole infrastructures.
