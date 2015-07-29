# This module contains classes and functions for talking to the uHTR.

from re import search
from subprocess import Popen, PIPE
import hcal_teststand
import qie
from ROOT import *

# CLASSES:

class status:
	# Construction:
	def __init__(self, ts=None, status=[], slot=-1, ips={}, fw_front=[], fw_type_front="", fw_back=[], fw_type_back="", links=[], dump=""):
		if not ts:
			ts = None
		self.ts = ts
		if not status:
			status = []
		self.status = status
		self.slot = slot
		if not ips:
			ips = {}
		self.ips = ips
		if not fw_front:
			fw_front = []
		self.fw_front = fw_front
		self.fw_type_front = fw_type_front
		if not fw_back:
			fw_back = []
		self.fw_back = fw_back
		self.fw_type_back = fw_type_back
		if not links:
			links = []
		self.links = links
		self.dump = dump
	
	# String behavior
	def __str__(self):
		if self.ts:
			return "<uhtr.status object: {0}>".format(self.status)
		else:
			return "<empty uhtr.status object>"
	
	# Methods:
	def update(self):
		self.good = (False, True)[bool(self.status) and len(self.status) == sum(self.status)]
	
	def Print(self, verbose=True):
		if verbose:
			print "[{0}] uHTR in slot {1} status: {2} <- {3}".format(("!!", "OK")[self.good], self.slot, ("BAD", "GOOD")[self.good], self.status)
			if self.good:
				print "\tFW front type: {0}".format(self.fw_type_front)
				print "\tFW front: {0}".format(self.fw_front)
				print "\tFW back type: {0}".format(self.fw_type_back)
				print "\tFW back: {0}".format(self.fw_back)
				print "\tLinks: {0}".format(self.links)
				print "\tIPs: {0}".format(self.ips)
		else:
			print "[{0}] uHTR in slot {1} status: {2}".format(("!!", "OK")[self.good], self.slot, ("BAD", "GOOD")[self.good])
	
	def log(self):
		output = "%% uHTR {0}\n".format(self.slot)
		output += "{0}\n".format(int(self.good))
		output += "{0}\n".format(self.status)
		output += "{0}\n".format(self.fw_type_front)
		output += "{0}\n".format(self.fw_front)
		output += "{0}\n".format(self.fw_type_back)
		output += "{0}\n".format(self.fw_back)
		output += "{0}\n".format(self.links)
		output += "{0}\n".format(self.ips)
		output += "{0}\n".format(self.dump)
		return output.strip()
	# /Methods

class link:		# An object that represents a uHTR link. It contains information about what it's connected to.
	qie_half_labels = ['bottom', 'top']
	
	# CONSTRUCTION
	def __init__(self, ts="unknown", uhtr_slot=-1, link_number=-1, qie_unique_id="unknown", qie_half=-1, qie_fiber=-1, on=False, qies=[-1, -1, -1, -1]):
		self.ts = ts
		self.slot = uhtr_slot
		self.n = link_number
		self.qie_unique_id = qie_unique_id
		self.qie_half = qie_half
		self.qie_half_label = "unknown"
		self.qie_fiber = qie_fiber
		self.on = on
		self.qies = qies		# The QIE numbers corresponding to the channel numbers of the link.
		if self.qie_half in [0, 1]: 
			self.qie_half_label = self.qie_half_labels[self.qie_half]
		self.ip = ""
		if hasattr(ts, "uhtr_ip_base"):
			self.ip = ts.uhtr_ip_base + ".{0}".format(self.slot * 4)
	# /CONSTRUCTION
	
	# METHODS
	def get_data_spy(self):
		data = get_data_spy(self.ts, self.slot , 300, self.n)
		if data:
			return data
		else:
			return False
	
	def Print(self):
		print "uHTR Info: Slot {0}, Link {1}".format(self.slot, self.n)
		print "QIE card ID:", self.qie_unique_id
		print "QIE card half:", self.qie_half_label
		print "Fiber:", self.qie_fiber
		print "Active:", (self.on == 1)
	# /METHODS
	
	def __str__(self):		# This just defines what the object looks like when it's printed.
		if self.n != -1:
			return "<link object: uHTR IP = {0}, n = {1}, status = {2}>".format(self.ip, self.n, "on" if self.on else "off")
		else:
			return "<empty link object>"
# /CLASSES

