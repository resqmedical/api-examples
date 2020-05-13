#!./venv/bin/python

import argparse
import datetime
import json
import requests
import statistics
import xlsxwriter

from dateutil.relativedelta import relativedelta

url = 'https://api.resqmedical.com'

def CreateParser():
    parser = argparse.ArgumentParser(
    description='This script generates an XLSX spreadsheet which includes WorkTime statistics for a group of residents over a specified period of time.  By default the script will generate this data for the current month (start of month until today) and all residents.  Use command-line options and wildcards to changes this behavior.')
    parser.add_argument('--institution-id', dest='InstitutionId', help='The institution ID. Example: lomalinda)')
    parser.add_argument('--api-key', dest='ApiKey', help='The API key to be used to fetch the data.')
    parser.add_argument('--num-months', default=1, dest='NumMonths', help='Number of months to fetch data for.  A value of 1 will only retreive data for the current month.')
    parser.add_argument('--pgy', default='*', dest='Pgy', help='Specify specific PGY to generate data for.')
    parser.add_argument('--program', default='*', dest='Program', help='Specify specific Program to generate data for.')
    return parser

def GetActiveResidentList(InstId, ApiKey, ProgramFilter, PgyFilter):

    active_users = []

    credentials = {
        'api_key': ApiKey,
        'inst_id': InstId
    }

    request = {
        'credentials': credentials,
        'is_active': True,
        'type': 'Resident'
    }

    if PgyFilter != '*':
        request['pgy'] = int(PgyFilter)
    if ProgramFilter != '*':
        request['program'] = ProgramFilter

    response = requests.post(
        url + '/users/',
        json=json.dumps(request))
    if response.status_code == 200:
        active_users = response.json()

    return active_users

