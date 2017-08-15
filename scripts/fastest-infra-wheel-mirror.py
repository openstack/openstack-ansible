#!/usr/bin/env python
#
# Copyright 2016, Rackspace US, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# (c) 2016, Jesse Pretorius <jesse.pretorius@rackspace.co.uk>
#
# Based on the mirror test script posted at
# http://code.activestate.com/recipes/284631-a-python-script-to-test-download-mirrors/

import platform
import Queue
import re
import threading
import time
import urllib

HTTP_TIMEOUT = 10.0         # Max. seconds to wait for a response
HTTP_TITLE = "Wheel Index"  # HTTP Title to look for to validate the page
MAX_THREADS = 10
MIRROR_LIST = [
    "http://mirror.dfw.rax.openstack.org/wheel/",
    "http://mirror.ord.rax.openstack.org/wheel/",
    "http://mirror.iad.rax.openstack.org/wheel/",
    "http://mirror.gra1.ovh.openstack.org/wheel/",
    "http://mirror.bhs1.ovh.openstack.org/wheel/",
    "http://mirror.sjc1.bluebox.openstack.org/wheel/",
    "http://mirror.nyj01.internap.openstack.org/wheel/",
    "http://mirror.regionone.infracloud-chocolate.openstack.org/wheel/",
    "http://mirror.regionone.infracloud-vanilla.openstack.org/wheel/",
    "http://mirror.kna1.citycloud.openstack.org/wheel/",
    "http://mirror.la1.citycloud.openstack.org/wheel/",
    "http://mirror.lon1.citycloud.openstack.org/wheel/",
    "http://mirror.sto2.citycloud.openstack.org/wheel/"
]


def TestUrl(workQueue, resultQueue):

    '''Worker thread procedure.

    Test how long it takes to return the mirror index page,
    then return the results into resultQueue.
    '''

    def SubthreadProc(url, result):

        '''Subthread procedure.

        Actually get the mirror index page in a subthread, so that we can time
        out using join rather than wait for a very slow server.  Passing in a
        list for result lets us simulate pass-by-reference, since callers
        cannot get the return code from a Python thread.
        '''

        startTime = time.time()
        try:
            data = urllib.urlopen(url).read()
        except Exception:
            # Could be a socket error or an HTTP error--either way, we
            # don't care--it's a failure to us.
            result.append(-1)
        else:
            if not CheckTitle(data):
                result.append(-1)
            else:
                elapsed = int((time.time() - startTime) * 1000)
                result.append(elapsed)

    def CheckTitle(html):

        '''Check that the HTML title is the expected value.

        Check the HTML returned for the presence of a specified
        title. This caters for a situation where a service provider
        may be redirecting DNS resolution failures to a web search
        page, or where the returned data is invalid in some other
        way.
        '''

        titleRegex = re.compile("<title>(.+?)</title>")
        try:
            title = titleRegex.search(html).group(1)
        except Exception:
            # If there is no match, then we consider it a failure.
            result.append(-1)
        else:
            if title == HTTP_TITLE:
                return True
            else:
                return False

    while 1:
        # Continue pulling data from the work queue until it's empty
        try:
            url = workQueue.get(0)
        except Queue.Empty:
            # work queue is empty--exit the thread proc.
            return

        # Create a single subthread to do the actual work
        result = []
        subThread = threading.Thread(target=SubthreadProc, args=(url, result))

        # Daemonize the subthread so that even if a few are hanging
        # around when the process is done, the process will exit.
        subThread.setDaemon(True)

        # Run the subthread and wait for it to finish, or time out
        subThread.start()
        subThread.join(HTTP_TIMEOUT)

        if [] == result:
            # Subthread hasn't give a result yet.  Consider it timed out.
            resultQueue.put((url, "TIMEOUT"))
        elif -1 == result[0]:
            # Subthread returned an error from geturl.
            resultQueue.put((url, "FAILED"))
        else:
            # Subthread returned a time.  Store it.
            resultQueue.put((url, result[0]))

# Set the number of threads to use
numThreads = min(MAX_THREADS, len(MIRROR_LIST))

# Build a queue to feed the worker threads
workQueue = Queue.Queue()
for url in MIRROR_LIST:
    # Build the complete URL
    distro = platform.linux_distribution()[0].split(' ')[0].lower()
    if distro == 'centos':
        version = platform.linux_distribution()[1].split('.')[0]
    else:
        version = platform.linux_distribution()[1]
    architecture = platform.machine()
    fullUrl = url + distro + "-" + version + "-" + architecture + "/"
    workQueue.put(fullUrl)

workers = []
resultQueue = Queue.Queue()

# Create worker threads to load-balance the retrieval
for threadNum in range(0, numThreads):
    workers.append(threading.Thread(target=TestUrl,
                                    args=(workQueue, resultQueue)))
    workers[-1].start()

# Wait for all the workers to finish
for w in workers:
    w.join()

# Separate the successes from failures
timings = []
failures = []
while not resultQueue.empty():
    url, result = resultQueue.get(0)
    if isinstance(result, str):
        failures.append((result, url))
    else:
        timings.append((result, url))

# Sort by increasing time or result string
timings.sort()
failures.sort()

# If all results are failed, then exit silently
if len(timings) > 0:
    # Print out the fastest mirror URL
    print(timings[0][1])
