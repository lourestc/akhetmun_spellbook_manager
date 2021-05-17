from spellbook import *

from pathlib import Path
import pickle
import lxml.html
import pandas as pd
import re
import csv
import sys

# resolver spells 'as X'
# ORDENAR SOURCES // "Also appears in"
# ADICIONAR SUMMON SLAs

def transcribe_PF(filename):

	library = []
	
	spelldf = pd.read_csv(filename,na_filter=False)

	for index,row in spelldf.iterrows():
	
		s = Spell()
		
		s.url = None # =/
		s.name = row['name']
		
		s.description = row['description']
		
		s.schools = row['school']
		s.subschools.update( row['subschool'] )
		s.descriptors.update( row['descriptor'] )
		
		for clvl in row['spell_level'].split(','):
			clist,lvl = clvl.rsplit(' ',1)
			for c in clist.split('/'):
				s.levels[c] = int(lvl)
		
		s.source = row['source']
		s.edition = "PF"
		
		s.castingtime = row['casting_time']
		
		r = re.compile(r'(?:[^,(]|\([^)]*\))+')
		for comp in r.findall(row['components']):
			s.components.add(comp)
			
		s.range = row['range']
		try:
			s.area = row['area']
		except:
			print( str(row['area']) )
		s.effect = row['effect']
		s.target = row['targets']
		s.duration = row['duration']
		s.saving = row['saving_throw']
		s.SR = row['spell_resistence']
				
		library.append(s)
		
	print( len(library), "PF spells found!" )
	
	return library
	
def transcribe_DND(pathname):

	library = []
	
	p = Path(pathname)

	for page in p.glob('*/*/*.html'):
	
		s = Spell()
		
		html = lxml.html.parse(str(page)).getroot()
		
		old_dndtools_url = html.cssselect('div.fb-comments')[0].get('data-href')
		s.url = 'https://dnd.arkalseif.info/' + '/'.join(old_dndtools_url.split('/')[3:])
		
		spellhtml = html.cssselect('div#content')[0]
		
		s.name = spellhtml.cssselect('h2')[0].text_content()
		#print( s.name )
		
		s.description = spellhtml.cssselect('div.nice-textile')[0].text_content().strip()
		spellhtml.cssselect('div.nice-textile')[0].drop_tree()
		
		s.schools = spellhtml.cssselect('a[href^="../../schools/"]')[0].text_content()
		
		s.subschools.update([x.text_content() for x in spellhtml.cssselect('a[href^="../../sub-schools/"]')])
		s.descriptors.update([x.text_content() for x in spellhtml.cssselect('a[href^="../../descriptors/"]')])
		
		classes = spellhtml.cssselect('a[href^="../../../classes/"]')
		for clvl in classes:
			c,lvl = clvl.text_content().rsplit(' ',1)
			s.levels[c] = int(lvl)
		
		s.source = spellhtml.cssselect('a[href^="../../../rulebooks/"]')[0].text_content()
		s.edition = "D&D 3.?"
		
		for comp in spellhtml.cssselect('abbr'):
			s.components.add(comp.text_content())
		
		strongs = spellhtml.cssselect('strong')
		for f in strongs:
			
			value = f.xpath('.//following-sibling::text()')[0]
			
			if f.text_content() == 'Casting Time:':
				s.castingtime = value
			elif f.text_content() == 'Range:':
				s.range = value
			elif f.text_content() == 'Target:':
				s.target = value
			elif f.text_content() == 'Effect:':
				s.effect = value
			elif f.text_content() == 'Area:':
				s.area = value
			elif f.text_content() == 'Duration:':
				s.duration = value
			elif f.text_content() == 'Saving Throw:':
				s.saving = value
			elif f.text_content() == 'Spell Resistance:':
				s.SR = value
			elif f.text_content() == 'Components:':
				continue
			elif f.text_content() == 'Level:':
				continue
			else:
				print("CAMPO: "+f.text_content())
				break
				
		library.append(s)
		
		# lxml.html.tostring(...)
		
	print( len(library), " D&D spells found!" )
	
	save_DND_to_csv(library,'dndtools_spells.csv')
	
	return library
	
def save_DND_to_csv(library,filename):
	with open(filename, 'w', encoding='UTF8') as csvfile:
		writer = csv.writer(csvfile)
		writer.writerow([ 'name', 'schools', 'subschools', 'descriptors', 'levels', 'components', 'castingtime', 'range', 'target', 'effect', 'area', 'duration', 'saving', 'SR', 'description', 'edition', 'source', 'url' ])
		for s in library:
			writer.writerow([	s.name,
									s.schools,
									', '.join([subs for subs in s.subschools]),
									', '.join([subs for subs in s.descriptors]),
									', '.join([c+' '+str(l) for c,l in s.levels.items()]),
									', '.join([subs for subs in s.components]),
									s.castingtime,
									s.range,
									s.target,
									s.effect,
									s.area,
									s.duration,
									s.saving,
									s.SR,
									s.description,
									s.edition,
									s.source,
									s.url ])

if __name__ == '__main__':

	library = []
	
	library.extend( transcribe_DND('dndtools_spells') )
	library.extend( transcribe_PF('PF_spells_19Jan2020.csv') )
	
	nextw = []
	for s in library: 
		nextw += s._check_if_derivative()
	nextw.sort()
	with open('nextw.txt','w') as outf:
		for w in nextw:
			outf.write(w+'\n')
	
	with open('Papiros Imperiais de Akhetmun-Heh.bin','wb') as outf:
		pickle.dump( library, outf )