import pygame
import fuzzywuzzy
from fuzzywuzzy import fuzz


#from collections import OrderedDict
from odict import OrderedDict

from compiler.ast import flatten
#import weakref


from dotdict import dotdict
from logger import ping, log
import element
import widgets
from menu import MenuItem, InfoMenuItem, HelpMenuItem
import tags
#better would be ch, wi, te, ?
from tags import ChildTag as ch, WidgetTag as w, TextTag as t, NewlineTag as nl, IndentTag as indent, DedentTag as dedent, ColorTag, EndTag, ElementTag#, MenuTag
import tags as asstags
asstags.asselement = element

import project
import colors




b = OrderedDict() #for staging builtins module and referencing builtin nodes by name, from python code




class val(list):
	"""
	a list of Values
	during execution, results of evaluation of every node is appended,
	so there is a history visible"""
	def val(self):
		"""the current value is the last one"""
		return self[-1]

	def append(self, x):
		assert(isinstance(x, Node))
		super(self, val).append(x)
		return x
	
	def set(self, x):
		"""constants call this"""
		assert(isinstance(x, Node))
		if len(self) > 0 and self[-1] == x:
			pass
		else:
			super(self, val).append(x)
		return x



class Node(element.Element):
	"""a node is more than an element,
	in the editor, nodes can be cut'n'pasted around on their own
	every node class has a corresponding decl object
	"""
	def __init__(self):
		super(Node, self).__init__()
		self.color = (0,255,0,255) #i hate hardcoded colors
		self.runtime = dotdict() #various runtime data herded into one place

	@property
	def compiled(self):
		return self

	def scope(self):
		"""what does this node see?"""
		r = []

		if isinstance(self.parent, List):
			r += [x.compiled for x in self.parent.above(self)]

		r += self.parent.scope()

		assert(r != None)
		assert(flatten(r) == r)
		return r

	def eval(self):
		self.runtime.value.append(self._eval())
		return self.runtime.value.val
	"""
	def program(self):
		if isinstance(self, Program):
			return self
		else:
			if self.parent != None:
				return self.parent.program()
			else:
				print self, "has no parent"
				return None
	"""
	@classmethod
	def fresh(cls):
		return cls()

	@classmethod
	def cls_palette(cls, scope):
		"generate menu item(s) with node(s) of this class"
		return []

	def on_keypress(self, e):
		if e.key == pygame.K_DELETE and e.mod & pygame.KMOD_CTRL:
			self.delete_self()
			return True

	def delete_self(self):
		self.parent.delete_child(self)



class Children(dotdict):
	pass