# FUNCTIONS:
def send_commands(ts, uhtr_slot, cmds):		# Sends commands to "uHTRtool.exe" and returns the raw output and a log. The input is a teststand object and a list of commands.
	log = ""
	raw_output = ""
	if isinstance(cmds, str):
		print 'WARNING: You probably didn\'t intend to run "uHTRtool.exe" with only one command: {0}'.format(cmds)
		print 'INFO: The "uhtr.send_commands" function takes a list of commands as an argument.'
		cmds = [cmds]
	cmds_str = ""
	for c in cmds:
		cmds_str += "{0}\n".format(c)
	uhtr_cmd = "uHTRtool.exe {0}".format(ts.uhtr[uhtr_slot])
	if hasattr(ts, "control_hub"):
		uhtr_cmd += " -o {0}".format(ts.control_hub)
	raw_output = Popen(['printf "{0}" | {1}'.format(cmds_str, uhtr_cmd)], shell = True, stdout = PIPE, stderr = PIPE).communicate()		# This puts the output of the command into a list called "raw_output" the first element of the list is stdout, the second is stderr.
	log += "----------------------------\nYou ran the following script with the uHTRTool:\n\n{0}\n----------------------------".format(cmds_str)
	
	return {
		"output": raw_output[0] + raw_output[1],
		"log": log,
	}

def send_commands_script(ts, uhtr_slot, cmds):		# Sends commands to "uHTRtool.exe" and returns the raw output and a log. The input is a teststand object and a list of commands.
	log = ""
	raw_output = ""
	if isinstance(cmds, str):
		print 'WARNING: You probably didn\'t intend to run "uHTRtool.exe" with only one command: {0}'.format(cmds)
		print 'INFO: The "uhtr.send_commands" function takes a list of commands as an argument.'
		cmds = [cmds]
	cmds_str = ""
	for c in cmds:
		cmds_str += "{0}\n".format(c)
	uhtr_cmd = "uHTRtool.exe {0}".format(ts.uhtr[uhtr_slot])
	if hasattr(ts, "control_hub"):
		uhtr_cmd += " -o {0}".format(ts.control_hub)
	with open("uhtr_script.cmd", "w") as out:
		out.write(cmds_str)
	raw_output = Popen(['{0} < uhtr_script.cmd'.format(uhtr_cmd)], shell = True, stdout = PIPE, stderr = PIPE).communicate()		# This puts the output of the command into a list called "raw_output" the first element of the list is stdout, the second is stderr.
	log += "----------------------------\nYou ran the following script with the uHTRTool:\n\n{0}\n----------------------------".format(cmds_str)
	
	return {
		"output": raw_output[0] + raw_output[1],
		"log": log,
	}

def setup(ts, uhtr_slot=False):
	# Variables:
	if uhtr_slot:
		uhtr_slots = uhtr_slot
	else:
		uhtr_slots = self.uhtr_slots
	
	# Define setup commands:
	cmds = [
		"0",
		"clock",
		"setup",
		"3",
		"quit",
		"link",
		"init",
		"1",		# Auto realign
		"92",		# Orbit delay
		"0",
		"0",
		"quit",
		"exit",
		"-1",
	]
	
	# Run setup commands:
	for uhtr_slot in uhtr_slots:
		output = uhtr.send_commands(ts, uhtr_slot, cmds)["output"]
	
	return True

def setup_links(ts, uhtr_slot=False):
	# Variables:
	if uhtr_slot:
		uhtr_slots = uhtr_slot
	else:
		uhtr_slots = self.uhtr_slots
	
	# Define setup commands:
	cmds = [
		"0",
		"link",
		"init",
		"1",		# Auto realign
		"92",		# Orbit delay
		"0",
		"0",
		"quit",
		"exit",
		"-1",
	]
	
	# Run setup commands:
	for uhtr_slot in uhtr_slots:
		output = uhtr.send_commands(ts, uhtr_slot, cmds)["output"]
	
	return True


def get_info_slot(ts, uhtr_slot):		# Returns a dictionary of information about the uHTR, such as the FW versions.
	log = ""
	data = {	# "HF-4800 (41) 00.0f.00" => FW = [00, 0f, 00], FW_type = [HF-4800, 41] (repeat for "back")
		"version_fw_front": [0, 0, 0],
		"version_fw_type_front": [0, 0],
		"version_fw_back": [0, 0, 0],
		"version_fw_type_back": [0, 0],
	}
	raw_output = send_commands(ts, uhtr_slot, ["0", "exit", "exit"])["output"]
