import sys
import os
import praw
from bs4 import BeautifulSoup

def build_data_set(training_data_folder, output_file):
	input_files = os.listdir(training_data_folder)
	entry = []
	for k in input_files:
		with open(training_data_folder+'/'+k, 'rb') as input_file:
			data = ''.join([str(x) for x in input_file])
			xmldata = BeautifulSoup(data)
			for k in xmldata.user:
				user = ''.join(k).encode('utf-8').strip()
			for k in xmldata.find_all('entry'):
				k = ''.join(k).encode('utf-8').strip()
				k = k.strip()
				k = k.replace(',', '')
				k = k.replace('.', '')
				k = k.replace('"', '')
				k = k.replace('\'', '')
				k = k.replace('\n', '')
				entry.append(k + ', ' + user)
	
	with open(output_file, 'wb') as ofile:
		ofile.write('comment,class'+'\r\n')
		for k in entry:
			ofile.write(k+'\r\n')
	
				
				
			


if __name__ == "__main__":
	training_data_folder = sys.argv[1]
	output_file = sys.argv[2]
	
	build_data_set(training_data_folder, output_file)
		
	
