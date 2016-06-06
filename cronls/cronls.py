#! /usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function

import sys
import subprocess
import datetime
import time
import os
import getpass
import re

from . import args

SYS_USER = 'root[sys]'

DAYS_OF_WEEK = {'mon':1,'tue':2,'wed':3,'thu':4,'fri':5,'sat':6,'sun':7}
DAYS_OF_WEEK_ALIASES = {7:0}

MONTHS_OF_YEAR = {'jan':1,'feb':2,'mar':3,'apr':4,'may':5,'jun':6,'jul':7,'aug':8,'sep':9,'oct':10,'nov':11,'dec':12}

# ==================================================================== #

USAGE = """
analizzatore_crontab.py <aaaammgg_hhmmss> <aaaammgg_hhmmss>
	Analizza i crontab di tutti gli utenti (necessita dei privilegi
	di root) nel periodo fornito
"""

# ==================================================================== #

class CronParseError(Exception):
	pass

# ==================================================================== #

def print_error(*args, **kwargs):
	print(*args, file=sys.stderr, **kwargs)

# ==================================================================== #

def read_file(file):
	f = open(file,'r')
	rows = f.readlines()
	f.close()
	return rows

# -------------------------------------------------------------------- #

def parsa_data(data):
	# data,ora = data.split('_')
	# argv = [int(data[:4]), int(data[4:6]), int(data[6:8]),
	#         int(ora[:2]), int(ora[2:4]), int(ora[4:6]) ]
	# return datetime.datetime(*argv)
	return time.strptime(data,'%y/%m/%d-%H:%M')

# ==================================================================== #

def get_crontab_files(input_args):
	"""

	Args:
		input_args ():

	Returns:
		List of dictionaries containing user and file contents for each crontab.
		Dictionaries are in the following form:
		{
			'user': '<user>',
			'cron': [
				'<cron line 1>',
				'<cron line 2>',
				...
			]
		}

	Raises:
		NotImplementedError: If "crontab" command seems not installed on the system
		OSError: Any other error with "crontab" command

	"""

	outlist = []

	if input_args.all:

		# Reads all crontabs from crontabs path
		status, output = subprocess.getstatusoutput('find %s -mindepth 1 -type f' % input_args.cron_dir)

		for file in output.split('/n'):
			with open(file, 'r') as f:
				outlist += [{
					'user': os.path.basename(file),
					'rows': f.readlines()
				}]

		# Reads the system cron
		if input_args.system_cron:
			with open(input_args.sys_cron_file, 'r') as f:
				outlist += [{
					'user': SYS_USER,
					'rows': f.readlines()
				}]

	else:
		# Reads only the user cron
		status, output = subprocess.getstatusoutput('crontab -l')

		# If crontab is not set for the user, return an empty list
		if status == 1 and output.lower().startswith('crontab: no crontab for'):
			return []

		if status > 1 and output.find('crontab: not found') >= 0:
			raise NotImplementedError('Seems that command "crontab" is not installed on the system')

		if status > 1:
			raise OSError('"crontab -l" ended with error code "{status}" ({output})'.format(**vars()))

		outlist += [{
			'user': getpass.getuser(),
			'rows': output
		}]

	return outlist



# ==================================================================== #

# Converte un campo di una regola in una lista di numeri.
# Il crontab viene supposto esatto
# I range vengono espressi per esteso (i.e. 1-6 => [1,2,3,4,5,6]).
# Se e` presente una mappatura, le stringhe indicate vengono convertite
#  nel numero indicato.
# Se e` presente una conversione, i numeri indicati vengono convertiti nei
#  corrispettivi numeri indicati
# Non e` implementato l'operatore '/' (ad es '*/3')
# Non viene considerata la stramberia per cui il "dow" e il "dom" siano
#  espressi con un "or" anziche` un "and" come per tutti gli altri campi
def conv_campo_reg(campo,regola,map={},conv={}):
	#print vars()
	try :
		l = regola[campo].split(',')
		new_l = []
		for c in l:
			#print repr(c)
			if c.find('-') >= 0 :
				da,a = c.split('-')
				for i in range(int(da), int(a)+1):
					new_l += [i]
			else :
				if map.has_key(c):
					new_l += map[c]
				
				elif c == '*':
					new_l += [c]
				
				elif c.startswith('*/'):
					step = c[2:]
					assert step.isdigit(), Exception ('Atteso valore numerico (es "*/5"). %s' % vars())
					if campo == 'm':
						new_l += range(0,59,int(step))
					elif campo == 'h':
						new_l += range(0,23,int(step))
					else:
						raise Exception('Step non gestito per campo "%s". [%s]' % (campo,vars()))
					 
				elif not c.isdigit():
					raise Exception('asd')
				
				else :
					new_l += [c]
		final_l = []
		for c in new_l :
			if c == '*':
				final_l += [ '*' ]
			elif conv.has_key(c):
				final_l += [ int(conv[c]) ]
			else :
				final_l += [ int(c) ]
	except :
		raise Exception('Regola %s, campo "%s": formato non trattato!' % (regola,campo) )
	
	return final_l

