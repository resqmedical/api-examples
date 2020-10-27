import datetime
import json
import requests

from dateutil.relativedelta import relativedelta

if __name__ == '__main__':

    API_KEY = 'FIXME'
    INST_ID = 'FIXME'
    USER_ID = 0

    credentials = {
        'api_key': API_KEY,
        'inst_id': INST_ID
    }

    # Program analytics for the last month.
    Now = datetime.datetime.now()
    StartDate = Now + relativedelta(day=1)
    EndDate = Now + relativedelta(day=1, months=+1, days=-1)
    request = {
        'credentials': credentials,
        'user_id': USER_ID,
        'date_range': {
            'start_date': StartDate.isoformat(),
            'end_date': EndDate.isoformat()
        }
    }

    url = 'https://api.resqmedical.com'

    response = requests.post(
        url + '/analytics/user',
        json=json.dumps(request))

    print(response)

    if response.status_code == 200:
        analytics = response.json()
        print(analytics)
