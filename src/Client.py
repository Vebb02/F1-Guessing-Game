import json
from google.oauth2 import service_account
import gspread

from Utils import get_json_path

class Client:
	data: dict[str, str] = None

	def load_json():
		f = open(get_json_path() + "sheets.json")
		Client.data = json.load(f)
		f.close()
	

	def get_id(name: str) -> str:
		if Client.data is None:
			Client.load_json()
		return Client.data[name]


	def get_proxy_id() -> str:
		return Client.get_id("proxy")


	def get_guesses_id() -> str:
		return Client.get_id("guesses")


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
