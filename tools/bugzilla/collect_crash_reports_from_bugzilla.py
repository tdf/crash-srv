# -*- Mode: python; tab-width: 4; indent-tabs-mode: nil; c-basic-offset: 4 -*- */
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
#

import bugzilla
import json
import configparser
import requests
import sys
import datetime

URL = "https://bugs.documentfoundation.org"

def set_bug_to_report(session, signature, bug):
    url = "https://crashreport.libreoffice.org/management/add-bug"

    data = {'signature': signature, 'bug_nr': bug}
    r = session.post(url, data = data)
    if r.status_code != 200:
        print("Error while setting tdf#%d to %s" % (bug, signature))

def main():

    login_url = "https://crashreport.libreoffice.org/accounts/login/"

    config = configparser.ConfigParser()
    config.read(sys.argv[1])

    bzapi = bugzilla.Bugzilla(URL)

    yesterday = datetime.date.today() - datetime.timedelta(days=60)
    bz_query_url = "https://bugs.documentfoundation.org/buglist.cgi?f1=cf_crashreport&f3=OP&f4=cf_crashreport&f5=creation_ts&j3=OR&list_id=620362&o1=isnotempty&o4=changedafter&o5=changedafter&product=LibreOffice&query_format=advanced&v4=%s&v5=%s" % (yesterday.isoformat(), yesterday.isoformat())
    query = bzapi.url_to_query(bz_query_url)

    bugs = bzapi.query(query)

    if len(bugs) == 0:
        sys.exit()

    user = config["CrashReport"]["User"]
    password = config["CrashReport"]["Password"]
    session = requests.session()
    t = session.get(login_url)
    print(t.content)
    print(session)
    print(session.cookies.values())
    csrftoken = session.cookies['csrftoken']

    login_data = { 'username': user,'password': password,
            'csrfmiddlewaretoken': csrftoken }
    r1 = session.post(login_url, data=login_data, headers={"Referer": login_url})

    for bug in bugs:

        bug_id = bug.id
        crash_report_entry = bug.cf_crashreport
        if crash_report_entry.strip().startswith("["):
            try:
                crash_reports = json.loads(bug.cf_crashreport)
                for crash_report in crash_reports:
                    set_bug_to_report(session, crash_report, bug_id)
            except Exception as e:
                print("exception setting bug report")
                print(bug_id)
                print(e)
        else:
            print(bug_id)
            print(crash_report_entry)


if __name__ == "__main__":
    main()

# vim:set shiftwidth=4 softtabstop=4 expandtab: */
