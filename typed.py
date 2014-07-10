import pygame
import fuzzywuzzy
from fuzzywuzzy import fuzz


#from collections import OrderedDict
from odict import OrderedDict #be compatible with older python

from compiler.ast import flatten
#import weakref


from dotdict import dotdict
from logger import ping, log
import element
import widgets
from menu_items import MenuItem
import tags
#better would be ch, wi, te, ?
from tags import ChildTag as ch, WidgetTag as w, TextTag as t, NewlineTag as nl, IndentTag as indent, DedentTag as dedent, ColorTag, EndTag, ElementTag, AttTag#, MenuTag
import tags as asstags
asstags.asselement = element

import project
import colors




b = OrderedDict() #for staging the builtins module and referencing builtin nodes from python code




class val(list):
	"""
	a list of Values
	during execution, results of evaluation of every node is appended,
	so there is a history visible"""
	@property
	def val(self):
		"""the current value is the last one"""
		return self[-1]

	def append(self, x):
		assert(isinstance(x, Node))
		super(val, self).append(x)
		return x
	
	def set(self, x):
		"""constants call this"""
		assert(isinstance(x, Node))
		if len(self) > 0:
			self[0] = x
		else:
			super(val, self).append(x)
		return x




class Node(element.Element):
	"""a node is more than an element,
	in the editor, nodes can be cut'n'pasted around on their own
	every node class has a corresponding decl object
	"""
	def __init__(self):
		super(Node, self).__init__()
		#self.color = (0,255,0,255) #i hate hardcoded colors
		self.brackets_color = "node brackets"
		self.runtime = dotdict() #various runtime data herded into one place
		self.clear_runtime_dict()
		self.isconst = False

	def clear_runtime_dict(s):
		s.runtime._dict.clear()
		s.runtime.value = val()

	@property
	def compiled(self):
		return self

	def scope(self):
		"""what does this node see?"""
		r = []

		if isinstance(self.parent, List):
			r += [x.compiled for x in self.parent.above(self)]

		r += [self.parent]
		r += self.parent.scope()

		assert(r != None)
		assert(flatten(r) == r)
		return r

	def eval(self):
		r = self._eval()
		assert isinstance(r, Node), str(self) + " _eval is borked"
		if self.isconst:
			self.runtime.value.set(r)
			log("const" + str(self))
		else:
			self.runtime.value.append(r)
		self.runtime.evaluated = True
		r.parent = self.parent

		return r

	def _eval(self):
		self.runtime.unimplemented = True
		return Text("not implemented")

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
		if e.key == pygame.K_F7:
			self.eval()
			return True

	def delete_self(self):
		self.parent.delete_child(self)

	#i dont get any visitors here, nor should my code
	def flatten(self):
		print self, "flattens to self"
		return [self]

	def to_python_str(self):
		return str(self)

	@property
	def vardecls(s):
		return []

	def to_python_str(s):
		return str(s)

class Children(dotdict):
	pass

class Syntaxed(Node):
	"""
	Syntaxed has some named children, kept in ch.
	their types are in child_types, both are dicts
	syntax is a list of objects from module tags
	its all defined in its decl
	"""
	def __init__(self, kids):
		super(Syntaxed, self).__init__()
		self.check_slots(self.slots)
		self.syntax_index = 0 #could be removed, alternative syntaxes arent supported now
		self.ch = Children()
		assert(len(kids) == len(self.slots))
		for k in self.slots.iterkeys():
			self.setch(k, kids[k])

	def fix_parents(self):
		self._fix_parents(self.ch._dict.values())

	def setch(self, name, item):
		assert(isinstance(name, str))
		assert(isinstance(item, Node))
		item.parent = self
		self.ch[name] = item
		#todo:log if not Compiler and not correct type

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
		#todo:refactor into find_child or something
	def delete_child(self, child):
		for k,v in self.ch.iteritems():
			if v == child:
				self.ch[k] = self.create_kids(self.slots)[k]
				new.parent = self
				return
		shit()
		#self.replace_child(child, Compiler(b["text"])) #toho: create new_child()

	def flatten(self):
		assert(isinstance(v, Node) for v in self.ch._dict.itervalues())
		return [self] + [v.flatten() for v in self.ch._dict.itervalues()]

	@staticmethod
	def check_slots(slots):
		if __debug__:
			assert(isinstance(slots, dict))
			for name, slot in slots.iteritems():
				assert(isinstance(name, str))
				assert isinstance(slot, (NodeclBase, Exp, ParametricType, Definition))


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
			if e.key == pygame.K_COMMA:
				self.prev_syntax()
				return True
			if e.key == pygame.K_COLON:
				self.next_syntax()
				return True
		return super(Syntaxed, self).on_keypress(e)

	@classmethod
	def create_kids(cls, slots):
		cls.check_slots(slots)
		kids = {}
		#fix:
		for k, v in slots.iteritems(): #for each child:
			#print v # and : #todo: definition, syntaxclass. proxy is_literal(), or should that be inst_fresh?
			if v in [b[x] for x in [y for y in ['text', 'number', 'statements', 'list', 'function signature list', 'untypedvar' ] if y in b]]:
				a = v.inst_fresh()
				#if v == b['statements']:
					#a.newline()#so, statements should be its own class and be defined as list of statment at the same time,
					#so the class could implement extra behavior like this?
			else:
				a = Compiler(v)
			assert(isinstance(a, Node))
			kids[k] = a
		return kids

	@classmethod
	def fresh(cls):
		r = cls(cls.create_kids(cls.decl.instance_slots))
		return r

	@property
	def name(self):
		"""override if this doesnt work for your subclass"""
		return self.ch.name.pyval

	@property
	def syntaxes(self):
		return [self.decl.instance_syntax] #got rid of multisyntaxedness for now

	@property
	def slots(self):
		return self.decl.instance_slots






