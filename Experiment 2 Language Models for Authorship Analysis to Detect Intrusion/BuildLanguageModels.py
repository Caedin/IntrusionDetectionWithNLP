import sys
import nltk
from nltk.corpus import wordnet as wn
from nltk.util import ngrams

def read_data(input_file):
	entries={}
	with open(input_file, 'rb') as input_file:
		line = input_file.next()
		for line in input_file:
			line = line.strip()
			line = line.split(',')
			try:
				entries[line[0]] = line[1].strip()
			except KeyError:
				print 'duplicate comment, skipping second occurence'
				continue
	return entries
	
def get_training_data(entries):
	author_table = {}
	for k in entries:
		if entries[k] not in author_table:
			author_table[entries[k]] = 1
		else:
			author_table[entries[k]] += 1
	
	authors = []
	for k in author_table:
		authors.append((k, author_table[k]))
	authors.sort(key = lambda x: x[1])
	authors.reverse()
	training_author = authors[0][0].strip()
	training_data = []
	for k in entries:
		if entries[k] == training_author:
			training_data.append(k)
	for x in xrange(len(training_data)):
		training_data[x] = nltk.word_tokenize(unicode(training_data[x], "utf-8"))
		
	return (training_author, training_data)
	
def transform_to_POS(training_data):
	pos_data = [0.0] * len(training_data)
	counter = 0
	for k in training_data:
		pos_line = nltk.pos_tag(k)
		for x in xrange(len(pos_line)):
			pos_line[x] = pos_line[x][1]
		pos_data[counter] = pos_line
		counter+=1
		print "POS Tagging: Line#", counter
	return pos_data
	
def transform_to_WSD(t_data, pos_data):
	if len(t_data)!= len(pos_data):
		print "input size error"
		return

	wsd_data = [[]] * len(t_data)
	counter = 0
	for x in xrange(len(t_data)):
		for y in xrange(len(t_data[x])):
			word = t_data[x][y]
			pos = pos_data[x][y][0].lower()
			try:
				if pos in ['a', 'n', 'v']:
					synset = wn.synsets(word, pos)[0]
					wsd_data[counter].append(synset.name())
				else:
					continue
			except IndexError:
				continue
			
		counter+=1
		print "Word Sense Disambiguation: Line#", counter
		
	return wsd_data
		
def extract_n_grams(data_set, number_to_keep, n_gram_max_size):
	# Data set comes in as a list of entries, each n-gram is then extracted and added to a table. The most frequent number_to_keep will be kept.
	# Returns a hash table of type ngram and frequency
	n_grams_table = {}

	
	#for x in xrange(1, n_gram_max_size+1):
	x = int(n_gram_max_size)
	for entry in data_set:
		for ngram in list(ngrams(entry, x)):
			phrase = ' '.join(ngram)
			if phrase not in n_grams_table:
				n_grams_table[phrase] = 1
			else:
				n_grams_table[phrase] += 1
	
	n_gram_list = []
	for k in n_grams_table:
		n_gram_list.append((k, n_grams_table[k]))
	n_gram_list.sort(key = lambda x: x[1])
	n_gram_list.reverse()
	final_table = {}
	for x in xrange(min(len(n_gram_list), number_to_keep)):
		final_table[n_gram_list[x][0]] = n_gram_list[x][1]
	return final_table
		
		
def compute_CNG(input_phrase, standard_set_of_ngrams, number_to_keep, n_gram_max_size):
	phrase_ngrams = extract_n_grams([input_phrase], number_to_keep, n_gram_max_size)
	distance = 0
	for key in phrase_ngrams:
		if key in standard_set_of_ngrams:
			phrasal_frequency = float(phrase_ngrams[key])
			standard_frequency = float(standard_set_of_ngrams[key])
			score = 2*(phrasal_frequency - standard_frequency) / (phrasal_frequency + standard_frequency)
			score = score*score
			distance = distance+score
	return distance
	
def save_new_data_set(input_file, output_file, t_ngrams, pos_ngrams, wsd_ngrams, number_to_keep, n_gram_max_size):
	new_file = ['comment, CNG-words, CNG-POS, CNG-WSD, author']
	counter = 0
	with open(input_file, 'rb') as ifile:
		next = ifile.next()
		for line in ifile:
			print "Calculating CNG distances, Line#:", counter
			counter+=1
			
			phrase = line.strip().split(',')
			#Compute_CNG words
			word_distance = compute_CNG(nltk.word_tokenize(unicode(phrase[0], "utf-8")), t_ngrams, number_to_keep, n_gram_max_size)
			#Compute_CNG POS
			tmp = nltk.pos_tag(nltk.word_tokenize(unicode(phrase[0], "utf-8")))
			pos = [x[1] for x in tmp]
			wrds = [x[0] for x in tmp]
			pos_distance = compute_CNG(pos, pos_ngrams, number_to_keep, n_gram_max_size)
			#Compute_CNG WSG
			wsd = []
			for y in xrange(len(tmp)):
				word = wrds[y]
				word_pos = pos[y][0].lower()
				try:
					if word_pos in ['a', 'n', 'v']:
						synset = wn.synsets(word, word_pos)[0]
						wsd.append(synset.name())
					else:
						continue
				except IndexError:
					continue
			
			WSG_distance = compute_CNG(wsd, wsd_ngrams, number_to_keep, n_gram_max_size)
			
			phrase.insert(1, str(word_distance))
			phrase.insert(2, str(pos_distance))
			phrase.insert(3, str(WSG_distance))
			
			phrase = ','.join(phrase)
			new_file.append(phrase)
	
	with open(output_file, 'wb') as ofile:
		for k in new_file:
			ofile.write(k.strip()+'\n')
			
	

if __name__ == "__main__":
	input_file = sys.argv[1]
	output_file = sys.argv[2]
	n_gram_size = sys.argv[3]
	
	print "Building training corpus."
	entries = read_data(input_file)
	t_author, t_data = get_training_data(entries)
	pos_data = transform_to_POS(t_data)
	wsd_data = transform_to_WSD(t_data, pos_data)
	t_ngrams = extract_n_grams(t_data, 5000, n_gram_size)
	pos_ngrams = extract_n_grams(pos_data, 5000, n_gram_size)
	wsd_ngrams = extract_n_grams(wsd_data, 5000, n_gram_size)
	
	save_new_data_set(input_file, output_file, t_ngrams, pos_ngrams, wsd_ngrams, 5000, n_gram_size)
	
	
	