class Syntaxed(Node):
	"""
	Syntaxed has some named children, kept in ch.
	their types are in child_types, both are dicts
	syntax is a list of objects from module tags
	its all defined in its decl
	todo: differentiate between raw and compiled children
	todo: wrap child types in Slots, so eval/immediate can be specified
	"""
	def __init__(self, kids):
		super(Syntaxed, self).__init__()
		self.check_child_types()
		self.syntax_index = 0 #could be removed, one one variant of syntax is supported now
		self.ch = Children()
		assert(len(kids) == len(self.child_types))
		for k in self.child_types.iterkeys():
			self.setch(k, kids[k])

	def fix_parents(self):
		self._fix_parents(self.ch.values())

	def setch(self, name, item):
		assert(isinstance(name, str))
		assert(isinstance(item, Node))
		#if isinstance(item, Compiler):
			#if item.type
		item.parent = self
		self.ch[name] = item

	def replace_child(self, child, new):
		"""child name or child value? thats a good question...its child the value!"""
		assert(child in self.ch.itervalues())
		assert(isinstance(new, Node))
		for k,v in self.ch.iteritems():
			if v == child:
				self.ch[k] = new
				new.parent = self
				return
		else_raise_hell()

	def delete_child(self, child):
		self.replace_child(child, Compiler(b["text"])) #toho: create new_child()

	def flatten(self):
		assert(isinstance(v, Node) for v in self.ch.itervalues())
		return [self] + [v.flatten() for v in self.ch.itervalues()]

	def check_child_types(self):
		if __debug__:
			assert(isinstance(self.child_types, dict))
			for name, type in self.child_types.iteritems():
				assert(isinstance(name, str))
				assert(isinstance(type, (NodeclBase, Definition, ParametricType))) #what else works as a type?

	@property
	def syntax(self):
		return self.syntaxes[self.syntax_index]

	def render(self):
		return self.syntax

	def prev_syntax(self):
		self.syntax_index  -= 1
		if self.syntax_index < 0:
			self.syntax_index = 0
		log("prev")

	def next_syntax(self):
		self.syntax_index  += 1
		if self.syntax_index == len(self.syntaxes):
			self.syntax_index = len(self.syntaxes)-1
		log("next")

	def on_keypress(self, e):
		if pygame.KMOD_CTRL & e.mod:
			if e.key == pygame.K_PAGEUP:
				self.prev_syntax()
				return True
			if e.key == pygame.K_PAGEDOWN:
				self.next_syntax()
				return True

	@classmethod
	def new_kids(cls, slots):
		assert(isinstance(slots, dict))
		kids = {}
		#fix:
		for k, v in slots.iteritems(): #for each child:
			#print v
			if v in [b[x] for x in ['text', 'number', 'statements']]:
				#todo: definition, list
				a = v.inst_fresh()
			else:
				a = Compiler(v)
			assert(isinstance(a, Node))
			kids[k] = a
		return kids

	@classmethod
	def fresh(cls):
		r = cls(cls.new_kids(cls.decl.instance_slots))
		return r

	@property
	def name(self):
		"""override if this doesnt work for your subclass"""
		return self.ch.name.pyval

	@property
	def syntaxes(self):
		return [self.decl.instance_syntax] #got rid of multisyntaxedness for now

	@property
	def child_types(self):
		return self.decl.instance_slots








class Collapsible(Node):
	"""Collapsible - List or Dict -
	they dont have a title, just a collapse button, right of which first item is rendered
	"""
	def __init__(self, expanded=True, vertical=True):
		super(Collapsible, self).__init__()	
		self.expand_collapse_button = widgets.Button(self)
		self.expand_collapse_button.push_handlers(on_click=self.on_widget_click)
		self.expanded = expanded
		self.vertical = vertical
	
	def render(self):
		self.expand_collapse_button.text = ("-" if self.expanded else "+")
		return [w('expand_collapse_button')] + [indent()] + (self.render_items() if self.expanded else [nl()]) + [dedent()]
	
	def toggle(self):
		self.expanded = not self.expanded
		if self.expanded:
			print "expand"
		else:
			print "collapse"

	def on_widget_click(self, widget):
		if widget is self.expand_collapse_button:
			self.toggle()

	def _eval(self):
		for i in self.items:
			i.eval()
		return self

	@classmethod
	def fresh(cls, decl):
		r = cls()
		r.decl = decl
		return r



class Dict(Collapsible):
	def __init__(self, expanded=True):
		super(Dict, self).__init__(expanded)
		self.items = OrderedDict()
		
	def render_items(self):
		r = []
		for key, item in self.items.iteritems():
			r += [t(key), t(":"), indent(), nl()]
			r += [ElementTag(item)]
			r += [dedent(), nl()]
		return r

	def __getitem__(self, i):
		return self.items[i]

	def __setitem__(self, i, v):
		self.items[i] = v
		v.parent = self

	def fix_parents(self):
		super(Dict, self).fix_parents()
		self._fix_parents(self.items.values())

	def flatten(self):
		return [self] + [v.flatten() for v in self.items.itervalues() if isinstance(v, Node)]
		#skip Widgets, as in settings

	def add(self, (key, val)):
		assert(not self.items.has_key(key))
		self.items[key] = val
		assert(isinstance(key, str))
		assert(isinstance(val, element.Element))
		val.parent = self


