from lxml import etree

from ttxfont import Font, Feature, \
	GSUB_Lookup, SingleSubstitution1, MultSubstitution, LigSubstitution, ChainSubstitution3, \
	GPOS_Lookup, SingleAdjustment, MarkBaseAttachment, MarkMarkAttachment, ChainPos

def read_properties(doc, prop_name, font):
	elem = doc.find(prop_name)
	for sub_elem in elem.findall('*'):
		if sub_elem.tag is None:
			None
		elif len(sub_elem.findall('*')) > 0:
			sub_properties = {}
			for subsub_elem in sub_elem.findall('*'):
				sub_properties[subsub_elem.tag] = subsub_elem.get('value')
			font.properties[prop_name][sub_elem.tag] = sub_properties
		else:
			font.properties[prop_name][sub_elem.tag] = sub_elem.get('value')

def read_name(elem, font):
	for sub_elem in elem.findall('namerecord'):
		nameID = sub_elem.get('nameID')
		platformID = sub_elem.get('platformID')
		platEncID = sub_elem.get('platEncID')
		langID = sub_elem.get('langID')
		unicode = sub_elem.get('unicode')
		text = sub_elem.text
		if unicode is None:
			unicode = 'False'
		font.name.append({'nameID': nameID, 'platformID': platformID, \
				'platEncID': platEncID, 'langID': langID, 'unicode': unicode, \
				'text': text})

def read_CPAL(elem, font):
	if elem is not None:
		for sub_elem in elem.findall('palette'):
			t = sub_elem.get('type')
			colors = []
			for color_elem in sub_elem.findall('color'):
				value = color_elem.get('value')
				colors.append(value)
			font.palettes.append({'type': t, 'colors': colors})

def read_cmap(elem, charset):
	if elem is not None:
		for map_elem in elem.findall('map'):
			code = int(map_elem.get('code'), 0)
			name = map_elem.get('name')
			charset[code] = name

def read_cmap14(elem, font):
	if elem is not None:
		for map_elem in elem.findall('map'):
			uv = int(map_elem.get('uv'), 0)
			uvs = int(map_elem.get('uvs'), 0)
			name = map_elem.get('name')
			font.vs_to_name[(uv, uvs)] = name

def read_GlyphOrder(elem, font):
	for sub_elem in elem.findall('GlyphID'):
		name = sub_elem.get('name')
		font.glyphs.append(name)

def read_hmtx(elem, font):
	for sub_elem in elem.findall('mtx'):
		name = sub_elem.get('name')
		width = int(sub_elem.get('width'))
		lsb = int(sub_elem.get('lsb'))
		font.width[name] = width
		font.lsb[name] = lsb

def read_vmtx(elem, font):
	for sub_elem in elem.findall('mtx'):
		name = sub_elem.get('name')
		height = int(sub_elem.get('height'))
		tsb = int(sub_elem.get('tsb'))
		font.height[name] = height
		font.tsb[name] = tsb

def read_post(elem, font):
	for sub_elem in elem.findall('*'):
		if sub_elem.tag is None:
			None
		elif sub_elem.tag == 'psNames':
			None
		elif sub_elem.tag == 'extraNames':
			for psname_elem in sub_elem.findall('psName'):
				font.extra_names.append(psname_elem.get('name'))
		else:
			font.post[sub_elem.tag] = sub_elem.get('value')

def read_glyf(elem, font):
	for glyph_elem in elem.findall('TTGlyph'):
		name = glyph_elem.get('name')
		if 'xMin' in glyph_elem.attrib:
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

def read_COLR(elem, font):
	if elem is not None:
		for sub_elem in elem.findall('ColorGlyph'):
			glyph_name = sub_elem.get('name')
			layers = []
			for layer_elem in sub_elem.findall('layer'):
				colorID = int(layer_elem.get('colorID'))
				name = layer_elem.get('name')
				layers.append((colorID, name))
			font.color_layers[glyph_name] = layers

def read_GlyphClassDef(elem, font):
	for def_elem in elem.findall('ClassDef'):
		glyph = def_elem.get('glyph')
		cl = int(def_elem.get('class'))
		font.glyph_to_class[glyph] = cl
	
def read_MarkAttachClassDef(elem, font):
	for def_elem in elem.findall('ClassDef') :
		glyph = def_elem.get('glyph')
		cl = int(def_elem.get('class'))
		font.mark_to_class[glyph] = cl

def read_MarkGlyphSetsDef(elem, font):
	for coverage_elem in elem.findall('Coverage'):
		index = int(coverage_elem.get('index'))
		glyph_elems = coverage_elem.findall('Glyph')
		glyphs = [g.get('value') for g in glyph_elems]
		font.index_to_glyphs[index] = glyphs

def read_coverage(cov):
	tokens = []
	for glyph_elem in cov.findall('Glyph'):
		tokens.append(glyph_elem.get('value'))
	return tokens

