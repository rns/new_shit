what is this
===
a protoprototype of a structural editor and a programming / shell language / user interface, inspired by inform 7, playing with natural language-like projections

<http://imgur.com/a/otY8X#1>


running it
===
requires fuzzywuzzy
"colors" package optional
libmarpa not critical but needed for parsing: https://github.com/jeffreykegler/libmarpa.git  

there is a proof-of-concept ncurses frontend, just need to come up with good key combinations and finish the translation table

the pygame frontend requires pygame, obviously

* apt-get install python-pygame python-pip
* pip install --user fuzzywuzzy colors
#(or without --user)

it should work with python 2.5, OrderedDict is bundled in (maybe not anymore)  

run main_curses.py, main_sdl.py, or faster.sh (disables assertions)  
if the latest commit doesnt run, git checkout HEAD^ until you find one that does:)

getting started
===
some info is in intro.txt, some in the builtins module inside lemon,
some context sensitive help is in the sidebars.  
Stop by in the irc channel. I can also take you on a tour in VNC.


resources
===
talk to us in [irc://irc.freenode.net/lemonparty](irc://irc.freenode.net/lemonparty)  
research and discussion: http://goo.gl/1XilSW


help wanted
===
here are some (random and possibly outdated) things that i think would help lemon further, sometimes directly, sometimes by making it more
accesible/interesting to other people. Some understanding of lemon is usually
necessary though. I will be more than happy to explain every detail, but be prepared that it takes some time.
some (messy) notes are also towards the end of stuff/the_doc.py, and search for "todo" in the source files..

* support for more human languages.
 would make lemon interesting as a non-english programming tool
 i think this is an easy task. A syntax defined in python code is a list of tags.
 Sometimes you may see them grouped in another list, so there are several alternatives.
 I would wrap each tags list in a dict with additional metadata: "lang" and maybe "verbosity"..  

* help me learn unipycation, yield python, kanren or other logic programming
<http://yieldprolog.sourceforge.net/>   (learning logpy currently, and liking it)
 it will be needed for a lot of features of lemon.
 you dont actually need to know lemon to help me with this

* improve the user interaction with nodes or the context help "system"

* add more standard library functions, operators for strings and lists

* help with the license

* look into runnig lemon in pypyjs or compiling it to asm.js

* improve the curses frontend, figure out what keys to use

* do more research on related projects (projectured, cedalion, MPS, eastwest..)

* figure out how to have a better font in pygame (for mathy expressions, for example) compatible with lemon license (search stuff/the_doc.py for 'font')

* give me feedback on the builtins module, it should server as a reference to the language, with documentation and examples. 

* migrate the google doc to something saner? github wiki? the_doc.py?

* add command line arguments or some other system to select/filter log messages by topic. use standard python logging module?

* revive the_doc.py, the settings module, the toolbar, add support for images or live graphic canvas..

* integrate some test framework, the few tests i have are simply ran on each start


files
===
* main_sdl.py: the frontend, handles a window, events, drawing. run this one.
* main_curses.py: proof-of-concept console frontend
* lemon.py: frontend-agnostic middlestuff with debug replay functionality
* nodes.py: AST classes
* widgets.py textbox, number box, button..
* element.py - both widgets and nodes descend from Element
* project.py: project() "projects" the AST tree into a grid of text
* tags.py: the results of calling element.render(), text, attribute, child..
* frames.py: the panels: Root, Menu, Info..
* lemon_colors.py: color settings
* lemon_args.py: command line arguments
* stuff/the_doc.py: an attempt to migrate all documentation into lemon



license
===
not decided yet, some standard license or this experiment: <https://github.com/koo5/Free-Man-License> 
For now: By contributing to lemon, you agree to granting me nonexclusive rights to use your contribution (with attribution) within lemon, in any way, including relicensing and reselling. Also, the patent claim protection clauses like in http://www.gnu.org/licenses/agpl-3.0.html apply.;)

