from apiclient.discovery import build
from httplib2 import Http
from oauth2client import file, client, tools
import datetime

def insert_event(data):
	all_day = False
	if data.get('date') == None:
		#set date to tomorrow
		data['date'] = datetime.date.today() + datetime.timedelta(days=1)

	if data.get('start_time') == None and data.get('end_time') == None:
		#set all day
		data['start_time'] = '00:00'
		data['end_time'] = '00:00'
		all_day = True

	SCOPES = 'https://www.googleapis.com/auth/calendar'
	store = file.Storage('./authentication/credentials.json')
	creds = store.get()
	if not creds or creds.invalid:
	    flow = client.flow_from_clientsecrets('./authentication/client_secret.json', SCOPES)
	    creds = tools.run_flow(flow, store)
	service = build('calendar', 'v3', http=creds.authorize(Http()))

	event = {
	  'summary': '{}'.format(data.get('event_name')),
	  'location': '{}'.format(data.get('location')),
	  'description': '{}'.format(data.get('description')),
	  'start': {
	    'dateTime': '{}T{}+07:00'.format(data.get('date'), data.get('start_time')),
	    'timeZone': 'Asia/Jakarta',
	  }
	}
	
	if all_day:
		data['date'] = datetime.datetime.strptime(data.get('date'), '%Y-%m-%d') + datetime.timedelta(days=1)
		data['date'] = str(data.get('date'))[:11]

	event['end'] = {
	    'dateTime': '{}T{}+07:00'.format(data.get('date'), data.get('end_time')),
	    'timeZone': 'Asia/Jakarta',
	}

	# Call the Calendar API
	event = service.events().insert(calendarId='primary', body=event).execute()
	print('Event created: %s' % (event.get('htmlLink')))
	return event.get('htmlLink')