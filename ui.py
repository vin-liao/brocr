from flask import Flask, render_template, jsonify, request
from ocr import img_to_txt
from api import insert_event

data = 'cmon bruh'
app = Flask(__name__)

@app.route('/')
def index():
	return render_template('index.html', text=data)

@app.route('/process', methods=['POST'])
def process():
	filename = request.form.get('filename')
	#call ocr function here
	data = img_to_txt(filename)
	data = jsonify(data)
	#returning jsonify object instead of pure dictionary
	return data

@app.route('/submit', methods=['POST'])
def submit():
	data_dict = dict()
	data_dict['event_name'] = request.form.get('event_name')
	data_dict['start_time'] = request.form.get('start_time')
	data_dict['end_time'] = request.form.get('end_time')
	data_dict['date'] = request.form.get('date')
	data_dict['location'] = request.form.get('location')
	data_dict['description'] = request.form.get('description')
	
	event_link = insert_event(data_dict)

	event_link = dict({'event_link': event_link})
	event_data = jsonify(event_link)
	return event_data

if __name__ == '__main__':
	app.run(debug=True)