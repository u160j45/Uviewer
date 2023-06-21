#!/usr/bin/env python3
# -*- coding: utf-8 -*-


from PIL import Image,  ImageFilter, ImageOps, ImageChops, ImageEnhance, ImageDraw

class Imagemodify:
	
		
	def uGrayscale(im, color = "gray", seuil = 127):
		image = im
		if color == "gray":
			if  image.mode == 'RGBA':
				imageNew = image.convert("LA")
			if image.mode == 'RGB':
				imageNew = ImageOps.grayscale(image)
				
		if color == "blackWhite":
			imageNew= image.convert('L').point(lambda x: 255 if x > seuil else 0)
			if image.mode == 'RGBA':
				imageNew =  Imagemodify.addAlpha(image, imageNew)

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
			
		if color == "purple": # Negatif purple
			source[R].paste(maskBleu) 
			source[V].paste(maskRouge)
			source[B].paste(maskVert)

		imageNegatif = Image.merge(image.mode, source)
		return imageNegatif
		
	def sepia(im):
		image = im
		source = image.split()
		if  image.mode == 'RGBA':
			imageNew  = image.convert("LA")
		if image.mode == 'RGB':
			imageNew  =  ImageOps.grayscale(image)
		
		imageNew  = imageNew.convert('RGB')
		source2 = imageNew.split()
		R, V, B = 0, 1, 2
		maskRouge = source2[R].point(lambda i: int(i * 0.393 + (i+1)* 0.769 + (i+2)* 0.189 ))
		maskVert = source2[V].point(lambda i:  int( i * 0.349 + (i+1)*0.686 + (i+2)*0.168))
		maskBleu = source2[B].point(lambda i:  int(i * 0.272 +(i+1)* 0.534 + (i+2)*0.131))
		
		source[R].paste(maskRouge)
		source[V].paste(maskVert)
		source[B].paste(maskBleu)

		imSepia = Image.merge(image.mode, source)
		return imSepia
		
	def dessin( im, mode = "normal"):
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
			#imageDessin =  ImageChops.darker(imageDessin, image)
			#imageDessin =  ImageChops.lighter(imageDessin, image)
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
		
		imEdge = image.filter(ImageFilter.MinFilter(size=3)) # assombri garde les pixels les plus foncer
		imEdge = imEdge.filter(ImageFilter.BLUR) # floute 
		imEdge = Imagemodify.color(imEdge, factor = 0.8) # down color
		
		image = Imagemodify.sharpness(image, factor = 2.0) # Augmente netteté (sharpness)
		#image = Imagemodify.color(image, factor = 1.2) # Augmente color
		image = Imagemodify.contrast(image, factor = 1.2) # Augmente contrast
		
		calque = Image.new('L', (width, height), 255) #creation du  calque
		draw = ImageDraw.Draw(calque)
		
		if forme == "rectangle":
			draw.rounded_rectangle([box[0], box[1],box[2],  box[3]],fill=000, width=1, radius=44)
			
		if forme == "ellipse":
			draw.ellipse([box[0], box[1],box[2],  box[3]],fill=000, width=1)
			
		calque = calque.filter(ImageFilter.GaussianBlur(40)) # Flou sur le calque pour Dégrader
		
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
		
	def diag_up(im, side = "right"):
		''' Diagonal qui part du bas vers le haut '''
		image = im
		width, height = image.size
		
		#imageGray = ImageOps.grayscale(image) # creat gray picture
		imageGray =   Imagemodify.brightness(image, factor = 0.8)
		
		if side == "right": # Gray picture right
			calque = Image.new('L', (width, height), 0) 
			draw = ImageDraw.Draw(calque)
			draw.polygon(((0,height),(width,height),(width,0)),fill=255) 
			
		if side == "left": # Gray picture left
			calque = Image.new('L', (width, height), 255) 
			draw = ImageDraw.Draw(calque)
			draw.polygon(((0,height),(width,height),(width,0)),fill=0) 
			
		calque = calque.filter(ImageFilter.GaussianBlur(40)) # Flou sur le calque pour Dégrader
		newim = ImageChops.composite(imageGray, image, calque)
		
		return newim
		
	def diag_down(im, side = "right"):
		''' Diagonal qui part du haut vers le bas '''
		image = im
		width, height = image.size
		
		#imageGray = ImageOps.grayscale(image) # creat gray picture
		imageGray =   Imagemodify.brightness(image, factor = 0.8)
		
		if side == "right": # Gray picture right
			calque = Image.new('L', (width, height), 0) 
			draw = ImageDraw.Draw(calque)
			draw.polygon(((0,0),(width, 0),(width, height)),fill=255)
			
		if side == "left": # Gray picture left
			calque = Image.new('L', (width, height), 255) 
			draw = ImageDraw.Draw(calque)
			draw.polygon(((0,0),(width, 0),(width, height)),fill=0)
			
		calque = calque.filter(ImageFilter.GaussianBlur(40)) # Flou sur le calque pour Dégrader
		newim = ImageChops.composite(imageGray, image, calque)
		
		return newim
		
	def gray_border(im, forme = "rectangle", ratio = 10):
		''' plus le ratio est grand plus la bordure sera petite, forme rectangle ou ellipse  '''
		image = im
		width, height = image.size
		
		box = ((width//ratio), (height//ratio), (width//ratio)*(ratio-1), (height//ratio)*(ratio-1))
		if  image.mode == 'RGBA':
			imageGray = image.convert("LA")
		if image.mode == 'RGB' or  image.mode == 'L':
			#imageGray = ImageOps.grayscale(image)
			imageGray =   Imagemodify.brightness(image, factor = 0.8)
			
		calque = Image.new('L', (width, height), 255) #creation du  calque
		draw = ImageDraw.Draw(calque)
		if forme == "rectangle":
			draw.rounded_rectangle([box[0], box[1],box[2],  box[3]],fill=000, width=1, radius=44)
		if forme == "ellipse":
			draw.ellipse([box[0], box[1],box[2],  box[3]],fill=000, width=1)
		
		calque = calque.filter(ImageFilter.GaussianBlur(40)) # Flou sur le calque pour Dégrader
		newim = ImageChops.composite(imageGray, image, calque) # On applique le calque
		
		return newim
		
	def damier(im, mode = "Gray", px=10):
		image = im
		width, height = image.size
		if mode == "Gray":
			if  image.mode == 'RGBA':
				imageGray = image.convert("LA")
			if image.mode == 'RGB':
				imageGray = ImageOps.grayscale(image)
				
		if mode == "Invert":
			#imageGray =  ImageOps.invert(image)
			imageGray =   Imagemodify.brightness(image, factor = 0.5)
			
		calque = Image.new('L', (width, height), 255) #creation du  calque
		draw = ImageDraw.Draw(calque)
		for i in range (height//px):#(width//10):
				offset = px * (i % 2)
				for k in range(width//px):#(height//10):
					posx = (px*2) * k + offset
					draw.rectangle(((posx, i*px), (posx+px), i*px+px), fill="#000000")
		
		newim = ImageChops.composite(imageGray, image, calque) # On applique le calque
		return newim
		
	def color(im, factor = 1.2):
		''' factor = 1.0 image d'origine, factor =  0.0 noir et blanc et de 1.1 à 2.0 augmente la couleur'''
		image = im
		enhancerColor = ImageEnhance.Color(image)
		newIm = enhancerColor.enhance(factor)
		return newIm
		
	def sharpness(im, factor = 1.9):
		'''Un facteur d'amélioration de 0.0 donne une image floue, un facteur de 1.0 donne l'image d'origine
		et un facteur de 2.0 donne une image plus nette.'''
		image = im
		enhancerSharpness = ImageEnhance.Sharpness(image)
		newIm = enhancerSharpness.enhance(factor)
		return newIm
	
	def contrast(im, factor = 1.2):
		''' Un facteur d'amélioration de 0.0 donne une image grise unie. Un facteur de 1.0 donne l'image d'origine
		et de 1.0 à 2.0 augmente le contrast'''
		image = im
		enhancerContrast = ImageEnhance.Contrast(image)
		newIm = enhancerContrast.enhance(factor)
		return newIm
		
	def  brightness( im , factor = 1.2):
		'''Un facteur d'amélioration de 0.0 donne une image noir . Un facteur de 1.0 donne l'image d'origine
		et de 1.0 à 2.0 augmente la luminosité'''
		image = im
		enhancerBrightness = ImageEnhance.Brightness(image)
		newIm = enhancerBrightness.enhance(factor)
		return newIm
		
	def addAlpha(im, imModify):
		''' Ajoute le canal alpha de l'image d'origine à l'image modifiée'''
		image = im
		imAddAlpha = imModify
		source = image.split()
		maskAlpha = source[3]
		imAddAlpha.putalpha(maskAlpha)
		return imAddAlpha



