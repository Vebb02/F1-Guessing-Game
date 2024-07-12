import json
from google.oauth2 import service_account
import gspread

from Utils import get_json_path

class Client:
	def __init__(self):
		self.client = Client.get_client()
		self.data: dict[str, str] = None


	def load_json(self):
		f = open(get_json_path() + "sheets.json")
		self.data = json.load(f)
		f.close()
	

	def get_id(self, name: str) -> str:
		if self.data is None:
			self.load_json()
		return self.data[name]


	def get_proxy_id(self) -> str:
		return self.get_id("proxy")


	def get_proxy_sheet(self):
		proxy_id = self.get_proxy_id()
		return self.client.open_by_key(proxy_id)


	def get_guesses_id(self) -> str:
		return self.get_id("guesses")


	def get_guesses_sheet(self):
		guesses_id = self.get_guesses_id()
		return self.client.open_by_key(guesses_id)


	def get_client():
		credentials: service_account.Credentials = (
			service_account.Credentials.from_service_account_file(
				get_json_path() + "credentials.json",
				scopes=[
					"https://www.googleapis.com/auth/spreadsheets",
					"https://www.googleapis.com/auth/spreadsheets.readonly",
				],
			)
		)

		return gspread.authorize(credentials)
