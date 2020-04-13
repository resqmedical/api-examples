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

    # First, fetch all programs accessible with this API key.
    request = {
        'credentials': credentials
    }

    url = 'https://api.resqmedical.com'

    response = requests.post(
        url + '/programs/',
        json=json.dumps(request))

    if response.status_code == 200:
        programs = response.json()
        for program in programs:
            prog_id = program['id']
            prog_name = program['name']

            print('Admins for Program "' + prog_name + '" (Last, First, Email)')

            # Now fetch all users for this program.  By adding `prog_id` to the
            # request we receive more detailed information about that program.
            request['prog_id'] = prog_id

            response2 = requests.post(
                url + '/programs/',
                json=json.dumps(request))

            if response2.status_code == 200:
                program_detail = response2.json()[0]
                user_ids = program_detail['users']

                # Finally, fetch info for all users to figure out which are
                # program admins.
                NoAdmins = True
                for user_id in user_ids:
                    user_request = {
                        'credentials': credentials,
                        'user_id': user_id
                    }

                    response3 = requests.post(
                        url + '/users/',
                        json=json.dumps(user_request))

                    if response3.status_code == 200:
                        user = response3.json()[0]
                        if user['type'] == 'Program Admin':
                            NoAdmins = False
                            print('  {}, {}, {}'.format(user['last_name'], user['first_name'], user['email']))
                if NoAdmins:
                    print('  NONE')
                print('')
