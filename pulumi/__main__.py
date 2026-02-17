import pulumi
import pulumi_aws as aws

key_name = "vockey"

sg = aws.ec2.SecurityGroup("vm-sg",
    description="Allow SSH, HTTP, 5000",
    ingress=[
        {"protocol": "tcp", "from_port": 22, "to_port": 22, "cidr_blocks": ["0.0.0.0/0"], "description": "SSH"},
        {"protocol": "tcp", "from_port": 80, "to_port": 80, "cidr_blocks": ["0.0.0.0/0"], "description": "HTTP"},
        {"protocol": "tcp", "from_port": 5000, "to_port": 5000, "cidr_blocks": ["0.0.0.0/0"], "description": "App port"},
    ],
    egress=[{"protocol": "-1", "from_port": 0, "to_port": 0, "cidr_blocks": ["0.0.0.0/0"]}]
)

vm = aws.ec2.Instance("devops-lab-vm",
    instance_type="t2.micro",
    vpc_security_group_ids=[sg.id],
    ami="ami-0b6c6ebed2801a5cb",
    key_name=key_name,
    tags={"Name": "pulumi-devops-vm"}
)

pulumi.export('public_ip', vm.public_ip)
pulumi.export('ssh_command', pulumi.Output.concat("ssh -i labsuser.pem ubuntu@", vm.public_ip))