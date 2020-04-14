#!./venv/bin/python

import datetime
import json
import requests

from dateutil.relativedelta import relativedelta

if __name__ == '__main__':

    credentials = {
        'api_key': 'FIXME',
        'inst_id': 'FIXME'
    }

    request = {
        'credentials': credentials,
        'date': datetime.datetime.utcnow().isoformat()
    }

    response = requests.post(
        'https://api.resqmedical.com/workforce/',
        json=json.dumps(request),
        verify=False)

    if response.status_code != 200:
        print(response.status_code)
        print(response.json()['message'])
    else:
        print('WorkForce Status (current)')
        response_data = response.json()
        if 'user_list' in response_data:
            for user in response_data['user_list']:
                if user['in_workzone']:
                    print('User {} is currently IN WorkZone {} (arrived {} hours ago)'.format(user['user_id'], user['workzone'], user['duration']))
                else:
                    print('User {} is OUT of all WorkZones (last seen at {} {} hours ago)'.format(user['user_id'], user['workzone'], user['duration']))
