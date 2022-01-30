import rpm, sys

script_mode = str(sys.argv[1])
package_name = str(sys.argv[2])
ts = rpm.TransactionSet()


#Funtion from file
def printing_hdr_values(package):
    for header in package:
        print("RELEASE........", header[rpm.RPMTAG_RELEASE].decode())

#Function from package name
def printing_package_values(package):
    print("RELEASE........", package[rpm.RPMTAG_RELEASE].decode())


if script_mode == 'name':
    try:
        package = ts.dbMatch('name', package_name)
        printing_hdr_values(package)
    except:
        print("Package name wrong of doesn't exist")

if script_mode == 'file':
    try:
        rpm_file = open(package_name)
        package = ts.hdrFromFdno(rpm_file)
        printing_package_values(package)
        rpm_file.close()
    except FileNotFoundError:
        print("File name wrong or doesn't exist")

if script_mode != 'name' and script_mode != 'file':
    print("Error in script mode, input \"name\" or \"file\" ")


'''
Usage for installed package name:
python3 hw4.py name openssh

For .rpm file
python3 hw4.py file rpm_demo-0.1-1.noarch.rpm
'''
