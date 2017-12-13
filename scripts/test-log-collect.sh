#!/usr/bin/env bash
# Copyright 2017, Logan Vig <logan2211@gmail.com>
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

## Shell Opts ----------------------------------------------------------------
set -e -u -x

# Store the clone repo root location
export OSA_CLONE_DIR="$(readlink -f $(dirname ${0})/..)"

## Functions -----------------------------------------------------------------
info_block "Checking for required libraries." 2> /dev/null || source "${OSA_CLONE_DIR}/scripts/scripts-library.sh"

## Main ----------------------------------------------------------------------
gate_job_exit_tasks
