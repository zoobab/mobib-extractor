#!/usr/bin/env python

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


from smartcard.System import readers
from smartcard.util import toHexString, toBytes
debug = 0

j = 0
r=readers()
print "Readers List: %s" %r
for i in range(len(r)):
	if str(r[i]) == "ACS ACR38 Smart Card Reader 00 00" or str(r[i]) == "ACS ACR38U 00 00":
			j = i

connection = r[j].createConnection()
connection.connect()

select_icc = toBytes("80 A4 08 00 04 3F 00 00 02")
select_holder = toBytes("80 A4 08 00 04 3F 00 3F 1C")
select_envhol = toBytes("80 A4 08 00 04 20 00 20 01")
select_eventlog = toBytes("80 A4 08 00 04 20 00 20 10")
select_contractlist = toBytes("80 A4 08 00 04 20 00 20 50")
select_contract = toBytes("80 A4 08 00 04 20 00 20 20")
select_counters = toBytes("80 A4 08 00 04 20 00 20 69")
select_loadlog = toBytes("80 A4 08 00 04 10 00 10 14")
select_purchaselog = toBytes("80 A4 08 00 04 10 00 10 15")
read_1record = toBytes("80 B2 01 04 1D")
read_2record = toBytes("80 B2 02 04 1D")
read_3record = toBytes("80 B2 03 04 1D")
read_4record = toBytes("80 B2 04 04 1D")
read_5record = toBytes("80 B2 05 04 1D")
read_6record = toBytes("80 B2 06 04 1D")
read_7record = toBytes("80 B2 07 04 1D")
read_8record = toBytes("80 B2 08 04 1D")


data,sw1,sw2 = connection.transmit(select_icc)
if debug:
	print "Select ICC: %02x %02x" % (sw1,sw2)
if sw2 == 0x19:
	data,sw1,sw2 = connection.transmit(read_1record)
	if debug:
		print "ReadRecord: %02x %02x" % (sw1,sw2)
	print ("ICC:     %s" % toHexString(data))
else:
	print ("Error in ICC select")

data,sw1,sw2 = connection.transmit(select_holder)
if debug:
	print "Select Holder: %02x %02x" % (sw1,sw2)
if sw2 == 0x19:
	data,sw1,sw2 = connection.transmit(read_1record)
	if debug:
		print "Holder1 ReadRecord: %02x %02x" % (sw1,sw2)
	print ("Holder1: %s" % toHexString(data))

	data,sw1,sw2 = connection.transmit(read_2record)
	if debug:
		print "Holder2 ReadRecord: %02x %02x" % (sw1,sw2)
	print ("Holder2: %s" % toHexString(data))
else:
	print ("Error in Holder select")

data,sw1,sw2 = connection.transmit(select_envhol)
if debug:
	print "Select EnvHol: %02x %02x" % (sw1,sw2)
if sw2 == 0x19:
	data,sw1,sw2 = connection.transmit(read_1record)
	if debug:
		print "EnvHol1 ReadRecord: %02x %02x" % (sw1,sw2)
	print ("EnvHol1: %s" % toHexString(data))

	data,sw1,sw2 = connection.transmit(read_2record)
	if debug:
		print "EnvHol2 ReadRecord: %02x %02x" % (sw1,sw2)
	print ("EnvHol2: %s" % toHexString(data))
else:
	print ("Error in EnvHol select")

data,sw1,sw2 = connection.transmit(select_eventlog)
if debug:
	print "Select EventLog: %02x %02x" % (sw1,sw2)
if sw2 == 0x19:
	data,sw1,sw2 = connection.transmit(read_1record)
	if debug:
		print "EvLog1 ReadRecord: %02x %02x" % (sw1,sw2)
	print ("EvLog1:  %s" % toHexString(data))

	data,sw1,sw2 = connection.transmit(read_2record)
	if debug:
		print "EvLog2 ReadRecord: %02x %02x" % (sw1,sw2)
	print ("EvLog2:  %s" % toHexString(data))

	data,sw1,sw2 = connection.transmit(read_3record)
	if debug:
		print "EvLog3 ReadRecord: %02x %02x" % (sw1,sw2)
	print ("EvLog3:  %s" % toHexString(data))

