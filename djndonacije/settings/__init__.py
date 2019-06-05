try:
	from .prod import *
except:
	from .dev import *