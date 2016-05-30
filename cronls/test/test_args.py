# -*- coding: utf-8 -*-

import argparse
import datetime
import cronls.args

# ==================================================================== #

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

def calc_datetime(hours):
	"""
	Add to the current timestamp "hours" hours.

	:param hours: Hours to be added (or subtracted if negative)
	:return:
	"""
	return datetime.datetime.now() + datetime.timedelta(0, hours*3600)

# ==================================================================== #

class TestDatetimeParse:
	"""
	Specific test for the datetime input
	"""

	def test_now(self):
		assert cmp_datetimes( cronls.args.check_datetime('now'), calc_datetime(0) )

	def test_hours_1(self):
		assert cmp_datetimes( cronls.args.check_datetime('+1'), calc_datetime(+1) )

	def test_hours_2(self):
		assert cmp_datetimes( cronls.args.check_datetime('-1'), calc_datetime(-1) )


# ==================================================================== #

def parse_args(cmd):
	return cronls.args.parse_cmd_args(cmd.split())

# -------------------------------------------------------------------- #

class TestCommandLineArgs:
	"""
	Tests for command line input

	TODO:
		- Tests for system cron file
		- Tests for cron directory
	"""

	def test_defaults(self):
		args = parse_args("")
		assert cmp_datetimes(args.start_time, calc_datetime(0))
		assert cmp_datetimes(args.stop_time, calc_datetime(+24))
		assert args.all == False
		assert args.system_cron == True
		assert hasattr(args,'cron_dir')
		assert hasattr(args, 'sys_cron_file')
		assert args.max_hourly_repetitions == 4

	def test_times_1(self):
		args = parse_args("-24 +24")
		assert cmp_datetimes(args.start_time, calc_datetime(-24))
		assert cmp_datetimes(args.stop_time, calc_datetime(+24))

	def test_times_2(self):
		args = parse_args("16/04/10 16/05/10-10:10")
		assert cmp_datetimes(args.start_time, datetime.datetime(2016,4,10))
		assert cmp_datetimes(args.stop_time, datetime.datetime(2016,5,10,10,10))

	def test_times_3(self):
		args = parse_args("--all")


# ==================================================================== #

if __name__ == '__main__':
	args = cronls.args.parse_cmd_args("".split())
	print(args)