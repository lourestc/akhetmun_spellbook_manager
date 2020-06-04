import string

class Spell:
	
	def __init__(self):
	
		self.name = None
		
		self.schools = None
		self.subschools = set()
		self.descriptors = set()
		
		self.levels = {}
		
		self.components = set()
		self.castingtime = None
		
		self.range = None
		self.target = None
		self.effect = None
		self.area = None
		self.duration = None
		
		self.saving = None
		self.SR = None
		
		self.description = None
		
		self.edition = None
		self.source = None
		self.url = None
		
	def in_name(self, query):
		return self.name and query.lower() in self.name.lower()
		
	def in_description(self, query):
		return self.description and query.lower() in self.description.lower()
		
	def in_schools(self, query):
		return self.schools and query.lower() in self.schools.lower()
		
	def in_subschools(self, query):
		return query.lower() in set(x.lower() for x in self.subschools)
	
	def in_descriptors(self, query):
		return query.lower() in set(x.lower() for x in self.descriptors)
		
	def in_components(self, query):
		return query.lower() in set(x.lower() for x in self.components)
	
	def in_classes(self, query):
		return query.lower() in set(x.lower() for x in self.levels.keys())
	
	def level(self, casterclass):
		cc = casterclass.lower()
		return { cname.lower():clevel for cname,clevel in self.levels.items() }[cc]
	
	def in_castingtime(self, query):
		return self.castingtime and query.lower() in self.castingtime.lower()
		
	def in_range(self, query):
		return self.range and query.lower() in self.range.lower()
		
	def in_target(self, query):
		return self.target and query.lower() in self.target.lower()
	
	def in_effect(self, query):
		return self.effect and query.lower() in self.effect.lower()
	
	def in_area(self, query):
		return self.area and query.lower() in self.area.lower()
	
	def in_duration(self, query):
		return self.duration and query.lower() in self.duration.lower()
	
	def in_saving(self, query):
		return self.saving and query.lower() in self.saving.lower()
	
	def in_SR(self, query):
		return self.SR and query.lower() in self.SR.lower()
	
	def in_edition(self, query):
		return self.edition and query.lower() in self.edition.lower()
	
	def in_source(self, query):
		return self.source and query.lower() in self.source.lower()
	
	def _check_if_derivative(self):
		nextw = []
		nopunct = str.maketrans('', '', string.punctuation)
		dterms = self.description.lower().translate(nopunct).split()
		for iw,w in enumerate(dterms):
			if w == "as":
				nextw.append(self.name+" ::: "+' '.join(dterms[iw-1:iw+5]))
				
		return nextw
	
	def update_derivative(self, original_spell):
		if not self.schools:
			self.schools = original_spell.schools
		if len(self.subschools)==0:
			self.subschools = original_spell.subschools
		if len(self.descriptors)==0:
			self.descriptors = original_spell.descriptors
		if len(self.levels)==0:
			self.levels = original_spell.levels
		if len(self.components)==0:
			self.components = original_spell.components
		if not self.castingtime:
			self.castingtime = original_spell.castingtime
		if not self.range:
			self.range = original_spell.range
		if not self.target:
			self.target = original_spell.target
		if not self.effect:
			self.effect = original_spell.effect
		if not self.area:
			self.area = original_spell.area
		if not self.duration:
			self.duration = original_spell.duration
		if not self.saving:
			self.saving = original_spell.saving
		if not self.SR:
			self.SR = original_spell.SR
		
def find_original_spells(library):

	nopunct = str.maketrans('', '', string.punctuation)
	#snames = [ s2.name.lower().translate(nopunct).split() for s2 in self.spells ]

	new_lib = []

	for s in library: 
		dterms = s.description.lower().translate(nopunct).split()
		for iw,w in enumerate(dterms):
			if w == "as" or w == "like":
				for s2 in library:
					sn = s2.name.lower().translate(nopunct).split()
					if dterms[iw-1] != "such" and dterms[iw+1:iw+1+len(sn)] == sn:
						#nextw.append(s.name+" ::: "+' '.join(sn))
						s.update_derivative(s2)
						break
		new_lib.append(s)
		
	return new_lib

class Spellbook:
	
	def __init__(self, library, casterclass, maxlevel=9):
		
		self.casterclass = casterclass
		self.maxlevel = maxlevel
		
		#newlib = find_original_spells(library)
		
		self.spells = [ s for s in library if s.in_classes(casterclass) and s.level(casterclass)<=maxlevel ]
		self.spells.sort( key = lambda s: s.level(casterclass) )
		
	def filter_forbidden_school(self, school):
		self.spells = [ s for s in self.spells if not s.in_schools(school) ]
		
	def search_spells(self, search_list):
		
		result_spells = self.spells
		
		for field,query in search_list:
			if field=='name':
				result_spells = [ s for s in result_spells if s.in_name(query) ]
			elif field=='name not':
				result_spells = [ s for s in result_spells if not s.in_name(query) ]
			elif field=='description':
				result_spells = [ s for s in result_spells if s.in_description(query) ]
			elif field=='description not':
				result_spells = [ s for s in result_spells if not s.in_description(query) ]
			elif field=='duration':
				result_spells = [ s for s in result_spells if s.in_duration(query) ]
			elif field=='duration not':
				result_spells = [ s for s in result_spells if not s.in_duration(query) ]
			elif field=='range':
				result_spells = [ s for s in result_spells if s.in_range(query) ]
			elif field=='range not':
				result_spells = [ s for s in result_spells if not s.in_range(query) ]
			elif field=='area':
				result_spells = [ s for s in result_spells if s.in_area(query) ]
			elif field=='area not':
				result_spells = [ s for s in result_spells if not s.in_area(query) ]
			elif field=='school':
				result_spells = [ s for s in result_spells if s.in_schools(query) ]
			elif field=='school not':
				result_spells = [ s for s in result_spells if not s.in_schools(query) ]
			elif field=='save':
				result_spells = [ s for s in result_spells if s.in_saving(query) ]
			elif field=='save not':
				result_spells = [ s for s in result_spells if not s.in_saving(query) ]
			elif field=='target':
				result_spells = [ s for s in result_spells if s.in_target(query) ]
			elif field=='target not':
				result_spells = [ s for s in result_spells if not s.in_target(query) ]
			else:
				print(f"ERROR! Invalid field: '{field}'.")
				return
		
		return result_spells