else:
	print ("Error in EventLog select")

data,sw1,sw2 = connection.transmit(select_contractlist)
if debug:
	print "Select ContractList: %02x %02x" % (sw1,sw2)
if sw2 == 0x19:
	data,sw1,sw2 = connection.transmit(read_1record)
	if debug:
		print "ContractList ReadRecord: %02x %02x" % (sw1,sw2)
	print ("ConList: %s" % toHexString(data))
else:
	print ("Error in ContractList select")

data,sw1,sw2 = connection.transmit(select_contract)
if debug:
	print "Select Contract: %02x %02x" % (sw1,sw2)
if sw2 == 0x19:
	data,sw1,sw2 = connection.transmit(read_1record)
	if debug:
		print "Contract1 ReadRecord: %02x %02x" % (sw1,sw2)
	print ("Contra1: %s" % toHexString(data))

	data,sw1,sw2 = connection.transmit(read_2record)
	if debug:
		print "Contract2 ReadRecord: %02x %02x" % (sw1,sw2)
	print ("Contra2: %s" % toHexString(data))

	data,sw1,sw2 = connection.transmit(read_3record)
	if debug:
		print "Contract3 ReadRecord: %02x %02x" % (sw1,sw2)
	print ("Contra3: %s" % toHexString(data))

	data,sw1,sw2 = connection.transmit(read_4record)
	if debug:
		print "Contract4 ReadRecord: %02x %02x" % (sw1,sw2)
	print ("Contra4: %s" % toHexString(data))

	data,sw1,sw2 = connection.transmit(read_5record)
	if debug:
		print "Contract5 ReadRecord: %02x %02x" % (sw1,sw2)
	print ("Contra5: %s" % toHexString(data))

	data,sw1,sw2 = connection.transmit(read_6record)
	if debug:
		print "Contract6 ReadRecord: %02x %02x" % (sw1,sw2)
	print ("Contra6: %s" % toHexString(data))

	data,sw1,sw2 = connection.transmit(read_7record)
	if debug:
		print "Contract7 ReadRecord: %02x %02x" % (sw1,sw2)
	print ("Contra7: %s" % toHexString(data))

	data,sw1,sw2 = connection.transmit(read_8record)
	if debug:
		print "Contract8 ReadRecord: %02x %02x" % (sw1,sw2)
	print ("Contra8: %s" % toHexString(data))

else:
	print ("Error in Contract select")


data,sw1,sw2 = connection.transmit(select_counters)
if debug:
	print "Select Counters: %02x %02x" % (sw1,sw2)
if sw2 == 0x19:
	data,sw1,sw2 = connection.transmit(read_1record)
	if debug:
		print "Counters ReadRecord: %02x %02x" % (sw1,sw2)
	print ("Counter: %s" % toHexString(data))
else:
	print ("Error in ContractList select")

data,sw1,sw2 = connection.transmit(select_loadlog)
if debug:
	print "Select LoadLog: %02x %02x" % (sw1,sw2)
if sw2 == 0x19:
	data,sw1,sw2 = connection.transmit(read_1record)
	if debug:
		print "ReadRecord: %02x %02x" % (sw1,sw2)
	print ("LoadLog: %s" % toHexString(data))
else:
	print ("Error in LoadLog select")

data,sw1,sw2 = connection.transmit(select_purchaselog)
if debug:
	print "Select PurchaseLog: %02x %02x" % (sw1,sw2)
if sw2 == 0x19:
	data,sw1,sw2 = connection.transmit(read_1record)
	if debug:
		print "PurchaseLog1 ReadRecord: %02x %02x" % (sw1,sw2)
	print ("Purcha1: %s" % toHexString(data))

	data,sw1,sw2 = connection.transmit(read_2record)
	if debug:
		print "PurchaseLog2 ReadRecord: %02x %02x" % (sw1,sw2)
	print ("Purcha2: %s" % toHexString(data))

else:
	print ("Error in PurchaseLog select")