class Collapsible(Node):
	"""Collapsible - List or Dict -
	they dont have a title, just a collapse button, right of which first item is rendered
	"""
	vm_collapsed = 0
	vm_oneline = 1
	vm_multiline = 2
	def __init__(self):
		super(Collapsible, self).__init__()	
		self.view_mode_widget = widgets.NState(self, 0, ("+","v","-"))

	@property
	def view_mode(s):
		return s.view_mode_widget.value
	@view_mode.setter
	def view_mode(s, m):
		s.view_mode_widget.value = m

	def render(self):
		return [w('view_mode_widget')] + [indent()] + (self.render_items() if self.view_mode > 0 else []) + [dedent()]
	
	@classmethod
	#watch out: List has its own
	def fresh(cls, decl):
		r = cls()
		r.decl = decl
		return r



class Dict(Collapsible):
	def __init__(self):
		super(Dict, self).__init__()
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
		return [self] + [v.flatten() for v in self.items.itervalues() if isinstance(v, Node)]#skip Widgets, for Settings

	def add(self, (key, val)):
		assert(not self.items.has_key(key))
		self.items[key] = val
		assert(isinstance(key, str))
		assert(isinstance(val, element.Element))
		val.parent = self


#todo: view ordering
class List(Collapsible):
	def __init__(self):
		super(List, self).__init__()
		self.items = []

	def render_items(self):
		r = [t('[')]
		for item in self.items:
			r += [ElementTag(item)]
			if self.view_mode == 2:
				r+= [nl()]
			else:
				r+= [t(', ')]
			#we will have to work towards having this kind of syntax
			#defined declaratively so Compiler can deal with it
		r += [t(']')]
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
		item_index = self.insertion_pos(e.frame, e.cursor)
		if e.key == pygame.K_DELETE and e.mod & pygame.KMOD_CTRL:
			if len(self.items) > item_index:
				del self.items[item_index]
			return True
		#???
		if e.key == pygame.K_RETURN:
			pos = self.insertion_pos(e.frame, e.cursor)
			p = Compiler(self.item_type)
			p.parent = self
			self.items.insert(pos, p)
			return True

	def insertion_pos(self, frame, (char, line)):
		i = -1
		for i, item in enumerate(self.items):
			if (item._render_lines[frame]["startline"] >= line and
				item._render_lines[frame]["startchar"] >= char):
				return i
		return i + 1

	def _eval(self):
		r = List()
		r.decl = self.decl
		r.items = [i.eval() for i in self.items]
		r.fix_parents()
		return r

	def copy(self):
		r = List()
		r.decl = self.decl
		r.items = [i.copy() for i in self.items]
		r.fix_parents()
		return r

	def flatten(self):
		return [self] + flatten([v.flatten() for v in self.items])

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

	def to_python_str(self):
		return "[" + ", ".join([i.to_python_str() for i in self.items]) + "]"

	@classmethod
	def fresh(cls, decl):
		r = cls()
		r.decl = decl
		r.newline()
		return r

	def delete_child(s, ch):
		if ch in s.items:
			s.items.remove(ch)



