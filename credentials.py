#! /usr/bin/env python

from __future__ import print_function
import os
import json
import socket
import uuid
import hashlib

import yaml
import cherrypy
import requests

import alsaaudio

try:
	from urllib.parse import quote
except ImportError:
	from urllib import quote

import alexapi.config


class Start(object):

	def index(self):
		sd = json.dumps({
			"alexa:all": {
				"productID": config['alexa']['Device_Type_ID'],
				"productInstanceAttributes": {
					"deviceSerialNumber": hashlib.sha256(str(uuid.getnode()).encode()).hexdigest()
				}
			}
		})

		url = "https://www.amazon.com/ap/oa"
		callback = cherrypy.url().replace("http:", "https:") + "code"
		payload = {
			"client_id": config['alexa']['Client_ID'],
			"scope": "alexa:all",
			"scope_data": sd,
			"response_type": "code",
			"redirect_uri": callback
		}
		req = requests.Request('GET', url, params=payload)
		prepared_req = req.prepare()
		raise cherrypy.HTTPRedirect(prepared_req.url)

	def code(self, var=None, **params):		# pylint: disable=unused-argument
		code = quote(cherrypy.request.params['code'])
		callback = cherrypy.url().replace("http:", "https:")
		payload = {
			"client_id": config['alexa']['Client_ID'],
			"client_secret": config['alexa']['Client_Secret'],
			"code": code,
			"grant_type": "authorization_code",
			"redirect_uri": callback
		}
		url = "https://api.amazon.com/auth/o2/token"
		response = requests.post(url, data=payload)
		resp = response.json()

		alexapi.config.set_variable(['alexa', 'refresh_token'], resp['refresh_token'])

		return (
			"<h2>Success!</h2><h3> Refresh token has been added to your "
			"config file, you may now reboot the Pi </h3><br>{}"
		).format(resp['refresh_token'])

	index.exposed = True
	code.exposed = True

cherrypy.config.update({'server.socket_host': '0.0.0.0'})
cherrypy.config.update({'server.socket_port': int(os.environ.get('PORT', '5050'))})
cherrypy.config.update({"environment": "embedded"})

credentials = ['Client_ID', 'Client_Secret', 'Device_Type_ID', 'Security_Profile_Description', 'Security_Profile_ID']

for cred in credentials:
    alexapi.config.set_variable(['alexa', cred], os.environ.get(cred))

# Configure input_device
input_devices = alsaaudio.pcms(alsaaudio.PCM_CAPTURE)
alexapi.config.set_variable(['sound', 'input_device'], input_devices[len(input_devices) - 1])

with open(alexapi.config.filename, 'r') as stream:
	config = yaml.load(stream)

# need to login to Amazon
if not config['alexa']['refresh_token']:
    public_url = os.environ.get('RESIN_DEVICE_UUID') + '.resindevice.io'
    print("Go to https://{} to begin the auth process".format(public_url))
    cherrypy.quickstart(Start())