# -------------------------------------------------------------------- #

def parse_and_remove_step(e):
	step = 1
	if '/' in e:
		if e.count('/') > 1:
			raise CronParseError('%(e)r: more than one "/" in the same field' % vars())
		e, step = e.split('/')

		try:
			step = int(step)
		except ValueError:
			raise CronParseError('%(e)r: %(step)r not numeric' % vars())

	return e, step

# -------------------------------------------------------------------- #

def expand_rule(val, field_type='', values_range=0, mapping={}, aliases={}):
	"""
	Expand a crontab field
	Args:
		val (str): field value to expand.

		field_type (str): field type between "m", "h", "dom", "mon", "dow".

		values_range (int): max possible value for this field. Only useful when there is a "*/x" rule.

		mapping (dict): dict that optionally map values that need to be converted in other values.
			The keys of the dict are the literal starting values (i.e. strings), the values are the final
			values (i.e. any data type).

			E.g: {'A': 1, 'B': 'b', ...}

		aliases (dict): after all processing, this dict map final values that should be converted in
			other values. This is only useful by far for converting 7 in 0 in days of week.

			E.g: {7: 0, 123: 1, ...}

	Returns:
	    list: List of expanded values

	Todo:
		- Handling a range of months in form "jan-apr" and a range of days of week in form "tue-fri"
	"""

	# Input parameters check
	assert values_range != 0

	# Expanding comma separated values (e.g. "1,3,5")
	l = val.split(',')

	# Expanding ranges and wildcards (doesn't touch other values)
	for e in list(l):
		e_orig = e

		if not e:
			raise CronParseError('%(val)r: Missed value before or after ","' % vars())

		# Expanding ranges (e.g. "10-20")
		if '-' in e:
			if e.count('-') > 1:
				raise CronParseError('%(val)r: more than one "-" in the same field' % vars())

			# Step parsing and removal (e.g. "10-20/2" becomes "10-20" step=2)
			e, step = parse_and_remove_step(e)

			# Indentify and check the range
			range_from,range_to = e.split('-')

			if range_from in mapping:
				range_from = mapping[range_from]
			if range_to in mapping:
				range_to = mapping[range_to]

			try:
				range_from = int(range_from)
				range_to = int(range_to)
			except ValueError:
				raise CronParseError('%(val)r: %(range_from)r or %(range_to)r not numeric' % vars())

			# Remove from list the old item and extend the same list with the computed range
			l.remove( e_orig )
			l.extend( range(range_from, range_to+1, step) )

		# Expanding wildcards (e.g. "*")
		if e.startswith('*'):

			# Step parsing and removal (e.g. "*/2" becomes "*" step=2)
			e, step = parse_and_remove_step(e)

			if e != '*':
				raise CronParseError('%(val)r: %(e)r should be only "*"' % vars())

			# Remove from list the old item and extend the same list with the computed range
			l.remove(e_orig)
			l.extend(range(0, values_range + 1, step))


	# Substitutions
	new_l = []

	for e in l:
		if e in mapping:
			e = mapping[e]

		e = int(e)
		
		if e in aliases:
			e = aliases[e]

		new_l.append( int(e) )

	return new_l


# -------------------------------------------------------------------- #