#	log += raw_output
	match = search("Front Firmware revision : (HF-\d+|BHM) \((\d+)\) ([0-9a-f]{2})\.([0-9a-f]{2})\.([0-9a-f]{2})", raw_output)
	if match:
		data["version_fw_type_front"][0] = match.group(1)
		data["version_fw_type_front"][1] = int(match.group(2))
		data["version_fw_front"][0] = int(match.group(3), 16)
		data["version_fw_front"][1] = int(match.group(4), 16)
		data["version_fw_front"][2] = int(match.group(5), 16)
	else:
#		print "Match failed: front version."
		log += '>> ERROR: Failed to find the front FW info.'
	match = search("Back Firmware revision : (HF-\d+|BHM) \((\d+)\) ([0-9a-f]{2})\.([0-9a-f]{2})\.([0-9a-f]{2})", raw_output)
	if match:
		data["version_fw_type_back"][0] = match.group(1)
		data["version_fw_type_back"][1] = int(match.group(2))
		data["version_fw_back"][0] = int(match.group(3), 16)
		data["version_fw_back"][1] = int(match.group(4), 16)
		data["version_fw_back"][2] = int(match.group(5), 16)
	else:
#		print "Match failed: front version."
		log += '>> ERROR: Failed to find the back FW info.'
	return {
		"version_fw_front": data["version_fw_front"],
		"version_fw_type_front": data["version_fw_type_front"],
		"version_fw_back": data["version_fw_back"],
		"version_fw_type_back": data["version_fw_type_back"],
		"version_fw_front_str": "{0:03d}.{1:03d}.{2:03d}".format(data["version_fw_front"][0], data["version_fw_front"][1], data["version_fw_front"][2]),
		"version_fw_back_str": "{0:03d}.{1:03d}.{2:03d}".format(data["version_fw_back"][0], data["version_fw_back"][1], data["version_fw_back"][2]),
		"slot": uhtr_slot,
		"log": log.strip(),
	}

def get_info(ts):		# A get_info function that accepts either an IP address or a teststand object.
	info = []
	for uhtr_slot in ts.uhtr_slots:
		info.append(get_info_slot(ts, uhtr_slot))
	return info

def get_status(ts=None, slot=-1, ping=True):		# Perform basic checks with the uHTRTool.exe:
	log = ""
	s = status(ts=ts, slot=slot)
	
	if ts:
		# Ping uHTR IPs:
		ip = ts.uhtr[slot]
		if ping:
			s.ips[ip] = 0
			ping_result = Popen(["ping -c 1 {0}".format(ip)], shell = True, stdout = PIPE, stderr = PIPE).stdout.read()
			if ping_result:
				s.ips[ip] = 1
				s.status.append(1)
			else:
				s.status.append(0)
		else:
			s.ips[ip] = -1
		
		# Make sure the versions are accessible:
		uhtr_info = get_info_slot(ts, slot)
		s.fw_type_front = uhtr_info["version_fw_type_front"]
		s.fw_front = uhtr_info["version_fw_front"]
		s.fw_type_back = uhtr_info["version_fw_type_back"]
		s.fw_back = uhtr_info["version_fw_back"]
		if s.fw_type_front[1] != 0:
			s.status.append(1)
		else:
			s.status.append(0)
		
		# Active links:
		s.links = list_active_links(ts, slot)
#		if s.links:
#				s.status.append(1)
#		else:
#				s.status.append(0)
		
		# Additional info:
		s.dump = get_dump(ts, slot)
		
		s.update()
	return s

def get_status_all(ts=None, ping=True):
	log = ""
	ss = []
	
	if ts:
		for slot in ts.uhtr_slots:
			ss.append(get_status(ts=ts, slot=slot, ping=ping))
	return ss

