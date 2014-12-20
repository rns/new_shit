from lemon_platform import SDL, CURSES
from keys import *
import lemon_client as client
from lemon_client import editor, menu, bye
from server_side import server
import replay


def change_font_size(x):
	"""dummy"""
	pass

def keypress(e):
	if global_key(e):
		server.global_handled()
	else:
		server.element_keypress(e):


def global_key(e):
	k = e.key
	if KMOD_CTRL & e.mod:

		if e.uni == '=':
			change_font_size(1)
		elif e.uni == '-':
			change_font_size(-1)

		elif k == K_LEFT:
			editor.prev_elem()
		elif k == K_RIGHT:
			editor.next_elem()
		elif k == K_HOME:
			editor.cursor_top()
		elif k == K_END:
			editor.cursor_bottom()

		elif k == K_f:
			editor.dump_to_file()
		elif k == K_q:
			server.bye()
		elif e.key == K_m:
			server.menu.menu_dump()


		elif SDL and e.key == K_UP:
			sidebar.move(-1)
		elif SDL and e.key == K_DOWN:
			sidebar.move(1)

		elif CURSES and e.key == K_INSERT: # todo: find better keybindings for curses
			sidebar.move(-1)
		elif CURSES and e.key == K_DELETE:
			sidebar.move(1)
		else:
			return False
		return True


	else: # with no modifier keys
		if k == K_F1:
			client.cycle_sidebar()
		elif k == K_F2:
			replay.do_replay()
		elif k == K_F8:
			editor.toggle_arrows()

		elif k == K_UP:
			editor.move_cursor_v(-1)
			editor.and_sides(e)
		elif k == K_DOWN:
			editor.move_cursor_v(+1)
			editor.and_sides(e)
		elif k == K_LEFT:
			editor.move_cursor_h(-1)
			editor.and_updown(e)
		elif k == K_RIGHT:
			editor.move_cursor_h(+1)
			editor.and_updown(e)
		elif k == K_HOME:
			editor.cursor_home()
		elif k == K_END:
			editor.cursor_end()
		elif k == K_PAGEUP:
			editor.move_cursor_v(-10)
		elif k == K_PAGEDOWN:
			editor.move_cursor_v(10)

		elif k == K_ESCAPE:
			if not replay.we_are_replaying:
				bye()
		elif e.uni == ' ':
			return menu.accept()
		else:
			return False
		return True


"""here we count on the fact that each client frame has been assigned to an
attribute of the server module. to do this with rpcing,
clients or client frames will have to act as servers too, with the messaging
loop integrated with the gui loop"""

#maybe when we have multiple editor frames,
#we will want to just pass the event on to perhaps the previously focused frame
#for now im trying having all top level handlers in one file here

#todo:look into FRP

#curses enter: http://lists.gnu.org/archive/html/bug-ncurses/2011-01/msg00011.html

