import os

file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "./cache.txt")
try:
	with open(file_path, "r") as f:
		text = f.read()
		print(text)
except FileNotFoundError:
	...
with open(file_path, "a") as f:
	f.write("Hello, World!")