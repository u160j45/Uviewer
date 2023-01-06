#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import numpy as np

from PIL import Image,  ImageFilter, ImageOps, ImageChops, ImageEnhance

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
		#imCrop2 = Imagemodify.contrast(imCrop2, factor = 1.2) # AUgmente contrast
		
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