## Parse raw uHTR output:
def parse_link_status(raw):		# Parses the raw ouput of the uHTRTool.exe's "LINK" > "STATUS".	
	# Variables:
	log = ""
	info = {}
	info["active"] = [0 for i in range(24)]		# There are 24 links per uHTR.
	info["orbit"] = [-1 for i in range(24)]		# There are 24 links per uHTR.
	
	# Parse active:
	n_times = 0
	for line in raw.split("\n"):
		if search("^BadCounter(\s*(X|ON)){12}", line):
			n_times += 1
			statuses_raw = line.replace("BadCounter", "").split()
			for i, status_raw in enumerate(statuses_raw):
				n_link = 12 * ((n_times - 1) % 2) + i
				if status_raw.strip() == "ON":
					info["active"][n_link] = 1
	if n_times < 2:
		log += ">> ERROR: No correct \"status\" was called on the link."
	elif n_times > 2:
		log += ">> ERROR: Hm, \"status\" was called on the link multiple times, so the active link list might be unreliable. (n_times = {0})".format(n_times)
	if (n_times % 2 != 0):
		log += ">> ERROR: Uh, there were an odd number of \"status\" lines, which is weird."
	
	# Parse orbit:
	n_times = 0
	for line in raw.split("\n"):
		if search("^OrbitRate\(kHz\)", line):
#			print line
			n_times += 1
			orbits_raw = line.replace("OrbitRate(kHz)", "").split()
			for i, orbit_raw in enumerate(orbits_raw):
				n_link = 12 * ((n_times - 1) % 2) + i
				info["orbit"][n_link] = float(orbit_raw)
	return info

## Get link information:
def get_info_links(ts, uhtr_slot):		# Statuses links and then returns a list of link indicies, for a certain uHTR.
	# Variables:
	log = ""
	
	# Get raw link information (LINK > STATUS):
	raw_output = get_raw_status(ts, uhtr_slot)
	
	# Parse the information:
	link_info = parse_link_status(raw_output)
	
	return link_info

def list_active_links(ts, uhtr_slot):		# Returns a list of the indices of the active links for a particular uHTR.
	link_info = get_info_links(ts, uhtr_slot)
	return [i_link for i_link, active in enumerate(link_info["active"]) if active]

## Get link objects:
def get_links(ts, uhtr_slot):		# Initializes and sets up links of a uHTR and then returns a list of links.
	# Set up the QIE card unique IDs:
	is_set = qie.set_unique_id_all(ts)
#	if is_set:
#		print ">> Unique IDs set up."
#	else:
#		print ">> ERROR: Something went wrong setting up the unique IDs."
	
	# Get a list of the active links:
	print "Fetching links from uHTR in slot {0}".format(uhtr_slot)
	active_links = list_active_links(ts, uhtr_slot)
#	print active_links
	
	# For each active link, read QIE unique ID and fiber number from SPY data:
	# (self, uhtr_ip = "unknown", link_number = -1, qie_unique_id = "unknown", qie_half = -1, qie_fiber = -1, on = False)
	result = ts.set_mode(mode=2)		# Turn on test mode B.
	if result:
		links = []
		for i in range(24):		# Every uHTR has 24 possible links labeled 0 to 23.
			if i in active_links:
				data = get_data_spy(ts, uhtr_slot, 50, i)		# Reading fewer than 50 "samples" sometimes results in no data ...
				if data:
	#				print data["raw"]
					qie_unique_id = "0x{0}{1} 0x{2}{3}".format(
						data[0][0].raw[2][1:5],
						data[0][0].raw[1][1:5],
						data[0][0].raw[4][1:5],
						data[0][0].raw[3][1:5]
					)
					qie_fiber = data[0][0].fiber
					qie_half = data[0][0].half
					links.append(link(
						ts=ts,
						uhtr_slot=uhtr_slot,
						link_number=i,
						qie_unique_id=qie_unique_id,
						qie_half=qie_half,
						qie_fiber=qie_fiber,
						on = True
					))
				else:
					links.append(link(
						ts=ts,
						on=True
					))
			else:
				links.append(link(
					ts=ts,
					uhtr_slot=uhtr_slot,
					link_number=i,
					on=False
				))
	result = ts.set_mode(mode=0)		# Return the teststand to normal mode operation.
	return links

def get_link_from_map(ts=False, uhtr_slot=-1, i_link=-1, f="", d="configuration/maps"):		# Returns a list of link objects configured with the data from the uhtr_map.
	if ts:
		qie_map = ts.read_qie_map(f=f, d=d)
