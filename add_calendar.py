from __future__ import print_function
import httplib2
import os
import datetime
import argparse
from dotenv import load_dotenv
from dateutil import tz

from apiclient import discovery
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

import google.auth

load_dotenv()

SCOPES = 'https://www.googleapis.com/auth/calendar'
CLIENT_SECRET_FILE = 'client_secret.json'
APPLICATION_NAME = 'Add Schedule to calendar'
calendarId = os.getenv("CALENDARID")

JST = tz.gettz('Asia/Tokyo')
UTC = tz.gettz('UTC')

def ArgParser():
    parser = argparse.ArgumentParser()
    
    parser.add_argument('--start_time', type=str)
    parser.add_argument('--end_time', type=str)
    parser.add_argument('--title', type=str)
    parser.add_argument('--description', type=str)
    parser.add_argument('--all_day', type=bool, default=False)

    parser.add_argument('--is_sa', type=bool, default=False)

    args = parser.parse_args()
    return args

# Use service account
def get_credentials_sa():
    credentials, project = google.auth.default()
    return credentials

def get_credentials():
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                CLIENT_SECRET_FILE, SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    
    return creds

def create_service(is_sa = False):
    cred = None
    if (is_sa):
        creds = get_credentials_sa()
    else:
        creds = get_credentials()
    service = build('calendar', 'v3', credentials=creds)
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

def get_schedule(calendarId, start_time, end_time, all_day, is_sa=False):
    
    # if (args is None):
    #     args = ArgParser()

    # service = create_service(args)
    service = create_service(is_sa)
    
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

def add_schedule(calendarId, start_time, end_time, title, description,all_day, is_sa=False):

    service = create_service(is_sa)
    # service = create_service(args)

    
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

    schedules = get_schedule(calendarId, start_time, end_time, all_day, is_sa)
    is_summary_of_schedules = ['summary' in schedule for schedule in schedules]
    if (not any(is_summary_of_schedules)):
        print(f"schedules : {schedules}")
        service.events().insert(calendarId = calendarId, body=event).execute()
    # elif (event['summary'] != schedules[is_summary_of_schedules.index(True)]["summary"]):
    elif (event['summary'] not in [schedule['summary'] for schedule in schedules if 'summary' in schedule]):
        print("event title : {}".format(event['summary']))
        # print("schedule title : {}".format(schedules[is_summary_of_schedules.index()]["summary"]))
        service.events().insert(calendarId = calendarId, body=event).execute()
    else:
        print("Already exists schedule")

def main():
    args = ArgParser()
    if (args.end_time is None):
        args.end_time = args.start_time
    print(args.all_day)
    # add_schedule(calendarId, args.start_time, args.end_time, args.title, args.description, all_day = args.all_day, args = args)
    # print("get_schedule")
    schedule = get_schedule(calendarId, args.start_time, args.end_time, all_day = args.all_day)
    print(schedule)
if __name__=='__main__':
    main()
