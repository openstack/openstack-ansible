# Put your cloud account username in here
USERNAME=''
# Put your cloud account API Key in here
APIKEY=''
# Specify the string for which to match (on entity names) and remove all alarm/schecks for those enttities
STRING_MATCH='THIS WILL NEVER MATCH ONLY CHANGE THIS TO A SENSIBLE VALUE'

# NB - use with caution, will remove all alarms/checks for enttities that are matched.
ENTITIES=$(raxmon-entities-list --username $USERNAME --api-key $APIKEY | grep $STRING_MATCH | awk '{print $2}' | cut -d = -f2)

for e in $ENTITIES; do CHECKS=$(raxmon-checks-list --username $USERNAME --api-key $APIKEY --entity-id $e | grep Check | awk '{print $2}' | cut -d = -f 2); for c in $CHECKS; do raxmon-checks-delete --username $USERNAME --api-key $APIKEY --entity-id $e --id $c; done; done