def read_flag(elem, lookup):
	flag = int(elem.get('value'))
	# https://learn.microsoft.com/en-us/typography/opentype/otspec160/chapter2
	right_to_left = bool(flag & 1) # only for GPOS Type 3
	lookup.ignore_base_glyphs = bool(flag & 2) # skips over base glyphs
	lookup.ignore_ligatures = bool(flag & 4) # skips over ligatures
	lookup.ignore_marks = bool(flag & 8) # skips over combining marks
	mark_filtering_set = bool(flag & 16) 
		# layout engine skips mark glyphs not in following mark filtering set
	lookup.mark_class = flag // 256

def read_single_subst(single, lookup):
	# Type 1: Replace one glyph with one glyph
	for sub_elem in single.findall('Substitution'):
		sub = SingleSubstitution1(sub_elem.get('in'), sub_elem.get('out'))
		lookup.add(sub)

def read_mult_subst(mult, lookup):
	# Type 2: Replace one glyph with more than one glyph
	for sub_elem in mult.findall('Substitution'):
		sub = MultSubstitution(sub_elem.get('in'), sub_elem.get('out').split(','))
		lookup.add(sub)

def read_ligature_subst(lig, lookup):
	# Type 4: Replace multiple glyphs with one glyph
	for child in lig.findall('*'):
		first = [child.get('glyph')]
		for l in child.findall('*'):
			comp_str = l.get('components')
			comps = [] if comp_str == '' else comp_str.split(',')
			inputs = first + comps
			output = l.get('glyph')
			sub = LigSubstitution(inputs, output)
			lookup.add(sub)

def read_chain_subst3(chain, lookup):
	# Type 6, Format 3: Replace one or more glyphs in chained context
	lefts = []
	inputs = []
	rights = []
	refs = []
	for child in chain.findall('*'):
		if child.tag == 'BacktrackCoverage':
			lefts.append(read_coverage(child))
		elif child.tag == 'InputCoverage':
			inputs.append(read_coverage(child))
		elif child.tag == 'LookAheadCoverage':
			rights.append(read_coverage(child))
		elif child.tag == 'SubstLookupRecord':
			seq_index = int(child.find('SequenceIndex').get('value'))
			lookup_index = int(child.find('LookupListIndex').get('value'))
			refs.append((seq_index, lookup_index))
		else:
			print('Unexpected in ChainContextSubst', child)
	sub = ChainSubstitution3(lefts, inputs, rights, refs)
	lookup.add(sub)

def read_reverse_subst(reverse, lookup):
	# type 8: Applied in reverse order, replace single glyph in chaining context
	lefts = []
	inputs = []
	rights = []
	outputs = []
	for child in chain.findall('*'):
		if child.tag == 'BacktrackCoverage':
			lefts.append(read_coverage(child))
		elif child.tag == 'Coverage':
			inputs.append(read_coverage(child))
		elif child.tag == 'LookAheadCoverage':
			rights.append(read_coverage(child))
		elif child.tag == 'Substitute':
			outputs.append(child.get('value'))
		else:
			print('Unexpected in ReverseChainSingleSubst', child)
	sub = ReverseSubstitution(lefts, input, rights, output)
	lookup.add_substitution(sub)

def read_single_pos(single, lookup):
	# Type 1: Adjust position of a single glyph
	form = 0
	glyphs = []
	adjustments = []
	for child in single.findall('*'):
		if child.tag is None:
			None
		elif child.tag == 'Coverage':
			for glyph_elem in child.findall('*'):
				glyphs.append(glyph_elem.get('value'))
		elif child.tag == 'ValueFormat':
			form = child.get('value')
			# 1 -> XPlacement
			# 2 -> YPlacement
		elif child.tag == 'Value':
			if form == '1':
				x = int(child.get('XPlacement'))
				adjustments.append({'XPlacement': x})
			else:
				y = int(child.get('YPlacement'))
				adjustments.append({'YPlacement': y})
		else:
			print('Unexpected in SinglePos', child)
	adjs = [{'glyph': g, 'placement': a} for (g, a) in zip(glyphs, adjustments)]
	posit = SingleAdjustment(form, adjs)
	lookup.add_positioning(posit)

