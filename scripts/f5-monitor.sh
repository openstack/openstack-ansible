#!/usr/bin/env bash

# Copy stdout to fd 3 and redirect stdout/stderr to /var/log/f5-monitor.log
exec 3>&1 &> /dev/null
#/var/log/f5-monitor.log - replace null with this file to enable logging when executing the script

# Auth connection
auth_proto="http"
auth_ip="INSERT-IP-HERE"
    #Internal IP address of f5 VIP
auth_port="5000"
auth_url="$auth_proto://$auth_ip:$auth_port/v2.0/tokens"

# Auth args pulled from source file
tenant="admin"
user="admin"
pass="INSERTPWHERE"
tenant_id="INSERTIDHERE"

# Save token to file
save_token() {
    echo "$token" > /var/tmp/keystone-token
}

# Get new token
new_token() {
    # Curl new token from keystone from user/pass for tenant
    IFS=$'\n' read -rd '' -a resp < <(curl -sk $auth_url -X POST -H "Accept: application/xml" -H "Content-Type: application/json" -H "User-Agent: f5-ltm" -d @- -w "\n%{http_code}" <<EOF
{
    "auth": {
        "tenantName": "$tenant",
        "passwordCredentials": {
            "username": "$user",
            "password": "$pass"
        }
    }
}
EOF
    )

    # Exit if status is 401 (invalid username/pass)
    if [[ "${resp[@]:(-1)}" == "401" ]]
    then
        echo "Exiting after failure to get a valid token: Check user/pass."
        printf "%s\n" "${resp[@]}"
        exit -1
    fi

    # Set token variable
    token=$(sed -nr '/<token/ s/^.*issued_at="(.*)" expires="(.*)" id="(.*)".*$/\3/p' <<< "${resp[@]:2:1}")

    # Might need to parse tenant ID
    #tenant=...

    # Mark as new token
    token_new=1

    # Save to file
    save_token
}

# Read token from file or get new one
get_token() {
    # If file exists
    if [[ -f /var/tmp/keystone-token ]]
    then
        # Read into token variable
        read -r token < /var/tmp/keystone-token
    else
        # Get new one
        new_token
    fi
}

do_check() {
    # Check connection
    check_proto="$auth_proto"
    check_ip=$1
    check_port=$2

    # Build check url by port
    case $check_port in
        5000)
            #Keystone
            check_url="$check_proto://$check_ip:$check_port/v2.0/"
            ;;
        8776)
            #Cinder
            check_url="$check_proto://$check_ip:$check_port/v2/"
            ;;
        9292)
            #Glance API
            check_url="$check_proto://$check_ip:$check_port/v1/"
            ;;
        9191)
            #Glance Registry
            check_url="$check_proto://$check_ip:$check_port/"
            ;;
        9696)
            #Neutron Server
            check_url="$check_proto://$check_ip:$check_port/v2.0/"
            ;;
        8774)
            #Nova API Compute
            check_url="$check_proto://$check_ip:$check_port/v3/"
            ;;
        8004)
            #Heat API
            check_url="$check_proto://$check_ip:$check_port/v1/$tenant_id/stacks?"
            ;;
        *)
            # Guard
            echo "Invalid port specified; bailing out"
            exit -1
    esac

    # Check endpoint
    IFS=$'\n' read -rd '' -a resp < <(curl -s -I -X GET -H "User-Agent: f5-ltm" -H "X-Auth-Token: $token"  $check_url -w "\n%{http_code}")

    # Store status code
    status="${resp[@]:(-1)}"

    # If 200, we're golden
    if [[ "$status" == "200" ]]
    then
        echo "Success" >&3
        exit 0
    # Check for 401 (token expiration or unauthorized)
    elif [[ "$status" == "401" ]]
    then
        # Exit if token is new
        if [[ "$token_new" == "1" ]]
        then
            echo "Exiting after failure to authorize with valid token $token on $check_url"
            printf "%s\n" "${resp[@]}"
            exit -1
        # Else we tried cached token
        else
            # Get a new token and try again
            new_token
            do_check
        fi
    # Something else happened, so bail
    else
        echo "Exiting on status: $status"
        printf "%s\n" "${resp[@]}"
        exit -1
    fi
}

# Get token
get_token
# Do endpoint check
do_check $1 $2