class Statements(List):
	def __init__(s):
		super(Statements, s).__init__()
		s.view_mode = Collapsible.vm_multiline
	@classmethod
	def fresh(cls):
		r = cls()
		r.newline()
		return r
	@property
	def item_type(self):
		return b['statement']
	@staticmethod
	def match(text):
		return None
	def render_items(self):
		r = []
		for item in self.items:
			r += [ElementTag(item)]
			if self.view_mode == 2:
				r+= [nl()]
			else:
				r+= [t(', ')]
			#we will have to work towards having this kind of syntax
			#defined declaratively so Compiler can deal with it
		r += []
		return r
	def run(self):
		[i.eval() for i in self.items]
		return Text("banana")



class Void(Node):
	"i dont like it"
	def __init__(self):
		super(Void, self).__init__()
	def render(self):
		return [t('void')]
	def to_python_str(self):
		return "void"


class WidgetedValue(Node):
	"""basic one-widget values"""
	def __init__(self):
		super(WidgetedValue, self).__init__()	
		self.isconst = True
	@property
	def pyval(self):
		return self.widget.value
	def render(self):
		return [w('widget')]
	def to_python_str(self):
		return str(self.pyval)
	def copy(s):
		return s.eval()
	def flatten(self):
		return [self]

class Number(WidgetedValue):
	def __init__(self, value="0"):
		super(Number, self).__init__()
		self.widget = widgets.Number(self, value)
		self.widget.brackets = ('','')
	def _eval(self):
		return Number(self.pyval)

	@staticmethod
	def match(text):
		"return score"
		if text.isdigit():
			return 300



class Text(WidgetedValue):

	def __init__(self, value=""):
		super(Text, self).__init__()
		self.widget = widgets.Text(self, value)
		self.brackets_color = "text brackets"
		self.brackets = ('[',']')

	def render(self):
		return self.widget.render()

	def on_keypress(self, e):
		return self.widget.on_keypress(e)

	def _eval(self):
		return Text(self.pyval)

	def __repr__(s):
		return object.__repr__(s) + "('"+s.pyval+"')"

	@staticmethod
	def match(text):
		return 100


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

	def clear(self):
		st = self.ch.statements
		#print "flatten:", st.flatten()
		for i in st.flatten():
			i.clear_runtime_dict()

	def run(self):
		self.clear()
		return self.ch.statements.run()

	def run_line(self, node):
		self.clear()
		while node != None and node not in self.ch.statements.items:
			node = node.parent
		if node:
			return node.eval()


class Ref(Node):
	"""points to another node.
	if a node already has a parent, you just want to point to it, not own it"""
	#todo: separate typeref and ref?..varref..?
	def __init__(self, target):
		super(Ref, self).__init__()
		self.target = target
	def render(self):
		return [t('*'), tags.ArrowTag(self.target), t(self.name)]
	@property
	def name(self):
		return self.target.name
	def works_as(self, type):
		return self.target.works_as(type)

class VarRef(Node):
	def __init__(self, target):
		super(VarRef, self).__init__()
		self.target = target
		assert isinstance(target, UntypedVar)
		log("varref target:"+str(target))
	def render(self):
		return [t('$'), tags.ArrowTag(self.target), t(self.name)]
	@property
	def name(self):
		return self.target.name
	def _eval(s):
		return s.target.runtime.value.val

class Exp(Node):
	def __init__(self, type):
		super(Exp, self).__init__()
		self.type = type
	def render(self):
		return [w("type"), t('expr')]
	@property
	def name(self):
		return self.type.name + " expr"


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
	def palette(self, scope, text):
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
	def palette(self, scope, text):
		nodecls = [x for x in scope if isinstance(x, (NodeclBase))]
		return [CompilerMenuItem(Ref(x)) for x in nodecls]

class VarRefNodecl(NodeclBase):
	def __init__(self):
		super(VarRefNodecl, self).__init__(VarRef)
		b['varref'] = self #add me to builtins
		VarRef.decl = self
	def palette(self, scope, text):
		r = []
		for x in scope:
			xc=x.compiled
			for y in x.vardecls:
				yc=y.compiled
				#log("vardecl compiles to: "+str(yc))
				if isinstance(yc, (UntypedVar, TypedArgument)):
					#log("vardecl:"+str(yc))
					r += [CompilerMenuItem(VarRef(yc))]
		#log (str(scope)+"varrefs:"+str(r))
		return r