def read_mark_base_pos(mark_base, lookup):
	# Type 4: Attach a combining mark to a base glyph
	marks = []
	bases = []
	for child in mark_base.findall('*'):
		if child.tag is None:
			None
		elif child.tag == 'MarkCoverage':
			for glyph_elem in child.findall('*'):
				mark = glyph_elem.get('value')
				marks.append({'glyph': mark})
		elif child.tag == 'BaseCoverage':
			for glyph_elem in child.findall('*'):
				base = glyph_elem.get('value')
				bases.append({'glyph': base, 'coordinates': {}})
		elif child.tag == 'MarkArray':
			for array_elem in child.findall('MarkRecord'):
				index = int(array_elem.get('index'))
				cl = int(array_elem.find('Class').get('value'))
				anchor_elem = array_elem.find('MarkAnchor')
				x = int(anchor_elem.find('XCoordinate').get('value'))
				y = int(anchor_elem.find('YCoordinate').get('value'))
				marks[index]['class'] = cl
				marks[index]['x'] = x
				marks[index]['y'] = y
		elif child.tag == 'BaseArray':
			for array_elem in child.findall('BaseRecord'):
				index = int(array_elem.get('index'))
				for anchor_elem in array_elem.findall('BaseAnchor'):
					class_index = int(anchor_elem.get('index'))
					x = int(anchor_elem.find('XCoordinate').get('value'))
					y = int(anchor_elem.find('YCoordinate').get('value'))
					bases[index]['coordinates'][class_index] = {'x': x, 'y': y}
		else:
			print('Unexpected in MarkBasePos', child)
	posit = MarkBaseAttachment(marks, bases)
	lookup.add_positioning(posit)

def read_mark_mark_pos(mark_base, lookup):
	# Type 6: Attach a combining mark to another mark
	marks1 = []
	marks2 = []
	for child in mark_base.findall('*'):
		if child.tag is None:
			None
		elif child.tag == 'Mark1Coverage':
			for glyph_elem in child.findall('*'):
				mark = glyph_elem.get('value')
				marks1.append({'glyph': mark})
		elif child.tag == 'Mark2Coverage':
			for glyph_elem in child.findall('*'):
				mark = glyph_elem.get('value')
				marks2.append({'glyph': mark, 'coordinates': {}})
		elif child.tag == 'Mark1Array':
			for array_elem in child.findall('MarkRecord'):
				index = int(array_elem.get('index'))
				cl = int(array_elem.find('Class').get('value'))
				anchor_elem = array_elem.find('MarkAnchor')
				x = int(anchor_elem.find('XCoordinate').get('value'))
				y = int(anchor_elem.find('YCoordinate').get('value'))
				marks1[index]['class'] = cl
				marks1[index]['x'] = x
				marks1[index]['y'] = y
		elif child.tag == 'Mark2Array':
			for array_elem in child.findall('Mark2Record'):
				index = int(array_elem.get('index'))
				for anchor_elem in array_elem.findall('Mark2Anchor'):
					mark_index = int(anchor_elem.get('index'))
					x = int(anchor_elem.find('XCoordinate').get('value'))
					y = int(anchor_elem.find('YCoordinate').get('value'))
					marks2[index]['coordinates'][mark_index] = {'x': x, 'y': y}
		else:
			print('Unexpected in MarkMarkPos', child)
	posit = MarkMarkAttachment(marks1, marks2)
	lookup.add_positioning(posit)

def read_chain_pos(chain, lookup):
	# Type 8 Position one or more glyphs in chained context
	left = []
	input = []
	right = []
	output = None
	for child in chain.findall('*'):
		if child.tag == 'BacktrackCoverage':
			left.append(read_coverage(child))
		elif child.tag == 'InputCoverage':
			input = read_coverage(child)
		elif child.tag == 'LookAheadCoverage':
			right.append(read_coverage(child))
		elif child.tag == 'PosLookupRecord':
			output = int(child.find('LookupListIndex').get('value'))
		else:
			print('Unexpected in ChainContextPos', child)
	posit = ChainPos(left, input, right, output)
	lookup.add_positioning(posit)

def read_ext_subst(ext, lookup):
	for child in ext.findall('*'):
		if child.tag is None:
			None
		elif child.tag == 'ExtensionLookupType':
			None
		elif child.tag == 'SingleSubst':
			read_single_subst(child, lookup)
		elif child.tag == 'MultipleSubst':
			read_mult_subst(child, lookup)
		elif child.tag == 'LigatureSubst':
			read_ligature_subst(child, lookup)
		elif child.tag == 'ChainContextSubst' and child.get('Format') == '3':
			read_chain_subst3(child, lookup)
		elif child.tag == 'ReverseChainSingleSubst':
			read_reverse_subst(child, lookup)
		else:
			print('Unexpected in ExtensionSubst', child)

def read_GSUB_lookup(lookup_elem, font):
	index = int(lookup_elem.get('index'))
	typ = '1'
	if lookup_elem.find('.//ExtensionLookupType') is not None:
		typ = '7/' + lookup_elem.find('.//ExtensionLookupType').get('value')
	if lookup_elem.find('.//ChainContextSubst') is not None:
		typ += '.' + lookup_elem.find('.//ChainContextSubst').get('Format')
	lookup = GSUB_Lookup(index, typ)
	for child in lookup_elem.findall('*'):
		if child.tag == 'LookupType':
			t = child.get('value') # ignored
		elif child.tag == 'LookupFlag':
			read_flag(child, lookup)
		elif child.tag == 'ExtensionSubst':
			read_ext_subst(child, lookup)
		elif child.tag == 'SingleSubst':
			read_single_subst(child, lookup)
		elif child.tag == 'MarkFilteringSet':
			lookup.filter_set = int(child.get('value'))
		else:
			print('Unexpected in GSUB Lookup', child)
	font.add_GSUB_lookup(index, lookup)

