# Geo citizen on AWS  
![](https://a0.awsstatic.com/libra-css/images/logos/aws_smile-header-desktop-en-white_59x35.png)

**Table of Contents**  
- [Geo citizen on AWS](#geo-citizen-on-aws)
  - [AWS account registration and free tier](#aws-account-registration-and-free-tier)
  - [Manual deploying](#manual-deploying)
    - [GUI creating instances](#gui-creating-instances)
    - [Connecting to the instances](#connecting-to-the-instances)
    - [Configuring the Geo citizen project](#configuring-the-geo-citizen-project)
  - [Adding some automation](#adding-some-automation)
    - [Terraform](#terraform)
      - [Installing](#installing)
      - [Create IAM user for terraform](#create-iam-user-for-terraform)
      - [Providing terraform with AWS credentials](#providing-terraform-with-aws-credentials)
      - [Configuring remote backend](#configuring-remote-backend)
      - [Resource creation](#resource-creation)
        - [DNS config](#dns-config)
        - [Terraform files](#terraform-files)
    - [Ansible](#ansible)
      - [Installing](#installing-1)
      - [Configuring](#configuring)
      - [Testing connection](#testing-connection)
      - [Configuring project](#configuring-project)
        - [Role **geo-db**](#role-geo-db)
        - [Role **geo-web**](#role-geo-web)
        - [Create playbook](#create-playbook)
      - [Ansible galaxy roles](#ansible-galaxy-roles)

Related repos:
- [terraform](https://github.com/Vladkarok/terraform-geocit-aws.git)
- [jenkins](https://github.com/Vladkarok/jenkins.git)
- [ansible-galaxy-db](https://github.com/Vladkarok/geo_db.git)
- [ansible-galaxy-web](https://github.com/Vladkarok/geo_web.git)
- [awx](https://github.com/Vladkarok/geo-awx.git)

Related runbooks:
- [AWX](https://github.com/Vladkarok/SSU-DevOps-Academy/blob/main/Milestone_2/AWX.md)
- [Jenkins](https://github.com/Vladkarok/SSU-DevOps-Academy/blob/main/Milestone_2/Jenkins.md)


## AWS account registration and free tier

Register your account, valid payment method required.  
For the new accounts **free tier** is given. It provides [a lot](https://aws.amazon.com/free/?nc1=h_ls&all-free-tier.sort-by=item.additionalFields.SortRank&all-free-tier.sort-order=asc&awsf.Free%20Tier%20Types=*all&awsf.Free%20Tier%20Categories=*all), but for now the main thing is 750 hours a month for running **EC2** (**E**lastic **c**ompute **c**loud) instance with specific VM shapes: `t2.micro` or `t3.micro` (depends on region). 
In general, t2.**\*** instances have the following capabilities  

Instance | vCPU* | CPU Credits/hour | Mem (GiB)	| Storage | Network Performance
--- | --- | --- | --- | --- | ---
t2.nano | 1 | 3 | 0.5 | EBS-Only | Low
**t2.micro** | **1** | **6** | **1** | **EBS-Only** | **Low to Moderate**
t2.small | 1 | 12 | 2 | EBS-Only | Low to Moderate
t2.medium | 2 | 24 | 4 | EBS-Only | Low to Moderate
t2.large | 2 | 36 | 8 | EBS-Only | Low to Moderate
t2.xlarge | 4 | 54 | 16 | EBS-Only | Moderate
t2.2xlarge | 8 | 81 | 32 | EBS-Only | Moderate

and t3.**\***

Instance | vCPU* | CPU Credits/hour | Mem (GiB) | Storage | Network Performance (Gbps)***
--- | --- | --- | --- | --- | ---
t3.nano | 2 | 6 | 0.5 | EBS-Only | Up to 5
**t3.micro** | **2** | **12** | **1** | **EBS-Only** | **Up to 5**
t3.small | 2 | 24 | 2 | EBS-Only | Up to 5
t3.medium | 2 | 24 | 4 | EBS-Only | Up to 5
t3.large | 2 | 36 | 8 | EBS-Only | Up to 5
t3.xlarge | 4 | 96 | 16 | EBS-Only | Up to 5
t3.2xlarge | 8 | 192 | 32 | EBS-Only | Up to 5

\* This is the default and maximum number of vCPUs available for this instance type. You can specify a custom number of vCPUs when launching this instance type.  
\*\*\* Instances marked with "Up to" Network Bandwidth have a baseline bandwidth and can use a network I/O credit mechanism to burst beyond their baseline bandwidth on a best effort basis.  
*t2.nano, t2.micro, t2.small, t2.medium have up to 3.3 GHz Intel Scalable Processor*  
*t3.**\*** have up to 3.1 GHz Intel Xeon Platinum Processor*
> A CPU Credit provides the performance of a full CPU core for one minute. The baseline performance is equivalent to 20% of a CPU core.   

[Source](https://aws.amazon.com/ec2/instance-types/?nc1=h_ls)

In Europe the one region that doesn't have t2.micro ec2 shape is `Europe (Stockholm)` - **eu-north-1**  
So here we can use `t3-micro` in free tier.

## Manual deploying  
### GUI creating instances
1. In the search field type *ec2* and you can "star" it for future convenient use (I will additionally select **IAM, S3, DynamoDB, Route53, RDS and VPC**)

![](img/ec2_select.jpg)

2. Select *Stockholm* region  
![](img/regions.jpg)  

3. Navigate to *Network & Security/Key Pairs* and generate/import the key pair which will be used for instances connection  
![](img/navigate_key.jpg) ![](img/create_key.jpg)  
I will use **ED25519** type (the difference you can find [here](https://security.stackexchange.com/questions/5096/rsa-vs-dsa-for-ssh-authentication-keys/46781#46781) or somewhere else in the Internet :) ) and **.pem** format.
> Note! When selecting **ED25519** only available file format is **.pem** and it's chosen automatically.

4. Navigate to **Instances** and press **Launch**
![](img/first_launch.jpg)  

5. Choose AMI of Ubuntu by manual selecting from list or you can type *ubuntu* in the search field and check *Free tier only* box  
![](img/choose_ami.jpg)  

6. Choose Instance Type and click *Next:*  
![](img/choose_instance_type.jpg)  

7. You can leave default values on next pages till page *5. Add Tags*. Create tag **Name** with some value, I set it to **Ubuntu**  
![](img/set_name.jpg)  

8. On the next page configure *Security group*. Add **8080** port fot Tomcat's service. Also you can limit access for your IP address for testing and security reason  
![](img/sec_group.jpg)  

9. Click on *Review and Launch* and then *Launch*. Then this window will appear, here you need to choose previously created ssh keys.
![](img/launch.jpg)
And finally click on *Launch instances*. Your first instance will be created shortly.  

Repeat steps above from 5 to create another instance with **Amazon Linux 2** AMI, on step 7 set **Name** to **Amazon Linux 2** and on step 8 instead of port *8080* add port *5432* for PostgreSQL service
![](img/choose_ami_amazon_linux.jpg)  

### Connecting to the instances  
When the instances were created, copy the public IP address from Ubuntu and then Amazon Linux 2 instances
![](img/ubuntu_pub_ip.jpg)  

Open your ssh config file (*user_home_path*/.ssh/config) and paste following

```
Host ubuntu
         HostName 16.171.11.6
         Port 22
         Forwardx11 no
         User ubuntu
         IdentityFile ~/.ssh/ss_geocit.pem
         Protocol 2
         Compression no
         ServerAliveInterval 60
         ServerAliveCountMax 20
         LogLevel Info

Host amazon-linux2
         HostName 16.170.216.173
         Port 22
         Forwardx11 no
         User ec2-user
         IdentityFile ~/.ssh/ss_geocit.pem
         Protocol 2
         Compression no
         ServerAliveInterval 60
         ServerAliveCountMax 20
         LogLevel Info
```
> Do not forget to paste your instances ip addresses and mention that for Ubuntu the default user is *ubuntu* and for Amazon Linux 2 is *ec2-user*

Then you can connect to the instances simply by command
```
ssh ubuntu
```
or
```
ssh amazon-linux2
```

### Configuring the Geo citizen project

From now there is no differences in configuring virtual machines and the project from [my previous runbook](https://github.com/Vladkarok/SSU-DevOps-Academy/tree/main/Geocitizen#centos---postgresql) but mention public and private ip addresses  

## Adding some automation  
### Terraform  
[Terraform](https://www.terraform.io/) is a tool for such concept as *Infrastructure as a code*. You can install it from [here](https://www.terraform.io/downloads).  
There is great [documentation](https://registry.terraform.io/providers/hashicorp/aws/latest/docs) for **aws provider** that we need to use.

#### Installing
I will use Ubuntu, so the installation process is following

```bash
curl -fsSL https://apt.releases.hashicorp.com/gpg | sudo apt-key add -
sudo apt-add-repository "deb [arch=amd64] https://apt.releases.hashicorp.com $(lsb_release -cs) main"
sudo apt-get update && sudo apt-get install terraform
```

#### Create IAM user for terraform
We will create a separate group for terraform and will give access only for services we will use, then we will create user and assign it to this group.  
Navigate to *IAM/User groups* and click on *Create user group*  
Give it some name.  
Scroll to *Attach permissions policies* and search and chek next policies:
```
AmazonEC2FullAccess
AmazonS3FullAccess
AmazonDynamoDBFullAccess
AmazonRoute53FullAccess
```
![](img/user_group.jpg)  
Then navigate to *Users* and add a user for terraform. Select AWS credential type as Access key
![](img/iam_terraform1.jpg)  
Next attach user to previously created group.  
Add some tags if you want, but for testing purposes it is not necessary. Then *Review* and *Create user*
> You will be provided with **Access key ID** and **Secret access key**in the next window. Copy this information and store it in a secure place. Later you wouldn't be able to review the Secret access key.  

#### Providing terraform with AWS credentials

There are [several ways](https://registry.terraform.io/providers/hashicorp/aws/latest/docs#authentication-and-configuration) to configure credentials for interaction with AWS provider. We will use credentials in environment variables. 
```bash
export AWS_ACCESS_KEY_ID=YOUR_ACCESS_KEY
export AWS_SECRET_ACCESS_KEY=YOUR_SECRET_ACCESS_KEY
```
These variables will be accessible **within the current terminal session**.

#### Configuring remote backend
One of the core items in Terraform is *terraform.tfstate* file. It keeps all information about currently configured items via terraform. It can be stored locally, but it is not the "right way".  
We will use terraform to create S3 bucket and DynamoDB tables for tfstate file and then we will use this remote file as remote backend.  
Create the directory for terraform jobs and remote baskend 

```bash
mkdir -p ~/terraform/backend
cd ~/terraform/backend
```

Create file

```bash
vim main.tf
```

And paste following code

```hcl
terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 4.0"
    }
  }
}
provider "aws" {
  region = "eu-north-1"
}
resource "aws_s3_bucket" "terraform_state" {
  bucket        = "terraform-tfstate-file-softserve-geocit"
  force_destroy        = true
}

resource "aws_s3_bucket_versioning" "terraform_state_versioning" {
  bucket = aws_s3_bucket.terraform_state.id
  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "terraform_state" {
  bucket = aws_s3_bucket.terraform_state.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

resource "aws_dynamodb_table" "terraform_locks" {
  name         = "terraform-state-locking"
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "LockID"
  attribute {
    name = "LockID"
    type = "S"
  }
}
```

Save and close this file. Now we can initialize terraform with the following command

``` bash
terraform init
```
Output:
```

Initializing the backend...

Initializing provider plugins...
- Finding hashicorp/aws versions matching "~> 4.0"...
- Installing hashicorp/aws v4.5.0...
- Installed hashicorp/aws v4.5.0 (signed by HashiCorp)

Terraform has created a lock file .terraform.lock.hcl to record the provider
selections it made above. Include this file in your version control repository
so that Terraform can guarantee to make the same selections by default when
you run "terraform init" in the future.

Terraform has been successfully initialized!

You may now begin working with Terraform. Try running "terraform plan" to see
any changes that are required for your infrastructure. All Terraform commands
should now work.

If you ever set or change modules or backend configuration for Terraform,
rerun this command to reinitialize your working directory. If you forget, other
commands will detect it and remind you to do so if necessary.
```

We can use:
- *plan* command to see what we are going to deploy, 
- *apply* command to actually deploy (approve required, but can do automatically with *auto-approve* command),
- *destroy* command to destroy infrastructure you created previously (approve required, but can do automatically with *auto-approve* command).  

You can use `terraform -help` to see all available commands but the ones above are the most commonly used.  

So now we can execute

```bash
terraform plan
```

to watch what we are going to deploy. Output:
```

Terraform used the selected providers to generate the following execution plan. Resource actions are indicated with the following symbols:
  + create

Terraform will perform the following actions:

  # aws_dynamodb_table.terraform_locks will be created
  + resource "aws_dynamodb_table" "terraform_locks" {
      + arn              = (known after apply)
      + billing_mode     = "PAY_PER_REQUEST"
      + hash_key         = "LockID"
      + id               = (known after apply)
      + name             = "terraform-state-locking"
      + read_capacity    = (known after apply)
      + stream_arn       = (known after apply)
      + stream_label     = (known after apply)
      + stream_view_type = (known after apply)
      + tags_all         = (known after apply)
      + write_capacity   = (known after apply)

      + attribute {
          + name = "LockID"
          + type = "S"
        }

      + point_in_time_recovery {
          + enabled = (known after apply)
        }

      + server_side_encryption {
          + enabled     = (known after apply)
          + kms_key_arn = (known after apply)
        }

      + ttl {
          + attribute_name = (known after apply)
          + enabled        = (known after apply)
        }
    }

  # aws_s3_bucket.terraform_state will be created
  + resource "aws_s3_bucket" "terraform_state" {
      + acceleration_status                  = (known after apply)
      + acl                                  = (known after apply)
      + arn                                  = (known after apply)
      + bucket                               = "terraform-tfstate-file-softserve-geocit"
      + bucket_domain_name                   = (known after apply)
      + bucket_regional_domain_name          = (known after apply)
      + cors_rule                            = (known after apply)
      + force_destroy                        = true
      + grant                                = (known after apply)
      + hosted_zone_id                       = (known after apply)
      + id                                   = (known after apply)
      + lifecycle_rule                       = (known after apply)
      + logging                              = (known after apply)
      + object_lock_enabled                  = (known after apply)
      + policy                               = (known after apply)
      + region                               = (known after apply)
      + replication_configuration            = (known after apply)
      + request_payer                        = (known after apply)
      + server_side_encryption_configuration = (known after apply)
      + tags_all                             = (known after apply)
      + versioning                           = (known after apply)
      + website                              = (known after apply)
      + website_domain                       = (known after apply)
      + website_endpoint                     = (known after apply)

      + object_lock_configuration {
          + object_lock_enabled = (known after apply)
          + rule                = (known after apply)
        }
    }

  # aws_s3_bucket_server_side_encryption_configuration.terraform_state will be created
  + resource "aws_s3_bucket_server_side_encryption_configuration" "terraform_state" {
      + bucket = (known after apply)
      + id     = (known after apply)

      + rule {
          + apply_server_side_encryption_by_default {
              + sse_algorithm = "AES256"
            }
        }
    }

  # aws_s3_bucket_versioning.terraform_state_versioning will be created
  + resource "aws_s3_bucket_versioning" "terraform_state_versioning" {
      + bucket = (known after apply)
      + id     = (known after apply)

      + versioning_configuration {
          + mfa_delete = (known after apply)
          + status     = "Enabled"
        }
    }

Plan: 4 to add, 0 to change, 0 to destroy.

────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────

Note: You didn't use the -out option to save this plan, so Terraform can't guarantee to take exactly these actions if you run "terraform
apply" now.
```

So everything seems good as expected. We can deploy these resourses now:

```
terraform apply
```

Type `yes` when prompted.
> You may face the error *Error creating S3 bucket: BucketAlreadyExists: The requested bucket name is not available. The bucket namespace is shared by all users of the system. Please select a different name and try again.* Just create more complicated bucket name.

From now the remote backend ready to be used.  
Create another directory

```bask
mkdir ~/terraform/project && cd ~/terraform/project
```

And create the file `main.tf` with the following content

```hcl
terraform {
  backend "s3" {
    bucket         = "terraform-tfstate-file-softserve-geocit"
    key            = "terraform.tfstate"
    region         = "eu-north-1"
    dynamodb_table = "terraform-state-locking"
    encrypt        = true
  }

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 4.0"
    }
  }
}
provider "aws" {
  region = var.region
}
```

Save and close file. Run init command again.

```
terraform init
```

Output:

```

Initializing the backend...

Successfully configured the backend "s3"! Terraform will automatically
use this backend unless the backend configuration changes.

Initializing provider plugins...
- Finding hashicorp/aws versions matching "~> 4.0"...
- Installing hashicorp/aws v4.5.0...
- Installed hashicorp/aws v4.5.0 (signed by HashiCorp)

Terraform has created a lock file .terraform.lock.hcl to record the provider
selections it made above. Include this file in your version control repository
so that Terraform can guarantee to make the same selections by default when
you run "terraform init" in the future.

Terraform has been successfully initialized!

You may now begin working with Terraform. Try running "terraform plan" to see
any changes that are required for your infrastructure. All Terraform commands
should now work.

If you ever set or change modules or backend configuration for Terraform,
rerun this command to reinitialize your working directory. If you forget, other
commands will detect it and remind you to do so if necessary.
```

From here we have configured and ready to use s3 remote backend.  
Now we can start to create instances for Geocitizen project

#### Resource creation

> **_NOTE:_**  You can use Visual Studio Code for editing files via SSH to the remote machines as we configured ssh config file previously. Just open "Remote explorer" and you will see your configured hosts. But you can face the problem like your virtual machine stucks, monitoring will show high cpu utilization, htop will show ssm-agent high cpu usage. The problem is in Visual Studio Code. This is [known issue](https://github.com/microsoft/vscode-remote-release/issues/2692) If you face it too frequently, just don't use VS Code to remotely edit files via SSH.

##### DNS config

We will use domain names instead of IPs, I have test domain *vladkarok.ml* registered in [freenom.com](https://www.freenom.com)  
Then I created hosted zone in AWS Route53 service
![](img/create_hosted_zone.jpg)  
Type your domain name and press orange button
![](img/create_hosted_zone_2.jpg)
After zone creation navigate to it's configuration and check the **NS** record. You will see something like this
![](img/ns.jpg)

Copy these values and paste them to your domain registrator configuration. In case of *freenom* it will look like this

![](img/ns_free.jpg)

##### Terraform files

We will create VPC, Security groups, DNS records, make some outputs, and use variables. It can be stored in one file, but it will be large and inconvenient to read. Terraform allows to split code into multiple files, so let's create them

```bash
touch compute.tf dns.tf outputs.tf sec-gr.tf vars.tf vpc.tf
```

Open `vpc.tf` and paste the following

```hcl
data "aws_availability_zones" "available" {}

resource "aws_vpc" "main" {
  cidr_block           = var.vpc_cidr_block
  enable_dns_hostnames = true
  tags = {
    Name = "Geocitizen-vpc"
  }
}

resource "aws_internet_gateway" "main" {
  vpc_id = aws_vpc.main.id
  tags = {
    Name = "Geocitizen-igw"
  }
}


resource "aws_subnet" "public_subnets" {
  vpc_id                  = aws_vpc.main.id
  cidr_block              = var.public_subnet_cidr
  availability_zone       = data.aws_availability_zones.available.names[0]
  map_public_ip_on_launch = true
  tags = {
    Name = "Geocitizen public subnet"
  }
}


resource "aws_route_table" "public_subnets" {
  vpc_id = aws_vpc.main.id
  route {
    cidr_block = var.all_cidr_block
    gateway_id = aws_internet_gateway.main.id
  }
  tags = {
    Name = "Geocitizen-route-public-subnets"
  }
}

resource "aws_route_table_association" "public_routes" {
  route_table_id = aws_route_table.public_subnets.id
  subnet_id      = aws_subnet.public_subnets.id
}
```

Save and close. Then open `sec-gr.tf` and paste the following

```hcl
# Add security group web
resource "aws_security_group" "allow_web" {
  name        = "allow_web"
  description = "Allow web inbound traffic"
  vpc_id      = aws_vpc.main.id

  dynamic "ingress" {
    for_each = var.allow_ports_web
    content {
      from_port   = ingress.value
      to_port     = ingress.value
      protocol    = "tcp"
      cidr_blocks = [var.all_cidr_block]
    }
  }

  ingress {
    description = "allow icmp"
    from_port   = 3
    to_port     = 4
    protocol    = "icmp"
    cidr_blocks = [var.all_cidr_block]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = [var.all_cidr_block]
  }

  tags = {
    Name = "Allow web"
  }
}

# Add security group db
resource "aws_security_group" "allow_db" {
  name        = "allow_db"
  description = "Allow db inbound traffic"
  vpc_id      = aws_vpc.main.id

  ingress {
    description = "ssh to ec2"
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = [var.all_cidr_block]
  }
  ingress {
    description = "db to ec2"
    from_port   = 5432
    to_port     = 5432
    protocol    = "tcp"
    cidr_blocks = [var.vpc_cidr_block]
  }

  ingress {
    description = "allow icmp"
    from_port   = 3
    to_port     = 4
    protocol    = "icmp"
    cidr_blocks = [var.all_cidr_block]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = [var.all_cidr_block]
  }

  tags = {
    Name = "Allow db"
  }
}
```

Then repeat for the `compute.tf`

```hcl
#Get Ubuntu ami
data "aws_ami" "ubuntu_latest" {
  owners      = ["099720109477"]
  most_recent = true
  filter {
    name   = "name"
    values = ["ubuntu/images/hvm-ssd/ubuntu-focal-20.04-amd64-server-*"]
  }
}

#Get Amazon-Linux ami
data "aws_ami" "amazon_linux_latest" {
  owners      = ["137112412989"]
  most_recent = true
  filter {
    name   = "name"
    values = ["amzn2-ami-kernel-5.10-hvm-*-x86_64-gp2"]
  }
}

# Create server with OS Ubuntu 20.04 for WEB
resource "aws_instance" "Ubuntu_Web" {
  ami                    = data.aws_ami.ubuntu_latest.id
  instance_type          = var.instance_type
  vpc_security_group_ids = [aws_security_group.allow_web.id]
  subnet_id              = aws_subnet.public_subnets.id
  availability_zone      = data.aws_availability_zones.available.names[0]
  key_name               = var.ssh_key_name
  user_data = <<EOF
#!/bin/bash
sudo apt update
sudo apt upgrade -y
sudo reboot now
EOF

  tags   = {
    Name = "Ubuntu-Web"
  }

  lifecycle {
    create_before_destroy = true
  }
  depends_on = [
    aws_instance.Amazon_Linux_DB
  ]
}

# Create server with OS Amazon-Linux for DB (PostgreSQL)
resource "aws_instance" "Amazon_Linux_DB" {
  ami                    = data.aws_ami.amazon_linux_latest.id
  instance_type          = var.instance_type
  vpc_security_group_ids = [aws_security_group.allow_db.id]
  subnet_id              = aws_subnet.public_subnets.id
  availability_zone      = data.aws_availability_zones.available.names[0]
  key_name               = var.ssh_key_name
  user_data = <<EOF
#!/bin/bash
sudo amazon-linux-extras install epel -y
sudo yum update -y
sudo reboot now
EOF
  tags   = {
    Name = "Amazon Linux 2 - DB"
  }

  lifecycle {
    create_before_destroy = true
  }
}
```

`dns.tf`

```hcl
data "aws_route53_zone" "primary" {
  name = var.domain
}

resource "aws_route53_record" "geo" {
  zone_id = data.aws_route53_zone.primary.zone_id
  name    = var.domain_web
  type    = "A"
  ttl     = "300"
  records = [aws_instance.Ubuntu_Web.public_ip]
}

resource "aws_route53_record" "www_geo" {
  zone_id = data.aws_route53_zone.primary.zone_id
  name    = var.domain_web_www
  type    = "A"
  ttl     = "300"
  records = [aws_instance.Ubuntu_Web.public_ip]
}

resource "aws_route53_record" "db_domain" {
  zone_id = data.aws_route53_zone.primary.zone_id
  name    = var.domain_db
  type    = "A"
  ttl     = "300"
  records = [aws_instance.Amazon_Linux_DB.private_ip]
}
```

`outputs.tf`

```hcl
output "Webserver_public_IP" {
  value = aws_instance.Ubuntu_Web.public_ip
}

output "Webserver_private_IP" {
  value = aws_instance.Ubuntu_Web.private_ip
}

output "DB_public_IP" {
  value = aws_instance.Amazon_Linux_DB.public_ip
}

output "DB_private_IP" {
  value = aws_instance.Amazon_Linux_DB.private_ip
}
```

And finally `vars.tf` where you can define your specific variables if you want

```hcl
variable "region" {
  type        = string
  description = "AWS region"
  default     = "eu-north-1" # Stockholm
}

variable "vpc_cidr_block" {
  type        = string
  description = "VPC cidr block"
  default     = "10.255.0.0/16"
}

variable "public_subnet_cidr" {
  default = "10.255.1.0/24"
}

variable "allow_ports_web" {
  type        = list(any)
  description = "Ports to open for web application"
  default     = ["22", "8080"]
}

variable "all_cidr_block" {
  type        = string
  description = "Cidr block to open all word"
  default     = "0.0.0.0/0"
}

variable "instance_type" {
  type        = string
  description = "The AWS instance type"
  default     = "t3.micro"
}

variable "ssh_key_name" {
  type        = string
  description = "SSH public key name"
  default     = "ss_geocit"
}
# ___________________________________________
# You should change values starting from here
variable "domain" {
  type        = string
  description = "Hosted domain pure"
  default     = "vladkarok.ml"
}

variable "domain_web" {
  type        = string
  description = "Hosted domain web"
  default     = "geocitizen.vladkarok.ml"
}

variable "domain_web_www" {
  type        = string
  description = "Hosted domain www web"
  default     = "www.geocitizen.vladkarok.ml"
}

variable "domain_db" {
  type        = string
  description = "Hosted domain db private ip"
  default     = "dbgeo.vladkarok.ml"
}
```

> Change domains variables to yours.  

> **_NOTE!_** Hosting domain in AWS Route53 service costs additional money, 50 cents a month, if you don't want to be charged with extra payments you can comment or delete all `dns.tf` file and use external free domain service (like *cloudflare*) or deal with IP addresses

You can find terraform files in [this](https://github.com/Vladkarok/terraform-geocit-aws) repository.

Now we can execute

```
terraform apply
```

Output:

```
...

Plan: 12 to add, 0 to change, 0 to destroy.

Changes to Outputs:
  + DB_private_IP        = (known after apply)
  + DB_public_IP         = (known after apply)
  + Webserver_private_IP = (known after apply)
  + Webserver_public_IP  = (known after apply)

Do you want to perform these actions?
  Terraform will perform the actions described above.
  Only 'yes' will be accepted to approve.

  Enter a value:
```

Type `yes` and wait till terraform performs resources creation

Output:

```
...

Apply complete! Resources: 12 added, 0 changed, 0 destroyed.

Outputs:

DB_private_IP = "10.255.1.201"
DB_public_IP = "13.49.77.25"
Webserver_private_IP = "10.255.1.243"
Webserver_public_IP = "13.53.36.240"
```

Starting from here we can configure the instances, not manually but with special tool - `Ansible`

### Ansible

Ansible is an IT automation tool. It can configure systems, deploy software, and orchestrate more advanced IT tasks such as continuous deployments or zero downtime rolling updates. We will use it for configuring our project.

#### Installing

According to [this](https://docs.ansible.com/ansible/latest/installation_guide/intro_installation.html#installing-ansible-on-ubuntu) documentation, the installation process on Ubuntu is the following:

```bash
sudo apt update
sudo apt install software-properties-common
sudo add-apt-repository --yes --update ppa:ansible/ansible
sudo apt install ansible -y

```
#### Configuring

Now we need to manage ansible authentication in AWS for generating dynamic inventory. Create directory and files for this:

```bash
mkdir ~/.aws
touch ~/.aws/config ~/.aws/credentials
chmod 600 ~/.aws/*
```

We should create in AWS IAM a new user for Ansible. It can have only EC2 read-only permissions. Note `aws_access_key_id` and `aws_secret_access_key` in secure place. Change directory to `.aws` and populate the next files with the following content
```
cd ~/.aws
```
```
vim config
```
```
[ansible]
region = eu-north-1
output = json
```
save&exit
```
vim credentials
```
```
[ansible]
aws_access_key_id = YOUR_ACCESS_KEY_ID
aws_secret_access_key = YOUR_SECRET_ACCESS_KEY
```
save&exit  
Then create directory for ansible projects and navigate to it

```
mkdir ~/ansible && cd ~/ansible
```

And create new file with following content

```
vim aws_ec2.yml
```
```yml
plugin: aws_ec2
aws_profile: ansible

groups:
  web: "'Ubuntu-Web' in tags.Name"
  db: "'Amazon Linux 2 - DB' in tags.Name"

```
Now we have to install python *boto3* module. First enshure we have python installed

```
python3 --version
```
Output:
```
Python 3.8.10
```
> If python isn't present - install it with `sudo apt-get install python3 -y`

Now install `pip3` and then `boto3` module

```
sudo apt-get install python3-pip -y && sudo pip3 install boto3
```

Then open ansible configuration file and add this

```
sudo vim /etc/ansible/ansible.cfg
```

```
[defaults]
inventory = /home/ubuntu/ansible/aws_ec2.yml
interpreter_python = auto_silent
host_key_checking = False
```
> **inventory** is the path where the `aws_ec2.yml` file is located

Copy the private ssh key for ec2 instances you created previously to ~/.ssh folder and change file permissions to `400`

```bash
cp PATH_TO_SSH_PRIVATE_KEY/ss_geocitizen.pem ~/.ssh/ss_geocitizen.pem
chmod 400 ~/.ssh/ss_geocitizen.pem
```

And finally create directory for ansible group vars with following content

```bash
mkdir ~/ansible/group_vars
touch ~/ansible/group_vars/db.yml ~/ansible/group_vars/web.yml
```
```
vim ~/ansible/group_vars/db.yml
```
```yml
ansible_ssh_private_key_file: ~/.ssh/ss_geocitizen.pem
ansible_ssh_user: ec2-user
ansible_ssh_common_args: '-o StrictHostKeyChecking=no'
```
save&exit

```
vim ~/ansible/group_vars/web.yml
```
```yml
ansible_ssh_private_key_file: ~/.ssh/ss_geocitizen.pem
ansible_ssh_user: ubuntu
ansible_ssh_common_args: '-o StrictHostKeyChecking=no'
```
save&exit

#### Testing connection

Now we should be able to run the following command:
```
ansible-inventory --list
```
Output
```
...

    },
    "db": {
        "hosts": [
            "ec2-13-49-77-25.eu-north-1.compute.amazonaws.com"
        ]
    },
    "web": {
        "hosts": [
            "ec2-13-53-36-240.eu-north-1.compute.amazonaws.com"
        ]
    }
}
```
So we have groups **db** and **web** with related hostnames.  
Execute following command

```
ansible web -m ping
```
Output:
```
ec2-13-53-36-240.eu-north-1.compute.amazonaws.com | SUCCESS => {
    "ansible_facts": {
        "discovered_interpreter_python": "/usr/bin/python3"
    },
    "changed": false,
    "ping": "pong"
}
```
and 

```
ansible db -m ping
```
Output:
```
ec2-13-49-77-25.eu-north-1.compute.amazonaws.com | SUCCESS => {
    "ansible_facts": {
        "discovered_interpreter_python": "/usr/bin/python3.7"
    },
    "changed": false,
    "ping": "pong"
}
```
The connection is successfull. We can begin to configuring our instances.

#### Configuring project

##### Role **geo-db**  

Create directory for roles
```
mkdir roles && cd roles
```
Execute command
```
ansible-galaxy init geo_web
ansible-galaxy init geo_db
```
The role *geo_web* and *geo_db* succesfully created. Now the sctucture of the ansible folder should be like this

```
.
├── aws_ec2.yml
├── group_vars
│   ├── db.yml
│   └── web.yml
└── roles
    ├── geo_db
    │   ├── README.md
    │   ├── defaults
    │   │   └── main.yml
    │   ├── files
    │   ├── handlers
    │   │   └── main.yml
    │   ├── meta
    │   │   └── main.yml
    │   ├── tasks
    │   │   └── main.yml
    │   ├── templates
    │   ├── tests
    │   │   ├── inventory
    │   │   └── test.yml
    │   └── vars
    │       └── main.yml
    └── geo_web
        ├── README.md
        ├── defaults
        │   └── main.yml
        ├── files
        ├── handlers
        │   └── main.yml
        ├── meta
        │   └── main.yml
        ├── tasks
        │   ├── main.yml
        ├── templates
        ├── tests
        │   ├── inventory
        │   └── test.yml
        └── vars
            └── main.yml

20 directories, 19 files
```

Change directory to geo_db

```bash
cd geo_db
```
Open file defaults/main.yml and add data

```bash
vim defaults/main.yml
```
```yml
---
# defaults file for geo_db
postgres_version: 12
```
save&exit  
Open file handlers/main.yml and add data

```bash
vim handlers/main.yml
```
```yml
---
# handlers file for geo_db
- name: restart postgres
  service: name=postgresql-{{ postgres_version }} state=restarted
```
save&exit  
Open file tasks/main.yml and add data

```bash
vim tasks/main.yml
```
```yml
- name: "Upgrade all packages"
  yum:
    name: '*'
    state: latest
    update_cache: true

- name: Add repository pgdg
  yum_repository:
    name: pgdg12
    description: Postgresql {{ postgres_version }} repo
    baseurl: https://download.postgresql.org/pub/repos/yum/{{ postgres_version }}/redhat/rhel-7-x86_64
    gpgcheck: no
    enabled: yes

- name: "Install packages"
  yum:
    name:
      - postgresql{{ postgres_version }}
      - postgresql{{ postgres_version }}-server
      - python3
      - python-pip
      - python3-pip
    update_cache: true
    state: latest

- name: "Install Python packages"
  pip:
    name: psycopg2-binary
    state: present

#MAIN TASK
- name: "Find out if PostgreSQL is initialized"
  ansible.builtin.stat:
    path: "/var/lib/pgsql/{{ postgres_version }}/data/pg_hba.conf"
  register: postgres_data

- name: "Initialize PostgreSQL"
  shell: "postgresql-{{ postgres_version }}-setup initdb"
  when: not postgres_data.stat.exists

- name: "Start and enable services"
  service: "name={{ item }} state=started enabled=yes"
  with_items:
    - postgresql-{{ postgres_version }}

- name: Create first database
  postgresql_db:
    state: present
    name: "{{ db_name }}"
  become: true
  become_user: postgres

- name: "Create db user"
  postgresql_user:
    state: present
    name: "{{ db_user }}"
    password: "{{ db_password }}"
  become: true
  become_user: postgres
  no_log: true

- name: "Grant db user access to app db"
  postgresql_privs:
    type: database
    database: "{{ db_name }}"
    roles: "{{ db_user }}"
    grant_option: no
    privs: all
  become: true
  become_user: postgres

- name: "Allow md5 connection for the db user"
  postgresql_pg_hba:
    dest: "~/{{ postgres_version }}/data/pg_hba.conf"
    contype: host
    databases: all
    method: md5
    users: "{{ db_user }}"
    address: samenet
    create: true
  become: true
  become_user: postgres
  notify: restart postgres

- name: Set listen addresses to host address
  postgresql_set:
    name: listen_addresses
    value: "*"
  register: set
  become: true
  become_user: postgres
  notify: restart postgres
```

##### Role **geo-web** 

Change directory to `geo_web`
```bash
cd ../geo_web
```
Open file defaults/main.yml and add data

```bash
vim defaults/main.yml
```
```yml
---
# defaults file for geo_web
JAVA_HOME: /usr/lib/jvm/java-11-openjdk-amd64
tomcat_ver: 9.0.60                          # Tomcat version to install. Check the current available
web_domain_name: geocitizen.vladkarok.ml
db_domain: dbgeo.vladkarok.ml
proj_dir: ~/Geocit134
tomcat_archive_url: https://archive.apache.org/dist/tomcat/tomcat-9/v{{ tomcat_ver }}/bin/apache-tomcat-{{ tomcat_ver }}.tar.gz
tomcat_archive_dest: /tmp/apache-tomcat-{{ tomcat_ver }}.tar.gz
tomcat_home: /opt/tomcat
```

Open file handlers/main.yml and add data

```bash
vim handlers/main.yml
```
```yml
---
# handlers file for geo_web
- name: restart tomcat
  service:
    name: tomcat
    state: restarted
```

Here we will use some cheat. As *pom.xml* does not depend on any IP of instances, it can be fixed one time and will be used as is later without editing. So just copy this file from *fixed* folder and paste it to *files/* folder of this ansible role.

Open file tasks/main.yml and add data
```bash
vim tasks/main.yml
```
```yml
---
# tasks file for geo_web

- include_tasks: "tomcat-setup-Debian.yml"
- include_tasks: "app_geo.yml"
- include_tasks: "mvn_build.yml"
```
```bash
vim tasks/tomcat-setup-Debian.yml
```
```yml
- name: update apt cache
  apt:
    upgrade: safe
    update_cache: yes
    cache_valid_time: 86400

- name: Ensure the system can use the HTTPS transport for APT.
  stat:
    path: /usr/lib/apt/methods/https
  register: apt_https_transport

- name: Install APT HTTPS transport.
  apt:
    name: "apt-transport-https"
    state: present
    update_cache: yes
  when: not apt_https_transport.stat.exists

- name: Install basic packages
  package:
    name: ['aptitude', 'bash-completion', 'wget', 'curl', 'git', 'openjdk-11-jdk', 'maven']
    state: present
    update_cache: yes

- name: Add tomcat group
  group:
    name: tomcat

- name: Add "tomcat" user
  user:
    name: tomcat
    group: tomcat
    home: "{{ tomcat_home }}"
    createhome: no
    system: yes

- name: Download Tomcat
  get_url:
    url: "{{ tomcat_archive_url }}"
    dest: "{{ tomcat_archive_dest }}"

- name: Create a tomcat directory
  file:
    path: "{{ tomcat_home }}"
    state: directory
    owner: tomcat
    group: tomcat

- name: Extract tomcat archive
  unarchive:
    src: "{{ tomcat_archive_dest }}"
    dest: "{{ tomcat_home }}"
    owner: tomcat
    group: tomcat
    remote_src: yes
    extra_opts: "--strip-components=1"
    creates: "{{ tomcat_home }}/bin"

- name: Copy tomcat service file
  template:
    src: templates/tomcat.service.j2
    dest: /etc/systemd/system/tomcat.service
  when: ansible_service_mgr == "systemd"

- name: Start and enable tomcat
  service:
    daemon_reload: yes
    name: tomcat
    state: started
    enabled: yes
  when: ansible_service_mgr == "systemd"
```
```bash
vim tasks/app_geo.yml
```
```yml
- name: "Find out if Geo citizen folder and pom.xml is present"
  stat:
    path: "{{ proj_dir }}/pom.xml"
  register: repo_data

- name: "Cloning git repository"
  git:
    repo: 'https://github.com/mentorchita/Geocit134.git'
    dest: "{{ proj_dir }}"
    clone: yes
  when: not repo_data.stat.exists

- name: "Copy pom.xml"
  copy:
    src: pom.xml
    dest: "{{ proj_dir }}/pom.xml"

- name: "Fix favicon"
  replace:
    path: "{{ proj_dir }}/src/main/webapp/index.html"
    regexp: '\/src\/assets'
    replace: ./static

- name: "Fix .js files"
  replace:
    path: "{{ item }}"
    regexp: 'localhost'
    replace: "{{ web_domain_name }}"
  loop:
    - "{{ proj_dir }}/src/main/webapp/static/js/app.6313e3379203ca68a255.js"
    - "{{ proj_dir }}/src/main/webapp/static/js/app.6313e3379203ca68a255.js.map"
    - "{{ proj_dir }}/src/main/webapp/static/js/vendor.9ad8d2b4b9b02bdd427f.js"
    - "{{ proj_dir }}/src/main/webapp/static/js/vendor.9ad8d2b4b9b02bdd427f.js.map"

- name: Template application.properties
  template:
    src: application.properties.j2
    dest: "{{ proj_dir }}/src/main/resources/application.properties"
```
```bash
vim tasks/mvn_build.yml
```
```yml
- name: stop Tomcat for releasing instance resources
  service: "name={{ item }} state=stopped"
  with_items:
    - tomcat

- name: "Maven install"
  shell: mvn clean install
  args:
    chdir: "{{ proj_dir }}"

- name: restart Tomcat
  service: "name={{ item }} state=restarted"
  with_items:
    - tomcat

- name: Copy citizen.war to Tomcat's directory
  shell: cp {{ proj_dir }}/target/citizen.war {{ tomcat_home }}/webapps/
  
```
```bash
vim templates/application.properties.j2
```
```json
#front
front.url=http://{{ web_domain_name }}:8080/citizen/#
front-end.url=http://{{ web_domain_name }}:8080/citizen/
#db
db.driver=org.postgresql.Driver
db.url=jdbc:postgresql://{{ db_domain }}:5432/{{ db_name }}
db.username={{ db_user }}
db.password={{ db_password }}
#hibernate
hibernate.dialect=org.hibernate.dialect.PostgreSQL92Dialect
hibernate.show_sql=true
entity_manager.packages.to.scan=com.softserveinc.geocitizen.entity
#liquibase
driver=org.postgresql.Driver
url=jdbc:postgresql://{{ db_domain }}:5432/{{ db_name }}
username={{ db_user }}
password={{ db_password }}
changeLogFile=src/main/resources/liquibase/mainChangeLog.xml
verbose=true
dropFirst=false
outputChangeLogFile=src/main/resources/liquibase/changeLog-NEW.postgresql.sql
referenceUrl=jdbc:postgresql://{{ db_domain }}:5432/ss_demo_1_test
diffChangeLogFile=src/main/resources/liquibase/diffChangeLog.yaml
referenceUsername=${db.username}
referencePassword=${db.password}
spring.liquibase.change-log=src/main/resources/liquibase/structure.yaml
#smtp
mail.smtps.host=smtp.gmail.com
mail.smtp.socketFactory.class=SSL_FACTORY
mail.smtp.socketFactory.fallback=false
mail.smtp.port=465
mail.smtp.socketFactory.port=465
mail.smtps.auth=true
mail.smtps.quitwait=false
email.username={{ email_login }}
email.password={{ email_password }}
#google maps
map.key=AIzaSyAHfXMw7b7POrZw9tGblzHBdFvQG9AX5oE
#fb
facebook.appKey=300883283736784
facebook.appSecret=e76dd647549085c4c16587e37629f89c
#google
google.appKey=1040577896732-mhc8k28pk7ovg0m3fkqib1p8k8fk8uib.apps.googleusercontent.com
google.appSecret=DtuBukqZ6MCj_c8yylB9rlZK
```

##### Create playbook

Create main playbook in root ansible directory
```bash
cd ~/ansible && vim playbook.yml
```
```yml
---
- name: DB
  hosts: db
  become: true
  vars_files: secret_vars.yml
  roles:
    - geo_db

- name: Web
  hosts: web
  become: true
  vars_files: secret_vars.yml
  roles:
    - geo_web
```

We have some sensitive data, like database users, passwords, database name, email login and password. We will create separate secret file and use ansible-vault to protect them (also exclude this file from source control)

```
vim secret_vars.yml
```

```yml
email_login: YOUR_EMAIL@LOGIN
email_password: YOUR_EMAIL_PASSWORD
db_user: DATABASE_USERNAME
db_password: DATABASE_USER_PASSWORD
db_name: DATABASE_NAME
```

Then encrypt this file with ansible-vault. Enter some password as prompted after

```
ansible-vault encrypt secret_vars.yml
```

And now we can run our playbook with the following command

```
ansible-playbook --ask-vault-pass playbook.yml
```

Open http://geocitizen.vladkarok.ml:8080/citizen/#/ (replace domain name) and the project should display.

#### Ansible galaxy roles

We can add our roles to **Ansible galaxy** for future simple usage

First go to [galaxy.ansible.com](https://galaxy.ansible.com/) and login using GitHub account.  
Then use [this](https://docs.github.com/en/get-started/importing-your-projects-to-github/importing-source-code-to-github/adding-locally-hosted-code-to-github#adding-a-local-repository-to-github-using-git) manual to create new repository. Do the comands untill `git commit` step.  
Authenticate cli to GitHub using [this](https://docs.github.com/en/authentication/connecting-to-github-with-ssh/generating-a-new-ssh-key-and-adding-it-to-the-ssh-agent#generating-a-new-ssh-key) guide.  
[Test](https://docs.github.com/en/authentication/connecting-to-github-with-ssh/testing-your-ssh-connection) your connetction.  
Then copy your repo **ssh** link to your repo and run following command
```
git remote add origin git@github.com:YOUR_USERNAME/YOUR_REPOSITORY.git
git branch -m master main
git branch --set-upstream-to=origin/main main
git pull
git add *
git commit -m "Initial commit for adding Ansible role"
git push --set-upstream origin main
```
On **Ansible galaxy** site go to **My Content** and click on **Add content** and **Import Role from GitHub**, select your repository.  
Refresh page and the role should be imported.  
Repeat these steps to add role **geo_web**

After that you don't have to create roles manually, you can run
```
ansible-galaxy install vladkarok.geo_db
ansible-galaxy install vladkarok.geo_web
```

and then use these roles in playbook like

```yml
---
- name: DB
  hosts: db
  become: true
  vars_files: secret_vars.yml
  roles:
    - vladkarok.geo_db

- name: Web
  hosts: web
  become: true
  vars_files: secret_vars.yml
  roles:
    - vladkarok.geo_web
```

