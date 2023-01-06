#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# sudo apt-get install pip
# pip install Pillow


import os,sys
import threading
import numpy as np

import gi 
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk, GdkPixbuf, GLib

from PIL import Image,  ImageFilter, ImageOps, ImageChops, ImageEnhance

CATEGORIE_FILTRE = ["Dessin", "Négatif",  "uLSD", "uModif", "uGrayscale"]
LARGEURMAX = Gdk.Screen().width() - 200
HAUTEURMAX = Gdk.Screen().height() - 250

class Imagemodify:
	
		
	def uGrayscale(im, color = "gray"):
		color = color
		image = im
		if color == "gray":
			if  image.mode == 'RGBA':
				imgray = image.convert("LA")
			if image.mode == 'RGB':
				imgray = ImageOps.grayscale(image)
				
			return imgray
			
		if color == "blackWhite":
			imBalckWhite = image.convert('L').point(lambda x: 255 if x > 127 else 0)
			if image.mode == 'RGBA':
				imageNew =  Imagemodify.addAlpha(image, imBalckWhite)
				return imageNew
				
			return imBalckWhite
		
		if color == "grayU": # gray darken
			imBlackWhite  =  Imagemodify.uGrayscale(image, color = "blackWhite")
			if imBlackWhite.mode == 'LA':
				imBlackWhite = imBlackWhite.convert('L') 
			largeur, hauteur = imBlackWhite.size
			imagecalque = Image.new('RGBA', (largeur, hauteur))
			imagecalque.putalpha(imBlackWhite)
			imageNew = ImageChops.composite(image, imBlackWhite, imagecalque)
			if image.mode == 'RGBA':
				imageNew =  Imagemodify.addAlpha(image, imageNew)
				
			return imageNew
			
	def negatif(im, color = "normal"):
		''' Je n'utilise pas  ImageOps.invert ça me permet de traiter du RGB et RGBA '''
		color = color
		image = im
		source = image.split()
		R, V, B = 0, 1, 2
		maskRouge = source[R].point(lambda i: 255 -i )
		maskVert = source[V].point(lambda i: 255 -i )
		maskBleu = source[B].point(lambda i: 255 -i )
		if color == "normal": # Negatif Normal
			source[R].paste(maskRouge) 
			source[V].paste(maskVert)
			source[B].paste(maskBleu)
			
		if color == "yellow": # Negatif Jaune
			source[R].paste(maskBleu) # On colle le masque bleu dans le canal rouge
			source[V].paste(maskVert)
			source[B].paste(maskRouge) # On colle le masque rouge dans le canal bleu 
			
		if color == "green": # Negatif vert
			source[R].paste(maskRouge) 
			source[V].paste(maskBleu)
			source[B].paste(maskVert)
			
		if color == "red": # Negatif Red
			source[R].paste(maskBleu) 
			source[V].paste(maskRouge)
			source[B].paste(maskRouge)
			
		if color == "purple": # Negatif 
			source[R].paste(maskBleu) 
			source[V].paste(maskRouge)
			source[B].paste(maskVert)

		imageNegatif = Image.merge(image.mode, source)
		return imageNegatif
		
		
	def dessin( im, mode = "normal", factor = 1.2):
		image = im
		if mode == "normal": 
			#imageDessin = image.filter(ImageFilter.CONTOUR)#artistique
			imageDessin = image.filter(ImageFilter.EDGE_ENHANCE_MORE)
			imagecalque  =  Imagemodify.uGrayscale(image, color = "blackWhite")
			imBlur =  image.filter(ImageFilter.BLUR)
			imBlur = Imagemodify.color(imBlur)
			imageDessin = ImageChops.composite(imBlur, imageDessin, imagecalque)
			#imageDessin = ImageChops.composite(imageDessin, imBlur, imagecalque)
			imageDessin =  ImageChops.darker(imageDessin, image)
			
			#imageDessin =  ImageChops.difference(imageDessin, image)#artistique
		if mode == "darken": 
			imageDessin = image.filter(ImageFilter.EDGE_ENHANCE_MORE)
			imagecalque  =  Imagemodify.uGrayscale(image, color = "blackWhite")
			imGrayU = Imagemodify.uGrayscale(image, color = "grayU")
			imageDessin = ImageChops.composite(imageDessin, imGrayU, imagecalque) #Origine gray
			
		if image.mode == 'RGBA':
			imageDessin =  Imagemodify.addAlpha(image, imageDessin)
			
		return imageDessin
		
		
	def blurred_edge(im, ratio = 10, forme = "rectangle"):
		''' Plus le ratio est grand plus la bordure sera petite '''
		image = im
		width, height = image.size
		
		delimitateurW1 = (width//ratio)
		delimitateurW2 = (width//ratio)*(ratio - 1)
		delimitateurH1 = (height//ratio)
		delimitateurH2 = (height//ratio)*(ratio - 1)
		
		imEdge = image.filter(ImageFilter.BLUR)
		#imEdge =  Imagemodify.color(imEdge, factor = 0.8)
		
		imCrop2 = im.crop((delimitateurH1, delimitateurH1, delimitateurW2 , delimitateurH2)) #(gauche, supérieur, droit, inférieur)
		imCrop2 = Imagemodify.sharpness(imCrop2, factor = 2.0) # Augmente netteté (sharpness)
		imCrop2 = Imagemodify.color(imCrop2, factor = 1.2) # Augmente color
		#imCrop2 = Imagemodify.contrast(imCrop2, factor = 1.2) # Augmente contrast
		
		calque = Image.new('L', (width, height), 255)
		draw = ImageDraw.Draw(calque)
		if forme == "rectangle":
			draw.rounded_rectangle([delimitateurH1, delimitateurH1, delimitateurW2 , delimitateurH2],fill=000, width=1, radius=44)
		if forme == "ellipse":
			draw.ellipse([delimitateurH1, delimitateurH1, delimitateurW2 , delimitateurH2],fill=000, width=1)
		calque = calque.filter(ImageFilter.GaussianBlur(40)) # Flou sur le calque pour Dégrader
		
		image.paste(imCrop2, ((delimitateurH1, delimitateurH1, delimitateurL2 , delimitateurH2)))
		
		newim = ImageChops.composite(imEdge, image, calque)
		return newim
	
	def color(im, factor = 1.3):
		image = im
		enhancerColor = ImageEnhance.Color(image)
		newIm = enhancerColor.enhance(factor)
		return newIm
	
	def sharpness(im, factor = 1.5):
		image = im
		enhancerSharpness = ImageEnhance.Sharpness(image)
		newIm = enhancerSharpness.enhance(factor)
		return newIm
		
	def contrast(im, factor = 1.5):
		image = im
		enhancerContrast = ImageEnhance.Contrast(image)
		newIm = enhancerContrast.enhance(factor)
		return newIm
		
	def addAlpha(im, imModify):
		image = im
		imAndAlpha = imModify
		source = image.split()
		maskAlpha = source[3]
		imAndAlpha.putalpha(maskAlpha)
		return imAndAlpha



class Main():
	
	
	
	'''Les Fonctions de navigation'''
	def forward(self, widget):
		if (self.filesNumber -1) == self.imageNumber :
			print("Retour au début de la liste")
			self.imageNumber = 0
			self.imageName = self.files_images[self.imageNumber]
		else:
			print("Suivant")
			self.imageNumber += 1
			self.imageName = self.files_images[self.imageNumber]
		print("Image : "+ self.imageName)
		self.image_display(self)
		
	def back(self, widget):
		if  self.imageNumber == 0 :
			self.imageNumber = (self.filesNumber -1)
			self.imageName = self.files_images[self.imageNumber]
		else:
			print("Précédent")
			self.imageNumber -= 1
			self.imageName = self.files_images[self.imageNumber]
		print("Image : "+ self.imageName)
		self.image_display(self)
		
	def on_key_press(self, widget, event):
		key = Gdk.keyval_name(event.keyval)
		if key == "Right":
			self.forward(self)
		if key == "Left":
			self.back(self)
		if key == "Delete":
			# Joindre fenetre d'avertissement
			self.delete(self)
			self.forward(self)
		if key == "m":
			self.changement_mode() # Change le mode modif
		if key == "Escape":
			Gtk.main_quit()
		#print(key)

	'''La fonction appellée au choix dans la liste déroulante permet de savoir  qu'elle fonction de modification appeller'''
	def choice_modif(self, widget):
		self.choice = self.listeDeroulante.get_active_text()
		self.imageName = self.files_images[self.imageNumber]
		if self.choice == "Modifier":
			pass
			
		else:
			print("Modification " + self.files_images[self.imageNumber])
			
			if self.choice == "uGrayscale":
				self.thread = threading.Thread(target=self.uGrayscale)
				self.thread.start()
				self.startProgressbar(self)
				
			if self.choice == "Négatif":
				self.thread = threading.Thread(target=self.negatif)
				self.thread.start()
				self.startProgressbar(self)
				
			if self.choice == "Dessin":
				self.thread = threading.Thread(target=self.dessin)
				self.thread.start()
				self.startProgressbar(self)
			self.confirmation()
		
		
		
	'''Les Fonctions pour afficher l'image en fonction de  sa taille et de celle de l'ecran '''
	def image_display(self, widget):
		image = Image.open(self.files_images[self.imageNumber])
		largeur, hauteur = image.size[0], image.size[1]
		if largeur > LARGEURMAX or hauteur > HAUTEURMAX:
			self.window.maximize()
			self.pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_scale(self.files_images[self.imageNumber], LARGEURMAX, HAUTEURMAX, preserve_aspect_ratio=True)
		else:
			self.pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_scale(self.files_images[self.imageNumber], largeur, hauteur, preserve_aspect_ratio=True)
		self.image.set_from_pixbuf(self.pixbuf)
		
	def image_modify_display(self, widget):
		image = Image.open(self.new_image)
		largeur, hauteur = image.size[0], image.size[1]
		if largeur > LARGEURMAX or hauteur > HAUTEURMAX:
			self.pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_scale(self.new_image, LARGEURMAX, HAUTEURMAX, preserve_aspect_ratio=True)
		else:
			self.pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_scale(self.new_image, largeur, hauteur, preserve_aspect_ratio=True)
		self.image.set_from_pixbuf(self.pixbuf)
		
	'''Les Fonctions pour modifier l'interface et option mode'''
	def confirmation(self):
		#Cache les boutons de navigation et affiche les boutons de confirmation
		self.button_grid.hide()
		self.button_quitter.hide()
		self.button_save.show()
		self.button_cancel.show()
		
	def refresh(self):
		#Cache es boutons de confirmation et affiche les boutons de navigation
		self.button_grid.show()
		self.button_quitter.show()
		self.button_save.hide()
		self.button_cancel.hide()
		self.listeDeroulante.set_active(0)
		
	def changement_mode(self):
		mode = self.mode
		if mode == "Normal":
			self.mode = "Darken"
		if mode == "Darken":
			self.mode = "Normal"
		self.window.set_title("Mode : " + self.mode)
		print("Mode = " + self.mode)
		
	''' Les Fonctions Sauvegarde , Supprimer et Annulation'''
	def sauvegarder(self, widget):
		#Sauvegarde l'image modifier
		print("Image enregistrer sous : " + self.new_image)
		if (self.filesNumber -1) == self.imageNumber : # Si c'est la derniere image
			self.files_images.append(self.new_image) # On l'ajoute à la fin de la liste
		else: # Sinon on l'insert dans la liste entre l'image d'origine et la suivante
			self.files_images.insert(self.imageNumber + 1  , self.new_image)
		self.imageNumber += 1
		self.filesNumber = len(self.files_images)
		self.image_display(self)
		self.new_image = ""
		
		self.refresh() #rafraichissement de l'interface
		#self.confirmation()
		
	def delete(self, widget):
		#Supprime l'image affichée 
		print("Supprimer : "+ self.files_images[self.imageNumber])
		os.remove(self.files_images[self.imageNumber])
		if (self.filesNumber -1) == self.imageNumber :
			del self.files_images[self.imageNumber]
			self.imageNumber = self.imageNumber - 1
		else:
			del self.files_images[self.imageNumber]
		
		self.filesNumber = len(self.files_images)
		
	def annuler(self,widget):
		#Supprime l'image modifier
		print("Annulation de la modification")
		os.remove(self.new_image)
		self.new_image = ""
		self.image_display(self)
		self.refresh()#rafraichissement de l'interface
		
	''' Gestion de la progressbar '''
	def startProgressbar(self, widget):
		#Démarrage de la progressbar lié à la fonction updateProgressbar
		self.progressbar.pulse()
		self.timeout_id = GLib.timeout_add(44, self.updateProgressbar, None)
		#self.progressbar.show()
		
	def updateProgressbar(self, widget):
		 if self.thread.is_alive():# Tant que le thread est en fonction 
			 self.progressbar.pulse()
			 return True
		# Quand le thread est terminer progressbar s'arrete 
		 self.progressbar.hide()#Cache la progressbar
		 #GLib.source_remove(self.timeout_id)
		 return False
		 
	'''Les  Fonctions de modification d'images '''
	def uGrayscale(self):
		self.progressbar.show()
		image = Image.open(self.imageName)
		if self.mode == "Normal":
			imModify = Imagemodify.uGrayscale(image)
		if self.mode == "Darken":
			imModify = Imagemodify.uGrayscale(image, color = "grayU")
		imModify.save(os.path.splitext(self.imageName)[0] + '_' + self.choice + '_' + self.mode + '.png')
		self.new_image = (os.path.splitext(self.imageName)[0] + '_' + self.choice + '_' + self.mode + '.png')
		self.image_modify_display(self)
		
	def negatif(self):
		self.progressbar.show()
		image = Image.open(self.imageName)
		if self.mode == "Normal":
			imModify =  Imagemodify.negatif(image)
		if self.mode == "Darken":
			imModify =  Imagemodify.negatif(image, color = "red")
		imModify.save(os.path.splitext(self.imageName)[0] + '_' + self.choice + '_' + self.mode + '.png')
		self.new_image = (os.path.splitext(self.imageName)[0] + '_' + self.choice + '_' + self.mode + '.png')
		self.image_modify_display(self)
		
	def dessin(self):
		self.progressbar.show()
		image = Image.open(self.imageName)
		if self.mode == "Normal": 
			imageDessin = Imagemodify.dessin(image)
		if self.mode == "Darken": 
			imageDessin = Imagemodify.dessin(image, mode ="darken")
		imageDessin.save(os.path.splitext(self.imageName)[0] + '_' + self.choice + '_' + self.mode + '.png')
		self.new_image = (os.path.splitext(self.imageName)[0] + '_' + self.choice + '_' + self.mode + '.png')
		self.image_modify_display(self)
		
		
		
		
	''' Création de l'interface '''
	def __init__(self):
		self.imageNumber = 0
		#os.chdir(os.path.dirname(sys.argv[1]))
		self.files_images = sorted([file for file in os.listdir(os.getcwd()) if file.split('.')[-1] in ['jpg', 'png', 'gif', 'jpeg', 'svg', 'jpeg']])
		#self.files_images.insert(0, os.path.basename(sys.argv[1]))
		self.filesNumber = len(self.files_images)
		self.new_image = ""
		self.mode = "Normal"
		 
		self.window = Gtk.Window()
		self.window.set_title('Python Image GTK')
		self.window.connect('delete-event', Gtk.main_quit)
		self.window.connect("key_press_event", self.on_key_press)
		
		main_layout = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
		
		self.pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_scale(self.files_images[self.imageNumber], LARGEURMAX, HAUTEURMAX, preserve_aspect_ratio=True)
		self.image = Gtk.Image.new_from_pixbuf(self.pixbuf)
		# Gtk.StateFlags.NORMAL,Gdk.RGBA(0,0,0,255)) Avoir l'image affichée sur un fond noir
		self.image.override_background_color(Gtk.StateFlags.NORMAL,Gdk.RGBA(0,0,0,255))
		
		self.image_display(self)
		main_layout.pack_start(self.image, True, True, 0)
		
		self.progressbar = Gtk.ProgressBar()
		main_layout.pack_start(self.progressbar, False, False, 0)
		
		button_back = Gtk.Button(stock = Gtk.STOCK_GO_BACK)
		button_forward = Gtk.Button(stock = Gtk.STOCK_GO_FORWARD)
		
		button_forward.connect("clicked" ,self.forward)
		button_back.connect("clicked" ,self.back)
		
		self.button_grid = Gtk.Grid()
		self.button_grid.set_column_homogeneous(True)
		
		self.listeDeroulante = Gtk.ComboBoxText()
		self.listeDeroulante.append_text("Modifier")
		for filtre in CATEGORIE_FILTRE:
			self.listeDeroulante.append_text(filtre)
		self.listeDeroulante.set_active(0)
		self.listeDeroulante.connect('changed', self.choice_modif)
		self.listeDeroulante.set_wrap_width(2) # 2 colonnes 
		#self.listeDeroulante.set_wrap_width(3) # 3 colonnes
		#self.listeDeroulante.set_hexpand(True)

		self.button_grid.attach(button_back, 0, 0, 1, 1)
		self.button_grid.attach(self.listeDeroulante, 1, 0, 1, 1)
		self.button_grid.attach(button_forward, 2, 0, 1, 1)
		
		main_layout.pack_start(self.button_grid,False, False, 0)
		
		self.button_quitter = Gtk.Button(label='Quitter')
		self.button_quitter.connect("clicked",Gtk.main_quit)
		
		self.button_save = Gtk.ToggleButton(label = "Valider")
		self.button_save.connect("clicked" ,self.sauvegarder)
		self.button_cancel = Gtk.ToggleButton(label = "Annuler")
		self.button_cancel.connect("clicked" ,self.annuler)
		
		
		main_layout.pack_start(self.button_save,False,False,0)
		main_layout.pack_start(self.button_cancel,False,False,0)
		main_layout.pack_start(self.button_quitter,False,False,0)
		
		self.window.add(main_layout)
		
		self.window.show_all()
		self.button_save.hide()
		self.button_cancel.hide()
		self.progressbar.hide()
		
		Gtk.main()
		


if __name__ == '__main__':
	Main()
