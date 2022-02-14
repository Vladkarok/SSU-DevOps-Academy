#!/bin/bash
# Delete directory if exist
sudo rm -r ~/Geocit134 || echo "Directory doesn't exist"
# Clone repo to home
git clone https://github.com/mentorchita/Geocit134.git ~/Geocit134
cd ~/Geocit134

## Repair pom.xml. Use this script in root directory of the project.
# Fix pom.xml with https on spting repos and javax
sed -i 's/http:\/\/repo.spring.io\/milestone/https:\/\/repo.spring.io\/milestone/g' pom.xml
sed -i 's/http:\/\/repo.spring.io\/libs-milestone/https:\/\/repo.spring.io\/libs-milestone/g' pom.xml
sed -i 's/<artifactId>servlet-api<\/artifactId>/<artifactId>javax.servlet-api<\/artifactId>/g' pom.xml
# Comment nexus selfhosted repo
sed -i 's/^<distributionManagement>/<!--<distributionManagement>/g' pom.xml
sed -i 's/<\/distributionManagement>$/<\/distributionManagement>-->/g' pom.xml
#-------------------------------------------------------------------------------------------------------
## Repair application.properties
serverip='192.168.56.105'
databaseip='192.168.56.106'
emailname='your@gmail.com'
emailpass='your_gmail_password'
dbname='ss_citizen'
dblogin='softserve'
dbpass='university'
# Change frontend server ip address
sed -i "s/http:\/\/localhost/http:\/\/$serverip/g" src/main/resources/application.properties
# Change postgres database connection properties
sed -i "s/postgresql:\/\/localhost/postgresql:\/\/$databaseip/g" src/main/resources/application.properties
# Change database name
sed -i "s/ss_demo_1$/$dbname/g" src/main/resources/application.properties
# Change database login
sed -i "s/db\.username=postgres/db.username=$dblogin/g" src/main/resources/application.properties
# Change database password
sed -i "s/db\.password=postgres/db.password=$dbpass/g" src/main/resources/application.properties
# Change liquibase login
sed -i "s/^username=postgres$/username=$dblogin/g" src/main/resources/application.properties
# Change liquibase password
sed -i "s/^password=postgres$/username=$dbpass/g" src/main/resources/application.properties
# Liquibase
sed -i "s/35\.204\.28\.238/$databaseip/g" src/main/resources/application.properties
# Change email name for sending messages
sed -i "s/ssgeocitizen\@gmail\.com/$emailname/g" src/main/resources/application.properties
sed -i "s/email.password=softserve/email.password=$emailpass/g" src/main/resources/application.properties
#--------------------------------------------------------------------------------------------------------
## Repair index.html favicon
sed -i "s/\/src\/assets/\.\/static/g" src/main/webapp/index.html
#--------------------------------------------------------------------------------------------------------
## Repair .js files (replace localhosts)
sed -i "s/localhost/$serverip/g" src/main/webapp/static/js/app.6313e3379203ca68a255.js
sed -i "s/localhost/$serverip/g" src/main/webapp/static/js/app.6313e3379203ca68a255.js.map
sed -i "s/localhost/$serverip/g" src/main/webapp/static/js/vendor.9ad8d2b4b9b02bdd427f.js
sed -i "s/localhost/$serverip/g" src/main/webapp/static/js/vendor.9ad8d2b4b9b02bdd427f.js.map

#--------------------------------------------------------------------------------------------------------
mvn install
warfilename='citizen.war'
sleep 5
sudo rm /opt/tomcat/latest/webapps/$warfilename || echo "Tomcat's webapp directory is empty"
sleep 10
sudo cp target/$warfilename /opt/tomcat/latest/webapps/
echo ".war has been copied to Tomcat"

