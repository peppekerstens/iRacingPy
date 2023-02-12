from  iracingdataapi.client import irDataClient
import pwinput

if __name__ == '__main__':
    if len(sys.argv) < 5:
        #raise BaseException('bla')  #does not work; processing is stopped see: https://docs.python.org/3/library/exceptions.html#Exception
        #print('Error: to few arguments!')
        #print('Usage: py [scriptname] [username] [password]')
        print('Going into interactive mode....')
        username = input("Enter username: ")
        #password = getpass.getpass('Enter password:') # hard in practise, does not show any input hint
        password = pwinput.pwinput(prompt='Enter password: ')
        session_id = input("Enter session_id: ")
        csv_name = input("Enter CSV name: ")

    if len(sys.argv) > 5:
        print('Error: to many arguments!')
        print('Usage: py get_session_data.py [username] [password] [session_id] [csv name]')
        sys.exit()

    if len(sys.argv) == 5:
        username = sys.argv[1] #first cmdline arg is acnt name
        password = sys.argv[2] #second cmdline arg is pwd
        session_id = sys.argv[3] #third cmdline arg is session_id
        csv_name = sys.argv[4] #third cmdline arg is csv_name

    irDataClient(username=username, password=password)