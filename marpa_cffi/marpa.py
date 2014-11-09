
"""
 * 
 * This file is based on Libmarpa, Copyright 2014 Jeffrey Kegler.
 * Libmarpa is free software: you can
 * redistribute it and/or modify it under the terms of the GNU Lesser
 * General Public License as published by the Free Software Foundation,
 * either version 3 of the License, or (at your option) any later version.
 *
 * Libmarpa is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
 * Lesser General Public License for more details.
 *
 * You should have received a copy of the GNU Lesser
 * General Public License along with Libmarpa.  If not, see
 * http://www.gnu.org/licenses/.
 */
"""

from cffi import FFI

ffi = FFI()


ffi.cdef(open("marpa.h.cffi.h", "r").read())


lib = ffi.verify("""
#include <marpa.h>
""", libraries=['marpa'])


print lib


assert lib.MARPA_MAJOR_VERSION == lib.marpa_major_version
assert lib.MARPA_MINOR_VERSION == lib.marpa_minor_version
assert lib.MARPA_MICRO_VERSION == lib.marpa_micro_version
#ver = ffi.new("int [3]")
#lib.marpa_version(ver)


assert lib.marpa_check_version (lib.MARPA_MAJOR_VERSION ,lib.MARPA_MINOR_VERSION, lib.MARPA_MICRO_VERSION ) == lib.MARPA_ERR_NONE


import marpa_codes as codes


config = ffi.new("Marpa_Config*")
lib.marpa_c_init(config)
#Always succeeds.

class Grammar(object):
	def __init__(s):
		s.g = ffi.gc(lib.marpa_g_new(config), lib.marpa_g_unref)
		s.check_config_error()
		assert lib.marpa_g_force_valued(s.g) >= 0
		s.check_config_error()
		#print s.g
	
	def check_config_error(s):
		msg = ffi.new("char **")
		assert lib.marpa_c_error(config, msg) == lib.MARPA_ERR_NONE,  mss

	def check_int(s, result):
		if result == -2:
			e = lib.marpa_g_error(s.g, ffi.new("char**"))
			assert e == lib.MARPA_ERR_NONE,  codes.errors[e]
		return result
		
	def error_clear(s):
		lib.marpa_g_error_clear(s.g)

	def symbol_new(s, name):
		return Symbol(s, name)
	
	def rule_new(s, lhs, rhs):
		return Rule(s, lhs, rhs)

	def sequence_new(s, lhs, rhs):
		return s.check_int(lib.marpa_g_sequence_new(g.g, lhs.s, [i.s for i in rhs], len(rhs)))


	def precompute(s):
		r = s.check_int(lib.marpa_g_precompute(s.g))
		s.print_events()
		return r

	def events(s):
		count = s.check_int(lib.marpa_g_event_count(s.g))
		print '%s events'
		result = ffi.new('Marpa_Event*')
		for i in xrange(count):
			event_type = s.check_int(lib.marpa_g_event(s.g, result, i))
			event_value = result.t_value
			r = event_type, event_value
			print r
			yield r

	def print_events(s):
		[None for dummy in s.events()]

class Symbol(object):#should symbols even be an object?
	def __init__(s, g, name):
		s.g = g
		s.name = name
		s.s = g.check_int(lib.marpa_g_symbol_new(g.g))
	def start_symbol_set(s):
		s.g.check_int( lib.marpa_g_start_symbol_set(s.g.g, s.s) )

class Rule(object):
	def __init__(s, g, lhs, rhs):
		s.r = g.check_int(lib.marpa_g_rule_new(g.g, lhs.s, [i.s for i in rhs], len(rhs)))

class Recce(object):
	def __init__(s, g):
		s.g = g
		s.r = lib.marpa_r_new(g.g)
	def __del__(s):
		lib.marpa_r_unref(s.r)
	def start_input(s):
		s.g.check_int(lib.marpa_r_start_input(s.r))
	def alternative(s, sym, val, length):
		r = lib.marpa_r_alternative(s.r, sym.s, val, length)
		if r != lib.MARPA_ERR_NONE:
			print codes.errors[r]
	def earleme_complete(s):
		if lib.marpa_r_earleme_complete(s.r) == -2:
			print "errrrrrrr"
	def latest_earley_set(s):
		return lib.marpa_r_latest_earley_set(s.r)

class Bocage(object):
	def __init__(s, r, earley_set_ID):
		s.g = r.g
		s.b = lib.marpa_b_new(r.r, earley_set_ID)
		print s.b
	def __del__(s):
		lib.marpa_b_unref(s.b)

class Order(object):
	def __init__(s, bocage):
		s.g = bocage.g
		s.o = lib.marpa_o_new(bocage.b)
		print s.o
	def __del__(s):
		lib.marpa_o_unref(s.o)

