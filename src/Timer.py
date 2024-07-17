import time

class Timer:
	def __init__(self):
		self.stamp()

	
	def get_time_since(prev_time: float) -> float:
		return time.perf_counter() - prev_time


	def get_delta_time(self) -> float:
		delta = Timer.get_time_since(self.time_stamp)
		return delta


	def print_delta_time(self, message: str):
		Timer.print_taken_time(message, self.get_delta_time())
		self.stamp()


	def print_taken_time(message: str, taken_time: float):
		message_limit = 35
		if (length := len(message)) > message_limit:
			raise Exception(f"Message can't be longer than {message_limit}. Was {length}.") 
		print(f"{message: <{message_limit}} {taken_time:>{6}.3f}")

	
	def stamp(self):
		self.time_stamp = time.perf_counter()
