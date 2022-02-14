from diagrams.custom import Custom
from diagrams.onprem.ci import Jenkins
from diagrams.onprem.vcs import Github
from diagrams.onprem.network import Tomcat
from diagrams import Diagram, Cluster, Edge
from diagrams.aws.compute import EC2Instance
from diagrams.generic.os import Centos, Ubuntu
from diagrams.programming.language import Java
from diagrams.onprem.database import Postgresql
from diagrams.onprem.iac import Ansible, Terraform
#    "forcelabels":"true"
 #   "concentrate":"true"
graph_attr = {
    "splines":"splines",
    "fontsize":"30"
}
edge_attr = {
    "minlen":"2.0",
    "penwidth":"4.0"
}
legend_attr = {
    "fontsize":"30",
    "minlen":"2.0",
    "penwidth":"4.0",
    "bgcolor":"white"
}
with Diagram("AWS Geo citizen application deploying", show=True, direction="LR", graph_attr=graph_attr, edge_attr=edge_attr):


    with Cluster("Legend", graph_attr=legend_attr):
        
        a1 = Custom(" ", "../customimages/a1.png")
        a2 = Custom(" ", "../customimages/a2.png")
        b1 = Custom(" ", "../customimages/b1.png")
        b2 = Custom(" ", "../customimages/b2.png")
        c1 = Custom(" ", "../customimages/c1.png")
        c2 = Custom(" ", "../customimages/c2.png")
        # d1 = Custom(" ", "../customimages/d1.png")
        # d2 = Custom(" ", "../customimages/d2.png")
        # d1 - Edge(color="red", style="dashed", label="Terraform responce") - d2
        e1 = Custom(" ", "../customimages/e1.png")
        e2 = Custom(" ", "../customimages/e2.png")
        f1 = Custom(" ", "../customimages/f1.png")
        f2 = Custom(" ", "../customimages/f2.png")
        g1 = Custom(" ", "../customimages/g1.png")
        g2 = Custom(" ", "../customimages/g2.png")
        #h1 = Custom(" ", "../customimages/h1.png")
        #h2 = Custom(" ", "../customimages/h2.png")
        a1 - Edge(color="red", style="bold", label="Terraform job", fontsize="30") - a2 - Edge(color="blue", style="bold", label="Ansible job", fontsize="30") - b1

        b2 - Edge(color="darkgreen", style="dashed", label="Jenkins starts Ansible \n after Terraform responce", fontsize="30") - c1 - \
        Edge(color="red", style="dashed", label="Terraform inventory file", fontsize="30") - c2

        e1 - Edge(color="orange", style="bold", label="Maven \ninstalls citizen.war", fontsize="30") - e2 - \
        Edge(color="purple", style="bold", label="Geo citizen communication \n with server's app", fontsize="30") - f1

        f2 - Edge(color="green", style="dashed", label="Intra app \n communication", fontsize="30") - g1 - \
        Edge(color="yellow", style="bold", label="Client with app\ncommunication", fontsize="30") - g2
    

    jenkins = Jenkins("Jenkins", fontsize="20")
    ansible = Ansible("Ansible", fontsize="20")
    github = Github("Github repository", fontsize="20")
    terraform =Terraform(" ")
    devops = Custom(" ", "./customimages/DevOps.png")
    browser = Custom(" ", "./customimages/Browser.png")
    
    with Cluster("Amazon Web Services", graph_attr=graph_attr):
        api_gateway = Custom(" ", "./customimages/aws.png")

        with Cluster("Elastic Compute Cloud", graph_attr=graph_attr):

            with Cluster("Ubuntu VM", graph_attr=graph_attr):
                ec2_ubuntu = EC2Instance("EC2-VM", fontsize="20")

                with Cluster("Ubuntu OS", graph_attr=graph_attr):
                    geocit = Custom(" ", "./customimages/select.png")
                    ubuntu = Ubuntu("Ubuntu", fontsize="20")
                    java = Java()
                    maven = Custom("", "./customimages/maven.png")
                    tomcat = Tomcat("Tomcat", fontsize="20")



            with Cluster("Centos VM", graph_attr=graph_attr):
                ec2_centos = EC2Instance("EC2-VM", fontsize="20")

                with Cluster("Centos OS", graph_attr=graph_attr):
                    centos = Centos(" ", fontsize="20")
                    postgresql = Postgresql("Postgresql", fontsize="20")

    ## Basic connection to demonstrate intra-OS communication
    #centos - postgresql
                    
    ## EC2 VM to Centos Operating system
    ec2_centos - Edge(color="red", style="dashed", fontsize="30") - centos

    ## Ansible playbook for PostgreSQL
    centos >> Edge(color="blue", style="bold", fontsize="30") >> postgresql 

    ## Common connections
    # Amazon Web Servicec API Gateway to EC2 VMs    
    api_gateway >> Edge(color="red", style="bold", fontsize="30") << ec2_ubuntu
    api_gateway >> Edge(color="red", style="bold", fontsize="30") << ec2_centos

    ## Basic connection to demonstrate intra-OS communication
    #ubuntu - tomcat

    ## Basic connection to demonstrate intra-OS communication
    #ubuntu - java

    ## Basic connection to demonstrate intra-OS communication
    #ubuntu - maven

    # EC2 VM to Ubuntu Operating system
    ec2_ubuntu - Edge(color="red", style="dashed", fontsize="30") - ubuntu

    # Ansible playbook for tomcat, java, maven
    ubuntu >> Edge(color="blue", style="bold", fontsize="30") >> tomcat
    ubuntu >> Edge(color="blue", style="bold", fontsize="30") >> java
    ubuntu >> Edge(color="blue", style="bold", fontsize="30") >> maven

    # Intra app communication that relies on java
    java >> Edge(color="green", style="dashed", fontsize="30") << maven
    java >> Edge(color="green", style="dashed", fontsize="30") << tomcat

    # Maven generates .war file for web server tomcat
    maven >> Edge(color="orange", style="bold", label="citizen.war", fontsize="30") >> tomcat

    # Tomcat serves Geo citizen app
    tomcat >> Edge(color="purple", style="bold", fontsize="30") << geocit

    # Api Gateway returnes responce about work finish to terraform, terraform to jenkins
    #api_gateway >> Edge(color="red", style="dashed", label=" ") >> \
    terraform >> Edge(color="red", style="line", label=" ", fontsize="30") >> jenkins

    # DevOps started the job, jenkins > terraform > api gateway
    devops >> Edge(color="darkgreen", style="line", label="Start", fontsize="30")\
    >> jenkins >> Edge(color="darkgreen", style="line", label="First", fontsize="30")\
    >> terraform >> Edge(color="red", style="bold", label="First - IAM credentials", fontsize="30")\
    << api_gateway

    # Cloning repo from Github to ubuntu, but main app that need that repo is Maven
    github >> Edge(color="blue", style="bold", label="git clone", fontsize="30") >> maven
    
    # Connection between two servers (tomcat and postgresql)
    postgresql >> Edge(color="purple", style="bold", fontsize="30") << geocit

    # Jenkins starts ansible
    jenkins >> Edge(color="darkgreen", style="dashed", label="Run after Terraform completion", fontsize="30") >> ansible
    terraform >> Edge(color="red", style="dashed", label="Second - Terraform \n inventory file", fontsize="30") >> ansible

    # Ansible connects to Linux OS for configuring
    ansible >> Edge(color="blue", style="bold", fontsize="30") << ubuntu
    ansible >> Edge(color="blue", style="bold", fontsize="30") << centos
    
    # Client browser interaction with Geo citizen app
    tomcat >> Edge(color="yellow", style="bold", label="Web", fontsize="30") << browser

    #jenkins - Edge(color="transparent") - a1