class List(Collapsible):
	def __init__(self, expanded=True, vertical=True):
		#if self.item_type ..
		super(List, self).__init__(expanded, vertical)
		self.items = []

	def render_items(self):
		r = []
		for item in self.items:
			r += [ElementTag(item)]
			if self.vertical: r+= [nl()] 
		return r

	def __getitem__(self, i):
		return self.items[i]

	def __setitem__(self, i, v):
		self.items[i] = v
		v.parent = self

	def fix_parents(self):
		super(List, self).fix_parents()
		self._fix_parents(self.items)

	def on_keypress(self, e):
		item_index = self.insertion_pos(e.cursor)
		if e.key == pygame.K_DELETE and e.mod & pygame.KMOD_CTRL:
			if len(self.items) > item_index:
				del self.items[item_index]
			return True
		#???
		if e.key == pygame.K_RETURN:
			pos = self.insertion_pos(e.cursor)
			p = Compiler(self.item_type)
			p.parent = self
			self.items.insert(pos, p)
			return True

	def insertion_pos(self, (char, line)):
		i = -1
		for i, item in enumerate(self.items):
			#print i, item, item._render_start_line, item._render_start_char
			if (item._render_start_line >= line and
				item._render_start_char >= char):
				return i
		return i + 1

	def eval(self):
		for i in self.items:
			i.eval()
		self.runtime.evaluated = True
		return self.runtime.value.append(Value([x.runtime.value.val for x in self.items]))
			
	def flatten(self):
		return [self] + [v.flatten() for v in self.items if isinstance(v, Node)]

	def replace_child(self, child, new):
		assert(child in self.items)
		self.items[self.items.index(child)] = new
		new.parent = self

	def add(self, item):
		self.items.append(item)
		assert(isinstance(item, Node))
		item.parent = self

	def newline(self):
		p = Compiler(self.item_type)
		p.parent = self
		self.items.append(p)

	@property
	def item_type(self):
		assert(isinstance(self.decl, ParametricType))
		return self.decl.ch.itemtype

	def above(self, item):
		assert(item in self.items)
		r = []
		for i in self.items:
			if i == item:
				return r
			else:
				r.append(i)


class WidgetedValue(Node):
	"""basic one-widget values"""
	def __init__(self):
		super(WidgetedValue, self).__init__()	
	@property
	def pyval(self):
		return self.widget.value
	def render(self):
		return [w('widget')]

class Number(WidgetedValue):
	def __init__(self, value=""):
		super(Number, self).__init__()
		self.widget = widgets.Number(self, value)

class Text(WidgetedValue):
	"""this one is tricky, works as an "input buffer" in Compiler node.
	its weird but it seems a good place for the menu function
	its also tricky now because im experimenting with removing one set of brackets
	and rendering the widget directly
	"""

	def __init__(self, value=""):
		super(Text, self).__init__()
		self.widget = widgets.Text(self, value)

	def render(self):
		return self.widget.render()

	def on_keypress(self, e):
		return self.widget.on_keypress(e)

	def menu(self):
		if not isinstance(self.parent, Compiler):
			return []

		#ev = self.slot.evaluated
		#node type (slot) specifies if a child should be of given type directly or an expression that evaluates to it
		#function definition specifies if the argument should be evaluated for it
		type = self.parent.type #self.slot.type

		scope = self.scope()
		nodecls = [x for x in scope if isinstance(x, NodeclBase)]
		nodecls.remove(b['builtinfunctiondecl'])
		menu = flatten([x.palette(scope) for x in nodecls])

		#slot type is Nodecl or Definition or AbstractType or ParametrizedType
		#first lets search for things in scope that are already of that type
		#for i in menu:
		#	if i.value.decl.eq(type):
		#		v.score += 1

		for item in menu:
			v = item.value
			item.score += fuzz.partial_ratio(v.decl.name, self.pyval) #0-100
			#print item.value.decl, item.value.decl.works_as(type), type.target

			if item.value.decl.works_as(type):
				item.score += 200
			else:
				item.valid = False

			#search thru syntaxes
			#if isinstance(v, Syntaxed):
			#	for i in v.syntax:
			#		if isinstance(i, t):
			#			item.score += fuzz.partial_ratio(i.text, self.pyval)
			#search thru an actual rendering(including children)
			r = v.render()
			re = " ".join([i.text for i in r if isinstance(i, t)])
			item.score += fuzz.partial_ratio(re, self.pyval)


		#doing nothing is the default (replacing self with self)
		s = CompilerMenuItem(self)
		s.score = 1000
		s.valid = True
		menu.append(s)

		menu.sort(key=lambda i: i.score)
		menu.reverse()#umm...
		return menu


