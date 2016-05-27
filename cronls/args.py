# -*- coding: utf-8 -*-

import os
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

	raise argparse.ArgumentTypeError(
		'"%s": not a valid format (admitted: "now", "[+|-]hh" (e.g. "+24" or "-4") or "yy/mm/dd[-HH:MM]")' % value)

# -------------------------------------------------------------------- #

def check_dir(value):
	if not os.path.exists(value):
		raise argparse.ArgumentTypeError('%s: Invalid path' % value)
	if not os.path.isdir(value):
		raise argparse.ArgumentTypeError('%s: Not a directory' % value)

	try:
		os.listdir(value)
	except OSError as e:
		raise argparse.ArgumentTypeError('%s: %s' % (value,e.strerror))

	return value

# -------------------------------------------------------------------- #

def check_file(value):
	pass

# -------------------------------------------------------------------- #

def parse_cmd_args(argv):
	parser = argparse.ArgumentParser(
		description='',
		epilog='',
	)

	parser.add_argument(
		'start_time',
		type=check_datetime,
		nargs='?',
		default='now',
		help='Start date or datetime. Admitted formats: "now", "[+|-]hh" (e.g. "+24" or "-4") or "yy/mm/dd[-HH:MM]"'
	)

	parser.add_argument(
		'stop_time',
		type=check_datetime,
		nargs='?',
		default='+24',
		help='Stop date or datetime. Admitted formats: "now", "[+|-]hh" (e.g. "+24" or "-4") or "yy/mm/dd[-HH:MM]"'
	)

	parser.add_argument(
		'-s', '--no-system-cron',
		dest="system_cron",
		action='store_false',
		default=True,
		help='Do not include system crons'
	)

	parser.add_argument(
		'-r', '--max-hourly-repetitions',
		dest="max_hourly_repetitions",
		action='store',
		type=int,
		default=4,
		help='Do not show jobs that execute more than X times per hour (noise reduction, default 4)'
	)

	parser.add_argument(
		'-d', '--cron-dir',
		dest="cron_dir",
		action='store',
		type=check_dir,
		default='/var/spool/cron',
		help='Directory where cronls looks for cron files'
	)

	args = parser.parse_args(argv)

	if args.start_time >= args.stop_time:
		argparse.ArgumentTypeError('Start time (%s) is higher then stop time (%s)' % (args.start_time, args.stop_time))

	return args

# -------------------------------------------------------------------- #

if __name__ == '__main__':
	args = parse_cmd_args("+2 -s -r 10 -d /var".split())
	print(args)