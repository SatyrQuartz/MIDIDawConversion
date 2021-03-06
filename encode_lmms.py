import json
import xml.etree.ElementTree as ET 
import _func_instrument
import _func_audio
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("lmmsout")

args = parser.parse_args()

print('--- ConvJsonOTMN to LMMS---')

def onetime2lmmstime(input):
	return int(round(float(input * 48)))

def oneto100(input):
	return round(float(input) * 100)

def lmms_encode_notelist(xmltag, json_notelist):
	print('\t\tNotes:', end=' ')
	printcountpat = 0
	for json_note in json_notelist:
		xml_pattern = ET.SubElement(xmltag, "note")
		key = json_note['key']
		position = int(round(float(json_note['position']) * 48))
		pan = oneto100(json_note['pan'])
		duration = int(round(float(json_note['duration']) * 48))
		vol = oneto100(json_note['vol'])
		xml_pattern.set('key', str(key))
		xml_pattern.set('pos', str(int(round(position))))
		xml_pattern.set('pan', str(pan))
		xml_pattern.set('len', str(int(round(duration))))
		xml_pattern.set('vol', str(vol))
		printcountpat += 1
		print(str(printcountpat), end=' ')
	print(' ')

def lmms_encode_plugin(xmltag, json_singletrack):
	pluginname = json_singletrack['instrumentdata']['plugin']
	if pluginname == 'none':
		xml_instrumentpreplugin = ET.SubElement(xmltag, "instrument")
		xml_instrumentpreplugin.set('name', "tripleoscillator")
	else:
		xml_instrumentpreplugin = ET.SubElement(xmltag, "instrument")
		xml_instrumentpreplugin.set('name', "tripleoscillator")

def lmms_encode_inst_track(xmltag, json_singletrack):
	xmltag.set('solo', "0")
	xmltag.set('name', "untitled")
	xmltag.set('type', "0")
	xmltag.set('muted', "0")
	if json_singletrack['muted'] is not None:
		xmltag.set('muted', str(json_singletrack['muted']))
	if json_singletrack['name'] is not None:
		xmltag.set('name', json_singletrack['name'])
	#instrumenttrack
	json_instrumentdata = json_singletrack['instrumentdata']
	xml_instrumenttrack = ET.SubElement(xmltag, "instrumenttrack")
	xml_instrumenttrack.set('pitch', "0")
	if json_instrumentdata['basenote'] is not None:
		xml_instrumenttrack.set('pan', str(json_instrumentdata['basenote'] - 3))
	xml_instrumenttrack.set('basenote', "57")
	xml_instrumenttrack.set('pan', "0")
	xml_instrumenttrack.set('usemasterpitch', "1")
	xml_instrumenttrack.set('pitchrange', "12")
	xml_instrumenttrack.set('vol', "100")
	if json_singletrack['pan'] is not None:
		xml_instrumenttrack.set('pan', str(oneto100(json_singletrack['pan'])))
	if json_singletrack['vol'] is not None:
		xml_instrumenttrack.set('vol', str(oneto100(json_singletrack['vol'])))
	lmms_encode_plugin(xml_instrumenttrack, json_singletrack)
	print('Audio Track Name: ' + json_singletrack['name'])

	#placements
	json_placementlist = json_singletrack['placements']
	tracksnum = 0
	printcountplace = 0
	while tracksnum <= len(json_placementlist)-1:
		print('\tPlacement ' + str(printcountplace) + ': ')
		printcountplace += 1
		json_placement = json_placementlist[tracksnum-1]
		json_notelist = json_placement['notelist']
		xml_pattern = ET.SubElement(xmltag, "pattern")
		xml_pattern.set('pos', str(int(json_placement['position'] * 48)))
		xml_pattern.set('muted', "0")
		xml_pattern.set('steps', "16")
		xml_pattern.set('name', "")
		xml_pattern.set('type', "1")
		lmms_encode_notelist(xml_pattern, json_notelist)
		tracksnum += 1


def lmms_encode_audio_track(xmltag, json_singletrack):
	xmltag.set('solo', "0")
	xmltag.set('name', "untitled")
	xmltag.set('type', "2")
	xmltag.set('muted', "0")
	tracksnum = 0
	xml_sampletrack = ET.SubElement(xmltag, "sampletrack")
	xml_sampletrack.set('pan', "0")
	xml_sampletrack.set('vol', "100")
	if json_singletrack['pan'] is not None:
		xml_sampletrack.set('pan', str(oneto100(json_singletrack['pan'])))
	if json_singletrack['vol'] is not None:
		xml_sampletrack.set('vol', str(oneto100(json_singletrack['vol'])))
	xmltag.set('name', json_singletrack['name'])
	xmltag.set('muted', str(json_singletrack['muted']))
	print('Audio Track Name: ' + json_singletrack['name'])

	#placements
	printcountplace = 0
	print('\tPlacements:', end=' ')
	json_placementlist = json_singletrack['placements']
	while tracksnum <= len(json_placementlist)-1:
		printcountplace += 1
		print(str(printcountplace), end=' ')
		json_placement = json_placementlist[tracksnum-1]
		xml_pattern = ET.SubElement(xmltag, "sampletco")
		xml_pattern.set('pos', str(int(round(json_placement['position'] * 48))))
		xml_pattern.set('len', str(int(round(json_placement['duration'] * 48))))
		xml_pattern.set('src', str(json_placement['file']))
		tracksnum += 1
	print('')

def lmms_encode_tracks(xmltag, json_tracks):
	for json_singletrack in json_tracks:
		xml_track = ET.SubElement(xml_trackcontainer, "track")
		if json_singletrack['type'] == "instrument":
			lmms_encode_inst_track(xml_track, json_singletrack)
		if json_singletrack['type'] == "audio":
			lmms_encode_audio_track(xml_track, json_singletrack)

with open('proj.conv_otmn', 'r') as progfile:
		json_proj = json.loads(progfile.read())

if json_proj['datatype'] != 'otmn':
	print("not an otmn convprojjson")
	exit

json_tracks = json_proj['tracks']
xml_proj = ET.Element("lmms-project")
xml_proj.set('type', "song")
xml_head = ET.SubElement(xml_proj, "head")
xml_head.set('masterpitch', "0")
xml_head.set('mastervol', "100")
xml_head.set('timesig_numerator', "4")
xml_head.set('timesig_denominator', "4")
xml_head.set('bpm', "140")
if json_proj['tracks'] is not None:
	xml_head.set('mastervol', str(oneto100(json_proj['mastervol'])))
if json_proj['tracks'] is not None:
	xml_head.set('timesig_numerator', str(json_proj['timesig_numerator']))
if json_proj['tracks'] is not None:
	xml_head.set('timesig_denominator', str(json_proj['timesig_denominator']))
if json_proj['tracks'] is not None:
	xml_head.set('bpm', str(json_proj['bpm']))

xml_song = ET.SubElement(xml_proj, "song")
xml_trackcontainer = ET.SubElement(xml_song, "trackcontainer")

lmms_encode_tracks(xml_trackcontainer, json_tracks)

outfile = ET.ElementTree(xml_proj)

ET.indent(outfile)
outfile.write(args.lmmsout, encoding='unicode')
