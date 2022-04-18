# Supervisor
**Table of Contents**
- [Supervisor](#supervisor)
  - [Installation](#installation)
  - [Simple demo program](#simple-demo-program)
  - [Geocitizen supervisation](#geocitizen-supervisation)

## Installation

```bash
sudo apt install supervisor
```
## Simple demo program

[example](https://www.digitalocean.com/community/tutorials/how-to-install-and-manage-supervisor-on-ubuntu-and-debian-vps)

## Geocitizen supervisation

We gonna create new image. But some preparation is needed.

For postgresql service we need a start [script](https://stackoverflow.com/questions/11092358/running-postgresql-with-supervisord).

`postgres_service.sh`

```bash
#!/bin/sh

# This script is run by Supervisor to start PostgreSQL in foreground mode

function shutdown()
{
    echo "Shutting down PostgreSQL"
    pkill postgres
}

if [ -d /var/run/postgresql ]; then
    chmod 2775 /var/run/postgresql
else
    install -d -m 2775 -o postgres -g postgres /var/run/postgresql
fi

# Allow any signal which would kill a process to stop PostgreSQL
trap shutdown HUP INT QUIT ABRT KILL ALRM TERM TSTP

exec su -l postgres -c "/usr/libexec/postgresql/postgres -D /var/lib/postgresql/data --config-file=/var/lib/postgresql/data/postgresql.conf"
```

`install.sh`

```bash
#!/bin/sh

apk update && apk add --no-cache postgresql12 supervisor openjdk11 curl
# Postgres
mkdir /var/lib/postgresql/data && chown postgres:postgres /var/lib/postgresql/data
chmod 0700 /var/lib/postgresql/data && mkdir /run/postgresql && chown postgres:postgres /run/postgresql/
su -l postgres -c 'initdb -D /var/lib/postgresql/data'
sed -i "s/#listen_addresses = 'localhost'/listen_addresses = '127.0.0.1'/g" /var/lib/postgresql/data/postgresql.conf

# Create user and db
db_user=geo_user
db_pass=some_pass
db_base=ss_geocitizen
su -l postgres -c 'pg_ctl start -D /var/lib/postgresql/data'
su -l postgres -c "psql -c \"CREATE ROLE $db_user WITH LOGIN;\""
su -l postgres -c "psql -c \"CREATE DATABASE $db_base;\""
su -l postgres -c "psql -c \"GRANT ALL PRIVILEGES ON DATABASE $db_base to $db_user;\""
su -l postgres -c "psql -c \"ALTER USER $db_user WITH PASSWORD $db_pass;\""

# Tomcat
VERSION=9.0.62
mkdir /opt/tomcat
wget https://www-eu.apache.org/dist/tomcat/tomcat-9/v${VERSION}/bin/apache-tomcat-${VERSION}.tar.gz -P /tmp
tar -xf /tmp/apache-tomcat-${VERSION}.tar.gz -C /opt/tomcat/
ln -s /opt/tomcat/apache-tomcat-${VERSION} /opt/tomcat/latest
chmod +x /opt/tomcat/latest/bin/*.sh



# Supervisor
supervisord -c /etc/supervisord.conf
supervisor_name=admin
supervisor_pass=some_pass
sed -i "s/;\[inet_http_server\]/[inet_http_server]/g" /etc/supervisord.conf
sed -i "s/;port=127.0.0.1/port=*/g" /etc/supervisord.conf
sed -i "s/;username=user/username=$supervisor_name/g" /etc/supervisord.conf
sed -i "s/;password=123/password=$supervisor_pass/g" /etc/supervisord.conf
mkdir /etc/supervisor.d
```
> **Note**: Change variables accordint to your environment.

`supervisord.ini`

```bash
[supervisord]
nodaemon=true

[program:postgres]
command=/usr/bin/postgres_service.sh
autostart=true
autorestart=true
stderr_logfile=/var/log/postgres_err.log
stdout_logfile=/var/log/postgres_out.log
stopsignal=QUIT


[program:tomcat]
command=/opt/tomcat/latest/bin/catalina.sh run
autorestart=true
startsecs=20
stopsignal=INT
stopasgroup=true
killasgroup=true
stdout_logfile=/var/log/catalina.out
stderr_logfile=/var/log/catalina.out
environment=JAVA_HOME="/usr/lib/jvm/default-jvm",JAVA_BIN="/usr/lib/jvm/default-jvm/bin"
```

`Dockerfile`

```dockerfile
FROM alpine:3.15

COPY --chmod=777 ./install.sh /home/install.sh
RUN ./home/install.sh

COPY --chmod=777 ./postgres_service.sh /usr/bin/postgres_service.sh

COPY ./supervisord.ini /etc/supervisor.d/supervisord.ini
# archive already prepared
COPY ./citizen.war /opt/tomcat/latest/webapps/citizen.war

EXPOSE 9001 8080

CMD ["/usr/bin/supervisord"]
```

```bash
docker build . -t supervisored_geocitizen
```

![](img/docker_buildkit.jpg)


```bash
docker run --name supervisored -p 9001:9001 -p 8080:8080 -d supervisored_geocitizen:latest
```

Also you can reach supervisor web interface on port 9001

![](img/supervisor_web.jpg)