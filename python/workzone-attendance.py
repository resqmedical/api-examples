import argparse
import datetime
import json
import requests
import xlsxwriter

from dateutil.relativedelta import relativedelta

url = 'https://api.resqmedical.com'

def CreateParser():
    parser = argparse.ArgumentParser(
    description='This script generates XLSX spreadsheets with WorkZone attendance details.  Each .xlsx document includes data for a single workzone and each sheet in the document includes data for one month.  By default the script will generate this data only for the current month.  Use command-line options to changes this behavior.')
    parser.add_argument('workzone', type=str, help='Name of the WorkZone.')
    parser.add_argument('--institution-id', dest='InstitutionId', help='The institution ID. Example: llu)')
    parser.add_argument('--api-key', dest='ApiKey', help='The API key to be used to fetch the data.')
    parser.add_argument('--num-months', default=1, dest='NumMonths', help='Number of months to fetch data for.  A value of 1 will only retreive data for the current month.')
    return parser

def GetActiveResidentList(InstId, ApiKey):

    active_users = []

    credentials = {
        'api_key': ApiKey,
        'inst_id': InstId
    }

    user_request = {
        'credentials': credentials,
        'active_only': True,
        'type': 'Resident'
    }

    response = requests.post(
        url + '/users/',
        json=json.dumps(user_request))

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

    workbook = xlsxwriter.Workbook('workzone-attendance.xlsx')

    ResidentList = GetActiveResidentList(InstitutionId, ApiKey)

    Now = datetime.datetime.now()

    month_count = 1
    while month_count < int(args.NumMonths)+1:

        DatePoint = Now - relativedelta(months=month_count)

        print('Generating sheet for month ' + DatePoint.strftime('%Y-%b'))

        StartDate = DatePoint + relativedelta(day=1)
        EndDate = DatePoint + relativedelta(day=1, months=+1, days=-1)

        # Prep a sheet for the current month.
        worksheet = workbook.add_worksheet(DatePoint.strftime('%Y-%b'))
        row = 0
        col = 0
        worksheet.write(row, col, 'LastName')
        col += 1
        worksheet.write(row, col, 'FirstName')
        col += 1
        worksheet.write(row, col, 'Program')
        col += 1
        worksheet.write(row, col, 'PGY')
        col += 1

        CurrentDate = StartDate
        while CurrentDate.strftime('%b') == DatePoint.strftime('%b'):
            worksheet.write(row, col, CurrentDate.strftime('%b-%d'))
            col += 1
            CurrentDate = CurrentDate + relativedelta(days=1)

        request['date_range']['start_date'] = StartDate.strftime('%Y-%m-%dT%H:%M:%S.%fZ')
        request['date_range']['end_date'] = EndDate.strftime('%Y-%m-%dT%H:%M:%S.%fZ')

        for resident in ResidentList:
            row = row + 1
            col = 0

            worksheet.write(row, col, resident['last_name'])
            col += 1
            worksheet.write(row, col, resident['first_name'])
            col += 1
            worksheet.write(row, col, resident['program'])
            col += 1
            worksheet.write(row, col, resident['pgy'])
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

                worktime_totals_by_day = dict()
                for worktime_log in worktime_logs:
                    if worktime_log['workzone'] == args.workzone:
                        try:
                            log_start = datetime.datetime.strptime(worktime_log['date_range']['start_date'], '%Y-%m-%dT%H:%M:%S.%f')
                        except ValueError:
                            log_start = datetime.datetime.strptime(worktime_log['date_range']['start_date'], '%Y-%m-%dT%H:%M:%S')

                        try:
                            log_end = datetime.datetime.strptime(worktime_log['date_range']['end_date'], '%Y-%m-%dT%H:%M:%S.%f')
                        except ValueError:
                            log_end = datetime.datetime.strptime(worktime_log['date_range']['end_date'], '%Y-%m-%dT%H:%M:%S')

                        log_start_day = log_start.strftime('%b-%d')
                        log_end_day = log_end.strftime('%b-%d')

                        if log_start_day == log_end_day:
                            duration = ((log_end - log_start).total_seconds() / 3600.0)
                            if log_start_day in worktime_totals_by_day:
                                worktime_totals_by_day[log_start_day] += round(duration, 1)
                            else:
                                worktime_totals_by_day[log_start_day] = round(duration, 1)
                        else:
                            log_midnight = datetime.datetime(log_end.year, log_end.month, log_end.day, 0, 0, 0)
                            duration_1 = ((log_midnight - log_start).total_seconds() / 3600.0)
                            duration_2 = ((log_end - log_midnight).total_seconds() / 3600.0)
                            if log_start_day in worktime_totals_by_day:
                                worktime_totals_by_day[log_start_day] += round(duration_1, 1)
                            else:
                                worktime_totals_by_day[log_start_day] = round(duration_1, 1)
                            if log_end_day in worktime_totals_by_day:
                                worktime_totals_by_day[log_start_day] += round(duration_2, 1)
                            else:
                                worktime_totals_by_day[log_start_day] = round(duration_2, 1)

                CurrentDate = StartDate
                while CurrentDate.strftime('%b') == DatePoint.strftime('%b'):
                    total_hours = 0
                    if CurrentDate.strftime('%b-%d') in worktime_totals_by_day:
                        total_hours = worktime_totals_by_day[CurrentDate.strftime('%b-%d')]
                    worksheet.write(row, col, total_hours)
                    col += 1
                    CurrentDate = CurrentDate + relativedelta(days=1)

        month_count += 1
        print('Month {}'.format(month_count))

    workbook.close()
