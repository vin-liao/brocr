from flask import Flask, render_template, jsonify, request
from ocr import img_to_txt
from api import insert_event

# data = img_to_txt()
# print('Creating a new event on Google Calendar')
# insert_event(data)

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


if __name__ == '__main__':
	app.run(debug=True)