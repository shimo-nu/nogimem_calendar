from __future__ import print_function
import httplib2
import os
import datetime
import argparse
from dotenv import load_dotenv

from apiclient import discovery
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage


load_dotenv()

SCOPES = 'https://www.googleapis.com/auth/calendar'
CLIENT_SECRET_FILE = 'client_secret.json'
APPLICATION_NAME = 'Add Schedule to calendar'
calendarId = os.getenv("CALENDARID")

def get_credentials(args = None):
    """Gets valid user credentials from storage.

    If nothing has been stored, or if the stored credentials are invalid,
    the OAuth2 flow is completed to obtain the new credentials.

    Returns:
        Credentials, the obtained credential.
    """
    home_dir = os.path.expanduser('~')
    credential_dir = os.path.join(home_dir, '.credentials')
    if not os.path.exists(credential_dir):
        os.makedirs(credential_dir)
    credential_path = os.path.join(credential_dir,
                                   'calendar-python-quickstart.json')

    store = Storage(credential_path)
    credentials = store.get()
    if not credentials or credentials.invalid:
        flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
        flow.user_agent = APPLICATION_NAME
        if args:
            credentials = tools.run_flow(flow, store, flags)
        else: # Needed only for compatibility with Python 2.6
            credentials = tools.run(flow, store)
        print('Storing credentials to ' + credential_path)
    return credentials
def ArgParser():
    parser = argparse.ArgumentParser(parents=[tools.argparser])
    
    parser.add_argument('--start_time', type=str)
    parser.add_argument('--end_time', type=str)
    parser.add_argument('--title', type=str)
    parser.add_argument('--description', type=str)

    args = parser.parse_args()
    return args
    
def get_schedule(calendarId, start_time, end_time, args=None):
    print(calendarId)
    if (args is None):
        args = ArgParser()
    credentials = get_credentials(args)
    http = credentials.authorize(httplib2.Http())
    service = discovery.build('calendar', 'v3', http=http)

    start_date = datetime.datetime.strptime(start_time, '%Y-%m-%d-%H-%M')
    if (end_time is None):
        end_date = start_date + datetime.timedelta(hours=1)
    else:
        end_date = datetime.datetime.strptime(end_time, '%Y-%m-%d-%H-%M')
    
    events = service.events().list(calendarId=calendarId, timeMin=start_date.isoformat() + 'Z',  timeMax=end_date.isoformat() + 'Z').execute()
    print(events)
    for event in events['items']:
        print(event['summary'])

def add_schedule(calendarId, start_time, end_time, title, description, all_day = False , args = None):
    print(calendarId)
    if (args is None):
        args = ArgParser()
    credentials = get_credentials(args)
    http = credentials.authorize(httplib2.Http())
    service = discovery.build('calendar', 'v3', http=http)

    data_format = "%Y-%m-%d-%H-%M"
    if (all_day):
        data_format = "%Y-%m-%d"
    start_date = datetime.datetime.strptime(start_time, data_format)
    if (end_time is None):
        end_date = start_date + datetime.timedelta(hours=1)
    else:
        end_date = datetime.datetime.strptime(end_time, data_format)
    event = {
        'summary': title,
        'description': description,
        'start':{
            'dateTime' : start_date.isoformat(),
            'timeZone' : 'Japan'
        },
        'end':{
            'dateTime' : end_date.isoformat(),
            'timeZone' : 'Japan'
        },
    }
    event = service.events().insert(calendarId = calendarId, body=event).execute()

def main():
    """Shows basic usage of the Google Calendar API.

    Creates a Google Calendar API service object and outputs a list of the next
    10 events on the user's calendar.
    """
    
    args = ArgParser()
    # add_schedule(calendarId, args.start_time, args.end_time, args.title, args.description, args)
    get_schedule(calendarId, args.start_time, args.end_time)

if __name__=='__main__':
    main()
