#!/usr/bin/python
# -*- coding: utf-8 -*-

#
# (c) 2009 MOBIB Extractor project. This software is provided 'as-is',
# without any express or implied warranty. In no event will the authors be held
# liable for any damages arising from the use of this software.
#
# Permission is granted to anyone to use this software for any purpose,
# including commercial applications, and to alter it and redistribute it
# freely, subject to no restriction.
#
# Technical remarks and questions can be addressed to
# <tania.martin@uclouvain.be>
# <jean-pierre.Szikora@uclouvain.be>
#


import re
import sys
import types
import time
import datetime
import string
import csv
import os
import shutil
import tkMessageBox

from tkFont import *
from Tkinter import *
from tkFileDialog import *
from smartcard.System import readers
from smartcard.util import toHexString, toBytes

from PIL import Image, ImageTk, ImageDraw, ImageFont



##################
## Informations ##
##################

numero = ['0','1','2','3','4','5','6','7','8','9']

## List of manufacturers
def list_manufacturers(x):
	if x == '02' or x == '11' or x == '20' or x == '2E':
		return 'Calyspo'
	if x == '00':
		return 'ASK'
	elif x == '01':
		return 'Intec'
	elif x == '03':
		return 'Ascom'
	elif x == '04':
		return 'Thales'
	elif x == '05':
		return 'Sagem'
	elif x == '06':
		return 'Axalto'
	elif x == '07':
		return 'Bull'
	elif x == '08':
		return 'Spirtech'
	elif x == '09':
		return 'BMS'
	elif x == '0A':
		return 'Oberthur'
	elif x == '0B':
		return 'Gemplus'
	elif x == '0C':
		return 'Magnadata'
	elif x == '0D':
		return 'Calmell'
	elif x == '0E':
		return 'Mecstar'
	elif x == '0F':
		return 'ACG Identification'
	elif x == '10':
		return 'STMicroelectronics'
	elif x == '12':
		return 'Giesecke & Devrient'
	elif x == '13':
		return 'OTI'
	elif x == '14':
		return 'Gemalto'
	elif x == '15':
		return 'Watchdata'
	elif x == '16':
		return 'Alios'
	elif x == '17':
		return 'S-P-S'
	elif x == '18':
		return 'IRSA'
	elif x == '21':
		return 'Innovatron'
	else:
		return 'RFU'
	

###############
## Fonctions ##
###############


## Hexadecimal to binary
def hex_to_bin(h):
	res = ''
	for i in range(0,len(h)):
		if h[i] in numero:
			a = int(h[i]) 
		else:
			if h[i] == "A":
				a = int(10)
			if h[i] == "B":
				a = int(11)
			if h[i] == "C":
				a = int(12)
			if h[i] == "D":
				a = int(13)
			if h[i] == "E":
				a = int(14)
			if h[i] == "F":
				a = int(15)
		for j in (3,2,1,0):
			if a-pow(2,j) >= 0:
				res = res + "1"
				a = a - pow(2,j)
			else:
				res = res + "0"
	return res


## Binary to alphabet with offset t (on 5 bits)
def bin_to_alphabet (b, t):
	res = ''
	a = int(0)
	if len(b)%5 == 0:
		r = 5
	else:
		r = len(b)%5
	
	for i in range(0+t,len(b)-(r+t), 5):
		a = int(b[i])*16 + int(b[i+1])*8 + int(b[i+2])*4 + int(b[i+3])*2 + int(b[i+4])
		if a > 26 or a < 1:
			res = res + ' '
		else:
			res = res + chr(64+a)
	return res


## Binary to number (on the total length)
def bin_to_number (b):
	a = int(0)
	for i in range(len(b)-1, -1, -1):
		a = a + int(b[i])*pow(2,len(b)-i-1)
	return str(a)


## Binary to number with offset t (on 4 bits)
def bin_to_number_dec (b, t):
	res = ''
	a = int(0)
	if len(b)%4 == 0:
		r = 4
	else:
		r = len(b)%4
	for i in range(0+t,len(b)-(r+t), 4):
		a = int(b[i])*8 + int(b[i+1])*4 + int(b[i+2])*2 + int(b[i+3])
		if a > 9:
			res = res + "x"
		else:
			res = res + str(a)
	return res	


## Find a date from the 1st January 1997
def find_date (x):
	init = datetime.date(1997, 1, 1)
	diff = datetime.timedelta(days=x)
	d = init + diff
	if d == init:
		return "NO TRAVEL REGISTERED"
	else:
		return d.strftime("%d/%m/%Y")


## Find a date from the 1st January 1990
def find_date_manuf (x):
	init = datetime.date(1990, 1, 1)
	diff = datetime.timedelta(days=x)
	d = init + diff
	if d == init:
		return "NO TRAVEL REGISTERED"
	else:
		return d.strftime("%d/%m/%Y")


## Find an hour
def find_hour (x):
	min = str(int(x)%60)
	if min in numero:
		min = '0'+min
	return (int(x)/60, min)
	


################
## CLASS DUMP ##
################

