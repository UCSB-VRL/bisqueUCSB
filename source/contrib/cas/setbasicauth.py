# Example script of how to login through CAS and set a basicauth password
# so modules that do not have CAS logins can work.
#
#
from bqapi import BQSession
import argparse

def setbasicauth(bisquehost, username, password):
    s = BQSession()
    s.init_cas (username, password, bisque_root=bisquehost, create_mex=False)
    r = s.c.post(bisquehost + "/auth_service/setbasicauth", data = { 'username': username, 'passwd': password})
    print r.text




def main():
    parser = argparse.ArgumentParser(description='Set Basic auth credentials on CAS protected Bisque')

    parser.add_argument ('-u', '--credentials', default=None, help="CAS credentials in form of user:password")
    parser.add_argument ("bisque_host", nargs=1)
    args = parser.parse_args()
    setbasicauth (args.bisque_host, *args.credential.split(':'))



if __name__ == "__main__":
    main()
