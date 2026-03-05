# Test provision with only docker
ansible-playbook playbooks/provision.yml --tags "docker"

# Skip common role
ansible-playbook playbooks/provision.yml --skip-tags "common"

# Install packages only across all roles
ansible-playbook playbooks/provision.yml --tags "packages"

# Check mode to see what would run
ansible-playbook playbooks/provision.yml --tags "docker" --check

# Run only docker installation tasks
ansible-playbook playbooks/provision.yml --tags "docker_install"
 ```
 root@eb4c97f4930a:/workspace/ansible# ansible-playbook playbooks/provision.yml --tags "docker" --ask-vault-pass
Vault password: 

PLAY [Provision web servers] ******************************************************************

TASK [Gathering Facts] ************************************************************************
[WARNING]: Host 'aws-vm' is using the discovered Python interpreter at '/usr/bin/python3.12', but future installation of another Python interpreter could cause a different interpreter to be discovered. See https://docs.ansible.com/ansible-core/2.19/reference_appendices/interpreter_discovery.html for more information.
ok: [aws-vm]

TASK [docker : Install Docker prerequisites] **************************************************
ok: [aws-vm]

TASK [docker : Add Docker GPG key] ************************************************************
ok: [aws-vm]

TASK [docker : Add Docker repository] *********************************************************
ok: [aws-vm]

TASK [docker : Install Docker packages] *******************************************************
ok: [aws-vm]

TASK [docker : Ensure Docker service is started and enabled] **********************************
ok: [aws-vm]

TASK [docker : Log Docker installation completion] ********************************************
changed: [aws-vm]

TASK [docker : Add ubuntu user to docker group] ***********************************************
ok: [aws-vm]

TASK [docker : Install python3-docker via apt] ************************************************
ok: [aws-vm]

TASK [docker : Log Docker user configuration completion] **************************************
changed: [aws-vm]

PLAY RECAP ************************************************************************************
aws-vm                     : ok=10   changed=2    unreachable=0    failed=0    skipped=0    rescued=0    ignored=0

root@eb4c97f4930a:/workspace/ansible# ansible-playbook playbooks/provision.yml --skip-tags "common" --ask-vault-pass
Vault password: 

PLAY [Provision web servers] ******************************************************************

TASK [Gathering Facts] ************************************************************************
[WARNING]: Host 'aws-vm' is using the discovered Python interpreter at '/usr/bin/python3.12', but future installation of another Python interpreter could cause a different interpreter to be discovered. See https://docs.ansible.com/ansible-core/2.19/reference_appendices/interpreter_discovery.html for more information.
ok: [aws-vm]

TASK [common : Update apt cache] **************************************************************
changed: [aws-vm]

TASK [common : Install common packages] *******************************************************
ok: [aws-vm]

TASK [common : Log package installation completion] *******************************************
changed: [aws-vm]

TASK [docker : Install Docker prerequisites] **************************************************
ok: [aws-vm]

TASK [docker : Add Docker GPG key] ************************************************************
ok: [aws-vm]

TASK [docker : Add Docker repository] *********************************************************
ok: [aws-vm]

TASK [docker : Install Docker packages] *******************************************************
ok: [aws-vm]

TASK [docker : Ensure Docker service is started and enabled] **********************************
ok: [aws-vm]

TASK [docker : Log Docker installation completion] ********************************************
changed: [aws-vm]

TASK [docker : Add ubuntu user to docker group] ***********************************************
ok: [aws-vm]

TASK [docker : Install python3-docker via apt] ************************************************
ok: [aws-vm]

TASK [docker : Log Docker user configuration completion] **************************************
changed: [aws-vm]

PLAY RECAP ************************************************************************************
aws-vm                     : ok=13   changed=4    unreachable=0    failed=0    skipped=0    rescued=0    ignored=0

root@eb4c97f4930a:/workspace/ansible# ansible-playbook playbooks/provision.yml --tags "packages" --ask-vault-pass
Vault password: 

PLAY [Provision web servers] ******************************************************************

TASK [Gathering Facts] ************************************************************************
[WARNING]: Host 'aws-vm' is using the discovered Python interpreter at '/usr/bin/python3.12', but future installation of another Python interpreter could cause a different interpreter to be discovered. See https://docs.ansible.com/ansible-core/2.19/reference_appendices/interpreter_discovery.html for more information.
ok: [aws-vm]

TASK [common : Update apt cache] **************************************************************
ok: [aws-vm]

TASK [common : Install common packages] *******************************************************
ok: [aws-vm]

TASK [common : Log package installation completion] *******************************************
changed: [aws-vm]

PLAY RECAP ************************************************************************************
aws-vm                     : ok=4    changed=1    unreachable=0    failed=0    skipped=0    rescued=0    ignored=0

root@eb4c97f4930a:/workspace/ansible# ansible-playbook playbooks/provision.yml --tags "docker_install" --ask-vault-pass
Vault password: 

PLAY [Provision web servers] ******************************************************************

TASK [Gathering Facts] ************************************************************************
[WARNING]: Host 'aws-vm' is using the discovered Python interpreter at '/usr/bin/python3.12', but future installation of another Python interpreter could cause a different interpreter to be discovered. See https://docs.ansible.com/ansible-core/2.19/reference_appendices/interpreter_discovery.html for more information.
ok: [aws-vm]

TASK [docker : Install Docker prerequisites] **************************************************
ok: [aws-vm]

TASK [docker : Add Docker GPG key] ************************************************************
ok: [aws-vm]

TASK [docker : Add Docker repository] *********************************************************
ok: [aws-vm]

TASK [docker : Install Docker packages] *******************************************************
ok: [aws-vm]

TASK [docker : Ensure Docker service is started and enabled] **********************************
ok: [aws-vm]

TASK [docker : Log Docker installation completion] ********************************************
changed: [aws-vm]

PLAY RECAP ************************************************************************************
aws-vm                     : ok=7    changed=1    unreachable=0    failed=0    skipped=0    rescued=0    ignored=0

root@eb4c97f4930a:/workspace/ansible# ansible-playbook playbooks/provision.yml --tags "docker" --check --ask-vault-pass
Vault password: 

PLAY [Provision web servers] ******************************************************************

TASK [Gathering Facts] ************************************************************************
[WARNING]: Host 'aws-vm' is using the discovered Python interpreter at '/usr/bin/python3.12', but future installation of another Python interpreter could cause a different interpreter to be discovered. See https://docs.ansible.com/ansible-core/2.19/reference_appendices/interpreter_disTASK [docker : Add Docker repository] *********************************************************
ok: [aws-vm]

TASK [docker : Install Docker packages] *******************************************************
ok: [aws-vm]

TASK [docker : Ensure Docker service is started and enabled] **********************************
ok: [aws-vm]

TASK [docker : Log Docker installation completion] ********************************************
changed: [aws-vm]

TASK [docker : Add ubuntu user to docker group] ***********************************************
ok: [aws-vm]

TASK [docker : Install python3-docker via apt] ************************************************
ok: [aws-vm]

TASK [docker : Log Docker user configuration completion] **************************************
changed: [aws-vm]

PLAY RECAP ************************************************************************************
aws-vm                     : ok=10   changed=2    unreachable=0    failed=0    skipped=0    rescued=0    ignored=0

root@eb4c97f4930a:/workspace/ansible#
```