class Dump:

	def __init__(self, input=None):
		self.logs = []   # Rmq : logs[0] = the last log recorded
		self.contracts = []
		self.readError = False
		self.readerError = False
		
		# Acquisition of a dump
		if input == None:
			self.r=readers()
			# If there is no reader connected
			if self.r == []:
				tkMessageBox.showerror("Reader problem","No reader connected !", icon='error')
				self.readerError = True
				return	
			# If the 2 readers (ACR122 and ACR38) are connected
			self.lecteur = 0
			if len(self.r) > 1:
				for i in range(len(self.r)):
					if str(self.r[i]) == "ACS ACR 38U-CCID 00 00" or str(self.r[i]) == "ACS ACR38 Smart Card Reader 00 00" or str(self.r[i]) == "ACS ACR38U 00 00":
						self.lecteur = self.lecteur + 1
				if self.lecteur == 2 :
					tkMessageBox.showerror("Reader problem","Please connect only ONE reader (ACR122 or ACR38) !", icon='error')
					self.readerError = True
					return	
			# Detect the reader
			self.activation = 0
			self.lecteur = 0
			for i in range(len(self.r)):
				if str(self.r[i]) == "ACS ACR 38U-CCID 00 00" and self.activation == 0:
					self.activation = 1
					os.system('./pymobibACR122.py > dump.txt')
				elif str(self.r[i]) == "ACS ACR38 Smart Card Reader 00 00" and self.activation == 0:
					self.activation = 1
					os.system('./pymobibACR38.py > dump.txt')
				elif str(self.r[i]) == "ACS ACR38U 00 00" and self.activation == 0:
					self.activation = 1
					os.system('./pymobibACR38.py > dump.txt')
				else:
					if i == len(self.r)-1 and self.activation == 0:
						tkMessageBox.showerror("Reader problem","No supported reader connected !", icon='error')
						self.readerError = True
						return
						
			fs = open("dump.txt", 'r')
			fs.readline()
			fs.readline()
			temp = fs.readline()
			# If there is no card on the reader
			if temp == '' or temp[0] == "N":
				self.readError = True
				return 
			fs.close()
			self.readDump("dump.txt")
		# Reading a dump	
		else:
			self.readDump(input)
			
		# Data Treatment
		self.processICC()
		self.processLoadLog()
		self.processHolder()
		self.processContracts()
		self.processLogs()
		#self.printResults() # if you want your results into the terminal



	###################
	## Reading dumps ##
	###################

	def readDump (self, input):
		f = open(input, 'r')
		while 1:
			txt = f.readline() 
			if txt =='': 
				break
			tmp = (txt.split(' '))
			tmp[len(tmp)-1] = tmp[len(tmp)-1][0] + tmp[len(tmp)-1][1]
			tmp2 = []
			for i in range(len(tmp)):
				if tmp[i] != '':
					tmp2.append(tmp[i])
			if tmp2[0] == 'ICC:':
				self.icc = tmp2[1:len(tmp2)]
			elif tmp2[0] == 'Holder1:':
				self.holder1 = tmp2[1:len(tmp2)]
			elif tmp2[0] == 'Holder2:':
				self.holder2 = tmp2[1:len(tmp2)]
			elif tmp2[0] == 'EnvHol1:':
				self.env_holder = tmp2[1:len(tmp2)]
			elif tmp2[0][1] == 'v':
				self.logs.append(tmp2[1:len(tmp2)])
			elif tmp2[0] == 'ConList:':
				self.contract_list = tmp2[1:len(tmp2)]
			elif tmp2[0][3] == 't': 
				self.contracts.append(tmp2[1:len(tmp2)])
			elif tmp2[0] == 'Counter:':
				self.counter = tmp2[1:len(tmp2)]
			elif tmp2[0] == 'LoadLog:':
				self.load_logs = tmp2[1:len(tmp2)]
		f.close()



	######################
	## ICC informations ##
	######################

	def processICC (self):

		hexa_manuf_data = ''
		for i in range(12):
			hexa_manuf_data = hexa_manuf_data + self.icc[i]

		self.card_serial_number = ''
		for i in range(12,20):
			self.card_serial_number = self.card_serial_number + self.icc[i]
		print "Card serial number : %s"%self.card_serial_number

		self.manuf_country = ''
		country = self.icc[20] + self.icc[21]
		if country == '0250':
			self.manuf_country = "FRANCE"
			print "Manufactured in : %s"%self.manuf_country
		if country == '0056':
			self.manuf_country = "BELGIUM"
			print "Manufactured in : %s"%self.manuf_country

		self.manuf_id = self.icc[22]
		print "Card manufacturer : %s"%list_manufacturers(self.manuf_id)
		manuf_info = self.icc[24]
		rfu1 = self.icc[23]
		rfu2 = self.icc[28]

		self.card_init_date = find_date_manuf(int(bin_to_number(hex_to_bin(self.icc[25] + self.icc[26]))))
		print "Card initialisation date : %s\n"%self.card_init_date

		check_value = self.icc[27]
		print "Check_value : %s"%bin_to_number(hex_to_bin(check_value))

		# Verification of the check value
		tmp_hexa = ''
		for i in range(1,27):
			tmp_hexa = tmp_hexa + self.icc[i]
		tmp_bin = hex_to_bin(tmp_hexa)
		cv = 5
		for i in range(len(tmp_bin)):
			if tmp_bin[i] == '0':
				cv = cv + 1
		print "Check_Value verified : %d\n"%(cv%110)
		
		
	##############
	## Load Log ##
	##############

	def processLoadLog (self):
		tmp_hexa = self.load_logs[0] + self.load_logs[1]
		tmp_bin = hex_to_bin(tmp_hexa)
		self.purchase_card = find_date(int(bin_to_number(tmp_bin[2:len(tmp_bin)])))
		if self.purchase_card == "NO TRAVEL REGISTERED":
			 self.purchase_card = "UNKNOWN DATE"
		print "Date of the card purchase : %s"%self.purchase_card 


	#########################################################################
	## Find Name + Birthdate + Post code + Card number + Remaining travels ##
	#########################################################################

	def processHolder (self):
		# self.holder1 has :
		# - bytes 0-1 : unknown data
		# - bytes 2-11 : the card number
		# - bytes 12-20 : unknown data
		# - bytes 21-24 : the birthday
		# - bytes 24-28 : the begining of the name
		# self.holder2 has the end of the name

		## Name
		hexa_name = self.holder1[25][1]
		for i in range(26, 29):
			hexa_name = hexa_name + self.holder1[i]
		for a in (self.holder2):
			hexa_name = hexa_name + a

		bin_name = ''
		for i in range(0,len(hex_to_bin(hexa_name))):
			bin_name = bin_name + hex_to_bin(hexa_name)[i]

		self.name = bin_to_alphabet(bin_name,1) # offset = 1
		
		hexa_type = self.holder1[25][0]
		bin_type = hex_to_bin(hexa_type)[0:2]
		if bin_type == '01':
			self.type = 'Mr'
		elif bin_type == '10':
			self.type = 'Mrs'
		print "Name : %s %s\n"%(self.type,self.name)

		## Birthday
		self.birthday = self.holder1[24] + " / " + self.holder1[23] + " / " + self.holder1[21] + self.holder1[22]
		print "Birthday : %s\n"%self.birthday

		## Zip code
		hexa_zipcode = self.env_holder[22] + self.env_holder[23] + self.env_holder[24][0]
		self.zipcode = bin_to_number(hex_to_bin(hexa_zipcode)[4:17]) 
		print "Zip code : %s\n"%self.zipcode
			
		## Card number
		hexa_card = ''
		for i in range(2, 12):
			hexa_card = hexa_card + self.holder1[i]
		hexa_card = hexa_card + self.holder1[12][0]

		self.num_card = bin_to_number_dec(hex_to_bin(hexa_card),2) # offset = 2
		print "Card number : %s\n"%self.num_card


	###############
	## Contracts ##
	###############

	def processContracts (self):
		## Remaining travels
		hexa_counter = []
		for i in range(0,26,3):
			hexa_counter.append(self.counter[i] + self.counter[i+1] + self.counter[i+2])
		self.c = int(0)
		for i in range(len(hexa_counter)):
			self.c = self.c + int(bin_to_number(hex_to_bin(hexa_counter[i])))

		## Contract type
		if self.c == 12034:
			self.c = "-"
			self.contract_type = "Day subscription"
		else:
			self.contract_type = "UNKNOWN"
		print "Contract type : %s\n"%self.contract_type
		print "Remaining travels : %s\n"%self.c

	
		## Number of contracts
		self.nb_contracts = bin_to_number(hex_to_bin(self.contract_list[0][0]))
		print "Number of contracts : %s"%self.nb_contracts

		self.purchase_contracts = []
		## Contracts purchase
		for i in range(int(self.nb_contracts)):
			bin_contracts = hex_to_bin(self.contracts[i][5] + self.contracts[i][6])
			self.purchase_contracts.append(find_date(int(bin_to_number(bin_contracts[1:len(bin_contracts)-1]))))
			print "Contracts purchase %s : %s\n"%(i+1, self.purchase_contracts[i])	


	########################
	## Interpretation log ##
	########################
	
	def processLogs (self):
		## Card total validations counter
		hexa_cp_total_log = ['','','']
		self.cp_total_log = ['','','']
		for i in range(3):
			hexa_cp_total_log[i] = self.logs[i][17] + self.logs[i][18] + self.logs[i][19] + self.logs[i][20][0] 
		for i in range(3):
			r = hex_to_bin(hexa_cp_total_log[i])
			self.cp_total_log[i] = bin_to_number(r[3:len(r)-2])
			
		## Travel connection counter
		hexa_cp_corresp_log = ['','','']
		self.cp_corresp_log = ['','','']
		for i in range(3):
			hexa_cp_corresp_log[i] = self.logs[i][20] + self.logs[i][21] + self.logs[i][22] + self.logs[i][23][0]
		for i in range(3):
			r = hex_to_bin(hexa_cp_corresp_log[i])
			self.cp_corresp_log[i] = bin_to_number(r[3:len(r)-2])

		## Card validation date
		hexa_date_valid = ['','','']
		self.date_valid = ['','','']
		for i in range(3):
			hexa_date_valid[i] = self.logs[i][0][1] + self.logs[i][1] + self.logs[i][2][0]
		for i in range(3):
			tmp_datev_bin = hex_to_bin(hexa_date_valid[i])
			self.date_valid[i] = find_date(int(bin_to_number(tmp_datev_bin[2:len(tmp_datev_bin)])))
			
		## Card validation date of the first transit travel
		hexa_date_transit = ['','','']
		self.date_transit = ['','','']
		for i in range(3):
			hexa_date_transit[i] = self.logs[i][23] + self.logs[i][24]
		for i in range(3):
			tmp_datet_bin = hex_to_bin(hexa_date_transit[i])
			self.date_transit[i] = find_date(int(bin_to_number(tmp_datet_bin[2:len(tmp_datet_bin)])))

		## Card validation hour
		hexa_heure_valid = ['','','']
		self.heure_valid = ['','','']
		for i in range(3):
			hexa_heure_valid[i] = self.logs[i][2][1] + self.logs[i][3]
		for i in range(3):
			tmp_heurev_bin = hex_to_bin(hexa_heure_valid[i])
			self.heure_valid[i] = find_hour(int(bin_to_number(tmp_heurev_bin[0:len(tmp_heurev_bin)-1])))	

		## Card validation hour of the first transit travel
		hexa_heure_transit = ['','','']
		self.heure_transit = ['','','']
		for i in range(3):
			hexa_heure_transit[i] = self.logs[i][25] + self.logs[i][26][0]
		for i in range(3):
			tmp_heuret_bin = hex_to_bin(hexa_heure_transit[i])
			self.heure_transit[i] = find_hour(int(bin_to_number(tmp_heuret_bin[0:len(tmp_heuret_bin)-1])))	

		## Transit or not ?
		self.transit = ['','','']
		for i in range(3):
			if self.logs[i][6][0] == '6':
				self.transit[i] = "YES"
			else:
				self.transit[i] = "NO"
				
		## Number of persons travelling
		self.nb_persons = ['','','']
		for i in range(3):
			bin_nb_persons = hex_to_bin(self.logs[i][6][1] + self.logs[i][7][0])[0:5]
			self.nb_persons[i] = bin_to_number(bin_nb_persons)
			
		## String Logs
		string_logs = ['','','']
		for i in range(3):
			tmp_hexa = ''
			for j in range(29):
				tmp_hexa = tmp_hexa + self.logs[i][j]
			string_logs[i] = hex_to_bin(tmp_hexa)
			
		## Station
		self.type_transport = ['','','']
		self.ligne = ['','','']
		self.station = ['','','']
		self.direction = ['','','']
		self.coordx = ['','','']
		self.coordy = ['','','']
		for i in range(3):
			# if the transport is a metro
			if string_logs[i][99:104] == '00000':
				if self.date_valid[i] == "NO TRAVEL REGISTERED":
					self.type_transport[i] = "NO TRAVEL REGISTERED"
					self.ligne[i] = "0"
					self.station[i] = "No info"
					self.direction[i] = "No info"
					self.coordx[i] = "-"
					self.coordy[i] = "-"
				else:
					self.type_transport[i] = 'Metro'
					reader = csv.reader(open("Database/Metro.csv", "rb"))
					# Special case: a reader at the station Gare Centrale does not have the correct UID !!!!
					if string_logs[i][104:131] == '000111001101011011011101010':
						self.ligne[i] = "1A/1B"
						self.station[i] = "Gare Centrale"
						self.direction[i] = "No info"
						self.coordx[i] = "1223"
						self.coordy[i] = "1347"
					else:
						for r in reader:
							if string_logs[i][104:110] == r[1] and string_logs[i][110:114] == r[2] and string_logs[i][114:121] == r[3]:
								self.ligne[i] = r[4]
								self.station[i] = r[5]
								self.direction[i] = "No info"
								self.coordx[i] = r[6]
								self.coordy[i] = r[7]
			# if the transport is a premetro
			elif string_logs[i][99:104] == '00111':
				self.type_transport[i] = 'Premetro'
				reader = csv.reader(open("Database/Metro.csv", "rb"))
				for r in reader:
					if string_logs[i][104:110] == r[1] and string_logs[i][110:114] == r[2] and string_logs[i][114:121] == r[3]:
						self.ligne[i] = r[4]
						self.station[i] = r[5]
						self.direction[i] = "No info"
						self.coordx[i] = r[6]
						self.coordy[i] = r[7]
			# if the transport is a tramway
			elif string_logs[i][99:104] == '10110':
				self.type_transport[i] = 'Tramway'
				self.ligne[i] = "No info"
				self.station[i] = "No info"
				self.direction[i] = "No info"
				self.coordx[i] = "-"
				self.coordy[i] = "-"
			# if the transport is a bus
			elif string_logs[i][99:104] == '01111':
				self.type_transport[i] = 'Bus'
				reader = csv.reader(open("Database/Bus.csv", "rb"))
				for r in reader:
					if bin_to_number(string_logs[i][92:99]) == r[0] and bin_to_number(string_logs[i][71:83]) == r[5]:
						self.ligne[i] = r[0]
						self.station[i] = r[4] 
						self.direction[i] = r[1]
						self.coordx[i] = r[2]
						self.coordy[i] = r[3]
						break
					else:
						if bin_to_number(string_logs[i][92:99]) == '0':
							self.ligne[i] = "Unknown"
						else:
							self.ligne[i] = bin_to_number(string_logs[i][92:99])
						self.station[i] = "No info" 
						self.direction[i] = "No info"
						self.coordx[i] = "-"
						self.coordy[i] = "-"
			# if the transport is unknown
			else:
				self.type_transport[i] = "Unknown"
				self.ligne[i] = "No info"
				self.station[i] = "No info"
				self.direction[i] = "No info"
				self.coordx[i] = "-"
				self.coordy[i] = "-"


	#############
	## Results ##
	#############

	def printResults (self):
		for i in range(3):
			print "\n---> For the log %d :\n"%i
			print "Transport : %s"%(self.type_transport[i])
			print "Ligne : %s"%(self.ligne[i])
			print "Station : %s"%(self.station[i])
			print "Direction : %s"%(self.direction[i])
			print "Card validation date : %s"%(self.date_valid[i])
			print "Card validation hour: %s:%s"%(self.heure_valid[i])
			print "Number of persons travelling : %s"%(self.nb_persons[i])
			print "In transit ? : %s"%(self.transit[i])
			print "Travel connection counter : %s"%(self.cp_corresp_log[i])
			print "Card validation date of the first transit travel : %s"%(self.date_transit[i])
			print "Card validation hour of the first transit travel : %s:%s"%(self.heure_transit[i])
			print "Card total validations counter : %s"%(self.cp_total_log[i])



