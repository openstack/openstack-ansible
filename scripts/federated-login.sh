#!/usr/bin/env bash

# Copyright 2015, Rackspace US, Inc.
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

# defaults
DOMAIN=Default
PROJECT=
SP_ID=

usage()
{
    echo Usage: $0 "--project <project-name>" "--domain <domain-name>" "<service-provider-name>" >&2
    echo "Options:" >&2
    echo "    -p | --project   The project on the SP cloud to log in to." >&2
    echo "    -d | --domain    The domain on the SP cloud to log in to. The default domain is used if not specified." >&2
    exit 1
}


while [[ $# > 0 ]]; do
    key="$1"
    case $key in
        -d|--domain)
            DOMAIN="$2"
            shift
            ;;
        -p|--project)
            PROJECT="$2"
            shift
            ;;
        -h|--help)
            usage
            ;;
        *)
            break
            ;;
    esac
    shift
done
SP_ID=$1

if [ "$DOMAIN" == "" ]; then
    echo Error: Domain must be specified.
fi
if [ "$PROJECT" == "" ]; then
    echo Error: Project must be specified.
fi
if [ "$SP_ID" == "" ]; then
    echo Error: Service provider must be specified.
fi
if [ "$DOMAIN" == "" -o "$PROJECT" == "" -o "$SP_ID" == "" ]; then
    usage
fi

echo Performing federated login...

# obtain a scoped token from the identity provider
curl -v -s -X POST -H "Content-Type: application/json" -d '{"auth":{"scope": {"project":{"domain": {"name": "'"$OS_DOMAIN_NAME"'"}, "name": "'"$OS_PROJECT_NAME"'"}},"identity":{"methods":["password"],"password":{"user":{"name":"'"$OS_USERNAME"'","password":"'"$OS_PASSWORD"'","domain":{"name":"'"$OS_DOMAIN_NAME"'"}}}}}}' $OS_AUTH_URL/auth/tokens >token.json 2>token.txt
if [ "$?" != "0" ]; then
    echo "Could not obtain IdP token, did you forget to import your openrc file? See token.json and error.log for details."
    exit 1
fi
IDP_TOKEN=`grep X-Subject-Token token.txt | grep -Po ': .*' | grep -Po '[a-zA-Z0-9-_%]*'`
echo - Obtained IdP token.

# obtain the service provider URLs
python -c "import json; t = json.loads(open('token.json').read()); sp = [x for x in t['token']['service_providers'] if x['id'] == '$SP_ID']; print('SP_URL='+sp[0][\"sp_url\"]+'\nSP_AUTH_URL='+sp[0][\"auth_url\"] if len(sp) > 0 else '')" > sp.txt
source sp.txt
if [ "$SP_URL" == "" -o "$SP_AUTH_URL" == "" ]; then
    echo "Could not find service provider $SP_ID."
    exit 1
fi
SP_KEYSTONE_V3_URL=`echo $SP_AUTH_URL  | grep -Po "(.*/v3)"`

# request a SAML2 assertion from the identity provider
curl -s -X POST -H "X-Auth-Token: $IDP_TOKEN" -H "Content-Type: application/json" -d '{"auth": {"scope": {"service_provider": {"id": "'"$SP_ID"'"}}, "identity": {"token": {"id":"'"$IDP_TOKEN"'"}, "methods": ["token"]}}}' $OS_AUTH_URL/auth/OS-FEDERATION/saml2/ecp >assertion.xml 2>error.log
if [ "$?" != "0" ] || grep -q error assertion.xml; then
    echo Could not obtain SAML2 assertion. See assertion.xml and error.log for details.
    exit 1
fi
echo - Obtained SAML2 assertion from IdP.

# send the assertion to the service provider
curl -s -X POST -H "Content-Type: application/vnd.paos+xml" -c cookies.txt -d "@assertion.xml" $SP_URL >error.log 2>&1
if [ "$?" != "0" ]; then
    echo The assertion was not accepted by the service provider. See error.log for details.
    exit 1
fi
echo - Submitted SAML2 assertion to SP.

# request an unscoped token from the service provider
curl -v -s -X GET -H "Content-Type: application/vnd.paos+xml" -b cookies.txt $SP_AUTH_URL >/dev/null 2>unscoped.txt
if [ "$?" != "0" ] || ! grep -q X-Subject-Token unscoped.txt; then
    echo Could not obtain unscoped token from service provider. See unscoped.txt and error.log for details.
    exit 1
fi
UNSCOPED_TOKEN=`grep X-Subject-Token unscoped.txt | grep -Po ': .*' | grep -Po '[a-zA-Z0-9-_%]*'`
echo - Obtained unscoped token from SP: $UNSCOPED_TOKEN

echo '- Domains available at sp: '
curl -v -s -X GET -H "X-Auth-Token: $UNSCOPED_TOKEN" "${SP_KEYSTONE_V3_URL}/OS-FEDERATION/domains" 2>error.log | python -m json.tool |awk '/"name":/{print $2}'

echo '- Projects  available at sp: '
curl -v -s -X GET -H "X-Auth-Token: $UNSCOPED_TOKEN" \
  "${SP_KEYSTONE_V3_URL}/OS-FEDERATION/projects" \
  >fed_projects.json \
  2>error.log
python -m json.tool <fed_projects.json |awk '/"name":/{print $2}'
grep -q $PROJECT fed_projects.json || { echo "$PROJECT is not available at $SP_ID"; exit 1; }


# exchange the unscoped token for a scoped token
curl -v -s -X POST -H "X-Auth-Token: $UNSCOPED_TOKEN" -H "Content-Type: application/json" -d '{"auth":{"identity":{"methods":["saml2"],"saml2":{"id":"'"$UNSCOPED_TOKEN"'"}},"scope":{"project":{"domain": {"name": "'"$DOMAIN"'"},"name":"'"$PROJECT"'"}}}}' $SP_KEYSTONE_V3_URL/auth/tokens >catalog.txt 2>scoped.txt
if [ "$?" != "0" ] || grep -q 401 scoped.txt; then
    echo Could not obtain scoped token and catalog from service provider. See scoped.txt and catalog.txt for details.
    exit 1
fi
SCOPED_TOKEN=`awk '/X-Subject-Token/{print $3}' scoped.txt`
python -m json.tool <catalog.txt >catalog.json
echo - Obtained scoped token from SP for project $PROJECT in domain $DOMAIN: $SCOPED_TOKEN
echo - Full catalog available in file catalog.json

cat <<EOF >_print_vars.py
import json
import sys

token = sys.argv[1]
catalog = json.loads(open(sys.argv[2]).read())

print('#----------------------------------------')
print('# Available endpoints:')
for service in catalog['token']['catalog']:
    svc_type = service['type']
    for endpoint in service['endpoints']:
        if endpoint['interface'] == 'public':
            svc_endpoint = endpoint['url']
    print(svc_type.upper().replace('-', '_') + '_URL=' + svc_endpoint)

print('#----------------------------------------')
print('# OpenStack client setup:')
print('export OS_TOKEN=' + token)
print('export OS_URL=<desired-service-endpoint>')
EOF
python _print_vars.py $SCOPED_TOKEN catalog.txt

# cleanup
rm token.json token.txt sp.txt assertion.xml cookies.txt unscoped.txt scoped.txt catalog.txt error.log _print_vars.py fed_projects.json
