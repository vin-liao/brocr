from PIL import Image
import cv2
import pytesseract
import re

def extract(text):
	data = {
		'event_name': 'unknown',
		'start_time': None, 
		'end_time': None, 
		'date': 'yyyy-mm-dd',
		'location': 'Binus Anggrek Campus',
		'description': ''
	}

	month_dict = {
		'january': '01',
		'february': '02',
		'march': '03',
		'april': '04',
		'may': '05',
		'june': '06',
		'july': '07',
		'august': '08',
		'september': '09',
		'october': '10',
		'november': '11',
		'december': '12'
	}


	'''
	============================================================
	event name
	search at the first half of the text, or even the first quarter
	usually the event name is capital, use isalpha until isalpha=false
	'''
	limit = int(len(text)/2)
	not_all_text = text[:limit]
	title_text = ''

	title = re.findall('[A-Z]+\s', not_all_text)
	for word in title:
		title_text += word

	title_text = re.sub('\n', ' ', title_text)
	data['event_name'] = title_text

	text = text.lower()
	month_list = [(['januari', 'jan'], 'january'),
				  (['febuari', 'feb'], 'february'),
				  (['maret', 'mar'], 'march'),
				  (['apr'], 'april'),
				  (['mei'], 'may'),
				  (['juni'], 'june'),
				  (['juli'], 'july'),
				  (['agustus', 'aug', 'agt'], 'august'),
				  (['september', 'sept', 'sep'], 'september'),
				  (['oktober', 'okt', 'oct'], 'october'),
				  (['nov'], 'november'),
				  (['desember', 'des', 'dec'], 'december')]
	
	for month, english in month_list:
		for name in month:
			text = re.sub(name + ' ', english + ' ', text)

	#soem possibilities
	#month dd yy
	#dd mm yy
	#dd month yy(yy)?
	#dd/mm/yy
	#dd month 'yy
	#dd month
	#dd mm (use current year)

	#not \d{2} but [x-y][a-b]
	#re [[0-1]?[0-9]month]?[0-3]?[0-9][ /][[0-1]?[0-9]month]?[ /]\d{2}(\d{2})?
	date_text = ''
	month_text = ''
	year_text = ''
	for k, v in month_dict.items():


		'''
		this regex match the following pattern
		month dd yy(yy)?
		dd month yy(yy)?
		dd mm yy(yy)?
		dd/mm/yy(yy)?

		TODO
		add pattern without year, and set it to this year automatically
		'''
		find_date = re.findall('(?:[0-3]?[0-9]\D?\D?[ /](?:[0-1]?[0-9]|{})|{}[ /][0-3]?[0-9]\D?\D?)[ /][12]?[09]?[0-9][0-9]'.format(k, k), text)
		if len(find_date) > 0 and find_date[0] is not '':
			date = find_date[0]
			#find month
			#find if there is any alphabet in date (month)
			for i, c in enumerate(date):
				if c.isalpha():
					month_text += c

			#if month is digit
			if len(month_text) == 0:
				for i, c in enumerate(date):
					if c == ' ' or c == '/':
						month_text += date[i+1]

						if date[i+2] == ' ' or date[i+2] == '/': #03 7 2013
							month_text = '0' + month_text
							break
						else: #03 07 2013
							month_text += date[i+2]
							break
			#if month is alphabet
			else:
				raw_month_text = month_text
				month_text = month_dict.get(month_text)
				if month_text == None:
					#first character is random e.g. 13t september 2017
					month_text = raw_month_text[1:]
					month_text = month_dict.get(month_text)
					if month_text == None:
						#the first two character is random e.g. 1st march 1990
						month_text = raw_month_text[2:]
						month_text = month_dict.get(month_text)

			#find year
			if date[-3] == ' ' or date[-3] == '/': # xx year format
				year_text = '20' + date[-2:]
			elif date[-5] == ' ' or date[-5] == '/': # xxxx year format
				year_text = date[-4:]

			#find date
			if date[0].isdigit() and date[1].isdigit() == False: #7 april
				date_text = '0' + date[0]
			elif date[:2].isdigit(): #13 april
				date_text = date[:2]
			else: #november 5 18
				for i, c in enumerate(date):
					if c.isdigit():
						date_text += c
						if date[i+1].isdigit() == False:
							break
			break

	if len(date_text) > 0 and len(month_text) > 0: #successfully detect date
		data['date'] = year_text + '-' + month_text + '-' + date_text
	else:
		data['date'] = None

	'''
	============================================================
	time
	start time = \s+(:|.)\s+
	end time = second occurence of start time

	\s *(pm|am)
	'''
	#time
	# match = re.search('\s+(:|.)\s+', text)
	# if match:
	#     result = match.group()
	#     print('RESULT: ', result)

	find_time = re.findall('(?:\d{2}[:\.]\d{2}|[01]?\d(?:[\.:]00)? ?(?:am|pm))', text)
	#find time result = hh?:mm or hh? ?(am|pm)
	start_time_text = ''
	end_time_text = ''
	if len(find_time) > 0:
		for i, time in enumerate(find_time):
			if i == 0:
				start_time_text = time
			elif i == 1:
				end_time_text = time
	else:
		data['start_time'] = None
		data['end_time'] = None

	#if there is only one time
	if len(start_time_text) > 0 and len(end_time_text) == 0:
		if start_time_text[:2] == '11' and start_time_text[-2:].isalpha():
			pass
			end_time_text = start_time_text
			end_time_text[:2] = ''

		elif start_time_text[:2] == '12' and start_time_text[-2:].isalpha():
			pass
		else:
			time = int(start_time_text[:2])
			end_time_text = str(time+2) + start_time_text[2:]

	#if find time is not empty
	if len(find_time) > 0:
		#replaceing "." with ":" for formatting
		start_time_text = re.sub('\.', ':', start_time_text)
		end_time_text = re.sub('\.', ':', end_time_text)
		time_list = [start_time_text, end_time_text]
		for i, time_text in enumerate(time_list):
			#hh (am|pm) format
			if time_text[-2:].isalpha(): 
				if time_text[:2].isdigit():
					time = int(time_text[:2])
					if time_text[-2] == 'p':
						time += 12
					time_list[i] = str(time) + ':00:00'
				elif time_text[0].isdigit() and time_text[1].isdigit() == False: #e.g. 8 pm
					time = int(time_text[0])
					if time_text[-2] == 'p':
						time += 12
					time_list[i] = str(time) + ':00:00'

			#hh:mm format
			else: 
				if time_text[:2].isdigit():
					time_list[i] = time_text + ':00'
				elif time_text[0].isdigit() and time_text[1].isdigit() == False:
					time_list[i] = '0' + time_text + ':00'	
		data['start_time'] = time_list[0]
		data['end_time'] = time_list[1]


	# try:
	# 	for i in hh:
	# 		if hh[i][-2:] == 'pm':
	# 			if hh[i][:2].isdigit():
	# 				hour = int(hh[i][:2])
	# 				hour += 12
	# 				hour = str(hour)
	# 			if hh[i][:2].isdigit() == False and hh[i][0].isdigit():
	# 				hour = int(hh[i][0])
	# 				hour += 12
	# 				hour = str(hour)

	# 		elif hh[i][-2:] == 'am':
	# 			if hh[i][:2].isdigit():
	# 				hour = hh[0][:2]
	# 			if hh[i][:2].isdigit() == False and hh[i][0].isdigit():
	# 				hour = '0'+hh[i][0]

	# 		if len(hh) == 1:
	# 				data['start_time'] = hour + ':00'
	# 				end = int(hour) + 2
	# 				data['end_time'] = end + ':00'
	# 		elif len(hh) >= 2:
	# 			if i == 0:
	# 				data['start_time'] = hour + ':00'
	# 			elif i == 1:
	# 				data['end_time'] = hour + ':00'

				# if hh[0][0] == '0' and hh[0][:2].isdigit(): #09 am
				# 	data['start_time'] = h[:2] + ':00'
				# elif hh[0][:2].isdigit(): # 12 pm
				# 	data['start_time'] = h[:2] + ':00'
				# elif hh[0][:2].isdigit() == False and hh[0][0].isdigit(): #7pm
				# 	data['start_time'] = '0' + h[0] + ':00'

		# data['start_time'] = hour + ':00'

		# data['end_time'] = hh[1]


	'''
	============================================================
	date
	
	month date year
	date-date month year
	dd/mm/yyyy

	'''

	'''
	============================================================
	place

	detect anggrek campus [aula, audit, R.\d{3}]
	detect syahdan campus [A-Z][1-3][A-Z] #K1D or soemthing
	'''
	audit = re.findall('(audit|auditorium|400)', text)
	aula = re.findall('(aula|800)', text) 
	exhibition = re.findall('(exhibition ?(hall)?)', text)
	anggrek_room = re.findall('[r]?\.?[1-8][0-2][0-9] ', text)
	syahdan_room = re.findall('[j-m][1-3][a-f]', text)
	alam_sutra = re.findall('alam ?(?:sutra|sutera)', text)
	if len(audit) > 0:
		data['location'] = 'Auditorium Room 400 Anggrek Campus'
	elif len(aula) > 0:
		data['location'] = 'Aula Room 800 Anggrek Campus'
	elif len(exhibition) > 0:
		data['location'] = 'Exhibition Hall Lt.3 Anggrek Campus'
	elif len(anggrek_room) > 0:
		data['location'] = 'Anggrek Campus Room {}'.format(anggrek_room[0])
	elif len(syahdan_room) > 0:
		data['location'] = 'Syahdan Campus Room {}'.format(syahdan_room[0])
	elif len(alam_sutra) > 0:
		data['location'] = 'Binus Alam Sutra Campus'
	else:
		pass

	#additional information
	price = re.findall('(?:rp[ \.]?\d+[\.,]\d{3,}?|\d+ ?k)', text)
	if len(price) > 0:
		data['description'] += 'Price ' + price[0] + ' '
	
	phone = re.findall('08\d{8,}', text)
	if len(phone) > 0:
		data['description'] += 'Contact Person ' + phone[0] + ' '

	return data