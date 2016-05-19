#! /usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function

import sys
import subprocess
import datetime

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

def parsa_data(data):
	data,ora = data.split('_')
	argv = [int(data[:4]), int(data[4:6]), int(data[6:8]), 
	        int(ora[:2]), int(ora[2:4]), int(ora[4:6]) ]
	return datetime.datetime(*argv)

# -------------------------------------------------------------------- #

def get_user_crontab_files():
	status,output = subprocess.getstatusoutput('find /var/spool/cron/ -mindepth 1')
	if status != 0:
		print("Script eseguibile solo da root!")
		sys.exit(1)
	crontab_files = output.split('\n')
	return crontab_files

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

def read_file(file):
	f = open(file,'r')
	righe = f.readlines()
	f.close()
	return righe

# -------------------------------------------------------------------- #

def main(data_iniz,data_fin):
	c_files = get_user_crontab_files()
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
	
	if len(sys.argv) == 2 and sys.argv[1] in ('-h','--help'):
		print(USAGE)
		sys.exit(0)
	
	if len(sys.argv) != 3:
		print("Numero argomenti errato!")
		sys.exit(1)
	
	try:
		data_iniz = parsa_data(sys.argv[1])
	except:
		print("Formato data iniziale errato!")
		sys.exit(1)
	
	try:
		data_fin = parsa_data(sys.argv[2])
	except:
		print("Formato data finale errato!")
		sys.exit(1)
	
	if (data_fin-data_iniz).days < 0:
		print("Data iniziale maggiore di quella finale!")
	
	main(data_iniz,data_fin)

