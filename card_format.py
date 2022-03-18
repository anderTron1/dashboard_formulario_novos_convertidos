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

class Card_format:
    def __init__(self):
        super()
    
    
    def editImage(self, imgToEdit, nameNewImage, data=None):
        img = cv2.imread(imgToEdit)
        imgPNG = cv2.imread('assets/image.png')
        
        cv2.putText(img,"ANDRE LUIZ PIRES GUIMARAES",(100,330),cv2.FONT_HERSHEY_TRIPLEX,1,0)
        cv2.putText(img,"DIACONO",(120,420),cv2.FONT_HERSHEY_TRIPLEX,1,0)
        cv2.putText(img,"15/07/1996",(490,420),cv2.FONT_HERSHEY_TRIPLEX,1,0)
        cv2.putText(img,"14/03/2022",(120,510),cv2.FONT_HERSHEY_TRIPLEX,1,0)
        cv2.putText(img,"12/03/2027",(440,510),cv2.FONT_HERSHEY_TRIPLEX,1,0)
        cv2.putText(img,"15648154-15",(120,610),cv2.FONT_HERSHEY_TRIPLEX,1,0)
        cv2.putText(img,"703.455.081-65",(420,610),cv2.FONT_HERSHEY_TRIPLEX,1,0)
        
        """cv2.putText(img, data["name"],(100,330),cv2.FONT_HERSHEY_TRIPLEX,1,0)
        cv2.putText(img, data["cargo"],(120,420),cv2.FONT_HERSHEY_TRIPLEX,1,0)
        cv2.putText(img, data["data_nascimento"],(490,420),cv2.FONT_HERSHEY_TRIPLEX,1,0)
        cv2.putText(img, data["emisao_card"],(120,510),cv2.FONT_HERSHEY_TRIPLEX,1,0)
        cv2.putText(img, data["venci_card"],(440,510),cv2.FONT_HERSHEY_TRIPLEX,1,0)
        cv2.putText(img, data["rg"],(120,610),cv2.FONT_HERSHEY_TRIPLEX,1,0)
        cv2.putText(img, data["cpf"],(420,610),cv2.FONT_HERSHEY_TRIPLEX,1,0)"""
        
        
        #cv2.imshow("janela",img)
        
        cv2.imwrite(nameNewImage,img)
        #cv2.waitKey(0)
        
    def editImageFundo(self, imgToEdit, nameNewImage, data=None):
        img = cv2.imread(imgToEdit)
        
        cv2.putText(img,"RAMILTON RIBEIRO GUIMARAES",(120,119),cv2.FONT_HERSHEY_TRIPLEX,1,0)
        cv2.putText(img,"JUCELIA PEREIRA PIRES",(120,210),cv2.FONT_HERSHEY_TRIPLEX,1,0)
        cv2.putText(img,"BRASILEIRO",(120,300),cv2.FONT_HERSHEY_TRIPLEX,1,0)
        cv2.putText(img,"MASCULINO",(755,300),cv2.FONT_HERSHEY_TRIPLEX,1,0)
        cv2.putText(img,"15/04/2012",(105,395),cv2.FONT_HERSHEY_TRIPLEX,1,0)
        cv2.putText(img,"15/02/2014",(390,395),cv2.FONT_HERSHEY_TRIPLEX,1,0)
        
        """cv2.putText(img, data["nome_pai"],(120,119),cv2.FONT_HERSHEY_TRIPLEX,1,0)
        cv2.putText(img, data["nome_mae"],(120,210),cv2.FONT_HERSHEY_TRIPLEX,1,0)
        cv2.putText(img, data["nacionalidade"],(120,300),cv2.FONT_HERSHEY_TRIPLEX,1,0)
        cv2.putText(img, data["sexo"],(755,300),cv2.FONT_HERSHEY_TRIPLEX,1,0)
        cv2.putText(img, data["conversao"],(105,395),cv2.FONT_HERSHEY_TRIPLEX,1,0)
        cv2.putText(img, data["batismo"],(390,395),cv2.FONT_HERSHEY_TRIPLEX,1,0)"""
        
        #cv2.imshow("janela",img)
        
        cv2.imwrite(nameNewImage,img)
        #cv2.waitKey(0)
        
    
    
    def trataImage(self, nameImg, insertImage=True):
        img = Image.open(nameImg)
        imgPNG = Image.open('assets/image.jpg')#.convert('L')
    
        if insertImage:
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
        imgPNG.close()
        
        
    def generate_pdf(self):
        c = canvas.Canvas("arquivo.pdf")
        c.drawImage("fundo_frente.jpg", 1,600, width=151, height=240)
        c.showPage()
        c.drawImage("fundo_fundo.jpg", 1,600, width=151, height=240)
        
        c.save()