task 2
```
root@eb4c97f4930a:/workspace/ansible# ansible-playbook playbooks/deploy.yml --ask-vault-pass
Vault password: 

PLAY [Deploy application] ******************************************************

TASK [Gathering Facts] *********************************************************
[WARNING]: Host 'aws-vm' is using the discovered Python interpreter at '/usr/bin/python3.12', but future installation of another Python interpreter could cause a different interpreter to be discovered. See https://docs.ansible.com/ansible-core/2.19/reference_appendices/interpreter_discovery.html for more information.
ok: [aws-vm]

TASK [docker : Install Docker prerequisites] ***********************************
ok: [aws-vm]

TASK [docker : Add Docker GPG key] *********************************************
ok: [aws-vm]

TASK [docker : Add Docker repository] ******************************************
ok: [aws-vm]

TASK [docker : Install Docker packages] ****************************************
ok: [aws-vm]

TASK [docker : Ensure Docker service is started and enabled] *******************
ok: [aws-vm]

TASK [docker : Log Docker installation completion] *****************************
ok: [aws-vm]

TASK [docker : Add ubuntu user to docker group] ********************************
ok: [aws-vm]

TASK [docker : Install python3-docker via apt] *********************************
ok: [aws-vm]

TASK [docker : Log Docker user configuration completion] ***********************
ok: [aws-vm]

TASK [web_app : Stop and remove old containers] ********************************
changed: [aws-vm]

TASK [web_app : Create application directory] **********************************
ok: [aws-vm]

TASK [web_app : Template docker-compose.yml] ***********************************
ok: [aws-vm]

TASK [web_app : Deploy with Docker Compose] ************************************
[WARNING]: Docker compose: unknown None: /opt/devops-app/docker-compose.yml: the attribute `version` is obsolete, it will be ignored, please remove it to avoid potential confusion
changed: [aws-vm]

TASK [web_app : Wait for application to be ready] ******************************
ok: [aws-vm]
[WARNING]: Docker compose: unknown None: /opt/devops-app/docker-compose.yml: the attribute `version` is obsolete, it will be ignored, please remove it to avoid potential confusion
changed: [aws-vm]

TASK [web_app : Wait for application to be ready] ******************************
ok: [aws-vm]

TASK [web_app : Wait for application to be ready] ******************************
ok: [aws-vm]
**********
ok: [aws-vm]
ok: [aws-vm]

TASK [web_app : Verify health endpoint] ****************************************
ok: [aws-vm]

TASK [web_app : Display health check result] ***********************************
ok: [aws-vm] => {
    "msg": "✅ Application is healthy: healthy"
}

TASK [web_app : Log deployment completion] *************************************
ok: [aws-vm]

PLAY RECAP *********************************************************************
aws-vm                     : ok=18   changed=2    unreachable=0    failed=0    skipped=0    rescued=0    ignored=0

root@eb4c97f4930a:/workspace/ansible# ansible-playbook playbooks/deploy.yml --ask-vault-pass
Vault password: 

PLAY [Deploy application] ******************************************************

TASK [Gathering Facts] *********************************************************
[WARNING]: Host 'aws-vm' is using the discovered Python interpreter at '/usr/bin/python3.12', but future installation of another Python interpreter could cause a different interpreter to be discovered. See https://docs.ansible.com/ansible-core/2.19/reference_appendices/interpreter_discovery.html for more information.
ok: [aws-vm]

TASK [docker : Install Docker prerequisites] ***********************************
ok: [aws-vm]

TASK [docker : Add Docker GPG key] *********************************************
ok: [aws-vm]

TASK [docker : Add Docker repository] ******************************************
ok: [aws-vm]

TASK [docker : Install Docker packages] ****************************************
ok: [aws-vm]

TASK [docker : Ensure Docker service is started and enabled] *******************
ok: [aws-vm]

TASK [docker : Log Docker installation completion] *****************************
ok: [aws-vm]

TASK [docker : Add ubuntu user to docker group] ********************************
ok: [aws-vm]

TASK [docker : Install python3-docker via apt] *********************************
ok: [aws-vm]

TASK [docker : Log Docker user configuration completion] ***********************
ok: [aws-vm]

TASK [web_app : Stop and remove old containers] ********************************
ok: [aws-vm]

TASK [web_app : Create application directory] **********************************
ok: [aws-vm]

TASK [web_app : Template docker-compose.yml] ***********************************
ok: [aws-vm]

TASK [web_app : Deploy with Docker Compose] ************************************
[WARNING]: Docker compose: unknown None: /opt/devops-app/docker-compose.yml: the attribute `version` is obsolete, it will be ignored, please remove it to avoid potential confusion
ok: [aws-vm]

TASK [web_app : Wait for application to be ready] ******************************
ok: [aws-vm]

TASK [web_app : Verify health endpoint] ****************************************
ok: [aws-vm]

TASK [web_app : Display health check result] ***********************************
ok: [aws-vm] => {
    "msg": "✅ Application is healthy: healthy"
}

TASK [web_app : Log deployment completion] *************************************
ok: [aws-vm]

PLAY RECAP *********************************************************************
aws-vm                     : ok=18   changed=0    unreachable=0    failed=0    skipped=0    rescued=0    ignored=0

root@eb4c97f4930a:/workspace/ansible#
```



