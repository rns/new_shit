#optimalization: what if we replaced it with an empty object?
class dotdict(object):
	def __init__(s):
		object.__setattr__(s, "_dict", dict())
	def __setattr__ (s, k, v):
		s._dict[k] = v
	def __setitem__(s, k, v):
		s._dict[k] = v
	def __getattr__ (s, k):
		return s._dict[k]
	def __getitem__ (s, k):
		return s._dict[k]
		
	


