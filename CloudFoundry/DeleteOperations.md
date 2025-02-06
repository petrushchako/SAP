# Cloud Foundry Delete Operations

This document provides a quick reference for deleting resources in Cloud Foundry (CF), including applications, services, and spaces.

## 1. Delete an Application
To delete an application from CF:
```sh
cf apps
cf delete APP_NAME -f -r
```
### Options:
- `-f` → Force deletion without confirmation.
- `-r` → Remove associated routes.
### Example:
```sh
cf delete my-app -f -r
```
### Delete all apps
```sh
cf apps | awk '{ print $1 }' | tail -n +4 | xargs -I {} cf delete {} -f -r
```

<br>

## 2. Delete a Service Instance
To delete a service instance:
```sh
cf service
cf delete-service SERVICE_INSTANCE_NAME -f
```
### Example:
```sh
cf delete-service my-database -f
```
**Note:** Ensure the service is not bound to any apps before deletion. You can unbind it first:
```sh
cf unbind-service APP_NAME SERVICE_INSTANCE_NAME
```
### Delete all services
```sh
cf services | awk '{ print $1 }' | tail -n +4 | xargs -I {} cf delete-service {} -f
```

<br>

## 3. Delete a Space
To delete a space in an org:
```sh
cf spaces
cf delete-space SPACE_NAME -f
```
### Example:
```sh
cf delete-space dev-space -f
```
**Warning:** This action is irreversible and will remove all apps, services, and configurations in the space.