```
ubuntu@ip-172-31-28-215:~$ ls -la /opt/devops-app/
total 12
drwxr-xr-x 2 root root 4096 Mar  5 10:13 .
drwxr-xr-x 4 root root 4096 Mar  5 10:12 ..
-rw-r--r-- 1 root root  396 Mar  5 10:12 docker-compose.yml
ubuntu@ip-172-31-28-215:~$ cat /opt/devops-app/docker-compose.yml
version: '3.8'

services:
  devops-app:
    image: sunflye/devops-info-service:latest
    container_name: devops-app
    ports:
      - "5000:5000"
    environment:
      PORT: "5000"
      HOST: "0.0.0.0"
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:5000/health"]     
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 10subuntu@ip-172-31-28-215:~$ docker ps
CONTAINER ID   IMAGE                                COMMAND           
CREATED         STATUS                     PORTS                      
                   NAMES
87f530789cca   sunflye/devops-info-service:latest   "python app.py"   6 minutes ago   Up 6 minutes (unhealthy)   0.0.0.0:5000->5000/tcp, [::]:5000->5000/tcp   devops-app
ubuntu@ip-172-31-28-215:~$ curl http://localhost:5000
{"endpoints":[{"description":"Service information","method":"GET","path":"/"},{"description":"Health check","method":"GET","path":"/health"}],"request":{"client_ip":"172.18.0.1","method":"GET","path":"/","user_agent":"curl/8.5.0"},"runtime":{"current_time":"2026-03-05T10:49:14.169009Z","timezone":"UTC","uptime_human":"0 hour, 7 minutes","uptime_seconds":450},"service":{"description":"DevOps course info service","framework":"Flask","name":"devops-info-service","version":"1.0.0"},"system":{"architecture":"x86_64","cpu_count":1,"hostname":"87f530789cca","platform":"Linux","platform_version":"Linux-6.14.0-1018-aws-x86_64-with-glibc2.41","python_version":"3.13.12"}}
ubuntu@ip-172-31-28-215:~$ curl http://localhost:5000/health
{"status":"healthy","timestamp":"2026-03-05T10:49:25.240764Z","uptime_seconds":461}
ubuntu@ip-172-31-28-215:~$
```

