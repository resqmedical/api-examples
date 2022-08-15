import datetime
import json
import requests

from dateutil.relativedelta import relativedelta

if __name__ == '__main__':

    API_KEY = 'fixme'
    INST_ID = 'fixme'
    USER_ID = 9800

    credentials = {
        'api_key': API_KEY,
        'inst_id': INST_ID
    }

    # WorkTime logs for the last month.
    Now = datetime.datetime.now()
    StartDate = Now + relativedelta(day=1)
    EndDate = Now + relativedelta(day=1, months=+1, days=-1)
    request = {
        'credentials': credentials,
        'user_id': USER_ID,
        'date_range': {
            'start_date': StartDate.isoformat() + 'Z',
            'end_date': EndDate.isoformat() + 'Z'
        }
    }

    url = 'https://api.resqmedical.com'

    response = requests.post(
        url + '/worktime',
        json=json.dumps(request))

    if response.status_code == 200:
        worktime_data = response.json()
        print(worktime_data)
