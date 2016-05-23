import argparse
import datetime
import cronls.args

# -------------------------------------------------------------------- #

def cmp_datetimes(d1,d2):
	"""
	Compare two datetimes object ignoring microsecond differences

	:param d1:
	:param d2:
	:return:
	"""

	if abs(d1 - d2) < datetime.timedelta(0, 1):
		return True
	else:
		return False

# -------------------------------------------------------------------- #

class TestDatetimeParse:
	"""
	Tests for the datetime input
	"""

	def test_now(x):
		assert cmp_datetimes( cronls.args.check_datetime('now'), datetime.datetime.now() )

	def test_hours(x):
		assert cmp_datetimes( cronls.args.check_datetime('+1'), datetime.datetime.now()+datetime.timedelta(0,3600) )