scenario 1
```
root@eb4c97f4930a:/workspace/ansible# ansible-playbook playbooks/deploy.yml --ask-vault-pass
Vault password: 

PLAY [Deploy application] ******************************************************

TASK [Gathering Facts] *********************************************************
[WARNING]: Host 'aws-vm' is using the discovered Python interpreter at '/usr/bin/python3.12', but future installation of another Python interpreter could cause a different interpreter to be discovered. See https://docs.ansible.com/ansible-core/2.19/reference_appendices/interpreter_discovery.html for more information.
ok: [aws-vm]

TASK [docker : Install Docker prerequisites] ***********************************
ok: [aws-vm]

TASK [docker : Add Docker GPG key] *********************************************
ok: [aws-vm]

TASK [docker : Add Docker repository] ******************************************
ok: [aws-vm]

TASK [docker : Install Docker packages] ****************************************
ok: [aws-vm]

TASK [docker : Ensure Docker service is started and enabled] *******************
ok: [aws-vm]

TASK [docker : Log Docker installation completion] *****************************
ok: [aws-vm]

TASK [docker : Add ubuntu user to docker group] ********************************
ok: [aws-vm]

TASK [docker : Install python3-docker via apt] *********************************
ok: [aws-vm]

TASK [docker : Log Docker user configuration completion] ***********************
ok: [aws-vm]

TASK [web_app : Include wipe tasks] ********************************************
included: /workspace/ansible/roles/web_app/tasks/wipe.yml for aws-vm

TASK [web_app : Stop and remove containers with Docker Compose] ****************
skipping: [aws-vm]

TASK [web_app : Remove docker-compose.yml file] ********************************
skipping: [aws-vm]

TASK [web_app : Remove application directory] **********************************
skipping: [aws-vm]

TASK [web_app : Log wipe completion] *******************************************
skipping: [aws-vm]

TASK [web_app : Remove old container (idempotent)] *****************************
changed: [aws-vm]

TASK [web_app : Create application directory] **********************************
ok: [aws-vm]

TASK [web_app : Template docker-compose.yml] ***********************************
ok: [aws-vm]

TASK [web_app : Deploy with Docker Compose] ************************************
[WARNING]: Docker compose: unknown None: /opt/devops-app/docker-compose.yml: the attribute `version` is obsolete, it will be ignored, please remove it to avoid potential confusion
changed: [aws-vm]

TASK [web_app : Wait for application to be ready] ******************************
ok: [aws-vm]

TASK [web_app : Verify health endpoint] ****************************************
ok: [aws-vm]

TASK [web_app : Display health check result] ***********************************
ok: [aws-vm] => {
    "msg": "✅ Application is healthy: healthy"
}

TASK [web_app : Log deployment completion] *************************************
ok: [aws-vm]

PLAY RECAP *********************************************************************
aws-vm                     : ok=19   changed=2    unreachable=0    failed=0    skipped=4    rescued=0    ignored=0

root@eb4c97f4930a:/workspace/ansible# 
```
2 сценарий
```
root@eb4c97f4930a:/workspace/ansible# ansible-playbook playbooks/deploy.yml -e "web_app_wipe=true" --tags web_app_wipe --ask-vault-pass     
Vault password: 

PLAY [Deploy application] ******************************************************

TASK [Gathering Facts] *********************************************************
[WARNING]: Host 'aws-vm' is using the discovered Python interpreter at '/usr/bin/python3.12', but future installation of another Python interpreter could cause a different interpreter to be discovered. See https://docs.ansible.com/ansible-core/2.19/reference_appendices/interpreter_discovery.html for more information.
ok: [aws-vm]

TASK [web_app : Include wipe tasks] ********************************************
included: /workspace/ansible/roles/web_app/tasks/wipe.yml for aws-vm

TASK [web_app : Stop and remove containers with Docker Compose] ****************
[WARNING]: Docker compose: unknown None: /opt/devops-app/docker-compose.yml: the attribute `version` is obsolete, it will be ignored, please remove it to avoid potential confusion
changed: [aws-vm]

TASK [web_app : Remove docker-compose.yml file] ********************************
changed: [aws-vm]

TASK [web_app : Remove application directory] **********************************
changed: [aws-vm]

TASK [web_app : Log wipe completion] *******************************************
ok: [aws-vm] => {
    "msg": "✅ Application devops-app wiped successfully"
}

PLAY RECAP *********************************************************************
aws-vm                     : ok=6    changed=3    unreachable=0    failed=0    skipped=0    rescued=0    ignored=0

root@eb4c97f4930a:/workspace/ansible# 

ubuntu@ip-172-31-28-215:~$ docker ps
CONTAINER ID   IMAGE     COMMAND   CREATED   STATUS    PORTS     NAMES
ubuntu@ip-172-31-28-215:~$ ls /opt
containerd
ubuntu@ip-172-31-28-215:~$
```

