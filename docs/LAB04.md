# Lab 4 — Infrastructure as Code (Terraform & Pulumi)

## Task 1 — Terraform VM Creation

### 1. Cloud Provider & Infrastructure

**Cloud Provider:** AWS

**Why AWS?**
- Offers Free Tier: 750 hours/month for `t2.micro`—perfect for labs and testing.
- Most popular and widely adopted cloud provider.
- Extensive documentation and community support.
- Free for 12 months for new accounts.

**Instance Type/Size and Why:**
- `t2.micro` (smallest free tier, sufficient for basic server/app deployment).

**Region/Zone Selected:**
- `us-east-1` (commonly chosen for AWS labs).

**Total Cost:** $0 (AWS Free Tier).

**Resources Created:**
- **VM Instance:** `t2.micro`, tagged as `devops-lab-vm`.
- **Network:** Default AWS VPC in region `us-east-1`.
- **Security Group/Firewall:**
  - SSH (22) open to all (`0.0.0.0/0`)
  - HTTP (80) open to all (`0.0.0.0/0`)
  - App port (5000) open to all (`0.0.0.0/0`)
- **Public IP:** Assigned automatically at creation. _(Note: may change on stop/start unless Elastic IP attached)_

![Instance example](/app_python/docs/screenshots/07-instanse.png)

---

### 2. Terraform Implementation

**Terraform Version:**
```bash
terraform version
Terraform v1.14.5
on windows_amd64
+ provider registry.terraform.io/hashicorp/aws v6.32.1
```

**Project Structure:**
```
terraform/
├── main.tf
├── variables.tf
├── outputs.tf
└── .gitignore

```

**Key Configuration Decisions:**
- Used variables for region, instance type, AMI, and key name.
- All essential ports opened (22, 80, 5000) for lab/demo purposes.
- Used default VPC (no explicit custom VPC for simplicity and to stay in Free Tier).
- Output public IP and ready-to-use SSH command.
- Sensitive files (`*.tfstate`, `*.pem`, `.terraform/`) included in `.gitignore`.



---

**Terminal output from key commands:**

**terraform init**

```plaintext
Initializing the backend...
Initializing provider plugins...
Terraform has been successfully initialized!
```

**terraform plan**
```plaintext
Terraform will perform the following actions:

  # aws_instance.vm will be created
  + resource "aws_instance" "vm" {
      + ami                                  = "ami-0b6c6ebed2801a5cb"
      + instance_type                        = "t2.micro"
      + key_name                             = "vockey"
      + tags                                 = {
          + "Name" = "devops-lab-vm"
        }
      ...
    }

  # aws_security_group.vm_sg will be created
  + resource "aws_security_group" "vm_sg" {
      + description = "Allow SSH, HTTP, 5000"
      + ingress     = [
          + { from_port = 22, to_port = 22, protocol = "tcp", cidr_blocks = ["0.0.0.0/0"], description = "SSH" },
          + { from_port = 80, to_port = 80, protocol = "tcp", cidr_blocks = ["0.0.0.0/0"], description = "HTTP" },
          + { from_port = 5000, to_port = 5000, protocol = "tcp", cidr_blocks = ["0.0.0.0/0"], description = "Custom App" },
        ]
      ...
    }

Plan: 2 to add, 0 to change, 0 to destroy.
```

**terraform apply**
```plaintext
...
Apply complete! Resources: 2 added, 0 changed, 0 destroyed.

Outputs:

public_ip = "34.233.135.93"
ssh_command = "ssh -i labsuser.pem ubuntu@34.233.135.93"
```

**Public IP of created VM:**
```
34.233.135.93
```
---

**SSH Connection proof:**

```plaintext
$ ssh -i labsuser.pem ubuntu@34.233.135.93
Welcome to Ubuntu 24.04.3 LTS (GNU/Linux 6.14.0-1018-aws x86_64)
...
Last login: Tue Feb 17 19:06:59 2026 from ...
ubuntu@ip-172-31-20-177:~$
```

---
## Task 2 — Pulumi VM Creation

---

### 1. Programming Language Chosen for Pulumi

I chose **Python** as the language for my Pulumi implementation because it is widely supported and allows use of rich programming constructs for infrastructure as code.

**Pulumi Version:**
```bash
pulumi version
v3.220.0
```
---


### 2. Terraform Destroy Output

