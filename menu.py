import pygame

import colors
from logger import ping,log


class Menu(object):
	@property
	def items(self):
		return self._items
	@items.setter
	def items(self, value):
		if self.sel > len(value) - 1:
			self.sel = len(value) - 1
		self._items = value
	
	def __init__(self):
		self.sel = 0
		self._items = [InfoMenuItem("hello")]
		self.element = None
		
	def draw(self, scr, font, x, y, size):
		#s = pygame.Surface((size[0], size[1]), pygame.SRCALPHA)
		menu_area = pygame.Rect(0,0,0,0)
		ypos = y
		for i, item in enumerate(self.items):
			#log(str(item))
			assert(isinstance(item, MenuItem))
			item_area = item.draw(self, scr, font, x, ypos)
			item.rect = (x,ypos, item_area.w, item_area.h)
			if i == self.sel:
				pygame.draw.rect(scr, colors.fg, (x, ypos, item_area.w, item_area.h), 1)
			else:
				pygame.draw.rect(scr, (0,0,200), (x, ypos, item_area.w, item_area.h), 1)
			menu_area = menu_area.union((0, ypos, item_area.w, item_area.h))
			ypos += item_area.h
			if ypos > size[1]:
				break
			#print area.h
		#pygame.draw.rect(scr, (100,100,100), (x,y,menu_area.w,menu_area.h), 1)
	
	def help(self):
		return [HelpMenuItem(t) for t in [
		"ctrl + up, down: menu movement",
		"space: menu selection"]]

	
	
	def keypress(self, e):
#		ping()
		if e.mod & pygame.KMOD_CTRL:
			if e.key == pygame.K_UP:
				self.move(-1)
				return True
			if e.key == pygame.K_DOWN:
				self.move(1)
				return True
		if e.key == pygame.K_SPACE:
#			print self.sel
#			log(self.items[self.sel])
			self.element.menu_item_selected(self.items[self.sel], None)
			self.sel = 0
			return True
				

	def move(self,y):
		ping()
		self.sel += y
		if self.sel < 0: self.sel = 0
		if self.sel >= len(self.items): self.sel = len(self.items) - 1
		print len(self.items), self.sel

#on mousedown or (mousemove if mouse is down):
#	self.sel = item under mouse

class MenuItem(object):
	def __init__(self):
		self.valid = True

class InfoMenuItem(MenuItem):
	def __init__(self, text):
		super(InfoMenuItem, self).__init__()
		self.text = "(" + text + ")"
		self.color = (200,200,200)

	def draw(self, menu, s, font, x, y):
		fs = font['font'].render(self.text, True, self.color, colors.bg)
		s.blit(fs,(x,y))
		return fs.get_rect()

class HelpMenuItem(InfoMenuItem):
	def __init__(self, text):
		super(HelpMenuItem, self).__init__("")
		self.text = text
		self.color = (255,255,255)

