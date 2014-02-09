





import nodes




def test_stuff():
	return Dict((
			"settings", Dict(
				("font_size", settings.FontSize(18)),
				("fullscreen", settings.Fullscreen())
				)
			),(
			"programs", List([
				Program(Statements([
					Placeholder(), 
					FunctionDefinition(Text("substring"))
					Asignment(Text("a"), Number(1)),
					Asignment(Text("b"), Number(5)), 
					While(IsLessThan(VariableRead("a"), VariableRead("b")),	Statements([
						Print(
							VariableRead("a")), #byname
							Placeholder()])),
					Placeholder()]), name="test1"),
					If(IsLessThan(VariableRead("a"), Number(4)),
						Statements([Print(Text("hi!\n"))]))
				#	For(VariableDeclaration("item")
						
				])
			),(
			"notes", List([
				Todo("""big themes: 
voice recognition (samson?)
eye tracking


"""),
				Todo("procrastinate more"),
				CollapsibleText(
					"""
<AnkhMorporkian_> it's probably a bad idea to have newline as its own class. it'd be better to maintain it in the document class, since you have to have that anyways when you're using it.
<AnkhMorporkian> i understand why the nodes handle their own rendering, but I don't see why simple text characters should be.
<sirdancealot_> i wanted to have it uniform, to avoid special handling of str inside the template render
					"""),

				CollapsibleText(
					"""
#couple options:
	store the positions of characters in an array ourselves - 
		hmm, this actually sounds pretty simple, might be dumping pyglets documents one day
	store positions in attributes char by char
		for everything
		for just active.. nope...clicks...
	settled for one position for each element now
					"""),
				Idea("""pick up the templating work, use an existing templating library, switch to formatted_from_text, implement functions dealing with the text with attributes if necessary"""),
				Todo("save/load nodes", priority=10),
				Todo("salvage the logger thingy...printing does get tedious...but its so damn quick")
				])
			),(
			"clock",Clock()
			)	
			)