class ExpNodecl(NodeclBase):
	def __init__(self):
		super(ExpNodecl, self).__init__(Exp)
		b['exp'] = self #add me to builtins
		Exp.decl = self
	def palette(self, scope, text):
		nodecls = [x for x in scope if isinstance(x, (NodeclBase))]
		return [CompilerMenuItem(Exp(x)) for x in nodecls]



class Nodecl(NodeclBase):
	"""for simple nodes (Number, Text, Bool)"""
	def __init__(self, instance_class):
		super(Nodecl, self).__init__(instance_class)
		instance_class.decl = self
		b[self.name] = self
		instance_class.name = self.name

	def palette(self, scope, text):
		r = CompilerMenuItem(666)
		i = self.instance_class

		m = i.match(text)
		if m:
			r.value = i(text)
			r.score = m
		else:
			r.value = i()
		return r



class SyntaxedNodecl(NodeclBase):
	"""
	child types of Syntaxed are like b["text"], they are "values",
	 children themselves are either Refs (pointing to other nodes),
	 or owned nodes (their .parent points to us)
	"""
	def __init__(self, instance_class, instance_syntax, instance_slots):
		super(SyntaxedNodecl , self).__init__(instance_class)
		instance_class.decl = self
		self.instance_slots = dict([(k, b[i] if isinstance(i, str) else i) for k,i in instance_slots.iteritems()])
		self.instance_syntax = instance_syntax
		b[self.instance_class.__name__.lower()] = self

	"""
	syntaxed match(items, nodes) :-

	Text match(item, nodes) :-
		isinstance(item, Text) and item.pyval.isnum() and

	FunctionDefinition match(items, nodes
		for s, i in zip(self.sig, items)
			if isinstance(s, Text):
				if isinstance(i, Text):
					i.pyval
	"""

class ParametricType(Syntaxed):
	"""like..list of <type>, the <type> will be a child of this node.
	 ParametricType is instantiated by ParametricNodecl"""
	def __init__(self, kids, decl):
		self.decl = decl
		super(ParametricType, self).__init__(kids)
	@property
	def slots(self):
		return self.decl.type_slots
	@property
	def syntaxes(self):
		return [self.decl.type_syntax]
	def inst_fresh(self):
		return self.decl.instance_class.fresh(self)
	@classmethod
	def fresh(cls, decl):
		return cls(cls.create_kids(decl.type_slots), decl)
	@property
	def name(self):
		return "parametric type (fix this)"
		#todo: refsyntax?

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
	def palette(self, scope, text):
		return [CompilerMenuItem(ParametricType.fresh(self))]
	#def obvious_fresh(self):
	#if there is only one possible node type to instantiate..


"""here we start putting stuff into b, which is then made into the builtins module"""

TypeNodecl() #..so you can say that your function returns a type value, or something
VarRefNodecl()

[Nodecl(x) for x in [Number, Text, Statements]]

"""the stuff down here isnt well thought-out yet..the whole types thing.."""

class SyntacticCategory(Syntaxed):
	"""this is a syntactical category(?) of nodes, used for "statement" and "expression" """
	def __init__(self, kids):
		super(SyntacticCategory, self).__init__(kids)
		b[self.ch.name.pyval] = self


class WorksAs(Syntaxed):
	"""a relation between two existing"""
	def __init__(self, kids):
		super(WorksAs, self).__init__(kids)
		b[self] = self
	@classmethod
	def b(cls, sub, sup):
		cls({'sub': Ref(b[sub]), 'sup': Ref(b[sup])})


class Definition(Syntaxed):
	"""should have type functionality (work as a type)"""
	def __init__(self, kids):
		super(Definition, self).__init__(kids)
		b[self.ch.name.pyval] = self
	def inst_fresh(self):
		return self.ch.type.inst_fresh()

class Union(Syntaxed):
	def __init__(self, children):
		super(Union, self).__init__(children)


SyntaxedNodecl(SyntacticCategory,
			   [t("syntactic category:"), ch("name")],
			   {'name': 'text'})
SyntaxedNodecl(WorksAs,
			   [ch("sub"), t("works as"), ch("sup")],
			   {'sub': 'type', 'sup': 'type'})
SyntaxedNodecl(Definition,
			   [t("define"), ch("name"), t("as"), ch("type")], #expression?
			   {'name': 'text', 'type': 'type'})

