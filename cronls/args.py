# -*- coding: utf-8 -*-

import argparse
import datetime

# -------------------------------------------------------------------- #

def check_datetime(value):
	# Case "now"
	if value == 'now':
		return datetime.datetime.now()

	# Case "+hh" and "-hh"
	if value.startswith('+') or value.startswith('-'):
		if not value[1:].isdigit():
			raise argparse.ArgumentTypeError('"%s": format admitted "[+|-]nn" (e.g +24)' % value)
		hours = int(value)
		return datetime.datetime.now() + datetime.timedelta(0, hours * 3600)

	# Case "%y/%m/%d-%H:%M"
	try:
		return datetime.datetime.strptime(value, '%y/%m/%d-%H:%M')
	except ValueError:
		pass

	# Case "%y/%m/%d"
	try:
		return datetime.datetime.strptime(value, '%y/%m/%d')
	except ValueError:
		pass

	raise argparse.ArgumentTypeError('"%s": not a valid format (admitted: "now", "[+|-]hh" (e.g. "+24" or "-4") or "yy/mm/dd[-HH:MM]")' % value)

# -------------------------------------------------------------------- #

def parse_cmd_args():
	parser = argparse.ArgumentParser(
		description='',
		epilog='',
	)

	parser.add_argument(
		'start_time',
		dest='start_time',
		type=str,
		required=False,
		default='now',
		help='Start date or datetime. Admitted formats: "now", "[+|-]hh" (e.g. "+24" or "-4") or "yy/mm/dd[-HH:MM]"'
	)

	parser.add_argument(
		'stop_time',
		dest='stop_time',
		type=str,
		required=False,
		default='now',
		help='Start date or datetime. Admitted formats: "now", "[+|-]hh" (e.g. "+24" or "-4") or "yy/mm/dd[-HH:MM]"'
	)

	args = parser.parse_args()

	return args

# -------------------------------------------------------------------- #