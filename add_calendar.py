from __future__ import print_function
import httplib2
import os
import datetime
import argparse
from dotenv import load_dotenv
from dateutil import tz

from apiclient import discovery
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage


load_dotenv()

SCOPES = 'https://www.googleapis.com/auth/calendar'
CLIENT_SECRET_FILE = 'client_secret.json'
APPLICATION_NAME = 'Add Schedule to calendar'
calendarId = os.getenv("CALENDARID")

JST = tz.gettz('Asia/Tokyo')
UTC = tz.gettz('UTC')

def ArgParser():
    parser = argparse.ArgumentParser(parents=[tools.argparser])
    
    parser.add_argument('--start_time', type=str)
    parser.add_argument('--end_time', type=str)
    parser.add_argument('--title', type=str)
    parser.add_argument('--description', type=str)
    parser.add_argument('--all_day', type=bool, default=False)

    args = parser.parse_args()
    return args

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
            credentials = tools.run_flow(flow, store, args)
        else: # Needed only for compatibility with Python 2.6
            credentials = tools.run(flow, store)
        print('Storing credentials to ' + credential_path)
    return credentials

def create_service(args):
    credentials = get_credentials(args)
    http = credentials.authorize(httplib2.Http())
    service = discovery.build('calendar', 'v3', http=http)
    return service

def create_event_format(title, description, start_date, end_date, all_day):

    if (all_day):
        event = {
            'summary': title,
            'description': description,
            'start':{
                'date' : start_date.isoformat(),
                'timeZone' : 'Japan'
            },
            'end':{
                'date' : end_date.isoformat(),
                'timeZone' : 'Japan'
            },
        }
    else:
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
    return event

def get_schedule(calendarId, start_time, end_time, all_day = False,  args=None):
    
    if (args is None):
        args = ArgParser()

    service = create_service(args)
    
    if (all_day):
        date_format = "%Y-%m-%d"
        start_date = datetime.datetime.strptime(start_time, date_format).astimezone(UTC).replace(tzinfo=None).isoformat() + 'Z'
        end_date = datetime.datetime.strptime(end_time, date_format).astimezone(UTC).replace(tzinfo=None) + datetime.timedelta(minutes=1)
        end_date = end_date.isoformat() + 'Z'
    else:
        date_format = "%Y-%m-%d-%H-%M"
        start_date = datetime.datetime.strptime(start_time, date_format).astimezone(UTC).replace(tzinfo=None).isoformat() + 'Z'
        end_date = datetime.datetime.strptime(end_time, date_format).astimezone(UTC).replace(tzinfo=None).isoformat() + 'Z'
    
    print(f"start date : {start_date}")
    print(f"end date : {end_date}")
    events = service.events().list(calendarId=calendarId, timeMin=start_date, timeMax=end_date).execute()
    return events["items"]

def add_schedule(calendarId, start_time, end_time, title, description, all_day = False , args = None):

    if (args is None):
        args = ArgParser()

    service = create_service(args)


    if (all_day):
        date_format = "%Y-%m-%d"
        start_date = datetime.datetime.strptime(start_time, date_format).date()
        end_date = datetime.datetime.strptime(end_time, date_format).date()
    else:
        date_format = "%Y-%m-%d-%H-%M"
        start_date = datetime.datetime.strptime(start_time, date_format)
        end_date = datetime.datetime.strptime(end_time, date_format)

        if (start_time == end_time):
            end_date += datetime.timedelta(hour=1)
    event = create_event_format(title, description, start_date, end_date, all_day)

    schedules = get_schedule(calendarId, start_time, end_time, all_day)
    is_summary_of_schedules = ['summary' in schedule for schedule in schedules]
    if (not any(is_summary_of_schedules)):
        print(f"schedules : {schedules}")
        service.events().insert(calendarId = calendarId, body=event).execute()
    elif (event['summary'] != schedules[is_summary_of_schedules.index(True)]["summary"]):
        print("event title : {}".format(event['summary']))
        # print("schedule title : {}".format(schedules[is_summary_of_schedules.index()]["summary"]))
        service.events().insert(calendarId = calendarId, body=event).execute()
    else:
        print("Already exists schedule")

def main():
    """Shows basic usage of the Google Calendar API.

    Creates a Google Calendar API service object and outputs a list of the next
    10 events on the user's calendar.
    """
    
    args = ArgParser()
    if (args.end_time is None):
        args.end_time = args.start_time
    print(args.all_day)
    add_schedule(calendarId, args.start_time, args.end_time, args.title, args.description, all_day = args.all_day, args = args)
    # print("get_schedule")
    # schedule = get_schedule(calendarId, args.start_time, args.end_time, all_day = args.all_day)
    # print(schedule)
if __name__=='__main__':
    main()