SyntacticCategory({'name': Text("statement")})
SyntacticCategory({'name': Text("expression")})
WorksAs.b("expression", "statement")
WorksAs.b("number", "expression")
WorksAs.b("text", "expression")

b['list'] = ParametricNodecl(List,
				 [t("list of"), ch("itemtype")],
				 {'itemtype': b['type']})
b['dict'] = ParametricNodecl(Dict,
				 [t("dict from"), ch("keytype"), t("to"), ch("valtype")],
				 {'keytype': b['type'], 'valtype': Exp(b['type'])})

WorksAs.b("list", "expression")
WorksAs.b("dict", "expression")

#Definition({'name': Text("statements"), 'type': b['list'].make_type({'itemtype': Ref(b['statement'])})})

SyntaxedNodecl(Module,
			   ["module:\n", ch("statements"),  t("end.")],
			   {'statements': b['statements']})

Definition({'name': Text("list of types"), 'type': b['list'].make_type({'itemtype': Ref(b['type'])})})

SyntaxedNodecl(Union,
			   [t("union of"), ch("items")],
			   {'items': b['list'].make_type({'itemtype': b['type']})}) #todo:should work with the definition from above instead
b['union'].notes="""should appear as "type or type or type", but a Syntaxed with a list is an easier implementation for now"""



class UntypedVar(Syntaxed):
	def __init__(self, kids):
		super(UntypedVar, self).__init__(kids)

SyntaxedNodecl(UntypedVar,
			   [ch("name")],
			   {'name': 'text'})

class For(Syntaxed):
	def __init__(self, children):
		super(For, self).__init__(children)
	@property
	def vardecls(s):
		return [s.ch.item]
	def _eval(s):
		items = s.ch.items.eval()
		assert isinstance(items, List)
		itemvar = s.ch.item.compiled
		assert isinstance(itemvar, UntypedVar)
		#r = b['list'].make_type({'itemtype': Ref(b['statement'])}).make_inst() #just a list of the "anything" type..dunno
		for item in items:
			itemvar.runtime.value.append(item)
			s.ch.body.run()

		return Void()

SyntaxedNodecl(For,
			   [t("for"), ch("item"), t("in"), ch("items"),
			        ":\n", ch("body")],
			   {'item': b['untypedvar'],
			    'items': Exp(
				    b['list'].make_type({
				        'itemtype': Ref(b['type'])
				    })),
			   'body': b['statements']})


"""
class Filter(Syntaxed):
	def __init__(self, kids):
		super(Filter, self).__init__(kids)
"""

class UntypedVar(Syntaxed):
	def __init__(self, kids):
		super(UntypedVar, self).__init__(kids)

SyntaxedNodecl(UntypedVar,
			   [ch("name")],
			   {'name': 'text'})




"""
compiler node

todo:hack it so that the first node, when a second node is added, is set as the
leftmost child of the second node..or maybe not..dunno
"""





