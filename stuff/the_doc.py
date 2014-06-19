# -*- coding: utf-8 -*-

import project
import widgets
from nodes import Text, List, Syntaxed, Node, Todo, Note, Collapsible
from tags import ElementTag, NewlineTag as nl, WidgetTag as w, TextTag as t, ChildTag as ch
from logger import ping

def the_doc():
	return List([
		Chapter("development", 
			Chapter("todo",	
				Todo("List should have its own menu"),
				Todo("strip leading tabs from text of Notes"),
				Todo("scrolling"),
				Todo("""bool, syntaxed, how? enum,
				True and False separate atoms with syntaxes?
				"""),
				Todo("nodeize the doc"),
				Todo("revive old code nodes"),
				Todo("curb hardcoded colors"),
				Todo("multiline text editor"),
				Todo("""modify event.py to not send self to uninterested event handlers
				..try catch
				actually, a lot of that module isnt needed at all
				"""),
				Todo("save/load nodes")
				
			),
					
			Chapter("Introduction", """
				
				syntax of the language is defined by two things: the preferred types
				passed to Placeholders by nodes, and by wat.pl, where a hierarchy is
				defined. In future it would ideally all be in one place.
				
				
				
				"""),
			
			Chapter("Assignment", """
				VariableReference will always reference the declaration ( function argument,
				not an Assignment. so, Assignment will add value to the declaration node,
				menu will not show assignments. we could return to c-style assignment-as-expression
				with a nice wording, like <while <<a>, now becoming <b>,> is <5>...
				
				Assignment to SomethingNew..can lets see how it works as a special case
				
				"""),
			
			Chapter("notes", """
				children as a separate class, avoid __getattr__ magic, allow use of pyDatalog?
				class children
					_dict
					__getattr__
					_types

				"""),
			
			Chapter("notes", """
			
			
				(CNL)
				http://www.irisa.fr/LIS/softwares/squall/
			
				ctrl+enter immediate evaluation

				think the editor can be projectional as it is now,
				will see if it really fits seemless editing. and navigation
				could be primarily structure-based maybe
			
				lemon the language vs lemon the desktop environment..
			
				dont pursue the NodeReference "xpath" stuff, leave it for lemon. although:
				https://code.google.com/p/asq/
				
				connection to jena: http://code.google.com/p/python-graphite/
				
				compilation > interpreter, for this bootstrap
				this thing may be falling apart, but lets see if it can compile itself
				1 interaction
				2 model, syntax 
				how to extend the syntax system,
				requirements:
					input: possible syntaxes of each: True, False, Number
					output:
			"""),
					
			Chapter("type system notes", """
			http://lambda-the-ultimate.org/node/3145
			
			"""),

			Chapter("funky wishes", """
			voice recognition (samson?)
			eye tracking
			gradient color changing animation
			
			systemic changes to consider:
				projectured needs to be tried out and evaluated for a possible use as the base of lemon.
				maybe also emacs
			"""),
			
			Chapter("profiling", """
			python -m cProfile -s cumulative  new_shit.py
			"""),				
			Chapter("coupling to pygame", """
			* using pyglets event module (standalone, copied out)
			* frontend uses pygame
			* nodes handle pygame events (keyboard and mouse)
			* frontend could be divided from backend, just passing lines and events back and forth
			"""),
			Quote("""It may be simpler to learn a DSL than an equivalent class library, but many people would prefer learning the class library. Class libraries give you something familiar (paradigm + basic language structures) to hold on to, while a DSL is likely completely new. That perception - that a class library is learnable while a new language is a big risk - is a big stumbling block to LanguageOrientedProgramming. """, URL("http://c2.com/cgi/wiki?StumblingBlocksForDomainSpecificLanguages"))
			
					
		),

		Chapter("introduction", 
			Chapter("wtf is this? / Что это?",
			"""what you see in the editor window is a tree of AST nodes and other, helper,
			elements like gui widgets. They are rendered onto a text grid, and you can move
			around with a cursor...
			text is white, red <s and >s show starts and ends of elements
			you can move the cursor to a spot with green and yellow <>s,
			thats a Placeholder.
			the thing on the right side is a menu, and shows what node you are on,
			and what items you can insert in the place.
			
			"""),
			Chapter("accesibility", """done: color inversion, background color and font size. "posterization" (full black or white) is underway. . . .?
			hardcoded colors are currently getting out of hand
			"""),
			Chapter("speed", """try python -O ( ./faster.sh ), disables assertions, makes things usable"""),
			Chapter("license", """licensing is still a work in progress, to find or develop a suitable license.  for now, see this experiment: """,URL("https://github.com/koo5/Free-Man-License"),"""
			your contributions will be regarded as shared with this future license.
			(in legalese: all your contributions are MINE, untill the license is developed
			into proper legalese)
			""")
		),

		Credits(),

		Chapter("compost heap", 
			Note("""unasked questions:
					what does lemon stand for?
					Language Editing Monster!""")
		
					best syntax for literate-programming? one character starts comment block, different starts code block?
		
		)
		,ReadmeGenerator()
	], False)



