import datetime
import json
import requests

from dateutil.relativedelta import relativedelta

if __name__ == '__main__':

    API_KEY = 'FIXME'
    INST_ID = 0
    PROG_ID = 0

    credentials = {
        'api_key': API_KEY,
        'inst_id': INST_ID
    }

    request = {
        'credentials': credentials,
        'prog_id': PROG_ID,
        'date_range': {
            'start_date': '2020-09-01T21:12:21.709Z',
            'end_date': '2020-09-06T00:00:00.000Z'
        }
    }

    url = 'https://api.resqmedical.com'

    # Program WorkTime Stats
    response = requests.post(
        url + '/analytics/program/stats',
        json=json.dumps(request),
        verify=False)
    if response.status_code != 200:
        print(response.status_code)
        print(response.json()['message'])
    else:
        print('WorkTime Stats')
        print(response.json())

    # Program Active Users
    response = requests.post(
        url + '/analytics/program/active_users',
        json=json.dumps(request),
        verify=False)
    if response.status_code != 200:
        print(response.status_code)
        print(response.json()['message'])
    else:
        print('Active Users')
        print(response.json())

    # Program WorkForce History
    response = requests.post(
        url + '/analytics/program/workforce_history',
        json=json.dumps(request),
        verify=False)
    if response.status_code != 200:
        print(response.status_code)
        print(response.json()['message'])
    else:
        print('Active Users')
        print(response.json())
