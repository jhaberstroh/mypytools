#!/usr/bin/env python
import shlex
import numpy as np
import argparse
import cPickle
import matplotlib.pyplot as plt

parser = argparse.ArgumentParser(description='Average over many .xvg energy trajectory files to get the average E(t) and S(t).')
parser.add_argument('--files', dest='file_list', nargs='+', type=str, help='A collection of all of the files to be averaged over')
parser.add_argument('-n', dest='total_time', type=int, default=0, help='The total number of time steps to average over. Overwritten by the number of time steps in the first file opened if this is smaller.')
parser.add_argument('-pkl', dest='pickle_name', type=str, default='', help='The name of the pickle file to send the output into.')

args = parser.parse_args()
istimelimit = 0;
if (args.total_time != 0):
	istimelimit = 1

e_t = list()
time = list()
e_t_sq = list()

file_count = 0;
for fname in args.file_list:
	print 'NEW FILE: ' + fname
	n = 0
	with open(fname, 'r') as f:
		e_t_temp = list()
		for line in f:
			if (istimelimit and n >= args.total_time):
				break
			if (line[0] != '#' and line[0] != '@'):
				cols = shlex.split(line);
				n = n+1
				if (file_count == 0):
					e_t.append(float(cols[1]))
					time.append(float(cols[0]))
				else:
					e_t_temp.append(float(cols[1]))
		if (file_count == 0):
			e_t    = np.array(e_t)
                        e_t_sq = e_t * e_t
			time   = np.array(time)
			file_count = file_count + 1;
                        #plt.plot(time, e_t, 'k-', alpha=.05, linewidth=2, zorder = 2)
		else:
			try:
                                e_t_temp = np.array(e_t_temp)
				e_t    = e_t    + e_t_temp
                                e_t_sq = e_t_sq + (e_t_temp * e_t_temp)
				file_count = file_count + 1;
                                #plt.plot(time, e_t_temp, 'k-', alpha=.05, linewidth=2, zorder=1)
			except ValueError:
				print "Current .xvg file is not an appropriate size to contribute to the rolling sum. Skipping this file."

e_t    /= file_count
e_t_sq /= file_count
std_err = np.sqrt(e_t_sq - (e_t * e_t))/np.sqrt(file_count - 1)
#print [e_t, time]

plt.title('Monitoring S(t) in FMO')
plt.ylabel('dE / (kJ/mol)')
plt.xlabel('time / ps')

plt.errorbar(time, e_t, yerr=std_err, linewidth = 1.5, zorder =2)
plt.show()

if (args.pickle_name != ""):
	print "Pickle requested!"
	pkl_out = open(args.pickle_name, 'w')
	cPickle.dump([time, e_t, std_err], pkl_out)
	pkl_out.close()
