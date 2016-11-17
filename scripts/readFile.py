import sys
import csv


fileout = open('topic_cond_word_probab.csv', 'w')

'''
for line in file1.readlines():
	lineSplit = line.split(',')
	topic = lineSplit[0]

	i = 1
	while i < len(lineSplit[1:]):
		fileout.write(str(lineSplit[i]+","+str(topic)+","+lineSplit[i+1])+"\n")
		i= i+2


fileout.close()
'''
	
with open(sys.argv[1], 'rb') as csvfile:
	spamreader = csv.reader(csvfile, delimiter=' ', quoting=csv.QUOTE_ALL)
	for row in spamreader:
		new_row = [row[0]]
		
		i = 1
		while i < len(row[1:]):
			fileout.write(row[i]+" "+row[0]+" "+row[i+1])
			fileout.write("\n")
			i = i+2


fileout.close()
