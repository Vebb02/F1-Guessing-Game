from google.oauth2 import service_account
import gspread
from Utils import get_json_path

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