#!/usr/bin/python
ie = 0
import urllib
import urllib2
import os
import sys
import netlib
import Operator
import getopt
import time
import tarfile
import Result #soon to be implemented to make output a lil prettier and extend the use of goodork
try:
	from bs4 import BeautifulSoup as soup
except ImportError:
	ie = 1
"""
www.google.{co.za|cn|mm|im|fr|gg|ad|ac|ca|ws|pl|st|co.nz|lu|cd|gl|com.mt|co.zm|mw|co.bw|sc|co.ug|co.tz|az|gr|co.ls|co.in
				|tl|com.sl|by|gy|co.ke|be|rs|hn|com.au|es|com.ar|sk|tt|kg|az} I think thas about enough
I'm gonna use these to try to avoid the query limit, by bouncing my query between them
			 
GooDork 2.1
	Some changes, and additions (my checklist)
		*Custom User Agents #DONE
		*Results Objects
		*More intellegent combination of the switches
	some comming attractions:
		*Database/XML file result saving
		*Preset dorks
			-MySQL vulns
			-PostgeSQL vulns
			-BackDoored Servers
			-XSS vulns
			-LFI vulns
			-DirTraversal Vulns
			-CSFR presets, allows you to find CSFR vulnerable applications based on form tag structure
		

"""
class GooDork:
	def getbs4(self):
		url = 'http://pypi.python.org/packages/source/b/beautifulsoup4/beautifulsoup4-4.1.3.tar.gz'
		file_name = url.split('/')[-1]
		u = urllib2.urlopen(url)
		f = open(file_name, 'wb')
		meta = u.info()
		file_size = int(meta.getheaders("Content-Length")[0])
		print "Downloading: %s Bytes: %s" % (file_name, file_size)
		
		file_size_dl = 0
		block_sz = 8192
		while True:
			buffer = u.read(block_sz)
			if not buffer:
				break
	
			file_size_dl += len(buffer)
			f.write(buffer)
			status = r"%10d  [%3.2f%%]" % (file_size_dl, file_size_dl * 100. / file_size)
			status = status + chr(8)*(len(status)+1)
			print status,
		
		f.close()
		tar = tarfile.open('beautifulsoup4-4.1.3.tar.gz','r')
		for items in tar:
			tar.extract(items,'bs4')
		os.chdir('bs4')
		os.chdir('beautifulsoup4-4.1.3')
		os.system('python setup.py install')
		print '\nbs4 should now be installed. If not, check if the python executable is in your PATH. Re-run GooDork'
		sys.exit()
		
	def __init__(self):
		self.operator = Operator.Operator() #instance of the operator object
		self.ResList = [] #a list of result objects
		self.links = [] #the list of links returned
		return
	def search(self): #the new extensions call for a seperate method
		return
	def setUserAgent(self,UA):
		self.operator.setUserAgent(UA)
		print "User-Agent was set to [%s]" % (self.operator.netlib.UserAgent)
	def run(self):
		#I've added the creation of Result objects here so gooDork will print more helpful results ;)
		results = []
		if len(sys.argv[1:]) == 0:
			self.usage()
			sys.exit()
		try:
			opts,args = getopt.getopt(sys.argv[2:],"a:b:u:t:L:U:")
			print opts
		except getopt.GetoptError,e:
			self.usage()
			sys.exit()
		#need to change this aswell
		#if any option is set that requires the processing of the HTML, get the html first!
		#after that simply scan through it using the regex's
		#before we do all this its best to get all the HTML first!
		#okay a more intellegent method must be applied here!
		#I need to make use of the start arguemtn
		hasOtherArgs=False #check to see if we need to inspect the results for anything
		for opt,arg in opts: #set the user agent
			if opt == '-U':
				self.setUserAgent(arg)
			elif opt != '-U':
				hasOtherArgs=True
		start = time.time()
		links = []
		res = [1]
		step = len(res)
		while len(res) > 0:
			res = self.operator.goosearch(step,sys.argv[1])
			print res
			if len(res) > 0:
				links += res
				links = list(set(links))
				step += max(len(res),100) #assuming that we get 100 results per query...
			print "step:",step,",results:",len(res)
		#think i should make Results an iterable as well :)...later!
		#Uhm I need to get all the details from the web servers if any of the switches a set
		self.links = links
		if links != False:
			if len(sys.argv[2:]) == 0 or hasOtherArgs == False:
				print "Results:"
				finish = time.time()
				resultsfile = open('results.txt','w')
				for i,link in enumerate(links):
					 print "%s" % (urllib.unquote(link))
					 resultsfile.write(urllib.unquote(link)+'\n')
				print "Found %d results in %f seconds" % (len(links),finish-start)
				resultsfile.close()
				sys.exit()
		else:
			print links[1]
		#check which results are set
		self.operator.buildResults(links) #build a list of the results objects to be looked after by the operator
		print "Inspecting options...."
		
		for opt,arg in opts:
			if opt == '-b':
				print "intext:",arg
				results+=self.intext(arg)
			elif opt == '-a':
				#print "inanchor:",arg
				results+=self.inanchor(arg)
			elif opt == '-t':
				#print "intitle:",arg
				results+=self.intitle(arg)
			elif opt == '-u':
				#print "inurl:",arg
				results+=self.inurl(arg)
		finish = time.time()
		results = set(results) #I just OR the results for now
		if len(results) != 0:
			print "Results of %s" % (sys.argv[1:]) #scrapping this old crapi
			for index,result in enumerate(results):
				print "%s" % (result)
			print "Found %d in %f s" % (len(results),finish-start)
		else:
			print "No Results match your regex"		
	def usage(self):
		print """.::GooDork::. 2.0

Usage: ./GooDork [dork] {-b[pattern]|-t[pattern]|-a[pattern]}

dork			-- google search query
pattern			-- a regular expression to search for
-b			-- search the displayable text of the dork results for 'pattern'
-t			-- search the titles of the dork results for 'pattern'
-u			-- search the urls of the dork results for 'pattern'
-a			-- search in the anchors of the dork results for 'pattern'
-L			-- Limit the amount of restults processed to the first L results
-U			-- Custom User-agent
e.g ./GooDork site:.edu -bStudents #returns urls to all pages in the .edu domain displaying 'Students'
"""
	def inurl(self,pattern): #need to rewrite this, so it makes full use of the Result Object
		sys.stderr.write("searching for %s in links\n" % pattern)
		return [link for link in self.links if self.operator.inurl(pattern,link)]
	def intext(self,pattern):
		sys.stderr.write("searching for %s in text\n" % pattern)
		return [link for link in self.links if self.operator.intext(pattern,link)]
	def intitle(self,pattern):
		sys.stderr.write("searching for %s in title\n" % pattern)
		return [link for link in self.links if self.operator.intitle(pattern,link)]
	def inanchor(self,pattern):
		sys.stderr.write("searching for %s in anchor\n" % pattern)
		return [link for link in self.links if self.operator.inanchor(pattern,link)] #<-- this is when im lazy!
if __name__ == "__main__":
	try:
		try:
			f = open("Banner","r")
			f = f.read()
			print f
		except:
			pass
		print "==================================="
		dork = GooDork()
		if ie:
			dork.getbs4()
			sys.exit()
		dork.run()
	except KeyboardInterrupt:
		print "User stopped dork"
