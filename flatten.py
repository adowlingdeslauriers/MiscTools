from types import NoneType


def flatten(obj):
	"""	Move all nested values to the top level of an opbject, annotating the source in the key. Intended for dumping complex objects to csv
	eg.  flatten({"a": {"b": {"c": 1, "d": 2}, "e": {"f": 3, "g": 4}}})    ->    {'a.b.c': 1, 'a.b.d': 2, 'a.e.f': 3, 'a.e.g': 4}
	"""
	return _flatten(obj)


def _flatten(obj, parents=None, out=None):
	"""	Recursively travel down object, keeping history of path, and write to out when a non-array element is found
	param obj: object to be flattened
	param parents: list of keys travelled so far
	param out: flattened object
	"""
	if parents == None:
		parents = []
	if out == None:
		out = {}

	if isinstance(obj, (NoneType, bool, int, float, str)):
		key = ".".join(parents)
		out[key] = obj

	elif isinstance(obj, dict):
		for key in obj.keys():
			val = obj[key]
			prefixes = parents[:]
			prefixes.append(str(key))
			out = _flatten(val, prefixes, out)

	elif isinstance(obj, list):
		prefixes = parents[:]
		#prefixes.append(str(obj))
		for val in obj:
			out = _flatten(val, prefixes, out)

	else:
		raise ValueError(f"Unable to flatten object: {obj}")
		# TODO grab object vars() and iterate? Implement as flag?

	return out


if __name__ == "__main__":
	indict = {"a": {"b": {"c": 1, "d": 2}, "e": {"f": 3, "g": 4}}}
	outdict = {'a.b.c': 1, 'a.b.d': 2, 'a.e.f': 3, 'a.e.g': 4}
	assert(flatten(indict) == outdict)
