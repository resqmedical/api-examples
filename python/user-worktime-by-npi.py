import datetime
import json
import requests

from dateutil.relativedelta import relativedelta

if __name__ == '__main__':

    API_KEY = 'FIXME'
    INST_ID = 'FIXME'
    NPI = 'FIXME'

    credentials = {
        'api_key': API_KEY,
        'inst_id': INST_ID
    }

    url = 'https://api.resqmedical.com'

    response = requests.post(
        url + '/users/',
        json=json.dumps({
            'credentials': credentials,
            'npi': NPI
        }),
        verify=False)

    if response.status_code == 200:
        users = response.json()
        if len(users) > 0:
            user_id = users[0]['id']

            # WorkTime logs for the last 7 days.
            Now = datetime.datetime.now()
            StartDate = Now + relativedelta(days=-7)
            EndDate = Now
            request = {
                'credentials': credentials,
                'user_id': user_id,
                'date_range': {
                    'start_date': StartDate.isoformat() + 'Z',
                    'end_date': EndDate.isoformat() + 'Z'
                }
            }

            response = requests.post(
                url + '/worktime',
                json=json.dumps(request))

            if response.status_code == 200:
                worktime_data = response.json()
                print(worktime_data)
