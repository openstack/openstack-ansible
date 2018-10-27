#!/bin/bash -xe
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

# Build English and translated version of project documentation

DOCNAME=doc
DIRECTORY=doc

# clean build dir
rm -rf  ${DIRECTORY}/build/

# create pot files
sphinx-build -a -b gettext \
    -d ${DIRECTORY}/build/doctrees.gettext \
    ${DIRECTORY}/source ${DIRECTORY}/source/locale/

# check all language translation resouce
for locale in `find ${DIRECTORY}/source/locale/ -maxdepth 1 -type d` ; do
    # skip if it is not a valid language translation resource.
    if [ ! -d ${locale}/LC_MESSAGES/ ]; then
        continue
    fi
    language=$(basename $locale)

    echo "===== Building $language translation ====="

    # prepare all translation resources
    for pot in ${DIRECTORY}/source/locale/*.pot ; do
        # get filename
        potname=$(basename $pot)
        resname=${potname%.pot}
        # merge all translation resources
        # "{resname}.pot" needs to be merged with "doc-{resname}.po" if exists
        if [ -e ${DIRECTORY}/source/locale/${language}/LC_MESSAGES/${DOCNAME}-${resname}.po ]; then
            msgmerge -q -o \
                ${DIRECTORY}/source/locale/${language}/LC_MESSAGES/${resname}.po \
                ${DIRECTORY}/source/locale/${language}/LC_MESSAGES/${DOCNAME}-${resname}.po \
                ${DIRECTORY}/source/locale/${potname}
        elif [ -e ${DIRECTORY}/source/locale/${language}/LC_MESSAGES/${DOCNAME}.po ]; then
            msgmerge -q -o \
                ${DIRECTORY}/source/locale/${language}/LC_MESSAGES/${resname}.po \
                ${DIRECTORY}/source/locale/${language}/LC_MESSAGES/${DOCNAME}.po \
                ${DIRECTORY}/source/locale/${potname}
        else
            msgcat ${DIRECTORY}/source/locale/${potname} > \
                ${DIRECTORY}/source/locale/${language}/LC_MESSAGES/${resname}.po
        fi
        # compile all translation resources
        msgfmt -o \
            ${DIRECTORY}/source/locale/${language}/LC_MESSAGES/${resname}.mo \
            ${DIRECTORY}/source/locale/${language}/LC_MESSAGES/${resname}.po
    done

    # build language version
    sphinx-build -a -b html -D language=${language} \
            -d ${DIRECTORY}/build/doctrees.languages/${language} \
            ${DIRECTORY}/source ${DIRECTORY}/build/html/${language}

    # remove newly created files
    git clean -f -q ${DIRECTORY}/source/locale/${language}/LC_MESSAGES/*.po
    git clean -f -x -q ${DIRECTORY}/source/locale/${language}/LC_MESSAGES/*.mo
    git clean -f -x -q ${DIRECTORY}/source/locale/.doctrees
    # revert changes to po file
    git reset -q ${DIRECTORY}/source/locale/${language}/LC_MESSAGES/
    for po in `git ls-files ${DIRECTORY}/source/locale/${language}/LC_MESSAGES` ; do
        git checkout -q -- $po
    done
done
# remove generated pot files
git clean -f -q ${DIRECTORY}/source/locale/*.pot

# build english version
sphinx-build -a -b html \
    -d ${DIRECTORY}/build/doctrees \
    ${DIRECTORY}/source ${DIRECTORY}/build/html/
