# -*- coding: utf-8 -*-
from nodes import *
import settings, toolbar
import the_doc

def test_root():
	r = Root(Dict([
			(
			#"placeholder test", Statements([Placeholder(types = [Node]),Placeholder(types = [Node])])
			#),(
			#"text widget test", widgets.Text(None, "Test me out!")
			#),(
			#"intro", Text("""hello...""")
			#),(
			"programs", List([Placeholder(types=['program'])
				
			])
			
				#Program(Statements([
					#Placeholder([], "statement")#,
					#FunctionDefinition(name = Text("substring")),
					#Asignment(Text("a"), Number(1)),
					#Asignment(Text("b"), Number(5)), 
					#While(IsLessThan(VariableRead("a"), VariableRead("b")),	Statements([
					#	Print(
					#		VariableRead("a")), #byname
					#		Placeholder()])),
					#laceholder()]), name="test1"),
					#If(IsLessThan(VariableRead("a"), Number(4)),
					#	Statements([Print(Text("hi!\n"))]))
				#	For(VariableDeclaration("item")
				#]), "hello world2", "koo5")]) #semanticize koo5:)
			
			#),(
			
			#),
			
			#),(
			
			#"gridtest",Grid(
			#	items = 'notes/items',
			#	grid = [
			#	[0,1,2,3],
			#	[4,5,6,None]])
			
			#),(
			
			#(
			),(
			"modules",
				List([			
					Module(Statements([
						SyntaxDef([t("program by "), ch("author"), t("created on "), ch("date_created"), nl(), ch("statements"), t("end."), w("run_button"), w("results")])
					]), name = "syntaxes for builtins"),
					
					Module(Statements(builtins()), name = "builtins"),

					Module(Statements([
						Note("stupid, but gotta start somewhere"),
						FunctionDefinition(
							signature = FunctionSignature([Text("disable screensaver")]), 
							body = Statements([ShellCommand("xset s off")]))
					]), name = "some functions"),
					
					Placeholder([Module], "new module") 
				], False)
			),(
			"docs", the_doc.the_doc()
			),(

			"tools", List(
				[
				toolbar.SetAllSyntaxesToZero(),
				Clock()
				#save, load
				], False)
			),(
			"settings", Dict([
				("webos hack", widgets.Toggle(None, False)),
				("font size", settings.FontSize(18)),
				#("fullscreen", widgets.Toggle(None, False)),
				("colors", Dict([
					("monochrome", widgets.Toggle(None, False)),
					("invert", widgets.Toggle(None, False)),
					("background", Dict([
						("R", widgets.Number(None, 0, (0, 255))),
						("G", widgets.Number(None, 0, (0, 255))),
						("B", widgets.Number(None, 0, (0, 255)))], False))
				])),
				("sdl key repeat", settings.KeyRepeat()),
				], True)
			)

			
			]))
	
	
	r.fix_relations()
	
	return r
#prototypes?

def builtins():
	return [NodeTypeDeclaration(x) for x in [
			Text, Number, Dict, List, CollapsibleText, Statements,
			VariableReference, Placeholder, Clock, SyntaxDef,
			Program, Module, ShellCommand,
			Root, While, Note, Todo, Idea]]



def mini_test_root():
	return Root(Dict([
			(
			"test", widgets.Text("banana", "Test me out!")
			)]))

	