```text
Changes to Outputs:
  - public_ip   = "34.233.135.93" -> null
  - ssh_command = "ssh ubuntu@34.233.135.93" -> null

Do you really want to destroy all resources?
  Terraform will destroy all your managed infrastructure, as shown above.
  There is no undo. Only 'yes' will be accepted to confirm.

  Enter a value: yes

aws_instance.vm: Destroying... [id=i-0122876d4c3947bed]
aws_instance.vm: Still destroying... [id=i-0122876d4c3947bed, 00m10s elapsed]
aws_instance.vm: Destruction complete after 1m2s
aws_security_group.vm_sg: Destroying... [id=sg-0e45f22278a7b1970]
aws_security_group.vm_sg: Destruction complete after 1s

Destroy complete! Resources: 2 destroyed.
```

---

### 3. Pulumi Preview and Up Output

#### pulumi preview:
```text
(venv) PS D:\INNOPOLIS\DEVOPS ENGINEERING\DevOps-course\pulumi> pulumi preview
Enter your passphrase to unlock config/secrets
     Type                      Name              Plan
 +   pulumi:pulumi:Stack       devops-lab04-dev  create
 +   ├─ aws:ec2:SecurityGroup  vm-sg             create
 +   └─ aws:ec2:Instance       devops-lab-vm     create
Outputs:
    public_ip  : [unknown]
    ssh_command: [unknown]

Resources:
    + 3 to create
```

#### pulumi up:
```text
(venv) PS D:\INNOPOLIS\DEVOPS ENGINEERING\DevOps-course\pulumi> pulumi up
Previewing update (dev):                                                       
     Type                 Name              Plan
     pulumi:pulumi:Stack  devops-lab04-dev
 +   └─ aws:ec2:Instance  devops-lab-vm     create
Outputs:
  + public_ip  : [unknown]
  + ssh_command: [unknown]

Resources:
    + 1 to create
    2 unchanged

Do you want to perform this update? yes
Updating (dev):
     Type                 Name              Status
     pulumi:pulumi:Stack  devops-lab04-dev
 +   └─ aws:ec2:Instance  devops-lab-vm     created (15s)
Outputs:
  + public_ip  : "52.23.239.48"
  + ssh_command: "ssh -i vockey.pem ubuntu@52.23.239.48"

Resources:
    + 1 created
    2 unchanged

Duration: 19s
```

---

### 4. Public IP of Pulumi-created VM

- **Public IP:** `52.23.239.48`

---

### 5. SSH Connection to Pulumi-created VM

```text
$ ssh -i vockey.pem ubuntu@52.23.239.48
The authenticity of host '52.23.239.48 (52.23.239.48)' can't be established.
ED25519 key fingerprint is SHA256:eaXqPPGBnIH/fpt1A415YD81rIXEp9qZzwI4mhZAX+Q.
Are you sure you want to continue connecting (yes/no/[fingerprint])? yes
Welcome to Ubuntu 24.04.3 LTS (GNU/Linux 6.14.0-1018-aws x86_64)
ubuntu@ip-172-31-20-165:~$
```

---

### 6. Code Differences (HCL vs Python)

**Terraform HCL (declarative):**
```hcl
resource "aws_instance" "vm" {
  ami                    = "ami-xxxxxx"
  instance_type          = "t2.micro"
  vpc_security_group_ids = [aws_security_group.vm_sg.id]
  key_name               = var.key_name
}
```

**Pulumi Python (imperative):**
```python
vm = aws.ec2.Instance(
    "devops-lab-vm",
    instance_type="t2.micro",
    vpc_security_group_ids=[sg.id],
    ami="ami-0b6c6ebed2801a5cb",
    key_name=key_name,
    tags={"Name": "pulumi-devops-vm"}
)
```
- Terraform uses a block structure where the “what” is described.
- Pulumi uses full Python; you can use loops, variables, functions, and conditionals.

---

### 7. Comparison: Terraform vs Pulumi Experience

**What was easier/harder than Terraform?**
- **Pulumi** was easier where custom logic or dynamic resource generation was needed, thanks to Python’s flexibility.
- **Terraform’s** declarative HCL was simpler for reading and building small or static environments.

**How does the code differ?**
- Pulumi’s Python code allowed more reuse and dynamic logic, whereas Terraform’s HCL is closer to a static config file.

**Which approach do you prefer and why?**
- For simple, repeatable cloud resources, I prefer Terraform for its simplicity.
---

### 8. Advantages of Pulumi Discovered

