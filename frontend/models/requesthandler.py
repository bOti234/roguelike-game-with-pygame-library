from concurrent.futures import ThreadPoolExecutor
import threading
from ..utils.database import fetch_scoreboard

# This class is for sending requests periodically and without freezing the game using threading
class Requesthandler():
	def __init__(self) -> None:
		self.fetched_data = None
		self.data_lock: threading.Lock = threading.Lock()
		self.request_executor: ThreadPoolExecutor = ThreadPoolExecutor(max_workers = 5)

	# Function to make a GET request
	def fetch_data(self):
		response = fetch_scoreboard()
		return response

	# Function to handle the result of the GET request
	def handle_response(self, future):
		try:
			data = future.result()
			with self.data_lock:
				self.fetched_data = data
		except Exception as e:
			print("Error fetching data:", e)

	# Function to make an asynchronous request
	def make_async_request(self):	# This is the function that gets called inside some of Game classes functions
		future = self.request_executor.submit(self.fetch_data)	# the executor submits the request call as a thread
		future.add_done_callback(self.handle_response)	# After it gets the response, it sets the fetched_data attribute to the fetched_data