#! /usr/bin/env python

import sys
import os
from getpass import getpass
from irods.session import iRODSSession
from irods.access import iRODSAccess

class BisQueIrodsIntegration:
    def __init__(self, host='localhost', port=1247, admin_user='', password='', zone=''):
        self.host = host
        self.port = port
        self.admin_user = admin_user
        self.password = password
        self.zone = zone


    def set_host(self, host='localhost', port=1247, admin_user='', password='', zone=''):
        self.host = host
        self.port = port
        self.admin_user = admin_user
        self.password = password
        self.zone = zone


    def load_from_env(self):
        host = os.environ.get('BISQUE_IRODS_HOST', '')
        port = 1247
        _port = os.environ.get("BISQUE_IRODS_PORT", '')
        if len(_port) > 0:
            if int(_port) > 0:
                port = int(_port)

        zone = os.environ.get('BISQUE_IRODS_ZONE', '')
        admin_user = os.environ.get('BISQUE_IRODS_ADMIN_USERNAME', '')
        password = os.environ.get('BISQUE_IRODS_ADMIN_PASSWORD', '')

        # verify
        if len(host) == 0:
            raise ValueError("Environment varaible 'BISQUE_IRODS_HOST' is not set")

        if port <= 0:
            raise ValueError("Environment varaible 'BISQUE_IRODS_PORT' is not set")

        if len(zone) == 0:
            raise ValueError("Environment varaible 'BISQUE_IRODS_ZONE' is not set")
        
        if len(admin_user) == 0:
            raise ValueError("Environment varaible 'BISQUE_IRODS_ADMIN_USERNAME' is not set")

        if len(password) == 0:
            raise ValueError("Environment varaible 'BISQUE_IRODS_ADMIN_PASSWORD' is not set")
        
        self.host = host
        self.port = port
        self.zone = zone
        self.admin_user = admin_user
        self.password = password


    def create_user(self, new_user='', password=''):
        # Create the user
        # should be done by admin
        with iRODSSession(host=self.host, port=self.port, user=self.admin_user, password=self.password, zone=self.zone) as session:
            # create the user
            # somehow, the password given as 'auth_str' param didn't work, 
            # so had to update password below
            session.users.create(new_user, "rodsuser", self.zone, password)

            # update password
            session.users.modify(new_user, 'password', password, self.zone)

            # add to groups
            session.user_groups.addmember('bisque_group', new_user, self.zone)
        
        # Set ACL
        # should be done by the new user 
        self.update_acl_userhome(new_user, password)


    def update_acl_userhome(self, new_user='', password=''):
        # Set ACL
        with iRODSSession(host=self.host, port=self.port, user=new_user, password=password, zone=self.zone) as session:
            userhome = "/%s/home/%s" % (self.zone, new_user)
            
            # enable ACL inheritance of the user's home directory
            acl_inherit = iRODSAccess('inherit', userhome)
            session.permissions.set(acl_inherit)

            # allow rodsadmin group to access the home directory
            acl_admin = iRODSAccess('write', userhome, 'rodsadmin', self.zone)
            session.permissions.set(acl_admin)


    def update_user_password(self, user='', password=''):
        # Update the user's password
        # should be done by admin
        with iRODSSession(host=self.host, port=self.port, user=self.admin_user, password=self.password, zone=self.zone) as session:
            # update password
            session.users.modify(user, 'password', password, self.zone)


def get_cmd_args(argv):
    host = os.environ.get('BISQUE_IRODS_HOST', '')
    port = 0
    _port = os.environ.get("BISQUE_IRODS_PORT", '')
    if len(_port) > 0:
        if int(_port) > 0:
            port = int(_port)

    zone = os.environ.get('BISQUE_IRODS_ZONE', '')
    admin_user = os.environ.get('BISQUE_IRODS_ADMIN_USERNAME', '')
    password = os.environ.get('BISQUE_IRODS_ADMIN_PASSWORD', '')


    if len(argv) == 3:
        host = argv[0]
        port = argv[1]
        zone = argv[2]
    elif len(argv) == 0:
        if len(host) == 0:
            host = input("iRODS host: ")
            if len(host) == 0:
                sys.stderr.write("iRODS host is not given\n")
                sys.exit(1)

        if port <= 0:
            _port = input("iRODS port [1247]: ")
            if len(_port) > 0:
                if int(_port) > 0:
                    port = int(_port)
            else:
                port = 1247

        if len(zone) == 0:
            zone = input("iRODS zone: ")
            if len(zone) == 0:
                sys.stderr.write("iRODS zone is not given\n")
                sys.exit(1)
    else:
        sys.stderr.write("Not sufficient arguments\n")
        sys.stderr.write("> python irods_user.py <host> <port> <zone>\n")
        sys.exit(1)

    if len(host) == 0:
        sys.stderr.write("iRODS host is not given\n")
        sys.exit(1)

    if port <= 0:
        sys.stderr.write("iRODS port is not given\n")
        sys.exit(1)

    if len(zone) == 0:
        sys.stderr.write("iRODS zone is not given\n")
        sys.exit(1)
    
    if len(admin_user) == 0:
        admin_user = input("Admin username: ")
        if len(admin_user) == 0:
            sys.stderr.write("Admin username is not given\n")
            sys.exit(1)

    if len(password) == 0:
        password = getpass(prompt="Admin password: ")
        if len(password) == 0:
            sys.stderr.write("Admin password is not given\n")
            sys.exit(1)
    
    new_user = input("New username: ")
    if len(new_user) == 0:
        sys.stderr.write("New username is not given\n")
        sys.exit(1)

    new_password = getpass(prompt="New user password: ")
    if len(new_password) == 0:
        sys.stderr.write("New user password is not given\n")
        sys.exit(1)


    return {
        "host": host,
        "port": port,
        "admin_user": admin_user,
        "password": password,
        "zone": zone,

        "new_user": new_user,
        "new_password": new_password,
    }

def main(argv):
    arg = get_cmd_args(argv)

    integ = BisQueIrodsIntegration(host=arg["host"], port=arg["port"], admin_user=arg["admin_user"], password=arg["password"], zone=arg["zone"])
    integ.create_user(arg["new_user"], arg["new_password"])

if __name__ == "__main__":
    main(sys.argv[1:])
    