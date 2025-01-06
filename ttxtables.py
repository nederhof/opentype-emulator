from lxml import etree

def read_basic_properties(filename, prop_name, font):
	doc = etree.parse(filename)
	for elem in doc.findall('*'):
		if elem.tag is None:
			None
		elif len(elem.findall('*')) > 0:
			sub_properties = {}
			for sub_elem in elem.findall('*'):
				sub_properties[sub_elem.tag] = sub_elem.get('value')
			font.properties[prop_name][elem.tag] = sub_properties
		else:
			font.properties[prop_name][elem.tag] = elem.get('value')

def read_post(filename, font):
	doc = etree.parse(filename)
	for elem in doc.findall('*'):
		if elem.tag is not None and elem.get('value') is not None:
			font.post[elem.tag] = elem.get('value')

def read_name(filename, font):
	doc = etree.parse(filename)
	for elem in doc.findall('namerecord'):
		nameID = elem.get('nameID')
		platformID = elem.get('platformID')
		platEncID = elem.get('platEncID')
		langID = elem.get('langID')
		unicode = elem.get('unicode')
		text = elem.text
		if unicode is None:
			unicode = 'False'
		font.name.append({'nameID': nameID, 'platformID': platformID, \
				'platEncID': platEncID, 'langID': langID, 'unicode': unicode, \
				'text': text})

def read_cmap(filename):
	doc = etree.parse(filename)
	code_to_name = {}
	for elem in doc.findall('map'):
		code = elem.get('code')
		name = elem.get('name')
		code_to_name[int(code, 0)] = name
	return code_to_name

def read_extra_names(filename, font):
	doc = etree.parse(filename)
	for elem in doc.findall('*'):
		font.add_extra_name(elem.get('name'))

def read_glyf(filename, font):
	doc = etree.parse(filename)
	for glyph_elem in doc.findall('TTGlyph'):
		name = glyph_elem.get('name')
		if glyph_elem.get('xMin') is not None:
			font.xmin[name] = int(glyph_elem.get('xMin'))
		if glyph_elem.get('yMin') is not None:
			font.ymin[name] = int(glyph_elem.get('yMin'))
		if glyph_elem.get('xMax') is not None:
			font.xmax[name] = int(glyph_elem.get('xMax'))
		if glyph_elem.get('yMax') is not None:
			font.ymax[name] = int(glyph_elem.get('yMax'))
		contours = []
		for contour_elem in glyph_elem.findall('contour'):
			contour = []
			for pt_elem in contour_elem:
				pt = (pt_elem.get('x'), pt_elem.get('y'), pt_elem.get('on'))
				contour.append(pt)
			contours.append(contour)
		font.contours[name] = contours
		components = []
		for component_elem in glyph_elem.findall('component'):
			glyphName = component_elem.get('glyphName')
			x = component_elem.get('x')
			y = component_elem.get('y')
			scale = component_elem.get('scale')
			scalex = component_elem.get('scalex')
			scaley = component_elem.get('scaley')
			scale01 = component_elem.get('scale01')
			scale10 = component_elem.get('scale10')
			flags = component_elem.get('flags')
			component = {'glyphName': glyphName, 'x': x, 'y': y, 'flags': flags}
			if scale is not None:
				component['scale'] = scale
			if scalex is not None:
				component['scalex'] = scalex
			if scaley is not None:
				component['scaley'] = scaley
			if scale01 is not None:
				component['scale01'] = scale01
			if scale10 is not None:
				component['scale10'] = scale10
			components.append(component)
		font.components[name] = components
		instructions = []
		for assembly_elem in glyph_elem.findall('instructions/assembly'):
			instructions.append(assembly_elem.text)
		font.assemblies[name] = instructions