class Root(Dict):
	def __init__(self):
		super(Root, self).__init__()
		self.parent = None
		self.post_render_move_caret = 0 #the frontend checks this
		self.indent_length = 4 #is this even used?

	def render(self):
		#there has to be some default color for everything..
		return [ColorTag((255,255,255,255))] + self.render_items() + [EndTag()]

	def scope(self):#unused(?)
		return []

	def delete_child(self, child):
		log("I'm sorry Dave, I'm afraid I can't do that.")

	def delete_self(self):
		log("I'm sorry Dave, I'm afraid I can't do that ")


class Module(Syntaxed):
	"""module or program, really"""
	def __init__(self, kids):
		super(Module, self).__init__(kids)

	def add(self, item):
		self.ch.statements.add(item)

	def __getitem__(self, i):
		return self.ch.statements[i]

	def __setitem__(self, i, v):
		self.ch.statements[i] = v

	def scope(self):
		#crude, but for now..
		if self != self.root["builtins"]:
			return self.root["builtins"].ch.statements.items
		else:
			return [] #nothing above but Root




class Ref(Node):
	"""points to another node.
	if a node already has a parent, you just want to point to it, not own it"""
	#todo: separate typeref and ref?..varref..?
	def __init__(self, target):
		super(Ref, self).__init__()
		self.target = target
	def render(self):
		return [t('*'), t(self.target.name)]
	@property
	def name(self):
		return self.target.name
	def works_as(self, type):
		return self.target.works_as(type)



class NodeclBase(Node):
	"""a base for all nodecls. Nodecls declare that some kind of nodes can be created,
	know their python class ("instance_class"), syntax and shit
	usually does something like instance_class.decl = self so we can instantiates the
	classes in code without going thru a corresponding nodecl"""
	def __init__(self, instance_class):
		super(NodeclBase, self).__init__()
		self.instance_class = instance_class
		self.decl = None
	def render(self):
		return [t("builtin node:"), t(self.name)]
		# t(str(self.instance_class))]
	@property
	def name(self):
		return self.instance_class.__name__.lower() #i dunno why tolower..deal with it..or change it..
	def instantiate(self, kids):
		return self.instance_class(kids)
	def inst_fresh(self):
		""" fresh creates default children"""
		return self.instance_class.fresh()
	def palette(self, scope):
			return [CompilerMenuItem(self.instance_class.fresh())] + \
			       self.instance_class.cls_palette(scope)


	def works_as(self, type):
		if isinstance(type, Ref):
			type = type.target
		if self == type: return True
		#todo:go thru definitions and IsSubclassOfs, in what scope tho?





class TypeNodecl(NodeclBase):
	""" "pass me a type" kind of value
	instantiates Refs ..maybe should be TypeRefs
	"""
	def __init__(self):
		super(TypeNodecl, self).__init__(Ref)
		b['type'] = self #add me to builtins
		Ref.decl = self
	def palette(self, scope):
		nodecls = [x for x in scope if isinstance(x, (NodeclBase))]
		return [CompilerMenuItem(Ref(x)) for x in nodecls]



class Nodecl(NodeclBase):
	"""for simple nodes (Number, Text, Bool)"""
	def __init__(self, instance_class):
		super(Nodecl, self).__init__(instance_class)
		instance_class.decl = self
		b[self.name] = self
		instance_class.name = self.name




class SyntaxedNodecl(NodeclBase):
	"""
	child types of Syntaxed are like b["text"], they are "values",
	 children themselves are either Refs (pointing to other nodes),
	 or owned nodes (their .parent points to us)
	"""
	def __init__(self, instance_class, instance_syntax, instance_slots):
		super(SyntaxedNodecl , self).__init__(instance_class)
		instance_class.decl = self
		self.instance_slots = instance_slots
		self.instance_syntax = instance_syntax
		b[self.name] = self



