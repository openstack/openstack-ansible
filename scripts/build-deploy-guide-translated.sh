#!/bin/bash

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

# Build English and translated versions of the OpenStack-Ansible *deploy-guide*.
#

set -e
set -x

DOCNAME=doc-deploy-guide
SRC=doc/source/deploy-guide/source
LOCALE=doc/source/locale
BUILD=doc/source/deploy-guide/build

# Sphinx warnings treated as an error
SPHINX_BUILD_OPTION_ENG='-W'
SPHINX_BUILD_OPTION_TRANS='-W'

# Initial env vars
SKIP_SPHINX_WARNINGS=${SKIP_SPHINX_WARNINGS:-0}
SPHINX_WARNINGS_TRANS=${SPHINX_WARNINGS_TRANS:-0}

# Skip -W option for english and translation builds
if [ ${SKIP_SPHINX_WARNINGS} -lt 1 ]; then
    SPHINX_BUILD_OPTION_ENG=''
fi

if [ ${SPHINX_WARNINGS_TRANS} -gt 0 ]; then
    SPHINX_BUILD_OPTION_TRANS=''
fi

function prepare_language_index {
    # Global variables
    HAS_LANG=0
    LANG_INDEX=`mktemp`

    cat <<EOF >> $LANG_INDEX
[
\`English <__BASE__/__INDEX__>\`__
EOF

    # Generate language index file
    for locale in `find ${LOCALE}/ -maxdepth 1 -type d` ; do
        # skip if it is not a valid language translation resource.
        if [ ! -e ${locale}/LC_MESSAGES/${DOCNAME}.po ]; then
            continue
        fi
        language=$(basename $locale)

        # Reference translated document from index file
        echo -n "| " >> $LANG_INDEX
        HAS_LANG=1
        get_lang_name_prog=$(dirname $0)/docstheme-lang-display-name.py
        if [ -e "$get_lang_name_prog" ]; then
            name=`python3 $get_lang_name_prog $language`
        else
            name=`docstheme-lang-display-name.py $language 2>/dev/null || echo $language`
        fi
        echo "\`$name <__BASE__/${language}/__INDEX__>\`__" >> $LANG_INDEX
    done

    cat <<EOF >> $LANG_INDEX
]

EOF
}

function _add_language_index {
    local target_file=$1
    local basepath=$2

    local basename
    basename=$(echo $target_file | sed -e "s|${SRC}/||" -e "s|\.rst$||")
    path_to_top_level=$(dirname $basename | sed -e 's|[^./]\+|..|g')

    local _basepath
    if [ "$basepath" = "." -a "$path_to_top_level" = "." ]; then
        _basepath="."
    elif [ "$basepath" = "." ]; then
        _basepath=$path_to_top_level
    elif [ "$path_to_top_level" = "." ]; then
        _basepath=$basepath
    else
        _basepath="$basepath/$path_to_top_level"
    fi

    cp -p $target_file $target_file.backup
    sed -e "s|__BASE__|$_basepath|" -e "s|__INDEX__|$basename.html|" $LANG_INDEX > $target_file
    cat $target_file.backup >> $target_file
}

function add_language_index_to_localized {
    for f in `find $SRC -name '*.rst'`; do
        _add_language_index $f ..
    done
}

function add_language_index_to_original {
    for f in `find $SRC -name '*.rst'`; do
        cp -p $f.backup $f
        _add_language_index $f .
    done
}

function recover_rst_files {
    for f in `find $SRC -name '*.rst'`; do
        if [ -f $f.backup ]; then
            mv $f.backup $f
        fi
    done
}

function remove_pot_files {
    rm -f ${LOCALE}/${DOCNAME}.pot
}

function cleanup {
    if [ $DOCSTHEME_BUILD_TRANSLATED__NO_CLEANUP ]; then
        echo "Skipping cleanup. Your repository is dirty."
        return
    fi
    [ $LANG_INDEX ] && rm -f -- $LANG_INDEX
    recover_rst_files
    remove_pot_files
}

trap cleanup EXIT

sphinx-build -a -W -b gettext \
    -d ${BUILD}/doctrees.gettext \
    ${SRC} ${LOCALE}/

prepare_language_index
if [ "$HAS_LANG" = "0" ]; then
    # No translations: just build English at the deploy-guide root.
    sphinx-build -a ${SPHINX_BUILD_OPTION_ENG} --keep-going -b html \
        -d ${BUILD}/doctrees \
        ${SRC} ${BUILD}/html/
    exit 0
fi

add_language_index_to_localized

# Build each available translation into ${BUILD}/html/<language>/.
for locale in `find ${LOCALE}/ -maxdepth 1 -type d` ; do
    # skip if it is not a valid language translation resource.
    if [ ! -e ${locale}/LC_MESSAGES/${DOCNAME}.po ]; then
        continue
    fi
    language=$(basename $locale)

    echo "===== Building $language translation ====="

    po=${LOCALE}/${language}/LC_MESSAGES/${DOCNAME}.po

    msgmerge -U --silent ${po} ${LOCALE}/${DOCNAME}.pot
    msgfmt -o ${LOCALE}/${language}/LC_MESSAGES/${DOCNAME}.mo ${po}

    # build translated guide
    sphinx-build -a ${SPHINX_BUILD_OPTION_TRANS} -b html -D language=${language} \
        -d ${BUILD}/doctrees.languages/${language} \
        ${SRC} ${BUILD}/html/${language}

    # revert changes
    git checkout -q -- ${po} 2>/dev/null || true
    rm -f ${LOCALE}/${language}/LC_MESSAGES/${DOCNAME}.mo
done

remove_pot_files

add_language_index_to_original

sphinx-build -a ${SPHINX_BUILD_OPTION_ENG} --keep-going -b html \
    -d ${BUILD}/doctrees \
    ${SRC} ${BUILD}/html/
