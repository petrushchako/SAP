# SSH into container running on Cloud Foundry
To SSH into a Cloud Foundry application container, you must ensure that SSH access is enabled at both the space and application levels. Follow these steps to verify access and connect.

### Step 1: Enable SSH Access
By default, SSH is disabled. You must enable it and then restart your application to apply the changes.

1. **Enable for the application:**
`cf enable-ssh <app-name>`
2. **Verify the space allows SSH:**
`cf allow-space-ssh <space-name>`
3. **Restart the app** (Required to inject the SSH keys into the container):
`cf restart <app-name>`


### Step 2: Verify SSH Availability
Check if the application is ready to accept SSH connections:
`cf ssh-enabled <app-name>`

> **Note:** If this returns `ssh is disabled`, repeat Step 1.

### Step 3: Connect to the Container
Once enabled and restarted, use the following command to open an interactive shell:

* **To connect to the default instance (Instance 0):**
`cf ssh <app-name>`
* **To connect to a specific instance (if running multiple):**
`cf ssh <app-name> -i <instance-index>`

<br><br><br>

### Useful Commands Once Inside
* **Check environment variables:** `env` or `printenv`
* **View Dynatrace logs (if applicable):** `cat /home/vcap/logs/dynatrace_agent.log`
