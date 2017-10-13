import http.client
import json
import os
import subprocess

import redis


class FootballDataAPI():
	def __init__(self):
		self.connection = http.client.HTTPConnection('api.football-data.org')
		self.headers = {
			'X-Auth-Token': '8128fabfbba5438faf651bf3fd29f54a',
			'X-Response-Control': 'minified'
		}

		self.redis = redis.Redis(host="localhost", port=6379, db=0)

		# start redis server
		os.chdir("C:\Program Files\Redis")
		process = subprocess.Popen("redis-server.exe")
		
	def _current_matchday(self, competition_id):
		self.connection.request('GET',
			'/v1/competitions/{}/'.format(competition_id),
			None, self.headers)
		response = json.loads(self.connection.getresponse().read().decode())
		return response["currentMatchday"]

	def retrieve_matchday_fixtures(self, competition_id):
		self.connection.request('GET',
			'/v1/competitions/{}/fixtures?matchday={}'.format(
			competition_id,
			self._current_matchday(competition_id)
			),
			None, self.headers )
		response = json.loads(self.connection.getresponse().read().decode())
		return response

	def latest_competition_results(self, competition_id):
		self.connection.request('GET',
			'/v1/competitions/{}/fixtures?matchday={}'.format(
			competition_id,
			self._current_matchday(competition_id)-1
			),
			None, self.headers )
		response = json.loads(self.connection.getresponse().read().decode())
		return response

	def single_team_fixtures(self, club_id):
		self.connection.request('GET',
			'/v1/teams/{}/fixtures?timeFrame=n10'.format(club_id),
			None, self.headers )
		response = json.loads(self.connection.getresponse().read().decode())
		return response

	def get_club(self, competition_id):
		r = self.redis
		if not r.hexists("team_dict", 66):
			self.connection.request('GET',
				'/v1/competitions/{}/teams'.format(competition_id),
				None, self.headers )
			response = json.loads(
				self.connection.getresponse().read().decode())

			team_dict = dict()
			for team in response["teams"]:
				team_dict[team.get('id')] = team.get('crestUrl')

			r.hmset("team_dict", team_dict)
			return r.hgetall("team_dict")

		return r.hgetall("team_dict")


FootballDataAPI().get_club(445)