class ParametricType(Syntaxed):
	"""like..list of <type>, the actual type will be a child of this node.
	 instantiated by ParametricNodecl"""
	def __init__(self, kids, decl):
		self.decl = decl
		super(ParametricType, self).__init__(kids)
	@property
	def child_types(self):
		return self.decl.type_slots
	@property
	def syntaxes(self):
		return [self.decl.type_syntax]
	def inst_fresh(self):
		return self.decl.instance_class.fresh(self)
	@classmethod
	def fresh(cls, decl):
		return cls(cls.new_kids(decl.type_slots), decl)
	@property
	def name(self):
		return "parametric type"



class ParametricNodecl(NodeclBase):
	"""says that "list of <type>" declaration could exist, instantiates it (ParametricType)
	only non Syntaxed types are parametric now(list and dict),
	so this contains the type instance's syntax and slots (a bit confusing)"""
	def __init__(self, instance_class, type_syntax, type_slots):
		super(ParametricNodecl, self).__init__(instance_class)
		self.type_slots = type_slots
		self.type_syntax = type_syntax
	def make_type(self, kids):
		return ParametricType(kids, self)
	def palette(self, scope):
		return [CompilerMenuItem(ParametricType.fresh(self))]
	#def obvious_fresh(self):
	#if there is only one possible node type to instantiate..












"""here we start putting stuff into b, which is then made into the builtins module"""

TypeNodecl() #..so you can say that your function returns a type, or something

[Nodecl(x) for x in [Number, Text]]

"""the stuff down here isnt well thought-out yet..the whole types thing.."""

class AbstractType(Syntaxed):
	"""this is a syntactical category(?) of nodes, used for "statement" and "expression" """
	def __init__(self, kids):
		super(AbstractType, self).__init__(kids)
SyntaxedNodecl(AbstractType,
               [t("abstract type:"), ch("name")],
               {'name': b['text']})













#just mocking up boolean properties here


class ObjectDeclaration(Syntaxed):
	"""just mocking stuff up"""
	def __init__(self, kids):
		super(ObjectDeclaration, self).__init__(kids)
	@classmethod
	def cls_palette(cls, scope):
		r = []
		for x in scope:
			x = x.compiled
			if x.decl == cls.decl:
				print x, x.decl, cls.decl
				r += [CompilerMenuItem(Ref(x))]
		return r

SyntaxedNodecl(ObjectDeclaration,
               [ch("name"), t("is an object")],
               {'name': b['text']})

class BooleanPropretyDeclaration(Syntaxed):
	"""just mocking stuff up"""
	def __init__(self, kids):
		super(BooleanPropretyDeclaration, self).__init__(kids)
SyntaxedNodecl(BooleanPropretyDeclaration,
               [ch("object"), t("can be"), ch("p1"), t("or"), ch("p2")],
               {'object': b['objectdeclaration'],
                'p1': b['text'],
				'p2': b['text']})

class BooleanProperty(Node):
	def __init__(self, value):
		super(BooleanProperty, self).__init__()
		self.value = value
	def render(self):
		return [t(value)]

class BooleanPropertyNodecl(NodeclBase):
	def __init__(self):
		super(BooleanPropertyNodecl, self).__init__(Ref)
		b['booleanproperty'] = self
		BooleanProperty.decl = self
	def palette(self, scope):
		r = []
		decls = [x for x in scope if isinstance(x, (BooleanPropretyDeclaration))]
		for d in decls:
			r += [CompilerMenuItem(BooleanProperty(x)) for x in [d.ch.p1, d.ch.p2]]
		return r

BooleanPropertyNodecl()

class BooleanPropretyAssignment(Syntaxed):
	def __init__(self, kids):
		super(BooleanPropretyAssignment, self).__init__(kids)
SyntaxedNodecl(BooleanPropretyAssignment,
               [ch("object"), t("is"), ch("property")],
               {'object': b['objectdeclaration'],
                'property': b['booleanproperty']})










