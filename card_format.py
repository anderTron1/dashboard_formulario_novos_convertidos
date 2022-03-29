# -*- coding: utf-8 -*-
"""
Created on Tue Mar 15 10:50:24 2022

@author: secretaria
"""
import cv2
import numpy as np
import os 
    
from reportlab.pdfgen import canvas
from PIL import Image, ImageDraw
import numpy as np

import unicodedata
import re
import pathlib

class Card_format:
    def __init__(self):
        super()
    
    def remove_caracter(self,palavra):

        # Unicode normalize transforma um caracter em seu equivalente em latin.
        nfkd = unicodedata.normalize('NFKD', palavra)
        palavraSemAcento = u"".join([c for c in nfkd if not unicodedata.combining(c)])
    
        # Usa expressão regular para retornar a palavra apenas com números, letras e espaço
        return re.sub('[^a-zA-Z0-9 \\\]', '', palavraSemAcento).upper()
    
    def editImage(self, imgToEdit, nameNewImage, data=None):
        img = cv2.imread(imgToEdit)
        imgPNG = cv2.imread('assets/image.png')
                
        #print(self.remove_caracter(data["name"]))
        cv2.putText(img, self.remove_caracter(data["name"]),(100,330),cv2.FONT_HERSHEY_TRIPLEX,1,0)
        cv2.putText(img, self.remove_caracter(data["cargo"]),(120,420),cv2.FONT_HERSHEY_TRIPLEX,1,0)
        cv2.putText(img, data["data_nascimento"],(490,420),cv2.FONT_HERSHEY_TRIPLEX,1,0)
        cv2.putText(img, data["emisao_card"],(120,510),cv2.FONT_HERSHEY_TRIPLEX,1,0)
        cv2.putText(img, data["venci_card"],(440,510),cv2.FONT_HERSHEY_TRIPLEX,1,0)
        cv2.putText(img, data["rg"],(120,610),cv2.FONT_HERSHEY_TRIPLEX,1,0)
        cv2.putText(img, data["cpf"],(420,610),cv2.FONT_HERSHEY_TRIPLEX,1,0)
        
        #cv2.imshow("janela",img)
        
        cv2.imwrite(nameNewImage,img)
        #cv2.waitKey(0)
        
    def editImageFundo(self, imgToEdit, nameNewImage, data=None):
        img = cv2.imread(imgToEdit)
                
        cv2.putText(img, self.remove_caracter(data["nome_pai"]),(120,119),cv2.FONT_HERSHEY_TRIPLEX,1,0)
        cv2.putText(img, self.remove_caracter(data["nome_mae"]),(120,210),cv2.FONT_HERSHEY_TRIPLEX,1,0)
        cv2.putText(img, data["nacionalidade"],(120,300),cv2.FONT_HERSHEY_TRIPLEX,1,0)
        cv2.putText(img, self.remove_caracter(data["sexo"]),(755,300),cv2.FONT_HERSHEY_TRIPLEX,1,0)
        cv2.putText(img, data["conversao"],(105,395),cv2.FONT_HERSHEY_TRIPLEX,1,0)
        cv2.putText(img, data["batismo"],(390,395),cv2.FONT_HERSHEY_TRIPLEX,1,0)
        
        #cv2.imshow("janela",img)
        
        cv2.imwrite(nameNewImage,img)
        #cv2.waitKey(0)
        
    
    
    def trataImage(self, nameImg, insertImage=True, img_member=None):
        img = Image.open(nameImg)
        
    
        if insertImage:
            format_img = ['jpeg', 'png', 'gif', 'jpg']
            
            for format_arq in format_img:
                for file in os.listdir("database/imagens_membros/"):
                    if file.endswith(img_member+'.'+format_arq):
                        path = "database/imagens_membros/"+file
            
            imgPNG = Image.open(path)#.convert('L')
            #imgPNG = imgPNG.resize((209, 259))
    
            height,width = imgPNG.size
            lum_img = Image.new('L', (height,width),0)
              
            draw = ImageDraw.Draw(lum_img)
            draw.rounded_rectangle(((0, 0), (height, width)), 90, fill="white")
            
            img_arr =np.array(imgPNG)
            lum_img_arr =np.array(lum_img)
            final_img_arr = np.dstack((img_arr, lum_img_arr))
    
            img_final= Image.fromarray(final_img_arr)
            
            img_final.thumbnail((210,290))
            
            img.paste(img_final, (738,369),0)
            
        #img = img.rotate(90, expand=True)  
        img = img.resize((733, 1068), Image.ANTIALIAS)
        
        
        img.save(nameImg)
        img.close()
        #imgPNG.close()
        
        
    def generate_pdf(self, frente, fundo):
        
        img_frente=Image.open(frente)
        img_fundo=Image.open(fundo)
        
        img_frente = img_frente.rotate(90, expand=True) 
        img_fundo = img_fundo.rotate(90, expand=True) 
        
        img_frente.save(frente)
        img_fundo.save(fundo)
        
        
        c = canvas.Canvas("arquivo PDF/arquivo.pdf")
        c.drawImage("database/modelos/fundo_frente.jpg", 1,600, width=151, height=240)
        c.showPage()
        c.drawImage("database/modelos/fundo_fundo.jpg", 1,600, width=151, height=240)
        
        c.save()