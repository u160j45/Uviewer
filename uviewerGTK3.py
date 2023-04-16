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

from PIL import Image
from Uclass import Imagemodify

CATEGORIE_FILTRE = ["Dessin", "Négatif","Old_School", "uBlurred_edge", "Gray_Border", "uGrayscale"]
LARGEURMAX = Gdk.Screen().width() - 200
HAUTEURMAX = Gdk.Screen().height() - 250


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
			
			if self.choice == "uBlurred_edge":
				self.thread = threading.Thread(target=self.blurred_edge)
				self.thread.start()
				self.startProgressbar(self)
			self.confirmation()
			
			if self.choice == "Gray_Border":
				self.thread = threading.Thread(target=self.gray_border)
				self.thread.start()
				self.startProgressbar(self)
				
			if self.choice == "Old_School":
				self.thread = threading.Thread(target=self.old_school)
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
	
	def blurred_edge(self):
		self.progressbar.show()
		image = Image.open(self.imageName)
		
		if self.mode == "Normal": 
			newIm = Imagemodify.blurred_edge(image, forme = "rectangle")
			
		if self.mode == "Darken":
			newIm = Imagemodify.blurred_edge(image, forme = "ellipse")
			
		newIm.save(os.path.splitext(self.imageName)[0] + '_' + self.choice + '_' + self.mode + '.png')
		self.new_image = (os.path.splitext(self.imageName)[0] + '_' + self.choice + '_' + self.mode + '.png')
		self.image_modify_display(self)
	
	def gray_border(self):
		self.progressbar.show()
		image = Image.open(self.imageName)
		
		if self.mode == "Normal": 
			newIm = Imagemodify.gray_border(image, forme = "rectangle")
			
		if self.mode == "Darken":
			newIm = Imagemodify.gray_border(image, forme = "ellipse")
			
		newIm.save(os.path.splitext(self.imageName)[0] + '_' + self.choice + '_' + self.mode + '.png')
		self.new_image = (os.path.splitext(self.imageName)[0] + '_' + self.choice + '_' + self.mode + '.png')
		self.image_modify_display(self)
		
	def old_school(self):
		self.progressbar.show()
		image = Image.open(self.imageName)
		if self.mode == "Normal":
			newIm = Imagemodify.old_school(image, mode = "normal")
		if self.mode == "Darken":
			newIm = Imagemodify.old_school(image, mode = "darken")
		newIm.save(os.path.splitext(self.imageName)[0] + '_' + self.choice + '_' + self.mode + '.png')
		self.new_image = (os.path.splitext(self.imageName)[0] + '_' + self.choice + '_' + self.mode + '.png')
		self.image_modify_display(self)
		
	''' Création de l'interface '''
	def __init__(self):
		self.imageNumber = 0
		#emplacement = os.getcwd()
		#if len(sys.argv)-1 == 0:
			#print("Lancer avec arguments:  ./uviewerGTK3.py /home/users/image.jpg")
			#sys.exit()
		
		#os.chdir(os.path.dirname(sys.argv[1]))
		self.files_images = sorted([file for file in os.listdir(os.getcwd()) if file.split('.')[-1].lower() in ['jpg', 'png',  'jpeg', 'svg', 'jpeg']])
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