#end of mocking up boolean properties, serious stuff ahead










class IsSubclassOf(Syntaxed):
	"""a relation between two existing"""
	def __init__(self, kids):
		super(IsSubclassOf, self).__init__(kids)

SyntaxedNodecl(IsSubclassOf,
               [ch("sub"), t("is a subclass of"), ch("sup")],
               {'sub': b['type'], 'sup': b['type']})

class Definition(Syntaxed):
	"""should have type functionality (work as a type)"""
	def __init__(self, kids):
		super(Definition, self).__init__(kids)
		b[self.ch.name.pyval] = self
	def inst_fresh(self):
		return self.ch.type.inst_fresh()

SyntaxedNodecl(Definition,
               [t("define"), ch("name"), t("as"), ch("type")], #expression?
               {'name': b['text'], 'type': b['type']})



b['statement'] = AbstractType({'name': Text("statement")})
b['expression'] =AbstractType({'name': Text("expression")})
b[0] = IsSubclassOf({'sub': Ref(b["expression"]), 'sup': Ref(b["statement"])})
#b[1] = IsSubclassOf([Ref(b["number"]), Ref(b["expression"])])
#b[2] = IsSubclassOf([Ref(b["somethingnew"]), Ref(b["expression"])])


b['list'] = ParametricNodecl(List,
                 [t("list of"), ch("itemtype")],
                 {'itemtype': b['type']})
b['dict'] = ParametricNodecl(Dict,
                 [t("dict from"), ch("keytype"), t("to"), ch("valtype")],
                 {'keytype': b['type'], 'valtype': b['type']})


#IsSubclassOf([Ref(b["list"]), Ref(b["expression"])])
#IsSubclassOf([Ref(b["dict"]), Ref(b["expression"])])


Definition({'name': Text("statements"), 'type': b['list'].make_type({'itemtype': Ref(b['statement'])})})

b['module'] = SyntaxedNodecl(Module,
               [t("module:"), nl(), ch("statements"), t("end.")],
               {'statements': b['statements']})

Definition({'name': Text("list of types"), 'type': b['list'].make_type({'itemtype': Ref(b['type'])})})

class Union(Syntaxed):
	def __init__(self, children):
		super(Union, self).__init__(children)

b['union'] = SyntaxedNodecl(Union,
               [t("union of"), ch("items")],
               {'items': b['list'].make_type({'itemtype': b['type']})}) #todo:should work with the definition from above instead
b['union'].notes="""should be "type or type or type..", but Syntaxed with a list is an easier implementation for now"""






"""
compiler node
"""





class Compiler(Node):
	"""the awkward input node with orange brackets"""
	def __init__(self, type):
		super(Compiler, self).__init__()
		self.type = type
		self.items = []
		self.add(Text(""))
		self.brackets_color = (255,155,0)
		self.decl = None

	@property
	def compiled(self):
		"""compilation isnt supported until logic programming is obtained,
		for now, just return what is there"""
		if len(self.items) < 2:
			#there is just the empty Text
			return self
		else:
			return self.items[1]

	def render(self):
		#replicating List functionality here
		r = []
		#r += [t("[")]
		for item in self.items:
			r += [ElementTag(item)]
		#r += [t("]")]
		if len(self.items) == 1 and isinstance(self.items[0], Text) and	self.items[0].pyval == "":
			r+=[ColorTag((100,100,100)), t('('+self.type.name+')'), EndTag()] #hint at the type expected
		return r

	def __getitem__(self, i):
		return self.items[i]

	def fix_parents(self):
		super(Compiler, self).fix_parents()
		self._fix_parents(self.items)

	def on_keypress(self, e):
		pass
	"""
		item_index = self.insertion_pos(e.cursor)
		if e.key == pygame.K_DELETE and e.mod & pygame.KMOD_CTRL:
			if len(self.items) > item_index:
				del self.items[item_index]
	"""
	"""
	def insertion_pos(self, (char, line)):
		i = -1
		for i, item in enumerate(self.items):
			#print i, item, item._render_start_line, item._render_start_char
			if (item._render_start_line >= line and
				item._render_start_char >= char):
				return i
		return i + 1
	"""
	def flatten(self):
		return [self] + [v.flatten() for v in self.items if isinstance(v, Node)]

	def add(self, item):
		self.items.append(item)
		assert(isinstance(item, Node))
		item.parent = self

	"""
	def replace_child(self, child, new):
		assert(child in self.items)
		self.items[self.items.index(child)] = new
		new.parent = self
		#add a blank at the end
		p = SomethingNew()
		p.parent = self
		self.items.append(p)
	"""
	"""
	def eval(self):
		i = self.items[0]
		i.eval()
		self.runtime = i.runtime
		return self.runtime.value.val
	"""

	def menu_item_selected(self, item, child):
		if not isinstance(item, CompilerMenuItem):
			log("not CompilerMenuItem")
			return

		if child in self.items:
			i = self.items.index(child)
			self.items[i] = item.value
			item.value.parent = self

			if not isemptytext(self.items[0]):
				n = Text()
				n.parent = self
				self.items.insert(0, n)
			if not isemptytext(self.items[-1]):
				n = Text()
				n.parent = self
				self.items.append(n)

		else:
			hmm()


