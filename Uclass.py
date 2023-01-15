#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import numpy as np

from PIL import Image,  ImageFilter, ImageOps, ImageChops, ImageEnhance, ImageDraw

class Imagemodify:
	
		
	def uGrayscale(im, color = "gray", seuil = 127):
		color = color
		image = im
		if color == "gray":
			if  image.mode == 'RGBA':
				imgray = image.convert("LA")
			if image.mode == 'RGB':
				imgray = ImageOps.grayscale(image)
				
			return imgray
			
		if color == "blackWhite":
			imBalckWhite = image.convert('L').point(lambda x: 255 if x > seuil else 0)
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
			imageDessin = image.filter(ImageFilter.EDGE_ENHANCE_MORE)
			imagecalque  =  Imagemodify.uGrayscale(image, color = "blackWhite")
			imBlur =  image.filter(ImageFilter.BLUR)
			imBlur = Imagemodify.color(imBlur)
			imageDessin = ImageChops.composite(imBlur, imageDessin, imagecalque)
			#imageDessin = ImageChops.composite(imageDessin, imBlur, imagecalque)
			imageDessin =  ImageChops.darker(imageDessin, image)
			
		if mode == "darken": 
			imageDessin = image.filter(ImageFilter.EDGE_ENHANCE_MORE)
			imagecalque  =  Imagemodify.uGrayscale(image, color = "blackWhite")
			imGrayU = Imagemodify.uGrayscale(image, color = "grayU")
			imageDessin = ImageChops.composite(imageDessin, imGrayU, imagecalque) #Origine gray
			
		if mode == "peinture":
			imageDessin = image.filter(ImageFilter.ModeFilter(6))
			
		if image.mode == 'RGBA':
			imageDessin =  Imagemodify.addAlpha(image, imageDessin)
			
		return imageDessin
	
	def blurred_edge(im, ratio = 10, forme = "rectangle"):
		''' rajoute de la nettetée au centre et du flou sur les bords
		plus le ratio est grand plus la bordure sera petite, forme rectangle ou ellipse 
		'''
		image = im
		width, height = image.size
		
		box = ((width//ratio), (height//ratio), (width//ratio)*(ratio-1), (height//ratio)*(ratio-1))
		
		imEdge = image.filter(ImageFilter.MinFilter(size=3)) # assombri
		imEdge = imEdge.filter(ImageFilter.BLUR) # floute 
		imEdge = Imagemodify.color(imEdge, factor = 0.8) # down color
		
		image = Imagemodify.sharpness(image, factor = 2.0) # Augmente netteté (sharpness)
		image = Imagemodify.color(image, factor = 1.2) # Augmente color
		image = Imagemodify.contrast(image, factor = 1.2)
		
		calque = Image.new('L', (width, height), 255) #creation du  calque
		draw = ImageDraw.Draw(calque)
		if forme == "rectangle":
			draw.rounded_rectangle([box[0], box[1],box[2],  box[3]],fill=000, width=1, radius=44)
		if forme == "ellipse":
			draw.rounded_rectangle([box[0], box[1],box[2],  box[3]],fill=000, width=1)
		calque = calque.filter(ImageFilter.GaussianBlur(40)) # Flou sur le calque pour Dégrader
		
		#image.paste(imCrop2, (box)) # on recolle le centre sur l'image
		
		newim = ImageChops.composite(imEdge, image, calque) # On applique le calque
		return newim
		
	def old_school(im, mode = "normal"):
		image = im
		datas = image.getdata()
		newim = Image.new(image.mode,  image.size)
		new_image_data = []
		
		if mode == "normal": 
			for item in datas:
				if  item[2] in list(range(0, 75)):
					new_image_data.append((102, 0, 0))# rouge foncer 
				if  item[2] in list(range(75, 150)):
					new_image_data.append((200, 100, 30)) # Orange foncer
				if  item[2] in list(range(150, 225)) :  #151,170
					new_image_data.append((218,165,32))
				if item[2]  in list(range(225, 256)):
					new_image_data.append((255,215,0))#or Jaune claire
			newim.putdata(new_image_data)
			
		if mode == "darken": 
			for item in datas:
				if  item[2] in list(range(0, 50)):
					new_image_data.append((102, 0, 0))# rouge foncer 
				if  item[2] in list(range(50, 100)):
					new_image_data.append((200, 100, 30)) # Orange foncer
				if  item[2] in list(range(100, 200)):  #151,170
					new_image_data.append((218,165,32))
				if item[2]  in list(range(200, 256)):
					new_image_data.append((255,215,0))#or
			newim.putdata(new_image_data)
				
		if image.mode == 'RGBA':
			newim =  Imagemodify.addAlpha(image, newim)
			
		return newim
		
	def color(im, factor = 1.2):
		image = im
		enhancerColor = ImageEnhance.Color(image)
		newIm = enhancerColor.enhance(factor)
		return newIm
		
	def sharpness(im, factor = 1.9):
		image = im
		enhancerSharpness = ImageEnhance.Sharpness(image)
		newIm = enhancerSharpness.enhance(factor)
		return newIm
	
	def contrast(im, factor = 1.2):
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



