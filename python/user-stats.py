import datetime
import json
import requests

from dateutil.relativedelta import relativedelta

if __name__ == '__main__':

    credentials = {
        'api_key': 'fixme',
        'inst_id': 'fixme'
    }

    request = {
        'credentials': credentials
    }

    response = requests.post(
        'https://api.resqmedical.com/users/',
        json=json.dumps(request))

    if response.status_code != 200:
        print(response.status_code)
        print(response.json()['message'])
    else:
        type_counts = dict()
        type_counts['active users'] = 0
        type_counts['residents'] = 0
        type_counts['attendings'] = 0
        type_counts['nurses'] = 0
        type_counts['student'] = 0
        type_counts['program admins'] = 0
        type_counts['gme admins'] = 0

        users = response.json()
        for user in users:
            if user['is_active'] is True:
                type_counts['active users'] += 1
            if user['type'] == 'Resident':
                type_counts['residents'] += 1
            if user['type'] == 'Attending':
                type_counts['attendings'] += 1
            if user['type'] == 'Nurse':
                type_counts['nurses'] += 1
            if user['type'] == 'Student':
                type_counts['student'] += 1
            if user['type'] == 'Program Admin':
                type_counts['program admins'] += 1
            if user['type'] == 'Institute Admin':
                type_counts['gme admins'] += 1

        for key, value in type_counts.items():
            print('{} {} ({}%)'.format(value, key, round(100*value/len(users))))
