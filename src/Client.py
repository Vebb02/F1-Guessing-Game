import json
from google.oauth2 import service_account
import gspread

from Utils import get_json_path


data: dict[str, str] = None


def load_json():
	global data
	f = open(get_json_path() + "sheets.json")
	data = json.load(f)
	f.close()
	

def get_id(name: str) -> str:
	global data
	if data is None:
		load_json()
	return data[name]


def get_proxy_id() -> str:
	return get_id("proxy")


def get_guesses_id() -> str:
	return get_id("guesses")


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
