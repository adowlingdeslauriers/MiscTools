class FileCache:
	"""A QnD caching system for expensive function calls.
	On first call, records function name, args, and result and stores on disc.
	Repeated calls to the same function/args pair will return the on-disc result.
	Delete file (or entry in history.json) to force cache refresh.

	Only string-ifiable function arguments are stored/used for comparision (eg str, int, float).
	Function call results are assumed to be JSON or decompilable to JSON.

	param dir_name: name of directory it makes to store results. Local to current working directory

	Usage:
	my_cache = FileCache(dir_name="my_cache")
	then add @cached decorator to functions you wish to cache

	eg.
	@cached
	def my_expensive_api_call(self, customer_name: str, order_id: int) -> JSONObject:
		pass

	Return result would be saved to "/[dir_name]/my_expensive_api_call(customer_name, order_id).json".
	Delete file (or entry in history.json) to force cache refresh.
	"""
	def __init__(self, dir_name="file_cache"):
		self.working_dir = os.path.join(os.getcwd(), dir_name)
		self.history_fp = os.path.join(self.working_dir, "history.json")
		self.history = self.load_history() # dict of (call_pattern: filepath) pairs. Lookup index for calls

	def load_history(self):
		if not os.path.isdir(self.working_dir):
			os.mkdir(self.working_dir)
		
		if not os.path.isfile(self.history_fp):
			with open(self.history_fp, "w") as file:
				file.write("{}")
				return {}

		with open(self.history_fp, "r") as file:
			return json.load(file)

	def update_history(self, call_pattern, fp):
		entry = {call_pattern: fp}
		self.history.update(entry)
		with open(self.history_fp, "w") as file:
			json.dump(self.history, file)

	def cache_hit(self, fp):
		with open(fp, "r") as file:
			return json.load(file)

	def cache_miss(self, call_pattern, func, *args, **kwargs):
		result = func(*args, **kwargs)
		fn = call_pattern + ".json"
		fp = os.path.join(self.working_dir, fn)
		with open(fp, "w") as file:
			json.dump(result, file)
		self.update_history(call_pattern, fp)
		return result

	def make_call_pattern(self, func, *args, **kwargs) -> str:
		"""Returns a string-ified version of the function and its arguments.
		Purpose is to provide a key to index function calls, while also being human-readable.
		Only stringifies string-like arguments (str, int, float).

		eg. call pattern for 
		my_expensive_call(1234, foo="bar")
		is the string
		'my_expensive_call(1234, foo="bar")'
		"""
		func_name = func.__name__
		out = ""
		if args:
			out += ", ".join([arg for arg in args if type(arg) in [str, int, float]])
		if kwargs:
			out += ", "
			out += ", ".join([f"{k}={v}" for k, v in kwargs.items()])
		call_pattern = f"{func_name}({out})"

		return call_pattern

	def cached(self, func):
		"""Records function name, args, and result.
		If function is called with same args, returns cached result.
		Delete on-disc file to clear cache entry and force cache refresh.
		"""
		def inner(*args, **kwargs):
			call_pattern = self.make_call_pattern(func, *args, **kwargs)
			if call_pattern in self.history:
				fp = self.history[call_pattern]
				if os.path.isfile(fp): # Allows one to delete file and re-run to refresh that cache
					return self.cache_hit(fp)
			return self.cache_miss(call_pattern, func, *args, **kwargs)

		return inner