# -*- coding: utf-8 -*-

"""Module containing command line parser definition."""

import os
import argparse
import datetime

# ==================================================================== #

def check_datetime(value):
	"""
	Check and convert "value" to a datetime object. Value can have multiple formats,
	according to the argparse.ArgumentParser doc (defined in :func:`parse_cmd_args`)

	Args:
		value (str): The input value

	Returns:
		datetime.datetime: the input value converted to a datetime object

	Raises:
		argparse.ArgumentTypeError
	"""

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
	"""
	Check if "value" is a valid directory (it must exists and the user must have
	list privileges).

	Args:
		value (str): The input value

	Returns:
		str: the same input value if all is correct

	Raises:
		argparse.ArgumentTypeError
	"""

	if not os.path.exists(value):
		raise argparse.ArgumentTypeError('%s: Invalid path' % value)
	if not os.path.isdir(value):
		raise argparse.ArgumentTypeError('%s: Not a directory' % value)

	try:
		os.listdir(value)
	except IOError as e:
		raise argparse.ArgumentTypeError('%s: %s' % (value,e.strerror))

	return value

# -------------------------------------------------------------------- #

def check_file(value):
	"""
	Check if "value" is a valid file (it must exists and the user must have
	read privileges).

	Args:
		value (str): The input value

	Returns:
		str: the same input value if all is correct

	Raises:
		argparse.ArgumentTypeError
	"""

	if not os.path.exists(value):
		raise argparse.ArgumentTypeError('%s: Invalid path' % value)
	if not os.path.isfile(value):
		raise argparse.ArgumentTypeError('%s: Not a file' % value)

	try:
		open(value, 'r')
	except OSError as e:
		raise argparse.ArgumentTypeError('%s: %s' % (value, e.strerror))

	return value


# ==================================================================== #

def parse_cmd_args(argv):
	"""
	Parse the given arguments.

	Args:
		argv (list): List of command line arguments (strings)

	Returns:
		argparse.ArgumentParser: The final parser object (which attributes are the
			input arguments)

	Raises:
		argparse.ArgumentTypeError
	"""

	# -------------------------------------- #
	# Parser definition

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
		'-a', '--all',
		dest="all",
		action='store_true',
		default=False,
		help='Search for all users and system crons instead for the current user only'
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
		type=str,
		default='/var/spool/cron',
		help='Directory where cronls looks for cron files'
	)

	parser.add_argument(
		'--sys-cron-file',
		dest="sys_cron_file",
		action='store',
		type=None,
		default='/etc/crontab',
		help='File that cronls scans for system crons'
	)
	# -------------------------------------- #

	# -------------------------------------- #
	# Arguments list parsing

	args = parser.parse_args(argv)
	# -------------------------------------- #

	# -------------------------------------- #
	# Post parsing checks

	if args.start_time >= args.stop_time:
		argparse.ArgumentTypeError('Start time (%s) is higher then stop time (%s)' % (args.start_time, args.stop_time))

	if args.all:
		check_dir(args.cron_dir)

		if args.system_cron:
			check_file(args.system_cron)
	# -------------------------------------- #

	return args

# ==================================================================== #

if __name__ == '__main__':
	#args = parse_cmd_args("+2 -s -r 10 -d /var --sys-cron-file /etc/hosts --all".split())
	args = parse_cmd_args("+2 -s -r 10".split())
	#args = parse_cmd_args("--all".split())

	print(args)