class Tree(object):
	def __init__(s, order):
		s.g = order.g
		s.t = lib.marpa_t_new(order.o)
		print s.t
	def __del__(s):
		lib.marpa_t_unref(s.t)
	def nxt(s):
		while True:
			r = s.g.check_int(lib.marpa_t_next(s.t))
			if r == -1:
				break
			yield r

class valuator(object):
	def __init__(s, tree):
		s.g = tree.g
		s.v = lib.marpa_v_new(tree.t)
		#print s.v
	def __del__(s):
		lib.marpa_v_unref(s.v)
	def step(s):
		return s.g.check_int(lib.marpa_v_step(s.v))
		

def test1():
	#based on the example at the end of https://metacpan.org/pod/Marpa::R2::Advanced::Thin
	class SimpleNamespace:
		def __init__(self, pairs):
			self.__dict__.update(pairs)
		def __repr__(self):
			keys = sorted(self.__dict__)
			items = ("{}={!r}".format(k, self.__dict__[k]) for k in keys)
			return "{}({})".format(type(self).__name__, ", ".join(items))

	g = Grammar()


	sy = SimpleNamespace([(name, g.symbol_new(name)) for name in "S E op number".split()])
	sy.S.start_symbol_set()
	rules = SimpleNamespace([(name, g.rule_new(lhs, rhs)) for name, lhs, rhs in [
		('start', sy.S, [sy.E]),
		('op'    , sy.E, [sy.E, sy.op, sy.E]),
		('number' , sy.E, [sy.number])]])
	
	g.precompute()
	
	r = Recce(g)
	r.start_input()

	print g
	print r
	
	
	#tokens = [(sy.number, 2),(sy.op, '-'),(sy.number, 1),(sy.op, '*'),
	#	(sy.number, 3),(sy.op, '+'),(sy.number, 1)]
	raw = '9-8*7+6'
	tokens = []
	for i,v in enumerate(raw):
		try:
			tokens.append((sy.number, int(raw[i])))
		except:
			tokens.append((sy.op, raw[i]))

	print [(i[0].name, i[1]) for i in tokens]
	

	for i, (sym, val) in enumerate(tokens):
		r.alternative(sym, i+1, 1)
		r.earleme_complete()
	#token value 0 has special meaning(unvalued), so lets i+1 over there and insert a dummy over here
	tokens.insert(0,'dummy') 
	
	latest_earley_set_ID = r.latest_earley_set()
	#print latest_earley_set_ID
	b = Bocage(r, latest_earley_set_ID)
	o = Order(b)
	tree = Tree(o)
	import gc
	for i in tree.nxt():
		do_steps(tree, tokens, rules)
		gc.collect

from collections import defaultdict

def do_steps(tree, tokens, rules):
	stack = defaultdict((lambda:666))
	v = valuator(tree)

	print
	print v.v
	
	while True:
		s = v.step()
		print "stack:%s"%dict(stack)#avoid ordereddict's __repr__
		print "step:%s"%codes.steps2[s]
		if s == lib.MARPA_STEP_INACTIVE:
			break
	
		elif s == lib.MARPA_STEP_TOKEN:

			tok_idx = v.v.t_token_value
			
			assert type(tokens[tok_idx][0]) == Symbol
			assert      tokens[tok_idx][0].s == v.v.t_token_id
			assert v.v.t_result == v.v.t_arg_n
			
			where = v.v.t_result
			print "token %s of type %s, value %s, to stack[%s]"%(tok_idx, tokens[tok_idx][0].name, repr(tokens[tok_idx][1]), where)
			stack[where] = tokens[tok_idx][1]
	
		elif s == lib.MARPA_STEP_RULE:
			r = v.v.t_rule_id
			#print "rule id:%s"%r
			print "rule:"+[key for key,val in rules.__dict__.iteritems() if val.r == r][0]
			arg0 = v.v.t_arg_0
			argn = v.v.t_arg_n
			
			if r == rules.start.r:
				string, val = stack[argn]
				stack[arg0] = "%s = %s"%(string, val)
			
			elif r == rules.number.r:
				num = stack[arg0]
				stack[arg0] = (str(num), num)
			
			elif r == rules.op.r:
				lstr, lval = stack[arg0]
				op = stack[arg0 + 1]
				rstr, rval = stack[argn]
				print stack[arg0], op, stack[argn]
				text = '(' + lstr + " " + op + " " + rstr + ')'
				if op == '+':
					res = lval + rval
				elif op == '-':
					res = lval - rval
				elif op == '*':
					res = lval * rval
				elif op == '/':
					res = lval / rval
				else:
					print op + '???'
					return
				stack[arg0] = (text, res)
			else:
				print "wat, %s?"%r
	print "tada:"+str(stack[0])
test1()