def analyze_cron_file(user, rows):
	
	# Remove trailing \n
	rows = [r.strip() for r in rows]

	# Filter empty lines
	rows = [r for r in rows if r]

	# Filter comment lines
	rows = [r for r in rows if r.find('#') != 0]

	# Filter variable definitions (e.g. "SHELL=...")
	rows = [r for r in rows if not re.match(r'\s*[A-Z_-]+=', r, re.IGNORECASE)]
	
	c_list = []
	for row in rows:
		try:
			c_fields = row.split(None, 5)
			d = {
				'user': user,
				'raw': row,

				'm': c_fields[0],
				'h': c_fields[1],
				'dom': c_fields[2],
				'mon': c_fields[3],
				'dow': c_fields[4],
				'cmd': c_fields[5],
			}
			d['m'] = conv_campo_reg('m',d,map={},conv={})
			d['h'] = conv_campo_reg('h',d,map={},conv={})
			d['dom'] = conv_campo_reg('dom',d,map=MONTHS_OF_YEAR,conv={})
			d['mon'] = conv_campo_reg('mon',d,map={},conv={})
			d['dow'] = conv_campo_reg('dow',d,map=DAYS_OF_WEEK, conv=DAYS_OF_WEEK_ALIASES)
			#print d
			c_list += [d]
		except Exception as e:
			#print tools_ascii.colorize('<red><b>Utente %(utente)s: Ignorata riga "%(riga)s" (%%s: %%s)</b></red>' % vars() % (e.__class__.__name__, e))
			print_error('Utente %(user)s: Ignorata riga "%(row)s" (%%s: %%s)' % vars() % (e.__class__.__name__, e))
	return c_list

# ==================================================================== #

def troppo_frequente(regola):
	if regola['m'][0] == '*' :
		return True
	if len(regola['m']) > MAX_MIN_FREQ :
		return True
	return False

# -------------------------------------------------------------------- #

def is_ok(campo,regola,valore_confronto):
	if regola[campo][0] == '*':
		return True
	
	ok = False
	for r in regola[campo] :
		if r == valore_confronto :
			ok = True
	return ok

# -------------------------------------------------------------------- #

def calcola_crontab(crontab_l,data_iniz,data_fin):
	un_minuto = datetime.timedelta(0,60)
	data_app = data_iniz + datetime.timedelta(0,0)
	
	while ( (data_fin - data_app).days >= 0 ):
		
		for regola in crontab_l :
			soddisfatta = True	
			soddisfatta = soddisfatta and is_ok('m',   regola, data_app.minute)
			soddisfatta = soddisfatta and is_ok('h',   regola, data_app.hour)
			soddisfatta = soddisfatta and is_ok('dom', regola, data_app.day)
			soddisfatta = soddisfatta and is_ok('mon', regola, data_app.month)
			soddisfatta = soddisfatta and is_ok('dow', regola, data_app.isoweekday())
			
			if soddisfatta and not troppo_frequente(regola):		
				print("%s :: %-7s :: %s" % (data_app,regola['user'],regola['raw']))
		
		data_app = data_app + un_minuto

# ==================================================================== #

def extend_sys_crontab(sys_l):
	sys_l_ext = []
	for regola in sys_l :
		dir = regola['cmd'].split('root run-parts ')[1]
		status,output = subprocess.getstatusoutput('find %s -mindepth 1' % dir)
		scripts = output.split('\n')
		for script in [ r for r in scripts if r ] :
			new_r = dict(regola)
			new_r['cmd'] = script
			new_r['raw'] += ' (%s)' % script
			sys_l_ext += [ new_r ]
	#for e in sys_l_ext: print e
	return sys_l_ext

# -------------------------------------------------------------------- #

def process_crontab(input_args):
	c_files = get_crontab_files(input_args)

	crontab_l = []

	for file in c_files:
		processed_cron = analyze_cron_file(**file, )

		if file['user'] == SYS_USER:
			# If crontab is the system one, we need to do some work
			crontab_l.extend(extend_sys_crontab(processed_cron))
		else:
			crontab_l.extend(processed_cron)

	# if input_args.system_cron :
	# 	sys_l = analyze_cron_file('sys', read_file('/etc/crontab')[4:])
	# 	sys_l_ext = extend_sys_crontab(sys_l)
	# 	crontab_l.extend( sys_l_ext )

	return crontab_l

# -------------------------------------------------------------------- #

def main(input_args):
	crontab_l = process_crontab(input_args)
	calcola_crontab(input_args, crontab_l)

# -------------------------------------------------------------------- #

if __name__ == '__main__':
	
	input_args = args.parse_cmd_args(sys.argv[1:])
	#main(input_args)

