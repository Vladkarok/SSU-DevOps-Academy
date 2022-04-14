# Terragrunt to GCP

**Table of contents**
- [Terragrunt to GCP](#terragrunt-to-gcp)
  - [Preparing the terraform configuration](#preparing-the-terraform-configuration)
    - [Configuring the Terraform backend on GCS](#configuring-the-terraform-backend-on-gcs)
    - [Authenticating with Google Cloud Platform](#authenticating-with-google-cloud-platform)
    - [Network](#network)
    - [Images](#images)
    - [Template files for instance startup_scripts](#template-files-for-instance-startup_scripts)
    - [Firewall](#firewall)
    - [Instances](#instances)
    - [DNS records](#dns-records)
    - [Variables](#variables)
    - [Outputs](#outputs)
  - [Terragrunt](#terragrunt)
  - [Launching](#launching)


## Preparing the terraform configuration 

[Getting started with Terraform for GCP](https://learn.hashicorp.com/tutorials/terraform/infrastructure-as-code?in=terraform/gcp-get-started)

### Configuring the Terraform backend on GCS

[Documentation](https://www.terraform.io/language/settings/backends/gcs)

My config:

```hcl
terraform {
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 4.0"
    }
  }
  backend "gcs" {
    bucket = "tf-state-ssita"
    prefix = "terraform/state"
  }
}
```
> **Note:** The bucket name must be unique for each project.
> And according to the documentation, the bucket must be already present.

For my case, I'm using DNS configuration from AWS Route53, so in order to populate DNS records there I'v added AWS provider too, so finished the configuration looks like this:

```hcl
terraform {
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 4.0"
    }
    aws = {
      source  = "hashicorp/aws"
      version = "~> 4.0"
    }
  }
  backend "gcs" {
    bucket = "tf-state-ssita"
    prefix = "terraform/state"
  }
}
```

And providers configuration:

```hcl
provider "google" {
  project = var.gcp_project
  region  = var.gcp_region
  zone    = var.gcp_zone
}

provider "aws" {
  region = var.aws_region
}
```
> **Note:** All the config above will be generated via Terragrunt in further steps, so here it is given only for reference, you shouldn't include it in your Terraform configuration.

### Authenticating with Google Cloud Platform

[Documentation](https://registry.terraform.io/providers/hashicorp/google/latest/docs/guides/provider_reference#authentication)

For my case I'm using the GCP service account role for my VM with terraform, so in case of creating infrastructure within same project I don't need additional configuration in code.  
For authentication with AWS, I've used environment variables.

### Network

I'm using default network, but in order to define for outputs **external ip addresses** I've used attached addresses.

```hcl
resource "google_compute_address" "static_web" {
  name = "ipv4-address-web"
}
resource "google_compute_address" "static_db" {
  name = "ipv4-address-db"
}
```

### Images

I'm using Ubuntu and Centos images:

```hcl
data "google_compute_image" "ubuntu_image" {
  family  = "ubuntu-2004-lts"
  project = "ubuntu-os-cloud"
}
data "google_compute_image" "centos_image" {
  family  = "centos-7"
  project = "centos-cloud"
}
```

### Template files for instance startup_scripts

```hcl
data "template_file" "template_web" {
  template = file("./init-web.tftpl")
  vars = {
    docker_username = "${var.nexus_docker_username}"
    docker_password = "${var.nexus_docker_password}"
  }
}
data "template_file" "template_db" {
  template = file("./init-db.tftpl")
  vars = {
    docker_username = "${var.nexus_docker_username}"
    docker_password = "${var.nexus_docker_password}"
  }
}
```
init-web.tftpl:
```bash
#!/bin/bash
set -ex
## Update the system
sudo apt-get update

## Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -a -G docker ubuntu

## Install docker-compose
sudo curl -L "https://github.com/docker/compose/releases/download/1.29.2/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

## Create docker-compose.yml
sudo sh -c 'cat > docker-compose.yml' << SOF
version: "3.9"
services:
  geocit_web:
    image: nexus.vladkarok.ml:5000/geocit8080:latest
    restart: always
    ports:
      - "8080:8080"
SOF
## Create password file for docker login
sh -c 'cat > password.txt' << SOF
${docker_password}
SOF

## Perform docker login
cat password.txt |sudo docker login --username ${docker_username} --password-stdin nexus.vladkarok.ml:5000

## Build and run image using docker-compose

sleep 90


sudo /usr/local/bin/docker-compose up -d

rm password.txt
```
init-db.tftpl:
```bash
#!/bin/bash
set -ex
## Update the system
sudo yum --disableplugin=fastestmirror update -y
sudo yum -y install deltarpm
sudo yum update -y
sudo yum -y install htop
## Install Docker

sudo yum install -y yum-utils
sudo yum-config-manager -y \
    --add-repo \
    https://download.docker.com/linux/centos/docker-ce.repo
sudo yum -y install docker-ce docker-ce-cli containerd.io
sudo systemctl start docker
sudo usermod -a -G docker vladkarok

## Install docker-compose
sudo curl -L "https://github.com/docker/compose/releases/download/1.29.2/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

## Create docker-compose.yml
sudo sh -c 'cat > docker-compose.yml' << SOF
version: "3.9"
services:
  geocit_db:
    image: nexus.vladkarok.ml:5000/ss_postgres:latest
    restart: always
    ports:
      - "5432:5432"
    volumes:
      - ./pg_data:/var/lib/postgresql/data
SOF
## Create password file for docker login
sh -c 'cat > password.txt' << SOF
${docker_password}
SOF

## Perform docker login
cat password.txt |sudo docker login --username ${docker_username} --password-stdin nexus.vladkarok.ml:5000

## Build and run image using docker-compose

sudo /usr/local/bin/docker-compose up -d
## Remove password file for docker login
rm password.txt
```

### Firewall

For Web server:

```hcl
resource "google_compute_firewall" "allow_web" {
  name          = "allow-web"
  description   = "Allow Web access"
  network       = "default"
  source_ranges = ["0.0.0.0/0"]
  target_tags   = ["web"]
  allow {
    protocol = "icmp"
  }
  allow {
    protocol = "tcp"
    ports    = var.web_ports
  }
}

For DB server:

```hcl
resource "google_compute_firewall" "allow_db_psql" {
  name        = "allow-db-psql"
  description = "Allow DB access for psql"
  network     = "default"
  source_tags = ["web"]
  target_tags = ["db"]
  allow {
    protocol = "icmp"
  }
  allow {
    protocol = "tcp"
    ports    = ["5432"]
  }
}
resource "google_compute_firewall" "allow_db_ssh" {
  name          = "allow-db-ssh"
  description   = "Allow DB access for ssh"
  network       = "default"
  source_ranges = ["${var.source_ranges}"]
  target_tags   = ["db"]
  allow {
    protocol = "icmp"
  }
  allow {
    protocol = "tcp"
    ports    = ["22"]
  }
}
```

### Instances

Web server:

```hcl
resource "google_compute_instance" "geo_db" {
  name         = "terraform-instance-db"
  machine_type = var.gcp_machine_type
  tags         = ["db", var.tag]
  boot_disk {
    initialize_params {
      image = data.google_compute_image.centos_image.self_link
    }
  }
  network_interface {
    network = "default"
    access_config {
      nat_ip = google_compute_address.static_db.address
    }
  }
  metadata_startup_script = data.template_file.template_db.rendered
}
```

DB server:

```hcl
resource "google_compute_instance" "geo_db" {
  name         = "terraform-instance-db"
  machine_type = var.gcp_machine_type
  tags         = ["db", var.tag]
  boot_disk {
    initialize_params {
      image = data.google_compute_image.centos_image.self_link
    }
  }
  network_interface {
    network = "default"
    access_config {
      nat_ip = google_compute_address.static_db.address
    }
  }
  metadata_startup_script = data.template_file.template_db.rendered
}
```
### DNS records

```hcl
data "aws_route53_zone" "primary" {
  name = var.domain
}

resource "aws_route53_record" "geo" {
  zone_id = data.aws_route53_zone.primary.zone_id
  name    = var.domain_web
  type    = "A"
  ttl     = "300"
  records = [google_compute_instance.geo_web.network_interface.0.access_config.0.nat_ip]
}

resource "aws_route53_record" "db_domain" {
  zone_id = data.aws_route53_zone.primary.zone_id
  name    = var.domain_db
  type    = "A"
  ttl     = "300"
  records = [google_compute_instance.geo_db.network_interface.0.network_ip]
}
```

### Variables

```hcl
variable "gcp_machine_type" {}
variable "tag" {}
variable "web_ports" {
  type = list(string)
}
variable "source_ranges" {}

variable "domain" {
  type        = string
  description = "Domain name"
  default     = "vladkarok.ml"
}

variable "domain_web" {
  type        = string
  description = "Hosted domain web"
  default     = "geocitizen.vladkarok.ml"
}

variable "domain_db" {
  type        = string
  description = "Hosted domain db private ip"
  default     = "dbgeo.vladkarok.ml"
}

variable "nexus_docker_username" {
  type      = string
  sensitive = true
}

variable "nexus_docker_password" {
  type      = string
  sensitive = true
}
```

### Outputs

```hcl
output "private_ip_db" {
  value = google_compute_instance.geo_db.network_interface.0.network_ip
}

output "public_ip_web" {
  value = google_compute_instance.geo_web.network_interface.0.access_config.0.nat_ip
}
```

## Terragrunt

Install [Terragrunt](https://terragrunt.gruntwork.io/docs/getting-started/quick-start/).  
[Documentation](https://terragrunt.gruntwork.io/docs/).  
[Helpful video](https://www.youtube.com/watch?v=SBXaENHfW70)

For Terragrunt impementation I'll be using next folder structure:

```
.
├── dev
│   ├── common.tfvars
│   └── terragrunt.hcl
├── modules
│   └── gcp_docker
│       ├── dns.tf
│       ├── init-db.tftpl
│       ├── init-web.tftpl
│       ├── main.tf
│       ├── outputs.tf
│       └── variables.tf
├── prod
│   ├── common.tfvars
│   └── terragrunt.hcl
└── terragrunt.hcl
```

I've placed terraform files in `modules/gcp_docker` folder.

Let's see root `terragrunt.hcl` file:

```hcl
remote_state {
  backend = "gcs"
  generate = {
    path      = "_backend.tf"
    if_exists = "overwrite"
  }
  config = {
    bucket   = "terr-tf-state-ssita"
    prefix   = "${path_relative_to_include()}/terragrunt_terraform.tfstate"
    project  = "elaborate-art-343920"
    location = "us-west1"
  }
}

generate "terraform_providers" {
  path      = "_providers.tf"
  if_exists = "overwrite"
  contents  = <<EOF
provider "google" {
  project = var.gcp_project
  region  = var.gcp_region
  zone    = var.gcp_zone
}
provider "aws" {
  region = var.aws_region
}
variable "gcp_project" {}
variable "gcp_region" {}
variable "gcp_zone" {}
variable "aws_region" {}
  EOF
}

# Load Variables
terraform {
  extra_arguments "common_vars" {
    commands = get_terraform_commands_that_need_vars()

    required_var_files = [
      "${get_terragrunt_dir()}/common.tfvars",
    ]
  }
}
```

There we configuring to generate new backend files and where to store them.
Then the providers itself. And finally we tell where to search variables.

Next, inspect `dev/` folder. 

common.tvars file:

```hcl
gcp_project = "elaborate-art-343920"
gcp_region = "us-west1"
gcp_zone = "us-west1-b"
aws_region = "eu-north-1"
```

terragrunt.hcl file:

```hcl
include "root" {
  path = find_in_parent_folders()
}

terraform {
  source = "..//modules/gcp_docker"
}

inputs = {
  gcp_machine_type = "f1-micro"
  tag              = "dev"
  web_ports        = ["22", "8080"]
  source_ranges    = "0.0.0.0/0"
}
```

`prod/` folder

common.tvars file:

```hcl
gcp_project = "elaborate-art-343920"
gcp_region = "us-west1"
gcp_zone = "us-west1-b"
aws_region = "eu-north-1"
```

terragrunt.hcl file:

```hcl
include "root" {
  path = find_in_parent_folders()
}

terraform {
  source = "..//modules/gcp_docker"
}

inputs = {
  gcp_machine_type = "e2-standard-4"
  tag              = "prod"
  web_ports        = ["8080"]
  source_ranges    = "127.0.0.1/32"
}
```
> **Note:** In this configuration, the nexus username and passwords still needs to specify somehow, or via environment variables of passwing in command line or defining in configuration files.

## Launching

From now you can navigate for example to `dev/` folder and perform
```
terragrunt plan
```
Terragrunt will automatically create cache folder with generated files, terraform module and download all required providers.
You can perform this command in `prod/` folder as well. To apply all configurations you can perform `terragrunt run-all plan` or `apply` command. Note that success of `run-all` command is depending on how your module is written, so if there any changes that may conflicting with each other, you should rewrite your module to avoid this, or use already written module from community.  
For all available commands you can run `terragrunt help` command.