import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk, GdkPixbuf

from ..model.game import SpecialField

class AnswerFactory:

    def __init__(self, playerManager):
        self.playerManager = playerManager

    def createAnswer(self, category, answer):
        if SpecialField.isSpecialField(answer) and SpecialField.IMAGE_ANSWER in answer.specialties:
            return ImageAnswer(self.playerManager, category, answer.scalar)

        return TextAnswer(self.playerManager, category, answer)

class Answer(Gtk.Box):

    def __init__(self, playerManager, category):
        Gtk.Box.__init__(self)
        self.playerManager = playerManager

        self.set_orientation(Gtk.Orientation.VERTICAL)
        self.pack_start(Gtk.Label(category, name="headline"), False, True, 0)
    
    def packed(self):
        pass

class TextAnswer(Answer):
    def __init__(self, playerManager, category, text):
        super().__init__(playerManager, category)

        self.pack_start(Gtk.Label(text), True, True, 0)

        self.show_all()

class ImageAnswer(Answer):
    def __init__(self, playerManager, category, imageUrl):
        super().__init__(playerManager, category)
        self.imageUrl = imageUrl
        self.pixbuf = GdkPixbuf.Pixbuf.new_from_file(self.imageUrl)
        self.image = None

    def packed(self):
        allocation = self.get_toplevel().get_allocation()
        desired_width = allocation.width * 0.8
        desired_height = allocation.height * 0.8 #TODO: keep aspect ratio

        pixbuf = self.pixbuf.scale_simple(desired_width, desired_height, GdkPixbuf.InterpType.BILINEAR)
        newImage = Gtk.Image.new_from_pixbuf(pixbuf)
        if not self.image is None:
            self.remove(self.image)
        self.pack_start(newImage, True, True, 0)
        self.image = newImage

        self.show_all()