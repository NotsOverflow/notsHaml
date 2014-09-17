'''---------------------------------------------------------------------------|
                                                              _____           |
      Autor: Notsgnik                                       /||   /           |
      Email: Labruillere gmail.com                         / ||  /            |
      website: notsgnik.github.io                         /  || /             |
      License: GPL v3                                    /___||/              |
      																		  |
---------------------------------------------------------------------------!'''

import copy, re

def debug(string = 0):
	strings = [
		"debug had no error fed to him",
		"cannot open file",
		"if statment not closing",
		"data not in varSet"
	]
	string = int(string)
	if string > -1 \
	and string <  len(strings):
		print 'log : ' + strings[string]
	else:
		print 'log : Unknow error'
	quit()

def multipleReplace(string="",varSet={}):
	varSet = dict((re.escape(k), v) for k, v in varSet.iteritems())
	pattern = re.compile("|".join(varSet.keys()))
	string = pattern.sub(lambda m: varSet[re.escape(m.group(0))], string)
	return string		


class Line(object):
	"""docstring for Line"""
	def __init__(self, line):
		super(Line, self).__init__()
		self.line = line.strip(" \n\t\r")
		if self.line == "":
			self.isEmpty = True
		else:
			self.isEmpty = False
		self.length = len(self.line)
		self.index = 0
		self.key = ""
		self.result = ""
		self.isKeyword = False
		self.conditions = ""
		self.closing = False
		self.lookFor = False
		self.passingChars = [" ", "\t", "%"]
		self.passingKeywords = ["else","for","if","endif","endfor","require","forfill", "fill","endfill","ajax","forajax","ajaxfill","forajaxfill","endajax"]
		self.selfClosing = False
		self.isAction = self.isOrder()

	def __repr__(self):
		return "<Line isKeyword : %s key : %s >" % (self.isKeyword, self.key)

	def __str__(self):
		return self.line

	def isOrder(self):
		if self.isEmpty:
			return False
		if self.line[self.index] == "%":
			if self.length == 1:
				self.closing = True
				return True
			self.index += 1
			while  self.index < self.length \
			and not self.passingChar(self.line[self.index]):
				self.key += self.line[self.index]
				self.index += 1
			self.isKeyword = self.passingKeyword(self.key)
			self.conditions = self.line[self.index:].strip(" \t")
			if self.conditions != "":
				if self.conditions[0] == "%":
					self.selfClosing = True
					self.conditions = self.conditions[1:].strip(" \t")
			if self.key == "for" \
			or self.key == "forfill" \
			or self.key == "forajaxfill" \
			or self.key == "forajax":
				self.lookFor = "endfor"
			elif self.key == "if":
				self.lookFor = "endif"
			elif self.key == "ajax":
				self.lookFor = "endajax"
			elif self.key == "fill":
				self.lookFor = "endfill"
			return True
		else:
			return False


	def passingChar(self,char):
		for c in self.passingChars:
			if c == char:
				return True
		return False
	def passingKeyword(self,keyword):
		for w in self.passingKeywords:
			if w == keyword:
				return True
		return False
		

