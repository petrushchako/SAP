# Cloud Foundry User Management

This document provides a guide on managing users in Cloud Foundry (CF), including adding and removing users, as well as assigning roles at the organization and space levels.

## 1. Adding a User
To add a user to Cloud Foundry:
```sh
cf create-user USERNAME PASSWORD
```
Example:
```sh
cf create-user john.doe@example.com MySecurePass123
```

<br>

## 2. Assigning Roles
### Assign an Organization Role
```sh
cf set-org-role USERNAME ORG_NAME ROLE
```
Roles:
- `OrgManager` - Manages users, billing, and quotas.
- `BillingManager` - Views billing details.
- `OrgAuditor` - Views org-level information but cannot modify it.

Example:
```sh
cf set-org-role john.doe@example.com my-org OrgManager
```

### Assign a Space Role
```sh
cf set-space-role USERNAME ORG_NAME SPACE_NAME ROLE
```
Roles:
- `SpaceManager` - Manages space users.
- `SpaceDeveloper` - Deploys and manages apps.
- `SpaceAuditor` - Views space information.

Example:
```sh
cf set-space-role john.doe@example.com my-org dev-space SpaceDeveloper
```

<br>

## 3. Removing Roles
### Remove an Organization Role
```sh
cf unset-org-role USERNAME ORG_NAME ROLE
```
Example:
```sh
cf unset-org-role john.doe@example.com my-org OrgManager
```

### Remove a Space Role
```sh
cf unset-space-role USERNAME ORG_NAME SPACE_NAME ROLE
```
Example:
```sh
cf unset-space-role john.doe@example.com my-org dev-space SpaceDeveloper
```

<br>

## 4. Removing a User
To remove a user from Cloud Foundry:
```sh
cf delete-user USERNAME -f
```
Example:
```sh
cf delete-user john.doe@example.com -f
```

<br>

## 5. Listing Users and Roles
### List Users in an Organization
```sh
cf org-users ORG_NAME
```
Example:
```sh
cf org-users my-org
```

### List Users in a Space
```sh
cf space-users ORG_NAME SPACE_NAME
```
Example:
```sh
cf space-users my-org dev-space
```

<br>

## 6. Additional Commands
- View logged-in user:
  ```sh
  cf whoami
  ```
- View available organizations:
  ```sh
  cf orgs
  ```
- View available spaces in an org:
  ```sh
  cf spaces
  ```

For more details, refer to the official [Cloud Foundry CLI documentation](https://cli.cloudfoundry.org).

