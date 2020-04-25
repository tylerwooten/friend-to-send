from __future__ import print_function
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import pandas as pd
from twilio.rest import Client
from secret import Secret

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']

# The ID and range of a sample spreadsheet.
SAMPLE_SPREADSHEET_ID = Secret.SAMPLE_SPREADSHEET_ID
SAMPLE_RANGE_NAME = Secret.SAMPLE_RANGE_NAME

def main():
    """Shows basic usage of the Sheets API.
    Prints values from a sample spreadsheet.
    """
    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'client_secret.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    service = build('sheets', 'v4', credentials=creds)

    # Call the Sheets API
    sheet = service.spreadsheets()
    result = sheet.values().get(spreadsheetId=SAMPLE_SPREADSHEET_ID,
                                range=SAMPLE_RANGE_NAME).execute()
    values = result.get('values', [])
    df = pd.DataFrame.from_records(values)
    df.columns = df.iloc[0]
    df = df.reindex(df.index.drop(0)).reset_index(drop=True)
    df.columns.name = None

    randomlySelected = df.sample(n=1)
    # print(randomlySelected)
    person = randomlySelected.to_dict(orient='records')[0]

    del person['Know (1-5)']
    del person['Badass Level (1-5)']
    del person['Keep Up With(months)']
    # Download the helper library from https://www.twilio.com/docs/python/install

    msg = "Your person to reach out to today is: " + person['First'] + ' ' + person['Last'] + '.\n'
    del person['First']
    del person['Last']

    for k, v in person.items():
        if v:
            msg += k + ': ' + v + '\n'

    # Your Account Sid and Auth Token from twilio.com/console
    # DANGER! This is insecure. See http://twil.io/secure
    account_sid = Secret.account_sid
    auth_token = Secret.auth_token
    client = Client(account_sid, auth_token)

    message = client.messages \
        .create(
        body= msg,
        from_=Secret.send_from_number,
        to=Secret.send_to_number
    )

    print(message.sid)
    #TODO: Be able to reply to my bot either "ANOTHER", "SKIP", "DONE". If I skip, get a new one. If I say done, go update my "reached out to" column in spreadsheets
    # can say another after I have said done
    #TODO: bot sends most recent twitter/facebook updates
    #TODO: bot sends phone number of person so I can click it easily

if __name__ == '__main__':
    main()