#! /usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function

import sys
import subprocess
import datetime
import time
import os
import getpass

from . import args

# Analizza anche i crontab di sistema
SYS_CRONTAB = True

# Massima frequenza in un'ora sopra la quale viene inibita la visualizzazione
MAX_MIN_FREQ = 3

# ==================================================================== #

USAGE = """
analizzatore_crontab.py <aaaammgg_hhmmss> <aaaammgg_hhmmss>
	Analizza i crontab di tutti gli utenti (necessita dei privilegi
	di root) nel periodo fornito
"""

# ==================================================================== #

def eprint(*args, **kwargs):
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

# -------------------------------------------------------------------- #

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
					'user': 'root[sys]',
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

def analyze_cron_file(utente,righe):
	
	# Rimozione \n finali
	righe = [r.strip() for r in righe]
	# Rimozione righe vuote
	righe = [ r for r in righe if r ]
	# Rimozione righe di commenti
	righe = [ r for r in righe if r.find('#') != 0 ]
	#print righe
	#print
	
	lista = []
	for riga in righe:
		try:
			d = {'user':utente, 'raw':riga}
			d['m'],d['h'],d['dom'],d['mon'],d['dow'],d['cmd'] = riga.split(None,5)
			d['m'] = conv_campo_reg('m',d,map={},conv={})
			d['h'] = conv_campo_reg('h',d,map={},conv={})
			d['dom'] = conv_campo_reg('dom',d,map={'jan':1,'feb':2,'mar':3,'apr':4,'may':5,'jun':6,'jul':7,'aug':8,'sep':9,'oct':10,'nov':11,'dec':12},conv={})
			d['mon'] = conv_campo_reg('mon',d,map={},conv={})
			d['dow'] = conv_campo_reg('dow',d,map={'mon':1,'tue':2,'wed':3,'thu':4,'fri':5,'sat':6,'sun':7}, conv={'0':7})
			#print d
			lista += [d]
		except Exception as e:
			#print tools_ascii.colorize('<red><b>Utente %(utente)s: Ignorata riga "%(riga)s" (%%s: %%s)</b></red>' % vars() % (e.__class__.__name__, e))
			eprint('Utente %(utente)s: Ignorata riga "%(riga)s" (%%s: %%s)' % vars() % (e.__class__.__name__, e))
	return lista

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

def main(input_args):
	c_files = get_crontab_files(input_args)
	crontab_l = []
	for file in c_files :
		user_l = analyze_cron_file(utente=file.split('/')[-1], righe=read_file(file))
		crontab_l.extend(user_l)
	
	if SYS_CRONTAB :
		sys_l = analyze_cron_file('sys',read_file('/etc/crontab')[4:])
		sys_l_ext = extend_sys_crontab(sys_l)
		crontab_l.extend( sys_l_ext )
	
	calcola_crontab(crontab_l,data_iniz,data_fin)

# -------------------------------------------------------------------- #

if __name__ == '__main__':
	
	input_args = args.parse_cmd_args(sys.argv[1:])
	#main(input_args)