class Compiler(Node):
	"""the awkward input node with orange brackets"""
	def __init__(self, type):
		super(Compiler, self).__init__()
		self.type = type
		assert isinstance(type, (Ref, NodeclBase, Exp, ParametricType, Definition, SyntacticCategory))
		#..in short, everything that works as a type..abstract it away later
		self.items = []
		self.brackets_color = "compiler brackets" #bye:)
		self.brackets = ('{', '}')
		self.decl = None #i am a free man, not a number!
		self.register_event_types('on_edit')

	@property
	def compiled(self):
		#default result:
		#raise an exception? make a NotCompiled node?
		r = Text("?"+str(self.items))

		if len(self.items) == 1:
			i0 = self.items[0]
			if isinstance(i0, Node):
				r = i0
			#demodemodemo
			elif isinstance(self.type, Ref):
				if self.type.target == b['text']:
					r = Text(i0)
				if self.type.target == b['number']:
					if Number.match(i0):
						r = Number(i0)

		r.parent = self
		#log(self.items, "=>", r)
		return r

	def _eval(self):
		return self.compiled.eval()

	def render(self):
		if len(self.items) == 0: #hint at the type expected
			return [ColorTag("compiler hint"), t('('+self.type.name+')'), EndTag()]

		r = []
		for i, item in enumerate(self.items):
			r += [AttTag("compiler item", i)]
			if isinstance(item, (str, unicode)):
				for j, c in enumerate(item):
					r += [AttTag("compiler item char", j), t(c), EndTag()]
			else:
				r += [ElementTag(item)]
			r += [EndTag()]
		return r

	def __getitem__(self, i):
		return self.items[i]

	@property
	def nodes(s):
		return [i for i in s.items if isinstance(i, Node) ]

	def fix_parents(self):
		super(Compiler, self).fix_parents()
		self._fix_parents(self.nodes)

	#this is a total mess and still doesnt work, needs to be rethinked
	#i could throw more info into the tags stream, about individual brackets
	#the backspace/forward problem isnt really specific to this nodeless thing tho,
	#it will have to be dealt with between/in nodes too
	def on_keypress(self, e):

		if not e.mod & pygame.KMOD_CTRL:
			assert self.root.post_render_move_caret == 0
			its = self.items

			if e.uni and e.key not in [pygame.K_ESCAPE, pygame.K_RETURN]:

				if len(its) == 0:
					self.items.append("")
					i = 0
					char = 0
					log("add")
					self.root.post_render_move_caret -= e.atts['char_index']

				else:
					i = self.mine(e.atts)
					if i != None:
					#cursor on my item
						if isinstance(its[i], (str, unicode)):
						#cursor on text
							if "compiler item char" in e.atts:
								char = e.atts["compiler item char"]
							else:
								char = len(its[i])
						else:
						#cursor on node
							return False
					else:
						#should test here if its on our closing bracket
						return False

				"""
				if e.key == pygame.K_BACKSPACE:
					if pos > 0 and len(self.text) > 0 and pos <= len(self.text):
						self.text = self.text[0:pos -1] + self.text[pos:]
		#				log(self.text)
						self.root.post_render_move_caret = -1
				if e.key == pygame.K_DELETE:
					if pos >= 0 and len(self.text) > 0 and pos < len(self.text):
						self.text = self.text[0:pos] + self.text[pos + 1:]
				"""

				#log(e)
				text = its[i]
				its[i] = text[:char] + e.uni + text[char:]
				self.root.post_render_move_caret += len(e.uni)

				#log(self.text + "len: " + len(self.text))
				self.dispatch_event('on_edit', self)
				return True

		return super(Compiler, self).on_keypress(e)

	def flatten(self):
		return [self] + flatten([v.flatten() for v in self.items if isinstance(v, Node)])

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

	def mine(self, atts):
		if "compiler item" in atts and atts["compiler item"] in self.items:
			return self.items.index(atts["compiler item"])
		elif len(self.items) != 0 and atts["node"] == self:
			#cursor is on the closing bracket of Compiler
			return len(self.items) - 1
		#else None

	def menu_item_selected(self, item, atts):
		assert isinstance(item, CompilerMenuItem)
		node = item.value

		#add it to our items
		i = self.mine(atts) #get index of my item under cursor
		if i != None:
			self.items[i] = node
		else:
			self.items.append(node)
		node.parent = self

		#move cursor to first child. this should go somewhere else.
		log(node)
		if isinstance(node, Syntaxed):
			for i in node.syntax:
				if isinstance(i, ch):
					self.root.post_render_move_caret = node.ch[i.name]
					break
		elif isinstance(node, FunctionCall):
			if len(node.args) > 0:
				self.root.post_render_move_caret = node.args[0]






	def menu(self, atts):


		i = self.mine(atts)
		if i == None:
			if len(self.items) == 0:
				text = ""
			else:
				return []
		else:
			if isinstance(self.items[i], Node):
				text = ""
			else:
				text = self.items[i]

		#print 'menu for:',text


		scope = self.scope()
		nodecls = [x for x in scope if isinstance(x, NodeclBase)]
		if b['builtinfunctiondecl'] in nodecls:#with the simplistic "scope" being simply items above us, some Compiler in builtins might not see it
			nodecls.remove(b['builtinfunctiondecl'])
		menu = flatten([x.palette(scope, text) for x in nodecls])

		#slot type is Nodecl or Definition or AbstractType or ParametrizedType
		#first lets search for things in scope that are already of that type
		#for i in menu:
		#	if i.value.decl.eq(type):
		#		v.score += 1

		type = self.type
		if isinstance(type, Exp):
			type = type.type
			exp = True
		else:
			exp = False


		for item in menu:
			v = item.value
			try:
				item.score += fuzz.partial_ratio(v.name, text) #0-100
			except Exception as e:
				#print e
				pass
			item.score += fuzz.partial_ratio(v.decl.name, text) #0-100
			#print item.value.decl, item.value.decl.works_as(type), type.target

			if item.value.decl.works_as(type):
				item.score += 200
			else:
				item.invalid = True

			#search thru syntaxes
			#if isinstance(v, Syntaxed):
			#	for i in v.syntax:
			#   		if isinstance(i, t):
			#			item.score += fuzz.partial_ratio(i.text, self.pyval)
			#search thru an actual rendering(including children)
			r =     v.render()
			re = " ".join([i.text for i in r if isinstance(i, t)])
			item.score += fuzz.partial_ratio(re, text)


		menu.sort(key=lambda i: i.score)
		menu.reverse()#umm...
		return menu

	def delete_child(s, ch):
		log("del")
		del s.items[s.items.index(ch)]

