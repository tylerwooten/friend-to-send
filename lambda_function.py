import json
import boto3
import os.path
import pandas as pd
import pygsheets

pinpoint = boto3.client('pinpoint')

def lambda_handler(event, context):
    ''' 

    EXAMPLES:
    DONE John Doe # update google docs with timestamp of last contact
    DONE John Doe . NOTES had a kid, loves spinach, birthday Feb 10th # update google docs with timestamp of last contact and notes
    ANOTHER # send another person
    SKIP # skip this person and send another
    '''
    message = json.loads(event['Records'][0]['Sns']['Message'])
    input_message_body = message['messageBody']
    
    keyword_options = ["ANOTHER", "SKIP", "DONE", "NOTES"] # keywords to create actions in lambda
    args = input_message_body.split('.')
    kwargs = {keyword:arg.replace(keyword,'').strip() for keyword in keyword_options for arg in args if keyword in arg}
    
    another = kwargs.get("ANOTHER")
    done = kwargs.get("SKIP")
    skip = kwargs.get("DONE")
    notes = kwargs.get("NOTES")
    
    output_message = 'no kwargs specified'
    
    if another or skip:
        output_message = get_random_friend()
    # if done:
    #     if notes:
    #         # update_sheet() #update sheet and notes section
    #.    else:
    #.        # update_sheet() #go update sheet
        
    send_message(output_message)

def get_all_friends_info():
    gc = pygsheets.authorize(service_file='auth.json')
    sheet = gc.open('skills')
    worksheet = sheet[1]

    all_friends_info = pd.DataFrame(worksheet.get_all_records(head=1))
    return all_friends_info
   
def get_random_friend():
    all_friends_info = get_all_friends_info()
    randomlySelected = all_friends_info.sample(n=1)
    friend = randomlySelected.to_dict(orient='records')[0]

    msg = "Your friend to reach out to today is: " + friend['First'] + ' ' + friend['Last'] + '.\n'
    
    # delete some info we don't want to send user
    del friend['First']
    del friend['Last']

    for attribute, value in friend.items():
        if value:
            msg += attribute + ': ' + value + '\n'
    return msg
    
def send_message(output_message):
    pinpoint.send_messages(
        ApplicationId='xxxxxxxxxxx',
        MessageRequest={
            'Addresses': {
                message['originationNumber']: {'ChannelType': 'SMS'}
            },
            'MessageConfiguration': {
                'SMSMessage': {
                    'Body': output_message,
                    'MessageType': 'PROMOTIONAL'
                }
            }
        }
    )