- **Full Programming Language:** Can use loops, conditions, functions, and abstractions
- **Better IDE Support:** Type hints, autocomplete, native debugging
- **Native Testing:** Can write unit tests for infrastructure
- **Flexible Configuration:** Dynamic resource generation based on conditions
- **Secrets Encrypted by Default:** Better security than Terraform's plain text state
- **Familiar Language:** If you know Python, less new syntax to learn


### 9. Terraform vs Pulumi Comparison

#### Ease of Learning
**Terraform** was easier to learn at first because its declarative HCL syntax is simple and focused—what you write closely maps to cloud resources with few abstractions. **Pulumi** requires understanding both the cloud provider’s constructs and general programming concepts, so there’s a steeper initial learning curve if you aren’t comfortable with Python.

#### Code Readability
For small or static infrastructures, **Terraform**’s HCL is more readable because of its concise and “configuration-file” style. For larger, more complex, or dynamic setups, **Pulumi** becomes more readable to me, since Python allows logical grouping, comments, and abstraction.

#### Debugging
**Pulumi** was somewhat easier to debug for me due to Python’s error outputs, stack traces, and the ability to use print statements or regular debugging tools. **Terraform** error messages are clear for straightforward mistakes, but harder to interpret for more complex logic or variable issues.

#### Documentation
**Terraform** has more extensive, mature documentation and a huge variety of real-world examples. **Pulumi** has good docs and is catching up, but community content, Stack Overflow answers, and blog posts are much more plentiful for Terraform at the moment.

#### Use Case
I would use **Terraform** for simple, standard infrastructure projects where configs are reused between teams and environments. **Pulumi** is best for advanced cases when I need to generate infrastructure dynamically, integrate with other Python libraries, or build highly automated/dev-programmable deployments.

---

### 10. Lab 5 Preparation & Cleanup

**VM for Lab 5:**

- **Are you keeping your VM for Lab 5?** No

  I will recreate a cloud VM using **Terraform** for Lab 5.

**Cleanup Status:**

- All Pulumi-created AWS resources have been destroyed (`pulumi destroy`).
- Terraform resources were already removed in Task 2 (`terraform destroy`).
---

#### Terminal Output — Pulumi Cleanup

```
(venv) PS D:\INNOPOLIS\DEVOPS ENGINEERING\DevOps-course\pulumi> pulumi destroy
Enter your passphrase to unlock config/secrets
    (set PULUMI_CONFIG_PASSPHRASE or PULUMI_CONFIG_PASSPHRASE_FILE to remember):
Enter your passphrase to unlock config/secrets
Previewing destroy (dev):
     Type                      Name              Plan                                                                                                                
 -   pulumi:pulumi:Stack       devops-lab04-dev  delete
 -   ├─ aws:ec2:Instance       devops-lab-vm     delete                                                                                                              
 -   └─ aws:ec2:SecurityGroup  vm-sg             delete                                                                                                              
Outputs:
  - public_ip  : "52.23.239.48"
  - ssh_command: "ssh -i labsuser.pem ubuntu@52.23.239.48"

Resources:
    - 3 to delete

Do you want to perform this destroy? yes
Destroying (dev):
     Type                      Name              Status
 -   pulumi:pulumi:Stack       devops-lab04-dev  deleted (0.06s)
 -   ├─ aws:ec2:Instance       devops-lab-vm     deleted (62s)
 -   └─ aws:ec2:SecurityGroup  vm-sg             deleted (1s)
Outputs:
  - public_ip  : "52.23.239.48"
  - ssh_command: "ssh -i labsuser.pem ubuntu@52.23.239.48"

Resources:
    - 3 deleted

Duration: 1m6s
(venv) PS D:\INNOPOLIS\DEVOPS ENGINEERING\DevOps-course\pulumi> 
```

#### Terminal Output — Terraform Cleanup

```
Changes to Outputs:
  - public_ip   = "34.233.135.93" -> null
  - ssh_command = "ssh ubuntu@34.233.135.93" -> null

Do you really want to destroy all resources?
  Terraform will destroy all your managed infrastructure, as shown above.
  There is no undo. Only 'yes' will be accepted to confirm.

  Enter a value: yes

aws_instance.vm: Destroying... [id=i-0122876d4c3947bed]
aws_instance.vm: Still destroying... [id=i-0122876d4c3947bed, 00m10s elapsed]
aws_instance.vm: Destruction complete after 1m2s
aws_security_group.vm_sg: Destroying... [id=sg-0e45f22278a7b1970]
aws_security_group.vm_sg: Destruction complete after 1s

Destroy complete! Resources: 2 destroyed.
```

---
