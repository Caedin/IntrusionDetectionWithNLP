import sys
import os
import praw
import numpy as np
from bs4 import BeautifulSoup

def import_data(data_file):
	entries = {}
	with open(data_file, 'rb') as input:
		for line in input:
			line = line.split(',')
			entries[line[0]] = len(line[0].split(' '))
	return entries


if __name__ == "__main__":
	entries = import_data(sys.argv[1])
	print 'Average words per entry: ', sum(entries.values())/len(entries)
	print 'Shortest Entry: ', min(entries.values())
	print 'Longest Entry: ', max(entries.values())
	print 'Standard Deviation of #Words: ', np.std(entries.values())
	unique_words = set()
	for key in entries:
		words = key.split(' ')
		for k in words:
			unique_words.add(k)
	
	print 'Number of Unique Words:	', len(unique_words)