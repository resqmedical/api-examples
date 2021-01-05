import datetime
import json
import requests
import xlsxwriter

import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

from dateutil.relativedelta import relativedelta

if __name__ == '__main__':

    API_KEY = 'FIXME'
    INST_ID = 'FIXME'
    PROG = 'FIXME'

    credentials = {
        'api_key': API_KEY,
        'inst_id': INST_ID
    }

    Now = datetime.datetime.now()
    EndDate = Now + relativedelta(day=31)
    StartDate = Now + relativedelta(day=1, months=-3)

    date_range = {
        'start_date': StartDate.isoformat() + 'Z',
        'end_date': EndDate.isoformat() + 'Z'
    }

    url = 'https://api.resqmedical.com'

    workbook = xlsxwriter.Workbook('program-weekly-hours-by-pgy.xlsx')
    worksheet = workbook.add_worksheet(PROG)
    header_written = False

    row = 1        
    for pgy in range(1, 6):
        response = requests.post(
            url + '/users',
            json=json.dumps({
                'credentials': credentials,
                'active_only': True,
                'program': PROG,
                'pgy': pgy,
                'type': 'Resident'
            }),
            verify=False)
        if response.status_code != 200:
            print(response.status_code)
            print(response.json()['message'])
        else:
            users = response.json()
            for user in users:
                worksheet.write(row, 0, user['last_name'])
                worksheet.write(row, 1, user['first_name'])
                worksheet.write(row, 2, user['pgy'])

                response = requests.post(
                    url + '/worktime',
                    json=json.dumps({
                        'credentials': credentials,
                        'user_id': user['id'],
                        'date_range': date_range
                    }),
                    verify=False)

                if response.status_code == 200:
                    weeks = response.json()['weeks']

                    if not header_written:
                        worksheet.write(0, 0, 'LastName')
                        worksheet.write(0, 1, 'FirstName')
                        worksheet.write(0, 2, 'PGY')
                        col = 3
                        for week in weeks:
                            worksheet.write(0, col, week['week_id'])
                            col += 1
                        header_written = True

                    col = 3
                    for week in weeks:
                        worksheet.write(row, col, week['total_hours'])
                        col += 1

                row += 1

    workbook.close()