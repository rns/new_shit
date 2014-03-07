import pygame

import colors
from logger import ping,log


class Menu(object):
	def __init__(self):
		self.sel = 0
		self.items = [InfoMenuItem("hello")]
		
	def draw(self, scr, font, x, y, size):
		#s = pygame.Surface((size[0], size[1]), pygame.SRCALPHA)
		self.fg = (255,255,255,255)
		self.bg = (0,0,0,100)
		
		for i, item in enumerate(self.items):
#			log(str(item))
			assert(isinstance(item, MenuItem))
			w,h = item.draw(self, scr, font, x, y)
			if i == self.sel:
				pygame.draw.rect(scr, self.fg, (x, y, w,h), 1)
			y += h
			
	def keypress(self, e):
		if e.mod & pygame.KMOD_CTRL:
			if e.key == pygame.K_UP:
				self.move(-1)
				return True
			if e.key == pygame.K_DOWN:
				self.move(1)
				return True
			if e.key == pygame.K_RETURN:
				log(self.items[self.sel])
				self.element.menu_item_selected(self.items[self.sel])
				return True
				

	def move(self,y):
		self.sel += y
		if self.sel < 0: self.sel = 0
		if self.sel >= len(self.items): self.sel = len(self.items) - 1

class MenuItem(object):
	pass

class InfoMenuItem(MenuItem):
	def __init__(self, text):
		self.text = "(" + text + ")"

	def draw(self, menu, s, font, x, y):
		fs = font['font'].render(self.text, True, (200,200,200), menu.bg)
		s.blit(fs,(x,y))
		return fs.get_width(), fs.get_height()