def isemptytext(item):
	return isinstance(item, Text) and item.pyval == ""


# hack here, to make a menu item renderable by project.project
#i think ill redo the screen layout as two panes of projection
class CompilerMenuItem(MenuItem):
	def __init__(self, value):
		super(CompilerMenuItem, self).__init__()
		self.value = value
		self.score = 0
		self.brackets_color = (0,0,255)
		#(and so needs brackets_color)

	#PlaceholderMenuItem is not an Element, but still has tags(),
	#called by project.project called from draw()
	def tags(self):
		return [ColorTag((0,255,0)),w('value'), t(" - "+str(self.value.__class__.__name__)), EndTag()]
		#and abusing "w" for "widget" here...not just here...

	def draw(self, menu, s, font, x, y):
		#replicating draw_root, but for now..
		#project._width = ..
		lines = project.project(self)
		area = pygame.Rect((x,y,0,0))
		for row, line in enumerate(lines):
			for col, char in enumerate(line):
				chx = x + font['width'] * col
				chy = (y+2) + font['height'] * row
				sur = font['font'].render(
					char[0],False,
					char[1]['color'],
					colors.bg)
				s.blit(sur,(chx,chy))
				area = area.union((chx, chy, sur.get_rect().w, sur.get_rect().h+2))
		return area





"""

functions

"""




#todo function arguments:#mode = eval/pass, untyped argument,
#todo optional function return type
#todo: show and hide argument names. syntaxed?

class TypedArgument(Syntaxed):
	def __init__(self, kids):
		super(TypedArgument, self).__init__(kids)

SyntaxedNodecl(TypedArgument,
               [ch("name"), t("-"), ch("type")],
               {'name': b['text'], 'type': b['type']})

tmp = b['union'].inst_fresh()
tmp.ch["items"].add(Ref(b['text']))
tmp.ch["items"].add(Ref(b['typedargument']))
Definition({'name': Text('function signature items'), 'type': tmp})

tmp = b['list'].make_type({'itemtype': Ref(b['function signature items'])})
Definition({'name': Text('function signature list'), 'type':tmp})




class FunctionDefinitionBase(Syntaxed):

	def __init__(self, kids):
		super(FunctionDefinitionBase, self).__init__(kids)
	@property
	def arg_types(self):
		if isinstance(self.sig, (List, Compiler)):#avoid crashes before sorting this out
			args = [i for i in self.sig.items if isinstance(i, TypedArgument)]
			return [i.ch.type for i in args]
		else: return []
	@property
	def sig(self):
		return self.ch.sig

class FunctionDefinition(FunctionDefinitionBase):

	def __init__(self, kids):
		super(FunctionDefinition, self).__init__(kids)

SyntaxedNodecl(FunctionDefinition,
               [t("deffun:"), ch("sig"), t(":\n"), ch("body")],
				{'sig': b['function signature list'],
				 'body': b['statements']})


