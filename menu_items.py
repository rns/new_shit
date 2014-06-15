from colors import colors
from element import Element
import widgets

class MenuItem(Element):
	def __init__(self):
		super(MenuItem, self).__init__()
		#self.brackets = ('<','>')

	@property
	def crrect(self):


class InfoItem(MenuItem):
	def __init__(self, text):
		super(InfoItem, self).__init__()
		self.text = text
		self.color = "info item text"
		self.visibility_toggle = widgets.Toggle(self, True, ("(X)", "show"))
		self.visibility_toggle.color = "info item visibility toggle"

	def render(self):
		return [TextTag(self.text + "  "), WidgetTag(self.visibility_toggle)]
