#!/bin/bash

SONAR_URL="https://sonarqube.com"
SONAR_TOKEN="squ_<token>"

USERS=("user-id-1" "user-id-2")
PROJECTS=("project-key-1" project-key-2)
PERMISSIONS=("user" "codeviewer" "issueadmin" "securityhotspotadmin" "admin" "scan")


echo "Starting batch permission update..."

for project in "${PROJECTS[@]}"; do
    echo "----------------------------------------------------"
    echo "Project: $project"
    
    for user in "${USERS[@]}"; do
        echo "  Processing User: $user"
        
        for perm in "${PERMISSIONS[@]}"; do
            # The API Call
            response=$(curl -s -u "$SONAR_TOKEN:" -X POST "$SONAR_URL/api/permissions/add_user?login=$user&permission=$perm&projectKey=$project")
            
            # Error Handling
            if [[ $response == *"errors"* ]]; then
                echo "    [ERROR] Failed to grant '$perm' to $user: $response"
            else
                echo "    [SUCCESS] Granted '$perm' to $user"
            fi
        done
    done
done

echo "----------------------------------------------------"
echo "Batch Update Complete!"