##########################################
## CLASS GRAPHICAL USER INTERFACE (GUI) ##
##########################################

class AutoScrollbar (Scrollbar):
    def set(self, lo, hi):
        if float(lo) <= 0.0 and float(hi) >= 1.0:
            # grid_remove is currently missing from Tkinter!
            self.tk.call("grid", "remove", self)
        else:
            self.grid()
        Scrollbar.set(self, lo, hi)
    def pack(self, **kw):
        raise TclError, "cannot use pack with this widget"
    def place(self, **kw):
        raise TclError, "cannot use place with this widget"


class GUI:

	def __init__(self):
		self.initialise = False
		self.openedFile = "dump.txt"
		self.root = Tk()
		self.root.title("Mobib Extractor")

		self.frame = Frame(self.root)
		self.frame2 = Frame(self.root)
		self.frame3 = Frame(self.root)
		self.frame4 = Frame(self.root)
		
		# Put the logos
		self.logo_gsi = Image.open("Images/logo-gsi.png")
		self.LOGO_GSI = ImageTk.PhotoImage(self.logo_gsi)
		self.logo_ucl = Image.open("Images/logo-ucl.png")
		self.LOGO_UCL = ImageTk.PhotoImage(self.logo_ucl)
		Label(self.frame3, image=self.LOGO_GSI).grid(row=0, column=0, sticky=W)
		Label(self.frame3, image=self.LOGO_UCL).grid(row=0, column=1, sticky=W)
		Label(self.frame4, text="<Double-Click> to zoom in/out").grid(row=0, column=0, sticky=E)
		
		self.vscroll = AutoScrollbar(self.root)
		self.hscroll = AutoScrollbar(self.root, orient=HORIZONTAL)
		self.can = Canvas(self.root, width=1400,height=600, bg="white", xscrollcommand=self.hscroll.set, yscrollcommand=self.vscroll.set)
		self.can.grid(row=1, column=0, sticky=N+S+E+W)

		self.isZoom = False

		self.loadMap()
		self.resizeMap()
		IM = ImageTk.PhotoImage(Image.new('RGBA',(1400,600),(0,0,0,0)))
		self.can.create_image(0,0,anchor=NW,image=IM)
		self.can.create_image(400,0,anchor=NW,image=self.img_total)

		# Mouse and keyboard events
		self.can.bind("<Double-Button-1>", self.zoom)	# zoom + or -
		self.can.bind_all("<MouseWheel>", self.roll)	# vertical scroll
		self.can.bind_all("<Left>", self.goleft)		# scroll left
		self.can.bind_all("<Right>", self.goright)		# scroll right
		self.can.bind_all("<Up>", self.goup)			# scroll up
		self.can.bind_all("<Down>", self.godown)		# scroll down
		self.can.bind_all("<Escape>", self.exit)		# leave the program
		self.can.bind_all("<a>", self.dumpCard)			# dump a card
		self.can.bind_all("<o>", self.openDump)			# open a dump
		self.can.bind_all("<s>", self.saveDump)			# save a dump

		# Put in place the window
		self.vscroll.config(command=self.can.yview)
		self.hscroll.config(command=self.can.xview)
		self.can.config(scrollregion=self.can.bbox("all"))

		self.can.grid(row=1, column=0, columnspan=2)
		self.frame.grid(row=3,column=0)
		self.frame2.grid(row=3,column=1)
		self.frame3.grid(row=0,column=0, sticky=W)
		self.frame4.grid(row=0,column=1, sticky=E)

		# Put in place the menu
		menu = Menu(self.root)
		filemenu = Menu(menu)
		menu.add_cascade(label="File", menu=filemenu)
		filemenu.add_command(label="Acquisition", command=self.dumpCard)
		filemenu.add_command(label="Open dump", command=self.openDump)
		filemenu.add_command(label="Save dump", command=self.saveDump)
		filemenu.add_separator()
		filemenu.add_command(label="Exit", command=self.frame.quit)
		helpmenu = Menu(menu)
		menu.add_cascade(label="Help", menu=helpmenu)
		helpmenu.add_cascade(label="Our help", command=self.ourHelp)
		helpmenu.add_cascade(label="About the application", command=self.about)
		self.root.config(menu=menu)
		
		self.root.mainloop()
		
		
	def initFrame (self):
		if self.initialise == False:
			self.bold = Font(weight='bold')
			# Init name
			self.Lname = Label(self.frame,text="", font=self.bold)
			self.Lname.grid(row=0,column=0,sticky=W)
			self.Lbirthday = Label(self.frame,text="")
			self.Lbirthday.grid(row=1,column=0,sticky=W)
			self.Lzipcode = Label(self.frame,text="")
			self.Lzipcode.grid(row=2,column=0,sticky=W)
			Label(self.frame,text="").grid(row=3,column=0,sticky=W)
			self.Lcp_total = Label(self.frame,text="")
			self.Lcp_total.grid(row=4,column=0,sticky=W)
			self.Llast_purchase = Label(self.frame,text="")
			self.Llast_purchase.grid(row=5,column=0,sticky=W)
			# Init logs
			self.insertRow(self.frame2, "Validation", "1", "2", "3", 0, "white", "red")
			self.Ltransport1, self.Ltransport2, self.Ltransport3 = self.insertRow(self.frame2, "Transport", "", "", "", 1)
			self.Lligne1, self.Lligne2, self.Lligne3 = self.insertRow(self.frame2, "Ligne", "", "", "", 2)
			self.Lstation1, self.Lstation2, self.Lstation3 = self.insertRow(self.frame2, "Station", "", "", "", 3)
			self.Ldirection1, self.Ldirection2, self.Ldirection3 = self.insertRow(self.frame2, "Direction", "", "", "", 4)
			self.Ldate1, self.Ldate2, self.Ldate3 = self.insertRow(self.frame2, "Date", "", "", "", 5)
			self.Ltime1, self.Ltime2, self.Ltime3 = self.insertRow(self.frame2, "Time", "", "", "", 6)
		self.initialise = True
		
		
	def saveDump (self, event=None):
		filename = asksaveasfilename()
		if filename == '':
			return 
		shutil.copyfile(self.openedFile, filename)


	def openDump (self, event=None):
		# Choose dump file
		file = askopenfilename(title="Open...")
		if file == '':
			return
		self.initFrame()
		self.dump = Dump(file)
		self.mapTreatment()
		self.openedFile = file
		
		
	def dumpCard (self, event=None):
		self.dump = Dump()
		# If there is a problem with the reader(s)
		if self.dump.readerError:
			return
		# If there is no card on the reader
		if self.dump.readError:
			tkMessageBox.showerror("No card","There is no card on the reader !", icon='error')
			return
		self.initFrame()
		self.mapTreatment()
	
		
	def mapTreatment (self):
		self.loadMap()

		# Put the stops
		x = [self.dump.coordx[0],self.dump.coordx[1],self.dump.coordx[2]]
		for i in range(3):
			if x[i] != '-':
				point = Image.open("Images/" + str(3-i) + ".png")
				self.im.paste(point, (int(self.dump.coordx[i]), int(self.dump.coordy[i])), point)
		if x[2] != '-' and x[1] != '-' and x[2] == x[1]:
			point = Image.open("Images/12.png")
			self.im.paste(point, (int(self.dump.coordx[2]), int(self.dump.coordy[2])), point)
		if x[2] != '-' and x[0] != '-' and x[2] == x[0]:
			point = Image.open("Images/13.png")
			self.im.paste(point, (int(self.dump.coordx[2]), int(self.dump.coordy[2])), point)
		if x[1] != '-' and x[0] != '-' and x[1] == self.dump.coordx[0]:
			point = Image.open("Images/23.png")
			self.im.paste(point, (int(self.dump.coordx[1]), int(self.dump.coordy[1])), point)
		if x[2] != '-' and x[1] != '-' and x[0] != '-' and x[2] == x[1] and x[2] == x[0]:
			point = Image.open("Images/123.png")
			self.im.paste(point, (int(self.dump.coordx[2]), int(self.dump.coordy[2])), point)
		
		self.resizeMap()
		self.can.create_image(400,0,anchor=NW,image=self.img_total)
		
		# If the last map is in zoom
		if self.isZoom:
			self.zoom(self)

		# Information holder
		self.Lname['text'] = self.dump.type + " " + self.dump.name
		self.Lbirthday['text'] = "Born on " + self.dump.birthday
		self.Lzipcode['text'] = "Living in " + self.dump.zipcode + " (zipcode)"
		self.Lcp_total['text'] = "You have validated " + self.dump.cp_total_log[0] + " times your card"
		self.Llast_purchase['text'] = "since the card purchase, the " + self.dump.purchase_card
		# Information logs
		self.Ltransport1['text'] = self.dump.type_transport[2]
		self.Ltransport2['text'] = self.dump.type_transport[1]
		self.Ltransport3['text'] = self.dump.type_transport[0]
		self.Lligne1['text'] = self.dump.ligne[2]
		self.Lligne2['text'] = self.dump.ligne[1]
		self.Lligne3['text'] = self.dump.ligne[0]
		self.Lstation1['text'] = self.dump.station[2]
		self.Lstation2['text'] = self.dump.station[1]
		self.Lstation3['text'] = self.dump.station[0]
		self.Ldirection1['text'] = self.dump.direction[2]
		self.Ldirection2['text'] = self.dump.direction[1]
		self.Ldirection3['text'] = self.dump.direction[0]
		self.Ldate1['text'] = self.dump.date_valid[2]
		self.Ldate2['text'] = self.dump.date_valid[1] 
		self.Ldate3['text'] = self.dump.date_valid[0] 
		self.Ltime1['text'] = str(self.dump.heure_valid[2][0]) + ":" + str(self.dump.heure_valid[2][1])
		self.Ltime2['text'] = str(self.dump.heure_valid[1][0]) + ":" + str(self.dump.heure_valid[1][1])
		self.Ltime3['text'] = str(self.dump.heure_valid[0][0]) + ":" + str(self.dump.heure_valid[0][1])
		
		# Button
		self.bouton1 = Button(self.frame2, text="More information", command=self.openInfo)
		self.bouton1.grid(row=2, column=4)
		
		
	def loadMap (self):
		self.im = Image.open("Images/plan.jpg")
		self.im.load()
	
	
	def resizeMap (self):
		self.img = ImageTk.PhotoImage(self.im)
		self.im_total = self.im.resize((600,600))
		self.img_total = ImageTk.PhotoImage(self.im_total)

				
	def openInfo (self):
		self.top = Toplevel()
		self.top.title("More information")
		self.insertLogsTotal(self.top, 0)


	def insertRow (self, master, title, value1, value2, value3, i, fgcolor = "black", bgcolor = "white"):
		Label(master,text=title, font=self.bold).grid(row=i,column=0,sticky=W)
		tmp1 = Label(master,text=value1, bg=bgcolor, fg=fgcolor)
		tmp2 = Label(master,text=value2, bg=bgcolor, fg=fgcolor)
		tmp3 = Label(master,text=value3, bg=bgcolor, fg=fgcolor)
		tmp1.grid(row=i,column=1,sticky=W)
		tmp2.grid(row=i,column=2,sticky=W)
		tmp3.grid(row=i,column=3,sticky=W)
		return tmp1,tmp2,tmp3
	
		
	def insertRowBis (self, master, title, value1, i, j):
		Label(master,text=title, font=self.bold).grid(row=i,column=0,sticky=W)
		tmp1 = Label(master,text=value1)
		tmp1.grid(row=i,column=1, columnspan=j,sticky=W)
		return tmp1
	
	
	def insertLogsTotal (self, master, initRow):
		self.insertRowBis(master, "Card number", self.dump.num_card, initRow, 3)
		self.insertRowBis(master, "Card serial number", self.dump.card_serial_number, initRow+1, 3)
		self.insertRowBis(master, "Card manufacturer : ", list_manufacturers(self.dump.manuf_id), initRow+2, 3)
		self.insertRowBis(master, "Manufactured in : ", self.dump.manuf_country, initRow+3, 3)
		self.insertRowBis(master, "Card initialisation date : ", self.dump.card_init_date, initRow+4, 3)
		self.insertRowBis(master, "Number of contracts", self.dump.nb_contracts, initRow+5, 3)
		self.insertRowBis(master, "Last contract purchase", self.dump.purchase_contracts[0], initRow+6, 3)
		self.insertRowBis(master, "Contract type", self.dump.contract_type, initRow+7, 3)
		self.insertRowBis(master, "Remaining travels", self.dump.c, initRow+8, 3)
		self.insertRow(master, "Validation", "1", "2", "3", initRow+9, "white", "red")
		self.insertRow(master, "Transport", self.dump.type_transport[2], self.dump.type_transport[1], self.dump.type_transport[0], initRow+10)
		self.insertRow(master, "Ligne", self.dump.ligne[2], self.dump.ligne[1], self.dump.ligne[0], initRow+11)
		self.insertRow(master, "Station", self.dump.station[2], self.dump.station[1], self.dump.station[0], initRow+12)
		self.insertRow(master, "Direction", self.dump.direction[2], self.dump.direction[1], self.dump.direction[0], initRow+13) 
		self.insertRow(master, "Date", self.dump.date_valid[2], self.dump.date_valid[1], self.dump.date_valid[0], initRow+14)
		self.insertRow(master, "Time", str(self.dump.heure_valid[2][0]) + ":" + str(self.dump.heure_valid[2][1]), str(self.dump.heure_valid[1][0]) + ":" + str(self.dump.heure_valid[1][1]), str(self.dump.heure_valid[0][0]) + ":" + str(self.dump.heure_valid[0][1]), initRow+15)
		self.insertRow(master, "Number of travelling people", self.dump.nb_persons[2], self.dump.nb_persons[1], self.dump.nb_persons[0], initRow+16)
		self.insertRow(master, "In transit ?", self.dump.transit[2], self.dump.transit[1], self.dump.transit[0], initRow+17)
		self.insertRow(master, "Travel transit counter", self.dump.cp_corresp_log[2], self.dump.cp_corresp_log[1], self.dump.cp_corresp_log[0], initRow+18)
		self.insertRow(master, "Date of the first transit", self.dump.date_transit[2], self.dump.date_transit[1], self.dump.date_transit[0], initRow+19)
		self.insertRow(master, "Time of the first transit", str(self.dump.heure_transit[2][0]) + ":" + str(self.dump.heure_transit[2][1]), str(self.dump.heure_transit[1][0]) + ":" + str(self.dump.heure_transit[1][1]), str(self.dump.heure_transit[0][0]) + ":" + str(self.dump.heure_transit[0][1]), initRow+20)
		self.insertRow(master, "Total validations counter", self.dump.cp_total_log[2], self.dump.cp_total_log[1], self.dump.cp_total_log[0], initRow+21)
		self.insertRowBis(master, " ", " ", initRow + 22, 3)
		self.insertRowBis(master, "Remark", "The mentions \"No info\" or \"Unknown\" indicated that the corresponding information cannot be retreived.", initRow+23, 3)
		

	def zoom (self, event=None):
		self.isZoom
		self.can.delete(ALL)
		if self.isZoom:
			self.can.xview_moveto(0.0)
			self.can.yview_moveto(0.0)
			self.can.create_image(400,0,anchor=NW,image=self.img_total)
			self.isZoom = False
			self.vscroll.config(command=self.can.yview)
			self.hscroll.config(command=self.can.xview)
			self.vscroll.grid(row=1, column=1, sticky=N+S)
			self.hscroll.grid(row=2, column=0, sticky=E+W)
			self.can.config(scrollregion=self.can.bbox("all"))
		else:
			if event == None:
				x = 0.5-0.25
				y = 0.5-0.11
			else:
				x = (event.x-400)/600.0-0.25
				y = event.y/600.0-0.11
			if x < 0:
				x = 0
			if y < 0:
				y = 0
			self.can.create_image(0,0,anchor=NW,image=self.img)
			self.isZoom = True
			self.vscroll.config(command=self.can.yview)
			self.hscroll.config(command=self.can.xview)
			self.vscroll.grid(row=1, column=2, sticky=N+S)
			self.hscroll.grid(row=2, column=0, columnspan=2, sticky=E+W)
			self.can.config(scrollregion=self.can.bbox("all"))
			self.can.xview_moveto(x)
			self.can.yview_moveto(y)
			#x= 0.49 y = 0.78


	def roll (self, event):
		if event.delta > 0:
			self.can.yview_scroll(-2, 'units')
		else:
			self.can.yview_scroll(2, 'units')

		
	def goleft (self, event):
		self.can.xview_scroll(-2,'units')


	def goright (self, event):
		self.can.xview_scroll(2,'units')


	def goup (self, event):
		self.can.yview_scroll(-2,'units')


	def godown (self, event):
		self.can.yview_scroll(2,'units')


	def exit (self, event):
		os.system('rm -rf dump.txt')
		self.frame.quit()
		
		
	def ourHelp (self):
		self.bold = Font(weight='bold')
		self.top1 = Toplevel()
		self.top1.title("Help")
		
		# Use
		h1 = Label(self.top1, text="How to use the application ?", font=self.bold)
		h2 = Label(self.top1, text="1- If you want to read a card:")
		h3 = Label(self.top1, text="   1.1- Plug your reader and put your card on")
		h4 = Label(self.top1, text="   1.2- Click <File> and click <Acquisition>")
		h5 = Label(self.top1, text="2- If you want to read an old dump file card:")
		h6 = Label(self.top1, text="   2.1- Click <File> and click <Open dump>")
		h7 = Label(self.top1, text="   2.2- Then select the file you want to read")
		h8 = Label(self.top1, text="3- If you want to save a dump card:")
		h9 = Label(self.top1, text="   3.1- Click <File> and click <Save dump>")
		h10 = Label(self.top1, text="   3.2- Then choose the name and directory to record the dump")
		h1.grid(row=0,column=0, columnspan=2, sticky=W)
		h2.grid(row=1,column=0, columnspan=2, sticky=W)
		h3.grid(row=2,column=0, columnspan=2, sticky=W)
		h4.grid(row=3,column=0, columnspan=2, sticky=W)
		h5.grid(row=4,column=0, columnspan=2, sticky=W)
		h6.grid(row=5,column=0, columnspan=2, sticky=W)
		h7.grid(row=6,column=0, columnspan=2, sticky=W)
		h8.grid(row=7,column=0, columnspan=2, sticky=W)
		h9.grid(row=8,column=0, columnspan=2, sticky=W)
		h10.grid(row=9,column=0, columnspan=2, sticky=W)

		space1 = Label(self.top1, text=" ")
		space1.grid(row=10,column=0, columnspan=2, sticky=W)
		
		i = 11
		# Keyboard shortcut help
		msg1 = Label(self.top1, text="Keyboard shortcuts:", font=self.bold)
		msg2 = Label(self.top1, text="- <Double-Click> to zoom + or -")
		msg3 = Label(self.top1, text="- <MouseWheel> to vertical scroll")
		msg4 = Label(self.top1, text="- <Left> to scroll left")
		msg5 = Label(self.top1, text="- <Right> to scroll right")
		msg6 = Label(self.top1, text="- <Up> to scroll up")
		msg7 = Label(self.top1, text="- <Down> to scroll down")
		msg8 = Label(self.top1, text="- <Escape> to leave the program")
		msg9 = Label(self.top1, text="- <a> to dump a card")
		msg10 = Label(self.top1, text="- <o> to open a dump")
		msg11 = Label(self.top1, text="- <s> to save a dump")
		msg1.grid(row=i+0,column=0,sticky=W)
		msg2.grid(row=i+0,column=1,sticky=W)
		msg3.grid(row=i+1,column=1,sticky=W)
		msg4.grid(row=i+2,column=1,sticky=W)
		msg5.grid(row=i+3,column=1,sticky=W)
		msg6.grid(row=i+4,column=1,sticky=W)
		msg7.grid(row=i+5,column=1,sticky=W)
		msg8.grid(row=i+6,column=1,sticky=W)
		msg9.grid(row=i+7,column=1,sticky=W)
		msg10.grid(row=i+8,column=1,sticky=W)
		msg11.grid(row=i+9,column=1,sticky=W)
	
	
	def about (self):
		self.bold = Font(weight='bold')
		self.top2 = Toplevel()
		self.top2.title("About the application")
		about1 = Label(self.top2, text="Software", font=self.bold) 
		about2 = Label(self.top2, text="  Version 1.0.6")
		about3 = Label(self.top2, text="  Freely provided by Gildas Avoine, Tania Martin and Jean-Pierre Szikora from the Université catholique de Louvain, Belgium")
		about4 = Label(self.top2, text="  For more details, see the webpage:")
		about5 = Label(self.top2, text="http://www.uclouvain.be/sites/security/")
		about6 = Label(self.top2, text=" ")
		about7 = Label(self.top2, text="(c) 2009 MOBIB Extractor project. This software is provided 'as-is', without any express or implied warranty.")
		about8 = Label(self.top2, text="In no event will the authors be held liable for any damages arising from the use of this software.")
		about9 = Label(self.top2, text="Permission is granted to anyone to use this software for any purpose, including commercial applications, and to alter it")
		about10 = Label(self.top2, text="and redistribute it freely, subject to no restriction.")
		about11 = Label(self.top2, text="Technical remarks and questions can be addressed to:")
		about12 = Label(self.top2, text="<tania.martin@uclouvain.be>")
		about13 = Label(self.top2, text="<jean-pierre.Szikora@uclouvain.be>")
		about14 = Label(self.top2, text=" ")
		about15 = Label(self.top2, text="Credit", font=self.bold)
		about16 = Label(self.top2, text="  The map is freely downloadable at:")
		about17 = Label(self.top2, text="http://www.stib.be/netplan-plan-reseau.html?l=fr")
		about1.grid(sticky=W)
		about2.grid(sticky=W)
		about3.grid(sticky=W)
		about4.grid(sticky=W)
		about5.grid()
		about6.grid(sticky=W)
		about7.grid(sticky=W)
		about8.grid(sticky=W)
		about9.grid(sticky=W)
		about10.grid(sticky=W)
		about11.grid(sticky=W)
		about12.grid(sticky=W)
		about13.grid(sticky=W)
		about14.grid(sticky=W)
		about15.grid(sticky=W)
		about16.grid(sticky=W)
		about17.grid()
		
		
		
gui = GUI()