#		uhtr_info = ts.uhtr_from_qie()
		qies = []
		for ch in range(4):
			qies.extend([i for i in qie_map if i["uhtr_slot"] == uhtr_slot and i["link"] == i_link and i["channel"] == ch])
		if len(qies) == 4:
			qie = qies[0]
			return link(
				ts=ts,
				uhtr_slot=uhtr_slot,
				link_number=i_link,
				qie_unique_id=qie["id"],
				qie_half=qie["half"],
				qie_fiber=qie["fiber"],
				on=True,
				qies=[qie["qie"] for qie in qies]
			)
		elif len(qies) > 1:
			print "ERROR (get_link_from_map): More than one QIE in the map matches your criterion of uhtr_slot = {0} and i_link = {1}.".format(uhter_slot, i_link)
			return False
		else:
			print "ERROR (get_link_from_map): No QIE in the map matches your criterion of uhtr_slot = {0} and i_link = {1}.".format(uhter_slot, i_link)
			return False
	else:
		print "ERROR (get_link_from_map): One of the arguments needs to be a teststand object."
		return False

def get_links_all_from_map(ts=False, f="", d="configuration/maps"):		# Returns a list of link objects configured with the data from the uhtr_map.
	links = []
	if ts:
		qie_map = ts.read_qie_map(f=f, d=d)
#		uhtr_info = ts.uhtr_from_qie()
		for qie in [i for i in qie_map if i["channel"] == 0]:
			uhtr_slot = qie["uhtr_slot"]
			link_i = qie["link"]
			links.append(link(
				ts=ts,
				uhtr_slot=uhtr_slot,
				link_number=link_i,
				qie_unique_id=qie["id"],
				qie_half=qie["half"],
				qie_fiber=qie["fiber"],
				on=True
			))
		return links
	else:
		print "ERROR (get_links_all_from_map): One of the arguments needs to be a teststand object."
		return links

# calls the uHTRs histogramming functionality
# ip - ip address of the uHTR (e.g. teststand("904").uhtr_ips[0])
# n_orbits  - number of orbits to integrate over
# sepCapID - whether to distinguish between different cap IDs
# (currently I think this means you can only read out range 0)
# fileName - output file name
def get_histo(ts=False, uhtr_slot=-1, n_orbits=1000, sepCapID=1, file_out=""):
	# Set up some variables:
	log = ""
	if not file_out:
		file_out = "histo_uhtr{0}.root".format(uhtr_slot)
	
	# Histogram:
	cmds = [
		'0',
		'link',
		'histo',
		'integrate',
		'{0}'.format(n_orbits),		# number of orbits to integrate over
		'{0}'.format(sepCapID),
		'{0}'.format(file_out),
		'0',
		'quit',
		'quit',
		'exit',
		'-1'
	]
	
	result = send_commands_script(ts, uhtr_slot, cmds)
	log += result["log"]
#	raw_output = result["output"]
	return file_out

def read_histo(file_in=""):
	result = []
	tf = TFile(file_in, "READ")
	tc = TCanvas("tc", "tc", 500, 500)
	for i_link in range(24):
			for i_ch in range(4):
				th = tf.Get("h{0}".format(4*i_link + i_ch))
				info = {}
				info["link"] = i_link
				info["channel"] = i_ch
				info["mean"] = th.GetMean()
				result.append(info)
	return result

# Perform basic uHTR commands:
## Returning raw output:
def get_raw_spy(ts, uhtr_slot, n, i_link):
	log = ""
	
	commands = [
		'0',
		'link',
		'spy',
		'{0}'.format(i_link),
		'0',
		'0',
		'{0}'.format(n),
		'quit',
		'exit',
		'-1',
	]
	
	uhtr_out = send_commands(ts, uhtr_slot, commands)
	raw_output = uhtr_out["output"]
	log += uhtr_out["log"]
	return raw_output

def get_raw_status(ts, uhtr_slot):
	log = ""
	
	commands = [
		'0',
		'link',
		'status',
		'quit',
		'exit',
		'-1',
	]
	
	uhtr_out = send_commands(ts, uhtr_slot, commands)
	raw_output = uhtr_out["output"]
	log += uhtr_out["log"]
	return raw_output

### get triggered data -
def get_triggered_data(ts, uhtr_slot , n , outputFile="testTriggeredData"):
	log = ""

	commands = [
		'0',
		'link',
		'init',
		'1',
		'92',
		'0',
		'0',
		'status',
		'l1acapture',
		'autorun',
		'{0}'.format(n),
		'5',
		'50',
		'0',
		'{0}'.format(outputFile),
		'6,7,8,9',
		'quit',
		'quit',
		'exit',
		'-1',
	]

	uhtr_out = send_commands(ts, uhtr_slot, commands)
	raw_output = uhtr_out["output"]
	log += uhtr_out["log"]
	#return uhtr_out