class NotsHaml(object):
	"""docstring for NotsHaml"""
	def __init__(self, file="", varSet = {}):
		super(NotsHaml, self).__init__()
		self.passingChars = [" ", "\t", "%"]
		self.passingKeywords = ["for","if","endif","endfor"]
		self.digits = ["0","1","2","3","4","5","6","7","8","9"]
		self.varSet = varSet
		self.fileStack = self.parseLineArray(self.fileToLineArray(file))


	def fileToLineArray(self, file = ""):
		baliseStack = []
		fileStack = []
		try:
			fd = open(file,"r")
		except:
			debug(1)
			return False
		for line in fd:
			curentLine = Line(line)
			if not curentLine.isEmpty:
				if curentLine.closing == True:
					curentLine.key = baliseStack.pop()
				elif curentLine.isKeyword == False:
					baliseStack.append(copy.copy(curentLine.key))
				fileStack.append(copy.copy(curentLine))
		fd.close()
		return copy.deepcopy(fileStack)


	def parseLineArray(self, lines = []):
		if lines == []:
			return []
		length = len(lines)
		curentIndex = 0
		while True:
			if curentIndex >= length:
				break
			curentLine = lines[curentIndex]
			if curentLine.isKeyword :
				if curentLine.key == "if":
					if curentLine.conditions in self.varSet:
						lines = self.elseifCareTaker(lines,curentIndex,length,self.varSet[curentLine.conditions])
						length = len(lines)
					else:
						debug(3)
						return False
					continue
				elif curentLine.key == "fill":
					if curentLine.conditions in self.varSet:
						lines, add = self.fillCareTaker(lines,curentIndex,length,self.varSet[curentLine.conditions])
						length = len(lines)
						curentIndex += add
					else:
						debug(3)
						return False
				elif curentLine.key == "for":
					isDigits = self.digitString(curentLine.conditions)
					if curentLine.conditions in self.varSet \
					or isDigits:
						if isDigits:
							times = int(curentLine.conditions)
						else:
							times = len(self.varSet[curentLine.conditions])
						lines, add = self.forCareTaker(lines,curentIndex,length,times)
						length = len(lines)
						curentIndex += add
					else:
						debug(3)
						return False
				elif curentLine.key == "require":
					lines = copy.deepcopy(lines[:curentIndex] + self.parseLineArray(self.fileToLineArray(curentLine.conditions)) + lines[curentIndex+1:])
					length = len(lines)
			curentIndex += 1
		return lines

	def forCareTaker(self,lines=[],index=0,length=0,times=0):
		forPos = index
		endForPos = 0
		index += 1
		forcross = 0
		while True:
			if index == length:
				break
			curentLine = lines[index]
			if curentLine.isKeyword :
				if curentLine.key == "for":
					forcross += 1
				elif curentLine.key == "endfor":
					if forcross == 0:
						endForPos = copy.copy(index)
					else:
						forcross -= 1
			index += 1
		templines = self.parseLineArray(lines[forPos+1:endForPos])
		size = len(templines) * times
		temp = []
		while times > 0:
			temp += copy.deepcopy(templines)
			times -= 1
		return temp, size

	def fillCareTaker(self,lines=[],index=0,length=0,conditionSet={}):
		fillPos = index
		endfillPos = 0
		index += 1
		fillcross = 0
		while True:
			if index == length:
				break
			curentLine = lines[index]
			if curentLine.isKeyword :
				if curentLine.key == "fill":
					fillcross += 1
				elif curentLine.key == "endfill":
					if fillcross == 0:
						endfillPos = copy.copy(index)
					else:
						fillcross -= 1
			index += 1
		templines = self.parseLineArray(lines[fillPos:endfillPos])
		templinesSize = len(templines)
		conditionSet = dict((re.escape(k), v) for k, v in conditionSet.iteritems())
		pattern = re.compile("|".join(conditionSet.keys()))
		for line in templines:
			if line.isKeyword == False:
				if line.isAction == True \
				and line.conditions != "":
					line.conditions = pattern.sub(lambda m: varSet[re.escape(m.group(0))], line.conditions)
				else:
					if line.line != "":
						line.line = pattern.sub(lambda m: varSet[re.escape(m.group(0))], line.line)
		templines = lines[:fillPos] + templines[:] + lines[endfillPos+1:]
		return copy.deepcopy(templines), templinesSize

	def elseifCareTaker(self,lines=[],index=0,length=0,ifStatement=False):
		ifPos = index
		elsePos = 0
		endifPos = 0
		index += 1
		ifcross = 0
		while True:
			if index == length:
				break
			curentLine = lines[index]
			if curentLine.isKeyword :
				if curentLine.key == "if":
					ifcross += 1
				elif curentLine.key == "else":
					if ifcross == 0:
						elsePos = copy.copy(index)
				elif curentLine.key == "endif":
					if ifcross == 0:
						endifPos = copy.copy(index)
					else:
						ifcross -= 1
			index += 1
		if endifPos == 0 :
			debug(2)
			return False
		if ifStatement == True:
			if elsePos != 0:
				tempLines = lines[:ifPos] + lines[ifPos+1:elsePos] + lines[endifPos+1:]
			else:
				tempLines = lines[:ifPos] + lines[ifPos+1:endifPos] + lines[endifPos+1:]
		else:
			if elsePos != 0:
				tempLines = lines[:ifPos] + lines[elsePos+1:endifPos] + lines[endifPos+1:]
			else:
				tempLines = lines[:ifPos] + lines[endifPos+1:]
		return copy.deepcopy(tempLines)

	def parseFile(self, file="", varSet={}):
		baliseStack = []
		fileStack = []
		iftrigger = False
		fd = open(file,"r")
		for line in fd:
			curentLine = Line(line)
			tmpStr = ""
			#print "new line : '%s' , %s chars" % (line, lineLength)
			if iftrigger == False :
				if curentLine.isAction :
					if not curentLine.isKeyword:
						if curentLine.length == 1:
							tmpStr = "</" + baliseStack.pop() + ">"
						else:
							if curentLine.selfClosing :
								tmpStr = "<" + curentLine.key +" "+ curentLine.conditions + " />"
							else:
								baliseStack.append(copy.copy(curentLine.key))
								tmpStr = "<" + curentLine.key +" "+ curentLine.conditions + ">"
						fileStack.append(copy.copy(tmpStr))
					else:
						if curentLine.key == "if":
							try:
								if varSet[curentLine.conditions] == True:
									continue
								raise Exception("unknow if condition")
							except:
								iftrigger = True
								continue
						elif curentLine.key == "require":
							for elem in self.parseFile(curentLine.conditions,varSet):
								fileStack.append(copy.copy(elem))
						else:
							print "unknow action"
							#fileStack.append(copy.copy(curentLine.line))
				else:
					fileStack.append(copy.copy(curentLine.line))
			else:
				if curentLine.key == "endif":
					iftrigger = False
					continue
			#print tmpStr
			#fileStack = self.parseForIf(fileStack,varSet)
		return copy.deepcopy(fileStack)

	def digitString(self,string):
		flag = False
		for c in string:
			flag = False
			for n in self.digits:
				if n == c:
					flag = True
			if flag == False:
				return False
		return True

if __name__ == "__main__":
	nh = NotsHaml("test.npt", {"users":[{"name":"jhon", "sex" : "m"}, {"name":"victoria", "sex" : "f"}], "isFriday": True, "test_if" : True})
	for line in nh.fileStack:
		print line