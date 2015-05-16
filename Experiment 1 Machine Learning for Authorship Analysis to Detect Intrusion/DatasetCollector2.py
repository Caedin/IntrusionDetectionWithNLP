import sys
import os
import praw

def download_user_data(user_name, output_file):
	user_agent = "Get data for authorship analysis research /u/caedin8"
	r = praw.Reddit(user_agent=user_agent)
	user = r.get_redditor(user_name)
	gen = user.get_comments(limit=sys.argv[1])
	with open(output_file, 'wb') as output_file:
		output_file.write('<xml>\n')
		output_file.write('<user>' + user_name + '</user>\n')
		for c in gen:
			output_file.write('<entry>\n')
			output_file.write(c.body.encode('utf-8')+'\n')
			output_file.write('</entry>\n')
		output_file.write('</xml>')

def get_users():
	r = praw.Reddit(user_agent="Get data for authorship analysis research /u/caedin8")
	users = []
	all_comments = r.get_comments('all')
	for k in all_comments:
		users.append(k.author)
	return users

if __name__ == "__main__":
	users = get_users()
	for k in users:
		download_user_data(str(k), 'BigData/'+str(k)+'.xml')
		
	
