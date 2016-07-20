import os
from flask import Flask, render_template, request, url_for, redirect
import json
import urllib
import urllib2
import urlparse
import base64

app = Flask(__name__)

@app.route('/')
def index():
	url_for('static', filename='img/filters.png')
	url_for('static', filename='img/GitHub_Logo.png')
	url_for('static', filename='img/Octocat.png')
	return render_template('cohorts.html')


@app.route('/cohorts', methods=['POST', 'GET'])
def parse_data():
	if request.method == "GET":
		return redirect(url_for('index'))
	params = request.args
	Cohort_Name, Token = urllib.unquote_plus(params['cohort']), params['token']
	userData = (json.loads(request.form.get('users')))

	#Usage tracking. Please remove if rehosting.
	urllib2.urlopen("http://api.mixpanel.com/track/?data=eyJldmVudCI6ICJDb2hvcnQgU2NyaXB0IFJ1biIsICJwcm9wZXJ0aWVzIjogeyJ0b2tlbiI6ICJkaWdnc3Rva2VuIn19")

	updateTemplate = {
		"token": Token,
		"$union": {"Cohorts": [Cohort_Name]},
		"$ignore_time": True,
		"$ip": 0
	}

	mpURL = "http://api.mixpanel.com/engage/?verbose=1"
	batch = []

	totalUsers = len(userData)
	# print "Webhook received. %d total users." % totalUsers
	for user in userData:
		update = updateTemplate.copy()
		update["$distinct_id"] = user["$distinct_id"]
		batch.append(update)
		if len(batch):
			req = urllib2.Request(mpURL,'data='+base64.b64encode(json.dumps(batch)))
			response = urllib2.urlopen(req)
			batch = []

	req = urllib2.Request(mpURL,'data='+base64.b64encode(json.dumps(batch)))
	response = urllib2.urlopen(req)

	return '200 OK'

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)