# hack here, to make a menu item renderable by project.project
#i think ill redo the screen layout as two panes of projection
print MenuItem
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
		return [w('value'), ColorTag("menu item extra info"), " - "+str(self.value.__class__.__name__)+' ('+str(self.score)+')', EndTag()]
		#and abusing "w" for "widget" here...not just here...



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
			   {'name': 'text', 'type': 'type'})

class TypedArgument(Syntaxed):
	def __init__(self, kids):
		super(TypedArgument, self).__init__(kids)

SyntaxedNodecl(TypedArgument,
			   [ch("name"), t("-"), ch("type")],
			   {'name': 'text', 'type': 'type'})

tmp = b['union'].inst_fresh()
tmp.ch["items"].add(Ref(b['text']))
tmp.ch["items"].add(Ref(b['typedargument']))
Definition({'name': Text('function signature node'), 'type': tmp})

tmp = b['list'].make_type({'itemtype': Ref(b['function signature node'])})
Definition({'name': Text('function signature list'), 'type':tmp})




class FunctionDefinitionBase(Syntaxed):

	def __init__(self, kids):
		super(FunctionDefinitionBase, self).__init__(kids)

	@property
	def args(self):
		c = self.sig.compiled
		if isinstance(c, List):
			return [i for i in c if isinstance(i, TypedArgument)]
		else:
			log("sig not a List")
			return []

	@property
	def arg_types(self):
		return [i.ch.type for i in self.args]

	@property
	def sig(self):
		return self.ch.sig

	#def typecheck():
		#for i, arg in enumerate(args):
		#	if not arg.type.eq(self.arg_types[i]):
		#		log("well this is bad")

	def call(self, args):
		args = [arg.eval() for arg in args]
		assert(len(args) == len(self.arg_types))
		r = self._call(args)
		assert isinstance(r, Node)
		return r

	def _eval(s):
		return Text("OK")


class FunctionDefinition(FunctionDefinitionBase):

	def __init__(self, kids):
		super(FunctionDefinition, self).__init__(kids)

	def _call(self, call_args):
		return self.ch.body.run()#Void()#

	def copy_args(self, call_args):
		for ca in call_args:
			name = ca.ch.name.pyval
			assert isinstance(name, str)#or maybe unicode
			for vd in self.vardecls:
				if vd.ch.name.pyval == name:
					vd.runtime.value.append(ca.copy())

	@property
	def vardecls(s):
		return s.args




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


class BuiltinFunctionDecl(FunctionDefinitionBase):

	def __init__(self, kids):
		super(BuiltinFunctionDecl, self).__init__(kids)

	@staticmethod
	def create(name, fun, sig):
		x = BuiltinFunctionDecl.fresh()
		x._name = name
		b[name] = x
		x.ch.name.widget.value = name
		x.fun = fun
		x.ch.sig = List()
		x.ch.sig.items = sig
		x.fix_parents()

	def _call(self, args):
		return self.fun(args)
		# todo use named *args i guess

	@property
	def name(s):
		return s._name


SyntaxedNodecl(BuiltinFunctionDecl,
			   [t("builtin function"), ch("name"), t(":"), ch("sig")],
				{'sig': b['function signature list'],
				 'name': b['text']})

def b_squared(args):
	return Number(args[0] * args[0])

BuiltinFunctionDecl.create("squared",
						   b_squared,
	[	TypedArgument({'name': Text("number"), 'type': Ref(b['number'])}),
		Text("squared")])

def b_list_squared(args):
	r = List() #todo:type
	[r.add(Number(i.pyval*i.pyval)) for i in args[0].items]
	return r

