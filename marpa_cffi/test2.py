from collections import defaultdict
from collections import namedtuple
from marpa import *
import sys; sys.path.append('..')
from dotdict import dotdict
import logger
print logger
logger.log('s')
from logger import topic, log

def ident(x):
	return x

@topic
def fresh():
	global rules, syms, g, known_chars, actions
	rules = dotdict()
	syms = dotdict()
	g = Grammar()
	symbol('any')
	known_chars = {}
	actions = {} # per-rule valuator functions

def symbol(name):
	r = g.symbol_new_int()
	assert name not in syms._dict
	syms[name] = r
	return r

def rule(name, lhs,rhs,action=(lambda x:x)):
	assert type(name) == str
	assert type(lhs) == symbol_int
	if type(rhs) != list:
		assert type(rhs) == symbol_int
		rhs = [rhs]
	assert name not in rules._dict
	r = rules[name] = g.rule_new_int(lhs, rhs)
	actions[r] = action
	return r


def sequence(name, lhs, rhs, action=(lambda x:x), separator=-1, min=1, proper=False,):
	assert type(name) == str
	assert type(lhs) == symbol_int
	assert type(rhs) == symbol_int
	assert name not in rules._dict
	r = rules[name] = g.sequence_new_int(lhs, rhs, separator, min, proper)
	actions[r] = action
	return r

def known(char):
	if not char in known_chars:
		known_chars[char] = symbol(char)
	return known_chars[char]

def test0():
	symbol("banana")
#	print syms.banana
	try:
		print syms.orange
		assert False
	except KeyError:
		pass
	rule("banana_is_a_fruit", symbol('fruit'), syms.banana)
	known('X')
	known('Y')
	rule( 'why',syms.X, syms.Y)
	print "test0:", syms._dict, rules._dict

fresh()
test0()


def setup():
	print "SETUP"
	symbol('digit')
	symbol('digits')
	for i in [chr(j) for j in range(ord('0'), ord('9')+1)]:
		rule(i + "_is_a_digit",syms.digit, known(i))
	

	sequence('digits_is_sequence_of_digit', syms.digits, syms.digit)
	symbol('number')
	rule('number_is_digits', syms.number, syms.digits)

	#
	#multiplication's syntax 1: ChildTag("A"), '*', ChildTag("B")
	#register_grammar:
	#	s.symbol = new_symbol()
	#	rhs = []
	#	for i in syntax:
	#		if i.type == ChildTag:
	#			rhs.append(s.ch[i.name].symbol)
	#		if i.type == str:
	#			rhs.append(known(i))
	#		...

	symbol('expression')
	rule('number_is_expression',syms.expression, syms.number)

	symbol('string_body')
	symbol('string')
	sequence('string_body_is_sequence_of_any', syms.string_body, syms.any)
	rule('string', syms.string, [known("'"), syms.string_body, known("'")])
	rule('string_is_expression', syms.expression, syms.string)


	symbol('multiplication')
	rule('multiplication', syms.multiplication, [syms.expression, known('*'), syms.expression])

	def known_string(s):
		rhs = [known(i) for i in s]
		lhs = symbol(s)
		return rule(s, lhs, rhs)

	symbol('do_x_times')

	rule('do_x_times',syms.do_x_times, [known_string('do'), syms.expression, known_string('times:')])


	symbol('start')
	g.start_symbol_set(syms.start)
	symbol('statement')

	rule('start', syms.start, syms.statement)
	rule('expression_is_statement', syms.statement, syms.expression)
	rule('do_x_times_is_statment',syms.statement, syms.do_x_times)





toktup = namedtuple("token", "symid pos")



def raw2tokens(raw):
	tokens = []
	for i, char in enumerate(raw):
		if char in known_chars:
			symid=known_chars[char]
		else:
			symid=syms.any
		tokens.append(toktup(symid, pos=i))
	return tokens



def test1(raw):
	tokens = raw2tokens(raw)

	g.precompute()
	r = Recce(g)
	r.start_input()

	print "TEST1"
	print g
	print r
	
	for i, (sym, pos) in enumerate(tokens):
		r.alternative_int(sym, i+1)
		r.earleme_complete()
	#token value 0 has special meaning(unvalued), so lets i+1 over there and insert a dummy over here
	tokens.insert(0,'dummy') 
	
	latest_earley_set_ID = r.latest_earley_set()
	print 'latest_earley_set_ID=%'%latest_earley_set_ID

	b = Bocage(r, latest_earley_set_ID)
	o = Order(b)
	tree = Tree(o)

	import gc
	for dummy in tree.nxt():
		do_steps(tree, tokens, rules)
		gc.collect #force an unref of the valuator and stuff so we can move on to the next tree


def symbol2name(s):
	for k,v in symbols.__dict.iteritems():
		if v == s:
			return k
	assert False

def rule2name(r):
	for k,v in rules.__dict.iteritems():
		if v == r:
			return k
	assert False


def do_steps(tree, tokens, rules):
	stack = defaultdict((lambda:666))
	v = valuator(tree)

	print
	print v.v
	
	while True:
		s = v.step()
		print "stack:%s"%dict(stack)#convert ordereddict to dict to get neater __repr__
		print "step:%s"%codes.steps2[s]
		if s == lib.MARPA_STEP_INACTIVE:
			break
	
		elif s == lib.MARPA_STEP_TOKEN:

			sym, pos = tokens[v.v.t_token_value]
			
			assert type(sym) == symbol_int
			assert sym == v.v.t_token_id

			assert v.v.t_result == v.v.t_arg_n

			char = raw[pos-1]
			where = v.v.t_result
			print "token %s of type %s, value %s, to stack[%s]"%(pos, symbol2name(sym), repr(char), where)
			stack[where] = char
	
		elif s == lib.MARPA_STEP_RULE:
			r = v.v.t_rule_id
			#print "rule id:%s"%r
			print "rule:"+rule2name(r)
			arg0 = v.v.t_arg_0
			argn = v.v.t_arg_n

			args = stack[arg0:argn+1]

			res = (rule2name(r), action[r])

			stack[arg0] = res

	print "tada:"+str(stack[0])

import operator

fresh()
setup()
print 'syms:%s'%sorted(syms._dict.items(),key=operator.itemgetter(1))
print 'rules:%s'%sorted(rules._dict.items(),key=operator.itemgetter(1))
test1('9321-82*7+6')
test1('do34*4times:')
