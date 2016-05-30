# -*- coding: utf-8 -*-

import cronls.args
import cronls.cronls

class TestGetFiles:
	"""
	Tests for command line input

	TODO:
		- Tests for system cron file
		- Tests for cron directory
	"""

	def test_1(self):
		input_args = cronls.args.parse_cmd_args(['--all'])
		l = cronls.cronls.get_crontab_files(input_args)


if __name__ == '__main__':
	import json
	input_args = cronls.args.parse_cmd_args(['--all'])
	l = cronls.cronls.get_crontab_files(input_args)
	print(json.dumps(l, indent=4))

	input_args = cronls.args.parse_cmd_args([])
	l = cronls.cronls.get_crontab_files(input_args)
	print(json.dumps(l, indent=4))
