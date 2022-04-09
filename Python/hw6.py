import sys
from io import BytesIO
from docker import APIClient



"""USAGE

python3 hw6.py homework:6

Prerequestiments

sudo apt install python3-pip && sudo pip3 install docker

MAIN DOCUMENTAION
https://docker-py.readthedocs.io/en/5.0.3/api.html
"""



# input paramether - tag_name with sysargv
tag_name = str(sys.argv[1])
tag_name_core = "centos7:hw"
# You can change it
opened_port = int(5555)
# base image (SHOULD BE LOCATED IN THE SAME DIRECTORY AS THIS FILE)
docker_image = 'centos7_hw.tar'

# Format input string
splitted = tag_name.split(':')
splitted[0] = splitted[0].capitalize()
formatted_input = "".join(splitted)+ '!'

# docker url to socket (INFO https://docker-py.readthedocs.io/en/5.0.3/api.html#low-level-api)
client = APIClient(base_url='unix://var/run/docker.sock')

# open docker .tar image as chunks for further loading (INFO https://docker-py.readthedocs.io/en/5.0.3/api.html#docker.api.image.ImageApiMixin.load_image)
# The data should be in binary format, so 'rb' option is used.
"""
For "importing" image into your system we can use **save/load** or **export/import** commands.
The difference between them is that **load** command loads an image or repository and RESTORES BOTH IMAGES, TAGS AND LAYERS/HISTORY,
while **import** command import the contents from a tarball to create a filesystem image WITHOUT ANY LAYER/HISTORY.
The problem could happen when you try to build a new image from a imported before with **import** command and there is no entrypoint command, 
or any other additional info that prevent's you from easy and fast building.
"""
with open(docker_image, 'rb') as binary_core_docker_file:
    # load docker image
    client.load_image(binary_core_docker_file)
    

## Building homework image

# Declare dockerfile as text
dockerfile = '''
FROM centos7/hw:latest

RUN yum -y --setopt=tsflags=nodocs install deltarpm && \\
    yum -y --setopt=tsflags=nodocs update && \\
    yum -y --setopt=tsflags=nodocs install httpd && \\
    yum clean all && \\
    echo -e '#!/bin/bash\\nrm -rf /run/httpd/* /tmp/httpd*\\nexec /usr/sbin/apachectl -DFOREGROUND'> /run-httpd.sh && \\
    chmod -v +x /run-httpd.sh && \\
    echo -e '<html>\\n<body bgcolor="purple">\\n<h2><font color="gold"><p style="text-align:center">{text_to_be_displayed}</p></font></h2>\\n</body>\\n</html>'> /var/www/html/index.html

EXPOSE 80

CMD ["/run-httpd.sh"]
'''.format(text_to_be_displayed=formatted_input)

# Build image based on given image centos7/hw:latest and dockerfile with provided tag_name as input paramether (INFO https://docker-py.readthedocs.io/en/5.0.3/api.html#module-docker.api.build)
response = [line for line in client.build(
    fileobj=BytesIO(dockerfile.encode('utf-8')), rm=True, tag=tag_name
    )]

## Running created container
# Specify container name
container_name = tag_name.split(':')[0]

# Create container INFO (https://docker-py.readthedocs.io/en/5.0.3/api.html#docker.api.container.ContainerApiMixin.create_container)
client.create_container(
    tag_name, detach=True, ports=[opened_port],
    host_config=client.create_host_config(port_bindings={
        80: opened_port
    }, restart_policy={'Name':'always'}), name=container_name
)

# Start created container INFO (https://docker-py.readthedocs.io/en/5.0.3/api.html#docker.api.container.ContainerApiMixin.start)

client.start(container_name)

"""
You can open your browser and visit http://IP_OF_DOCKER_MACHINE:5555 or run command:
curl http://IP_OF_DOCKER_MACHINE:5555
to get http responce where you can find required string.
"""