BuiltinFunctionDecl.create("list squared",
						   b_list_squared,
	[	TypedArgument({'name': Text("list of numbers"), 'type': b['list'].make_type({'itemtype': Ref(b['number'])})}),
		Text(", squared")])

def b_multiply(args):
	return Number(args[0].pyval * args[1].pyval)

BuiltinFunctionDecl.create("multiply",
						   b_multiply,
	[	TypedArgument({'name': Text("left"), 'type': Ref(b['number'])}),
		Text("*"),
		TypedArgument({'name': Text("right"), 'type': Ref(b['number'])})])

def b_sum(args):
	return Number(sum([i.pyval for i in args[0].items]))

BuiltinFunctionDecl.create("sum",
						   b_sum,
	[	Text("the sum of"),
		TypedArgument({'name': Text("list"), 'type': b['list'].make_type({'itemtype': Ref(b['number'])})})])

def b_range(args):
	if not isinstance(args[0], Number) or not isinstance(args[1], Number):
		return Text("error:)")
	r = List()
	r.decl = b["list"].make_type({'itemtype': Ref(b['number'])})
	r.items = [Number(i) for i in range(args[0].pyval, args[1].pyval + 1)]
	r.fix_parents()
	return r

BuiltinFunctionDecl.create("range",
						   b_range,
	[	Text("numbers from"),
		TypedArgument({'name': Text('from'), 'type': Ref(b['number'])}),
		Text("to"),
		TypedArgument({'name': Text('to'), 'type': Ref(b['number'])})
		])


def b_print(args):
	print(args[0].to_python_str())
	return Void()

BuiltinFunctionDecl.create("print",
	b_print,
	[ Text("print"), TypedArgument({'name': Text("expression"), 'type': Ref(b['expression'])})])


class FunctionCall(Node):
	def __init__(self, target):
		super(FunctionCall, self).__init__()
		assert isinstance(target, FunctionDefinitionBase)
		self.target = target
		self.args = [Compiler(v) for v in self.target.arg_types] #this should go to fresh()
		self._fix_parents(self.args)

	def delete_child(self, child):
		for i,a in Enumerate(self.args):
			if a == child:
				self.args[i] = Compiler(self.target.arg_types[i])
				self.args[i].parent = self
				return

	def _eval(s):
		args = s.args#[i.compiled for i in s.args]
		log("function call args:"+str(args))
		return s.target.call(args)

	def replace_child(self, child, new):
		assert(child in self.args)
		self.args[self.args.index(child)] = new
		new.parent = self


	def render(self):
		r = []
		argument_index = 0
		sig = self.target.sig.compiled
		if not isinstance(sig, List):
			r+=[t("sig not a List, " + str(sig))]
		else:
			for v in [v.compiled for v in sig]:
				if isinstance(v, Text):
					r += [t(v.pyval)]
				elif isinstance(v, TypedArgument):
					r += [ElementTag(self.args[argument_index])]
					argument_index+=1
				else:
					log("item in sig is"+str(v))
		return r

	@property
	def name(s):
		return s.target.name

	def flatten(self):
		return [self] + flatten([v.flatten() for v in self.args])




class FunctionCallNodecl(NodeclBase):
	def __init__(self):
		super(FunctionCallNodecl, self).__init__(Ref)
		b['call'] = self
		FunctionCall.decl = self
	def palette(self, scope, text):
		decls = [x for x in scope if isinstance(x, (FunctionDefinitionBase))]
		return [CompilerMenuItem(FunctionCall(x)) for x in decls]

FunctionCallNodecl()









class Clock(Node):
	def __init__(self):
		super(Clock,self).__init__()
		self.datetime = __import__("datetime")
	def render(self):
		return [t(str(self.datetime.datetime.now()))]
	def _eval(self):
		return Text(str(self.datetime.datetime.now()))



class PythonEval(Syntaxed):
	def __init__(self, children):
		super(PythonEval, self).__init__(children)

SyntaxedNodecl(PythonEval,
			   [t("python eval"), ch("text")],
			   {'text': Exp(b['text'])})




#Const({'name': Text("meaning of life"), 'value': Number(42)})
"""the end"""




def make_root():
	r = Root()
	r.add(("program", b['module'].inst_fresh()))
	r["program"].ch.statements.newline()
	r.add(("builtins", b['module'].inst_fresh()))
	r["builtins"].ch.statements.items = list(b.itervalues())
	r["builtins"].ch.statements.add(Text("---end of builtins---"))
	#r["builtins"].ch.statements.expanded = False
	return r