def read_GSUB(table, font):
	scripttag_elem = table.find('.//ScriptTag')
	font.script = scripttag_elem.get('value')
	for f_record_elem in table.findall('FeatureList/FeatureRecord'):
		f_tag = f_record_elem.find('FeatureTag').get('value')
		feature = Feature(f_tag)
		lookup_elems = f_record_elem.findall('Feature/LookupListIndex')
		for lookup_elem in lookup_elems:
			index = int(lookup_elem.get('value'))
			feature.add_lookup_index(index)
		font.add_GSUB_feature(feature)
	lookup_elems = table.findall('.//Lookup')
	for lookup_elem in lookup_elems:
		read_GSUB_lookup(lookup_elem, font)

def read_ext_pos(ext, lookup):
	for child in ext.findall('*'):
		if child.tag is None:
			None
		elif child.tag == 'ExtensionLookupType':
			None
		elif child.tag == 'SinglePos':
			read_single_pos(child, lookup)
		elif child.tag == 'MarkBasePos':
			read_mark_base_pos(child, lookup)
		elif child.tag == 'MarkMarkPos':
			read_mark_mark_pos(child, lookup)
		elif child.tag == 'ChainContextPos':
			read_chain_pos(child, lookup)
		else:
			print('Unexpected in ExtensionSubst', child)

def read_GPOS_lookup(lookup_elem, font):
	index = int(lookup_elem.get('index'))
	typ ='9/' +  lookup_elem.find('.//ExtensionLookupType').get('value')
	lookup = GPOS_Lookup(index, typ)
	for child in lookup_elem.findall('*'):
		if child.tag == 'LookupType':
			t = child.get('value') # ignored
		elif child.tag == 'LookupFlag':
			read_flag(child, lookup)
		elif child.tag == 'ExtensionPos':
			read_ext_pos(child, lookup)
		elif child.tag == 'MarkFilteringSet':
			lookup.filter_set = int(child.get('value'))
		else:
			print('Unexpected in GPOS Lookup', child)
	font.add_GPOS_lookup(index, lookup)

def read_GPOS(table, font):
	f_index_elems = table.findall('.//FeatureIndex')
	for f_index_elem in f_index_elems:
		f_index = f_index_elem.get('value')
		f_record_elem = table.find('FeatureList/FeatureRecord[@index="' + f_index + '"]')
		f_tag = f_record_elem.find('FeatureTag').get('value')
		feature = Feature(f_tag)
		lookup_elems = f_record_elem.findall('Feature/LookupListIndex')
		for lookup_elem in lookup_elems:
			index = int(lookup_elem.get('value'))
			feature.add_lookup_index(index)
		font.add_GPOS_feature(feature)
	lookup_elems = table.findall('.//Lookup')
	for lookup_elem in lookup_elems:
		read_GPOS_lookup(lookup_elem, font)

def read_ttx(filename):
	font = Font()
	doc = etree.parse(filename)
	read_properties(doc, 'head', font)
	read_properties(doc, 'hhea', font)
	read_properties(doc, 'vhea', font)
	read_properties(doc, 'maxp', font)
	read_properties(doc, 'OS_2', font)
	read_name(doc.find('name'), font)
	read_CPAL(doc.find('CPAL'), font)

	read_cmap(doc.find('cmap/cmap_format_4[@platformID="0"]'), font.charset_large)
	read_cmap(doc.find('cmap/cmap_format_6'), font.charset_small)
	read_cmap(doc.find('cmap/cmap_format_12[@platformID="0"]'), font.charset_total)
	read_cmap14(doc.find('cmap/cmap_format_14'), font)

	read_GlyphOrder(doc.find('GlyphOrder'), font)
	read_hmtx(doc.find('hmtx'), font)
	read_vmtx(doc.find('vmtx'), font)
	read_post(doc.find('post'), font)
	read_glyf(doc.find('glyf'), font)
	read_COLR(doc.find('COLR'), font)

	read_GlyphClassDef(doc.find('GDEF/GlyphClassDef'), font)
	read_MarkAttachClassDef(doc.find('GDEF/MarkAttachClassDef'), font)
	read_MarkGlyphSetsDef(doc.find('GDEF/MarkGlyphSetsDef'), font)
	read_GSUB(doc.find('GSUB'), font)
	read_GPOS(doc.find('GPOS'), font)
	return font
