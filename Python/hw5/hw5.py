import os, sqlite3, sys

project_to_edit = 'Project3'
app_to_edit = 'apache'
port_to_edit_to = 80

db = os.path.join(os.path.dirname(__file__), str(sys.argv[1]))

conn = sqlite3.connect(db)
c = conn.cursor()

def select_servertype(projectname, servertype):
    with conn:
        c.execute('''SELECT port_number, proj_name, type_name FROM ServerPorts 
            INNER JOIN Servers ON Servers.id = ServerPorts.servers_id 
            INNER JOIN ServerTypes ON ServerTypes.id = Servers.servertypes_id 
            INNER JOIN ServerProjects ON ServerProjects.servers_id = Servers.id 
            INNER JOIN Projects ON Projects.id = ServerProjects.projects_id 
            WHERE Projects.proj_name = :projectname AND ServerTypes.type_name = :type_name;''', {'projectname': projectname, 'type_name': servertype})
        return c.fetchall()

def update_portnumber(portnumber):
    with conn:
        c.execute('''UPDATE ServerPorts SET port_number = :portnumber WHERE ServerPorts.id IN (
            SELECT ServerPorts.id FROM ServerPorts
            INNER JOIN Servers ON Servers.id = ServerPorts.servers_id
            INNER JOIN ServerTypes ON ServerTypes.id = Servers.servertypes_id
            INNER JOIN ServerProjects ON ServerProjects.servers_id = Servers.id
            INNER JOIN Projects ON Projects.id = ServerProjects.projects_id
            WHERE Projects.proj_name = 'Project3' AND ServerTypes.type_name = 'apache');''', {'portnumber': portnumber})



select_apache = select_servertype(project_to_edit, app_to_edit)

print("Before edition", "\n", select_apache)

update_portnumber(port_to_edit_to)

select_apache = select_servertype(project_to_edit, app_to_edit)

print("After edition", "\n", select_apache)

conn.close()