3 сценарий
```
root@eb4c97f4930a:/workspace/ansible# ansible-playbook playbooks/deploy.yml -e "web_app_wipe=true" --ask-vault-pass
Vault password: 

PLAY [Deploy application] ******************************************************

TASK [Gathering Facts] *********************************************************
[WARNING]: Host 'aws-vm' is using the discovered Python interpreter at '/usr/bin/python3.12', but future installation of another Python interpreter could cause a different interpreter to be discovered. See https://docs.ansible.com/ansible-core/2.19/reference_appendices/interpreter_discovery.html for more information.
ok: [aws-vm]

TASK [docker : Install Docker prerequisites] ***********************************
ok: [aws-vm]

TASK [docker : Add Docker GPG key] *********************************************
ok: [aws-vm]

TASK [docker : Add Docker repository] ******************************************
ok: [aws-vm]

TASK [docker : Install Docker packages] ****************************************
ok: [aws-vm]

TASK [docker : Ensure Docker service is started and enabled] *******************
ok: [aws-vm]

TASK [docker : Log Docker installation completion] *****************************
ok: [aws-vm]

TASK [docker : Add ubuntu user to docker group] ********************************
ok: [aws-vm]

TASK [docker : Install python3-docker via apt] *********************************
ok: [aws-vm]

TASK [docker : Log Docker user configuration completion] ***********************
ok: [aws-vm]

TASK [web_app : Include wipe tasks] ********************************************
included: /workspace/ansible/roles/web_app/tasks/wipe.yml for aws-vm

TASK [web_app : Stop and remove containers with Docker Compose] ****************
[ERROR]: Task failed: Module failed: "/opt/devops-app" is not a directory
Origin: /workspace/ansible/roles/web_app/tasks/wipe.yml:4:7

2 - name: Wipe web application
3   block:
4     - name: Stop and remove containers with Docker Compose
        ^ column 7

fatal: [aws-vm]: FAILED! => {"changed": false, "msg": "\"/opt/devops-app\" is not a directory"}
...ignoring

TASK [web_app : Remove docker-compose.yml file] ********************************
ok: [aws-vm]

TASK [web_app : Remove application directory] **********************************
ok: [aws-vm]

TASK [web_app : Log wipe completion] *******************************************
ok: [aws-vm] => {
    "msg": "✅ Application devops-app wiped successfully"
}

TASK [web_app : Remove old container (idempotent)] *****************************
ok: [aws-vm]

TASK [web_app : Create application directory] **********************************
changed: [aws-vm]

TASK [web_app : Template docker-compose.yml] ***********************************
changed: [aws-vm]

TASK [web_app : Deploy with Docker Compose] ************************************
[WARNING]: Docker compose: unknown None: /opt/devops-app/docker-compose.yml: the attribute `version` is obsolete, it will be ignored, please remove it to avoid potential confusion
changed: [aws-vm]

TASK [web_app : Wait for application to be ready] ******************************
ok: [aws-vm]

TASK [web_app : Verify health endpoint] ****************************************
ok: [aws-vm]

TASK [web_app : Display health check result] ***********************************
ok: [aws-vm] => {
    "msg": "✅ Application is healthy: healthy"
}

TASK [web_app : Log deployment completion] *************************************
ok: [aws-vm]

PLAY RECAP *********************************************************************
aws-vm                     : ok=23   changed=3    unreachable=0    failed=0    skipped=0    rescued=0    ignored=1   

root@eb4c97f4930a:/workspace/ansible# 


ubuntu@ip-172-31-28-215:~$ docker ps
CONTAINER ID   IMAGE                                COMMAND           
CREATED          STATUS                             PORTS             
                            NAMES
913fcc423fb1   sunflye/devops-info-service:latest   "python app.py"   54 seconds ago   Up 54 seconds (health: starting)   0.0.0.0:5000->5000/tcp, [::]:5000->5000/tcp   devops-app
```
4 сценарий
```
root@eb4c97f4930a:/workspace/ansible# ansible-playbook playbooks/deploy.yml --tags web_app_wipe --ask-vault-pass
Vault password: 

PLAY [Deploy application] ******************************************************

TASK [Gathering Facts] *********************************************************
[WARNING]: Host 'aws-vm' is using the discovered Python interpreter at '/usr/bin/python3.12', but future installation of another Python interpreter could cause a different interpreter to be discovered. See https://docs.ansible.com/ansible-core/2.19/reference_appendices/interpreter_discovery.html for more information.
ok: [aws-vm]

TASK [web_app : Include wipe tasks] ********************************************
included: /workspace/ansible/roles/web_app/tasks/wipe.yml for aws-vm

TASK [web_app : Stop and remove containers with Docker Compose] ****************
skipping: [aws-vm]

TASK [web_app : Remove docker-compose.yml file] ********************************
skipping: [aws-vm]

TASK [web_app : Remove application directory] **********************************
skipping: [aws-vm]

TASK [web_app : Log wipe completion] *******************************************
skipping: [aws-vm]

PLAY RECAP *********************************************************************
aws-vm                     : ok=2    changed=0    unreachable=0    failed=0    skipped=4    rescued=0    ignored=0

root@eb4c97f4930a:/workspace/ansible# 
```
![task3](/ansible/docs/screenshots/task3_lab6.png)
