from flask import Flask
from flask import request
from flask import redirect
from flask import session, escape
from flask import render_template
from flask import url_for
from datetime import timedelta
import requests
import os
import heapq

app = Flask(__name__)
app.secret_key = os.environ['KEY']


@app.before_request
def before_request():
    session.permanent = True
    app.permanent_session_lifetime = timedelta(minutes=5)

@app.route('/')
def index():
    if 'username' in session:
    	return render_template('index.html') 
    else:
    	return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        return login()
    else:
        return login_form()

@app.route('/logout', methods=['GET', 'POST'])
def logout():
 	session.clear()
 	return render_template('loggedOut.html')

@app.route('/searchOrgData', methods=['GET'])
def search_org_data():
	 	org = request.args.get('org')
	 	topNumber = request.args.get('topNum')
	 	url = "https://api.github.com/orgs/"+org+"/repos"
	 	returnData = {}
 		req = requests.get(url, headers={'Authorization': 'token %s' %  escape(session['token'])})
 		if req.status_code == 200:
 			searchData = req.json()
 			topNumber =  len(searchData) if topNumber == "" else int(topNumber)
 			returnData["TopForks"] = topRepos(searchData,"forks_count", topNumber)
 			returnData["TopStars"] = topRepos(searchData, "stargazers_count", topNumber)
 			returnData["TopContributors"] = topReposContributors(searchData, topNumber)
 			return render_template('topTables.html', returnData = returnData) 
 		else:
 			return "Failed to grab data for github make sure you provided a token."

def login():
 	session['username'] = request.form['uname']
 	session['token'] = request.form['token']
 	return redirect(url_for('index'))

def login_form():
 	return render_template('login.html')

def topRepos(searchData, queryType, topNumber):
	heap = []
	returnData = []
	count = 0
	for x in searchData:
		heapq.heappush(heap, (-int(x[queryType]),x["full_name"]))
	while heap and count < topNumber:
		data = heapq.heappop(heap)
		returnData.append((data[1],-data[0]))
		count += 1
	return returnData

def topReposContributors(searchData, topNumber):
	heap = []
	returnData = []
	count = 0
	for x in searchData:
		req = requests.get(x["contributors_url"],headers={'Authorization': 'token %s' %  escape(session['token'])})
		if req.status_code == 200:
			heapq.heappush(heap, (-len(req.json()),x["full_name"]))
	while heap and count < topNumber:
		data = heapq.heappop(heap)
		returnData.append((data[1],-data[0]))
		count += 1
	return returnData