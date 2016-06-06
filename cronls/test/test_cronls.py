# -*- coding: utf-8 -*-

import cronls.args
import cronls.cronls

class TestGetFiles:
	"""
	Tests for command line input

	TODO:
		- Tests for system cron file
		- Tests for cron directory

	Alas, this type of tests are not straighforward
	"""

	def test_1(self):
		input_args = cronls.args.parse_cmd_args(['--all'])
		l = cronls.cronls.get_crontab_files(input_args)
		# TODO...


if __name__ == '__main__':

	# Simple test for see if everything is ok

	import json

	input_args = cronls.args.parse_cmd_args(['--all'])
	l1 = cronls.cronls.get_crontab_files(input_args)
	#print(json.dumps(l1, indent=4))
	l2 = cronls.cronls.process_crontab(input_args)
	print(json.dumps(l2, indent=4))

	input_args = cronls.args.parse_cmd_args([])
	l1 = cronls.cronls.get_crontab_files(input_args)
	print(json.dumps(l1, indent=4))
