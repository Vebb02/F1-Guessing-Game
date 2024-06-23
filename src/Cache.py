from io import TextIOWrapper
from Utils import get_main_path
import os

CACHE_PATH = get_main_path() + "cache/"
CACHE_FILE_END = "_cache.txt"

def init_cache():
	if not os.path.exists(CACHE_PATH):
	    os.makedirs(CACHE_PATH)


def get_cache_path(file: str) -> str:
	return CACHE_PATH + file + CACHE_FILE_END


def cache(data: list[list[list[str]]], file: str):
	path = get_cache_path(file)
	with open(path, "a", encoding="UTF-8") as f:
		for row in data:
			f.write(",".join(row) + "\n")
		f.write("\n")


def get_from_cache(file: str) -> list[list[list[str]]]:
	path = get_cache_path(file)
	try:
		with open(path, "r", encoding="UTF-8") as f:
			return read_cache_file(f)
	except FileNotFoundError:
		return []


def read_cache_file(f: TextIOWrapper) -> list[list[str]]:
	data = []
	rows = f.readlines()
	entry = []
	for row in rows:
		if row == "\n":
			if len(entry) != 0:
				data.append(entry)
				entry = []
		else:
			row = row[:-1]
			entry.append(row.split(","))
	return data