class ReadmeGenerator(Syntaxed):

	def __init__(self):
		super(ReadmeGenerator, self).__init__()
		self.setch('body', List([
		Chapter("getting started", """
			requires python version 2 and pygame: 
			apt-get install python python-pygame
			or
			pip install --user pygame

			talk to us in #lemonparty on freenode (hey, we are already 2 there!)
			
			if latest version doesnt compile, try older: git checkout HEAD^
			"""),	
		NodeReference("docs/title=introduction/0"),
		NodeReference("docs/title=introduction/name=license")
		]))

		self.button = widgets.Button(self, "generate README.md")
		self.syntaxes = [[w('button'), nl(), ch('body')]]
		self.button.push_handlers(on_click = self.generate)
		
	def generate(self, widget):
		ping()
		f = open("README.md", "w")
		project._width = 80
		lines = project.project(self)
		for line in lines:
			for char in line:
				f.write(char[0])
			f.write("\n")
		f.close()
		

class Chapter(Collapsible):

	def __init__(self, title, *body):
		super(Chapter, self).__init__(False)
		self.title = widgets.Text(self, title)
		if isinstance(body[0], str):
			body = FancyText(list(body))
		else:
			body = List(list(body))
		self.setch('body', body)
		
	def render_items(self):
		if self.expanded:
			return [w('title'), nl(), ch('body')]
		else:
			return [w('title')]



class URL(str):
	
	pass
	
	
	
class FancyText(Node):

	def __init__(self, value):
		super(FancyText, self).__init__()
		#for i,x in enumerate(value):
		#	if isinstance(x, str):
		#		r = ""
		#		for line in x.split("\n"):
		#			r += line.strip()
		#		value[i] = Text(r)
		self.value = [x.strip() for x in value]
	def render(self):
		#return [ElementTag(x) for x in self.value]
		return [t(x) for x in self.value]
		
		
		
class NodeReference(Syntaxed):
	
	def __init__(self, path):
		super(NodeReference, self).__init__()
		assert(isinstance(path, str))
		self.path = widgets.Text(self, path)
		self.syntaxes = [[t("node path:"), w('path'), nl(), w('node')]]
		self.refresh_button = widgets.Button(self, "not found, refresh.")
		self.path.push_handlers(on_edit = self.refresh)
		self.refresh_button.push_handlers(on_click = self.refresh)
		self.node = self.refresh_button

	def refresh(self, widget):
		self.node = self.root.find(self.path.text)
		if self.node == None:
			self.node = self.refresh_button



class Credits(Syntaxed):

	def __init__(self):
		super(Credits, self).__init__()
		self.syntaxes = [[t("this project would suck much more without:")],
						 [t("theplic - made me write the doc")],
						 [t("gremble - actually understood the whole idea")],
 						 [t("AnkhMorporkian - his coding frenzy brought about the projection system")],
 						 [t("rszeno - had endless patience")],
						 [t("pyglet authors - lemon uses event.py copied from pyglet")],
						 [t("...")]]




"""
musings:
version control:
f1: propagate change to master

"lenses":
lense is a custom node
it is declared in some included module
we are in a "console" node - basically a statements list,
ctrl-enter executes current line
the syntax is "songmeanings" <songmeanings search text>
before prolog integration, menu can directly offer the songmeanings node. Asks songmeanings search text node for
autocomplete
SongmeaningsSearchText is a custom node...
in the guts, some sort of asynchronous def songmeanings_autocomplete(text) returning SongmeaningsSearchText nodes with data
or maybe SongmeaningsAuthor, SongmeaningsSong..






dbpedia:use SuRF
<fetch <dbpedia <dbpedia url>>>




status
===
3/6
==
running in pycharm in debugging mode is too slow. optimalization notes:
limiting the amount of lines rendered by render() is kinda useless until
we can limit if from the top, that is, not call render(root) but render(some other element)
and that needs thinking thru but must be doable. Simply dont care if something up there above
the screen changes. Touches upon textual vs nodal navigation. As does deleting children.
draw_menu() is slow, first should be redone to project()
draw_lines is the heavy bit that could be separated out into a C frontend, but that
could get inflexible if more features were wanted. Slightly better is making it a C module
for python..(calling pygame how?)
sanest option might be an alternative python interpreter, just dunno how that would work with pycharm


1/6
==
* added scrolling and sanitized cursor movement a bit
* crude ordering of menu using fuzzywuzzy, based on decl name

31/5
==
* i added some awareness of types to the editor so the slots of nodes can specify a type they accept, as opposed to just a python class of node
* also, added function definition and call nodes (must be tested out yet)
* well, rewrote half of nodes.py, its now typed.py

and pondering what i will do next

* have to introduce the Slot objects yet
* might redo the menu system to actually use the same way of rendering as nodes
* or might work on the contents of the menu..the "palettes" that each node type offers, so inserting nodes actually works again
* (?)or start extending the way Syntaxed specifies syntax now, like, for List, it would be '[', ListItemWithComma*, ListItem?, ']'
* ListItemWithComma, ListItem...implies the concrete syntax nodes would co-exist with the AST nodes..(?)

other todo options:
* triples: predicate definition node, accepts Text or URL as subject and object
* math notations (solve pygame unicode problem)
* add more notes to nodes
* bring shadowedtext back

or start working out what is needed for the more natural way of editing
you dont want to deal with a tree hierarchy all the time, instead,
just a flat list of tokens that keep background information
but i think what i got so far is relevant


PYTHONPATH=~/pygame_cffi pypy new_shit/new_shit.py



Levels of detail
IP systems also offer several levels of detail, allowing the programmer to "zoom in" or out. In the example above, the programmer could zoom out to get a level that would say something like:
<<print the numbers 1 to 10>>
en.wikipedia.org/wiki/Intentional_programming




"it" without code figuring out what is meant, draw an arrow instead
