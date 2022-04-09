# Dockerization

**Table of Contents**
- [Dockerization](#dockerization)
  - [Add repo to Nexus](#add-repo-to-nexus)
  - [Install docker to your machine (on Jenkins agent preferred)](#install-docker-to-your-machine-on-jenkins-agent-preferred)
  - [Login to repo](#login-to-repo)
  - [Build docker image for Geocitizen frontend](#build-docker-image-for-geocitizen-frontend)
  - [Build and deliver this image to Nexus via Jenkins](#build-and-deliver-this-image-to-nexus-via-jenkins)
  - [Pull docker image](#pull-docker-image)
  - [Pull docker images and run containers on your machines](#pull-docker-images-and-run-containers-on-your-machines)

## Add repo to Nexus

[Add](https://www.coachdevops.com/2020/08/how-to-configure-nexus-3-as-docker.html).  
You may want to [add listen port](https://www.baeldung.com/linux/assign-port-docker-container) to nexus docker container. *(If you used [this](https://github.com/Vladkarok/nexus-nginx-letsencrypt-docker) tutorial - additional ports are already added)*

## Install docker to your machine (on Jenkins agent preferred)

Install [docker](https://docs.docker.com/engine/install/ubuntu/) + [Post-installation steps in Linux](https://docs.docker.com/engine/install/linux-postinstall/)  
Install [docker-compose](https://docs.docker.com/compose/install/)


## Login to repo

[Docker login](https://docs.docker.com/engine/reference/commandline/login/)

```bash
docker login -u <username> -p <password> <repo>
```
If you don't have valid ssl certificate on your registry, you have to follow [this](https://docs.docker.com/registry/insecure/)

## Build docker image for Geocitizen frontend

Create `Dockerfile` with following content:

```dockerfile
FROM tomcat:9

COPY ./citizen.war /usr/local/tomcat/webapps/

EXPOSE 8080
```

It based on [this](https://hub.docker.com/_/tomcat) image.  
To test it you have to download `citizen.war` and put it in the same directory as `Dockerfile`.  
Then you can run
```
docker build -t some_name .
``` 
to build **image**.  
To run the **container** from this image you can use 
```
docker run -d -p 8080:8080 some_name
```
To [push](https://docs.docker.com/engine/reference/commandline/push/) **image** to your repo you can use 
```
docker image tag some_name registry-host:5000/some_name:latest
docker image push registry-host:5000/some_name:latest
```
## Build and deliver this image to Nexus via Jenkins

Store your `Dockerfile` in GitHub, then create the Pipeline with following content:

```groovy
pipeline {
    
    agent {
        label 'docker'
    }

    environment {
        imageName = "SOME_NAME"
        registryCredentials = "YOUR_REGISTRY_CREDENTIALS"
        registry = "YOUR_REGISTRY_HOST_WITH_PORT"
        dockerImage = ''
    }

    stages {
    
        stage ('Clean WS') {
            steps {
                // clean current workspace directory
                cleanWs()

            }
        }

        stage ('Clone Geo Citizen project') {
            steps {             
                git branch: 'YOUR_BRANCH', credentialsId: 'CREDENTIALS_FOR_GITHUB', url: 'git@github.com:USERNAME/REPO_NAME.git'

            }
        }

        stage('Get latest Geo Ciizen .war file') {
            steps {
                // curl link may be different and depending on your nexus settings, you can always refer to API documentation in Nexus itself
                withCredentials([usernamePassword(credentialsId: 'CREDENTIALS_FOR_NEXUS_REPOSIORY_MAVEN', usernameVariable: 'nexus_user_login', passwordVariable: 'nexus_user_pass')]) {

                    sh '''
                    curl -L  \
                    --output "citizen.war" \
                    --user "$nexus_user_login:$nexus_user_pass" \
                    "https://YOUR_NEXUS_REPO/service/rest/v1/search/assets/download?sort=version&direction=desc&repository=maven-snapshots&maven.groupId=com.softserveinc&maven.artifactId=geo-citizen&maven.baseVersion=1.0.5-SNAPSHOT&maven.extension=war"
                    '''
                }
                
            }
        }       
        
        stage('Building image') {
            steps{
                script {
                    dockerImage = docker.build imageName
                }
            }
        }

        stage('Deploy Image') {
            steps{
                script {
                    docker.withRegistry( 'https://'+registry, registryCredentials ) {
                        dockerImage.push("${env.BUILD_NUMBER}")
                        dockerImage.push('latest')
                    }
                }
            }
        }

        stage('Remove Unused docker image') {
            steps{
                sh "docker rmi -f $registry/$imageName:${env.BUILD_NUMBER}"
                sh "docker rmi -f $imageName:latest"
                sh "docker rmi -f $registry/$imageName:latest"
            }
        }
    }
}
```
> Note!: Change names in environment section as well as in **Clone Geo Citizen project** and **Get latest Geo Ciizen .war file** stages.

## Pull docker image

If your Nexus repository is accessible from internet or from some special instance if you configured so, you can pull image from it by following command:

```
docker pull registry-host:5000/some_name:latest
```
>Note!: If you don't allow anonymous pull, you have to [login](#login-to-repo) to your registry first.

## Pull docker images and run containers on your machines

If we have fresh instance (like some ec2 instance), we want to install docker and dokce-compose first, then pull our created previously images and run containers from them.

So I prepeared some initial script that you can add manually or in terraform `user_data` section while instance creation.  
Ubuntu:
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
    image: YOUR_REPO_WITH_PORT/IMAGE_NAME:TAG
    restart: always
    ports:
      - "8080:8080"
SOF
## Create password file for docker login
sh -c 'cat > password.txt' << SOF
${docker_password}
SOF

## Perform docker login
cat password.txt |docker login --username ${docker_username} --password-stdin YOUR_REPO_WITH_PORT

## Build and run image using docker-compose

docker-compose up -d

rm password.txt
```
**YOUR_REPO_WITH_PORT** - your repository host with port.  
**IMAGE_NAME** - name of your image.  
**TAG** - tag of your image.  
You can specify directly **\${docker_username}** and **\${docker_password}** in your script or it's preferred to pass this variables as environment variables:  
In terraform you can can do the following - create file named `some_name.tftpl`, add the previous content, specified only CAPS variables but left ${variables} as it is. Then in user_data section you can specify the file name.  
```hcl
user_data = templatefile("./some_name.tftpl", {
    docker_username = "${var.nexus_docker_username}"
    docker_password = "${var.nexus_docker_password}"
  }
)
```
Do not forget to declare these variables in your terraform code:

```hcl
variable "nexus_docker_username" {
  type      = string
  sensitive = true
}

variable "nexus_docker_password" {
  type      = string
  sensitive = true
}
```

Then while performing terraform commands you should specify the variables:

```hcl
terraform <command> -var "nexus_docker_username=YOUR_DOCKER_USERNAME" -var "nexus_docker_password=YOUR_DOCKER_PASSWORD"
```

For manual performing it's better even to defile *.tfvars file with variables, but in Jenkins pipelines it is appropriate way, or you can use environment variables specified with **`TF_VAR_`** prefix.