# Parse uHTRTool.exe SPY data:
def parse_spy(raw):		# From raw uHTR SPY data, return a list of adcs, cids, etc. organized into sublists per fiber.
	# Variables:
	data = {
		"cid": [],
		"adc": [],
		"tdc_le": [],
		"tdc_te": [],
		"fiber": [],
		"half": [],
		"raw": [],
	}
	
	# Extract the raw data lines from the raw uhtr input:
#	print raw
	raw_data = []
	for line in raw.split("\n"):
		if search("\s*\d+\s*[0-9A-F]{5}", line):
			raw_data.append(line.strip())
	
	# Put all the data in the data dictionary:
	raw_temp = []
	for line in raw_data:
#		print line
		cid_match = search("CAPIDS", line)
		if cid_match:
			data["cid"].append([int(i) for i in line.split()[-4:]][::-1])		# This has to be reversed because the SPY prints the links out in reverse order.
		adc_match = search("ADCs", line)
		if adc_match:
			data["adc"].append([int(i) for i in line.split()[-4:]][::-1])
		tdc_le_match = search("LE-TDC", line)
		if tdc_le_match:
			data["tdc_le"].append([int(i) for i in line.split()[-4:]][::-1])
		tdc_te_match = search("TE-TDC", line)
		if tdc_te_match:
			data["tdc_te"].append([int(i) for i in line.split()[-4:]][::-1])
		half_match = search("(TOP|BOTTOM)", line)
		if half_match:
			if half_match.group(1) == "BOTTOM":
				data["half"].append(0)
			elif half_match.group(1) == "TOP":
				data["half"].append(1)
		fiber_match = search("fiber\s([012])", line)
		if fiber_match:
			data["fiber"].append(int(fiber_match.group(1)))
		raw_match = search("\d+\s+([0-9A-F]{5})\s*(.*)", line)
		if raw_match:
			raw_string = raw_match.group(1)
			raw_thing = raw_match.group(2)
			raw_temp.append(raw_string)
			if not raw_thing:
				data["raw"].append(raw_temp)
				raw_temp = []
	
	# Prepare the output:
	if not data["raw"]:
		return False
	else:
		# Format the data dictionary into datum objects:
#		print data
		results = [[] for i in range(4)]		# Will return a list of datum objects for each channel.
		for bx, adcs in enumerate(data["adc"]):
			for ch, adc in enumerate(adcs):
				results[ch].append(qie.datum(
					adc=adc,
					cid=data["cid"][bx][ch],
					tdc_le=data["tdc_le"][bx][ch],
					tdc_te=data["tdc_te"][bx][ch],
					raw=data["raw"][bx],
					raw_uhtr=reduce(lambda x, y: x + "\n" + y, raw_data[bx*6:(bx + 1)*6]),		# The data for the relevant BX ...
					bx=bx,
					ch=ch,
					half=data["half"][bx],
					fiber=data["fiber"][bx]
				))
		return results

def get_data_spy(ts, uhtr_slot, n, i_link):
	result = parse_spy(get_raw_spy(ts, uhtr_slot, n, i_link))
	if result:
		return result
	else:
		print "ERROR (uhtr.get_data_spy): There was no SPY data in the raw uhtr output for uhtr slot {0} and link {1}".format(uhtr_slot, ch)
		return False

def get_dump(ts, uhtr_slot):
	log = ""
	
	commands = [
		"0",
		"LINK",
		"STATUS",
		"QUIT",
		"DTC",
		"STATUS",
		"QUIT",
		"LUMI",
		"QUIT",
		"DAQ",
		"STATUS",
		"QUIT",
		"EXIT",
		"EXIT",
	]
	
	uhtr_out = send_commands(ts, uhtr_slot, commands)
	raw_output = uhtr_out["output"]
	log += uhtr_out["log"]
	return raw_output
# /FUNCTIONS

if __name__ == "__main__":
	print "Hang on."
	print 'What you just ran is "uhtr.py". This is a module, not a script. See the documentation ("readme.md") for more information.'