if __name__ == '__main__':

    parser = CreateParser()

    args = parser.parse_args()

    InstitutionId = None
    if args.InstitutionId != None:
        InstitutionId = args.InstitutionId
    else:
        InstitutionId = input('Input Institution ID (e.g., lomalinda) and Press Enter: ')

    ApiKey = None
    if args.ApiKey != None:
        ApiKey = args.ApiKey
    else:
        ApiKey = input('Input API Key and Press Enter: ')

    credentials = {
        'api_key': ApiKey,
        'inst_id': InstitutionId
    }

    request = {
        'credentials': credentials,
        'date_range': {
            'start_date': '',
            'end_date': ''
        },
        'user_id': 0
    }

    workbook = xlsxwriter.Workbook('worktime-stats.xlsx')

    print('Retrieving active users...')
    ResidentList = GetActiveResidentList(InstitutionId, ApiKey, args.Program, args.Pgy)

    EndDate = datetime.datetime.now()
    StartDate = EndDate - relativedelta(day=1, months=args.NumMonths, days=-1)

    # Prep a sheet for the current month.
    print('Preparing spreadsheets...')
    users_ws = workbook.add_worksheet('users')
    logs_ws = workbook.add_worksheet('logs')
    shifts_ws = workbook.add_worksheet('shifts')
    stats_ws = workbook.add_worksheet('stats')
    row = 0
    col = 0
    users_ws.write(row, col, 'UserID')
    logs_ws.write(row, col, 'UserID')
    shifts_ws.write(row, col, 'UserID')
    stats_ws.write(row, col, 'Statistic')
    col += 1
    users_ws.write(row, col, 'LastName')
    logs_ws.write(row, col, 'LogID')
    shifts_ws.write(row, col, 'Start (UTC)')
    stats_ws.write(row, col, 'Mean')
    col += 1
    users_ws.write(row, col, 'FirstName')
    logs_ws.write(row, col, 'Start (UTC)')
    shifts_ws.write(row, col, 'End (UTC)')
    stats_ws.write(row, col, 'Median')
    col += 1
    users_ws.write(row, col, 'Program')
    logs_ws.write(row, col, 'End (UTC)')
    shifts_ws.write(row, col, 'Log IDs')
    stats_ws.write(row, col, 'Maximum')
    col += 1
    users_ws.write(row, col, 'PGY')
    logs_ws.write(row, col, 'WorkZone')
    shifts_ws.write(row, col, 'Duration (Hours)')
    stats_ws.write(row, col, 'Standard Deviation')
    col += 1
    logs_ws.write(row, col, 'Duration (Hours)')
    col += 1

    users_row = row
    logs_row = row
    shifts_row = row
    stats_row = row

    shift_durations = []
    log_durations = []

    request['date_range']['start_date'] = StartDate.isoformat()
    request['date_range']['end_date'] = EndDate.isoformat()

    print('Retrieving and writing WorkTime data...')
    for resident in ResidentList:

        users_row += 1
        col = 0
        users_ws.write(users_row, col, resident['id'])
        col += 1
        users_ws.write(users_row, col, resident['last_name'])
        col += 1
        users_ws.write(users_row, col, resident['first_name'])
        col += 1
        users_ws.write(users_row, col, resident['program'])
        col += 1
        users_ws.write(users_row, col, resident['pgy'])
        col += 1

        request['user_id'] = resident['id']

        response = requests.post(
            url + '/worktime/',
            json=json.dumps(request))

        if response.status_code != 200:
            print(response.status_code)
            print(response.json()['message'])
        else:
            worktime_data = response.json()

            worktime_logs = worktime_data['logs']
            for log in worktime_logs:
                logs_row += 1

                try:
                    log_start = datetime.datetime.strptime(log['date_range']['start_date'], '%Y-%m-%dT%H:%M:%S.%f')
                except ValueError:
                    log_start = datetime.datetime.strptime(log['date_range']['start_date'], '%Y-%m-%dT%H:%M:%S')

                try:
                    log_end = datetime.datetime.strptime(log['date_range']['end_date'], '%Y-%m-%dT%H:%M:%S.%f')
                except ValueError:
                    log_end = datetime.datetime.strptime(log['date_range']['end_date'], '%Y-%m-%dT%H:%M:%S')

                duration = ((log_end - log_start).total_seconds() / 3600.0)
                log_durations.append(duration)

                workzone = log['workzone']

                col = 0
                logs_ws.write(logs_row, col, resident['id'])
                col += 1
                logs_ws.write(logs_row, col, log['log_id'])
                col += 1
                logs_ws.write(logs_row, col, log_start.isoformat())
                col += 1
                logs_ws.write(logs_row, col, log_end.isoformat())
                col += 1
                logs_ws.write(logs_row, col, workzone)
                col += 1
                logs_ws.write(logs_row, col, duration)
                col += 1

            worktime_shifts = worktime_data['shifts']
            for shift in worktime_shifts:
                shifts_row += 1

                try:
                    shift_start = datetime.datetime.strptime(shift['date_range']['start_date'], '%Y-%m-%dT%H:%M:%S.%f')
                except ValueError:
                    shift_start = datetime.datetime.strptime(shift['date_range']['start_date'], '%Y-%m-%dT%H:%M:%S')

                try:
                    shift_end = datetime.datetime.strptime(shift['date_range']['end_date'], '%Y-%m-%dT%H:%M:%S.%f')
                except ValueError:
                    shift_end = datetime.datetime.strptime(shift['date_range']['end_date'], '%Y-%m-%dT%H:%M:%S')

                duration = ((shift_end - shift_start).total_seconds() / 3600.0)
                shift_durations.append(duration)

                col = 0
                shifts_ws.write(shifts_row, col, resident['id'])
                col += 1
                shifts_ws.write(shifts_row, col, shift_start.isoformat())
                col += 1
                shifts_ws.write(shifts_row, col, shift_end.isoformat())
                col += 1
                shifts_ws.write(shifts_row, col, ','.join([str(i) for i in shift['log_ids']]))
                col += 1
                shifts_ws.write(shifts_row, col, duration)
                col += 1

    print('Computing and writing WorkTime statistics...')
    stats_row += 1
    col = 0
    stats_ws.write(stats_row, col, 'Log Duration')
    col += 1
    stats_ws.write(stats_row, col, statistics.mean(log_durations))
    col += 1
    stats_ws.write(stats_row, col, statistics.median(log_durations))
    col += 1
    stats_ws.write(stats_row, col, max(log_durations))
    col += 1
    stats_ws.write(stats_row, col, statistics.stdev(log_durations))
    col += 1
    stats_row += 1
    col = 0
    stats_ws.write(stats_row, col, 'Shift Duration')
    col += 1
    stats_ws.write(stats_row, col, statistics.mean(shift_durations))
    col += 1
    stats_ws.write(stats_row, col, statistics.median(shift_durations))
    col += 1
    stats_ws.write(stats_row, col, max(shift_durations))
    col += 1
    stats_ws.write(stats_row, col, statistics.stdev(shift_durations))
    col += 1

    workbook.close()