"""
class PassedFunctionCall(Syntaxed):
	def __init__(self, definition):
		super(FunctionCall, self).__init__()
		assert isinstance(definition, FunctionDefinition)
		self.definition = definition
		self.arguments = List([Placeholder() for x in range(len(self.definition.signature.items.items))], vertical=False) #todo:filter out Texts

	def render(self):
		r = [t('(call)')]
		for i in self.definition.signature.items:
			if isinstance(i, Text):
				r += [t(i.widget.text)]
			elif isinstance(i, ArgumentDefinition):
				r += [ElementTag(self.arguments.items[i])]

		return r
"""


"""
class PythonFunctionDecl(Syntaxed):
	def __init__(self, fun, sig, arg):
		self.setch('signature', FunctionSignature(sig))


PythonFunctionDecl(
	operator.div,
	signature = [ad("left"), tl("/"), ad("right")],
	arg_types = {'left': b['expression'], 'right': b['expression']})
"""


class BuiltinFunctionDecl(FunctionDefinitionBase):
	def __init__(self, kids):
		super(BuiltinFunctionDecl, self).__init__(kids)
	@staticmethod
	def create(name, fun, sig):
		x = BuiltinFunctionDecl.fresh()
		b[name] = x
		x.ch.name.widget.value = name
		x.fun = fun
		x.ch.sig.items = sig


SyntaxedNodecl(BuiltinFunctionDecl,
               [t("builtin function"), ch("name"), t(":"), ch("sig")],
				{'sig': b['function signature list'],
				 'name': b['text']})

def multiply_eval(args):
		l,r = args.left.eval(), args.right.eval()
		assert(isinstance(l, Value))
		assert(isinstance(r, Value))
		res = Value(b['number'], l.value * r.value)
		return res

BuiltinFunctionDecl.create("multiply",
                           multiply_eval,
	[	TypedArgument({'name': Text("left"), 'type': Ref(b['number'])}),
		Text("*"),
		TypedArgument({'name': Text("right"), 'type': Ref(b['number'])})])

"""
def print_eval(args):
		v = args.expression.eval()
		assert(isinstance(v, Value))
		res = Value(b['number'], l.value * r.value)
		return res

BuiltinFunctionDecl.create("print",
                           print_eval,
		[ Text("print"), TypedArgument({'name': Text("expression"), 'type': Ref(b['expression'])})])
"""

class FunctionCall(Node):
	def __init__(self, target):
		super(FunctionCall, self).__init__()
		assert isinstance(target, FunctionDefinitionBase)
		self.target = target
		self.args = [Compiler(v) for v in self.target.arg_types]
		self._fix_parents(self.args)

	def replace_child(self, child, new):
		assert(child in self.args)
		self.args[self.args.index(child)] = new
		new.parent = self


	def render(self):
		r = [t('!')]
		argument_index = 0
		if not isinstance(self.target.sig, (List, Compiler)):
			r+=[t("sig not List, " + str(self.target.sig))]
		else:
			for v in self.target.sig:
				if isinstance(v, Text):
					r += [t(v.pyval)]
				elif isinstance(v, TypedArgument):
					r += [ElementTag(self.args[argument_index])]
					argument_index+=1
		return r

	@staticmethod
	def palette(scope):
		defuns = [x for x in scope if isinstance(x,(BuiltinFunctionDecl, FunctionDefinition))]
		return [CompilerMenuItem(FunctionCall(x)) for x in defuns]





class FunctionCallNodecl(NodeclBase):
	def __init__(self):
		super(FunctionCallNodecl, self).__init__(Ref)
		b['call'] = self
		FunctionCall.decl = self
	def palette(self, scope):
		decls = [x for x in scope if isinstance(x, (FunctionDefinitionBase))]
		return [CompilerMenuItem(FunctionCall(x)) for x in decls]

FunctionCallNodecl()


"""the end"""


def make_root():
	r = Root()
	r.add(("program", b['module'].inst_fresh()))
	r["program"].ch.statements.newline()
	r.add(("builtins", b['module'].inst_fresh()))
	r["builtins"].ch.statements.items = list(b.itervalues())
	return r



