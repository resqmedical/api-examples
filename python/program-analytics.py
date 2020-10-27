import datetime
import json
import requests

from dateutil.relativedelta import relativedelta

if __name__ == '__main__':

    credentials = {
        'api_key': 'FIXME',
        'inst_id': 'FIXME'
    }

    # Program analytics for the last month.
    Now = datetime.datetime.now()
    StartDate = Now + relativedelta(day=1, months=-1)
    EndDate = Now + relativedelta(day=1, months=+1, days=-1)
    request = {
        'credentials': credentials,
        'user_id': 9772,
        'date_range': {
            'start_date': '2020-08-02T17:17:54.679Z',
            'end_date': '2020-09-01T17:17:54.679Z'
        }
    }

    url = 'https://api.resqmedical.com'

    response = requests.post(
        url + '/worktime',
        json=json.dumps(request))

    print(response)

    if response.status_code == 200:
        analytics = response.json()
        print(analytics)
