from datetime import datetime
import iso8601
from dateutil import tz
from crest import Crest


from footyapi import FootballDataAPI


class HtmlHandler():
	def __init__(self):
		self.html_file = "Email_File.html"

	def time_converter(self, date_time):
		utc = iso8601.parse_date(date_time)
		local_time = utc.astimezone(tz.tzlocal())
		return local_time

	def extract_date(self, date_time):
		utc = iso8601.parse_date(date_time)
		return datetime.strftime(utc, "%d %b %y")

	def unique_dates(self, list_dict):
		date = {self.extract_date(i['date']) for i in list_dict['fixtures']}
		return sorted(date)

	def create_html_file(self, fixtures, team_fixtures, results):
		self.write_to_file("Epl latest results", results, mode="w")
		self.write_to_file("Man Utd's upcomings", team_fixtures, mode="a")
		self.write_to_file("Epl fixtures", fixtures, mode="a")

	def write_to_file(self, title, list_dict, mode):
		unique_dates = self.unique_dates(list_dict)
		
		with open(self.html_file, mode=mode) as outfile:
			outfile.write('''
				<html>
					<table cellpadding=5 style="min-width:40%">'''
			)
			outfile.write('''<tr><td align="center" colspan="3">
				<br><strong>\t {}</strong></td></tr>'''.format(title))
			
			for title_date in unique_dates:
				outfile.write('''<tr>
					<td align="center" colspan="3"
						style="background-color:#e0e0e0">
						{}
					</td>
					</tr>'''.format(title_date)
				)
				for data_dict in list_dict["fixtures"]:
					if title_date == self.extract_date(data_dict.get('date')):
						competition_id = data_dict.get('competitionId')
						home_crest, away_crest = Crest().team_crest(competition_id,
							data_dict.get('homeTeamId'),
							data_dict.get('awayTeamId'))
						
						match_time = datetime.strftime(
							self.time_converter(data_dict.get('date')),
							"%H:%M")
						halftime = data_dict.get('result').get('halfTime')
						
						if halftime is None:
							center_box = match_time, "", ""
						else:
							goals_ht = data_dict['result'].get('goalsHomeTeam')
							goals_at = data_dict['result'].get('goalsAwayTeam')
							center_box = goals_ht, " - ", goals_at

						outfile.write('''<tr>
							<td align="right">
							<span style="color:blue"><b>{0}</b></span>
							&nbsp;&nbsp;
							<img src="{2}" height="16" width="16">
							</td>
							<td style="background-color:#e0e0e0">
								<strong>
									<span style="color:black">{4}</span>
								</strong>
								{5}
								<strong>
									<span style="color:black">{6}</span>
								</strong>
							</td>
							<td align="left">
							<img src="{3}" height="16" width="16">
							&nbsp;&nbsp; <span style="color:blue"><b>{1}</b>
							</td>
							</tr>\n'''.format(
							data_dict.get('homeTeamName').replace(" FC", ""),
							data_dict.get('awayTeamName').replace(" FC", ""),
							home_crest,
							away_crest,
							*center_box
							)
						)
			outfile.write('</table></html>\n')

			return outfile

# pseudo test
if __name__ == '__main__':
	from footyapi import FootballDataAPI
	obj = FootballDataAPI()
	HtmlHandler().create_html_file(obj.retrieve_matchday_fixtures(445),
									obj.single_team_fixtures(66),
									obj.latest_competition_results(445)
									)


