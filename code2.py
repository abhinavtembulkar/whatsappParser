	
from random import random
import re
import time
import datetime as dt
import json
import os
from turtle import back
from numpy import double
import requests
import shutil
import pickle
from PIL import Image
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import NoSuchElementException, ElementNotVisibleException, StaleElementReferenceException
from selenium.webdriver.common.alert import Alert
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.chrome.options import Options
from urllib.parse import urlencode
from bs4 import BeautifulSoup
from time import sleep
from xlwt import Workbook

CHROME_PATH = "D:/whatsappParser/chromedriver.exe"

class WhatsAppElements:
    search = (By.CSS_SELECTOR, "#side > div.uwk68 > div > label > div > div._13NKt.copyable-text.selectable-text")
    chats = (By.CSS_SELECTOR, "#main > div._1LcQK > div > div._33LGR")
    catalog = (By.CLASS_NAME, "_2qiMb")
    items = (By.CLASS_NAME,'_3DpBF._2nY6U.vq6sj._16m7g')
    item = (By.CLASS_NAME,'_2P1rL.ZIBLv._2ROcQ')
    back_button = (By.CLASS_NAME,'_18eKe')

class WhatsApp:
    browser =  None
    timeout = 10*60  # The timeout is set for about ten seconds
    catalogs = []

    def __init__(self, wait=timeout, screenshot=None, session=None):
        self.sets = set()
        self.browser = webdriver.Chrome(executable_path=CHROME_PATH)# change path
        self.browser.get("https://web.whatsapp.com/") #to open the WhatsApp web
        # you need to scan the QR code in here (to eliminate this step, I will publish another blog
        WebDriverWait(self.browser,wait).until( 
        EC.presence_of_element_located(WhatsAppElements.search)) #wait till search element appears
    
    def goto_main(self):
        try:
            self.browser.refresh()
            Alert(self.browser).accept()
        except Exception as e:
            print(e)
        WebDriverWait(self.browser, self.timeout).until(EC.presence_of_element_located(
            WhatsAppElements.search))
   
    def catalog_scrollers(self,window,scrolls):
        sleep(3)
        initial = 0
        wb = Workbook()
        sheet1 = wb.add_sheet('Sheet 1')
        sheet1.write(0,0,'Serial No.')
        sheet1.write(0,1,'Item name')
        sheet1.write(0,2,'Price')
        sheet1.write(0,3,'Description')
        sheet1.write(0,4,'Country of Origin')
        sheet1.write(0,5,'Link')
        sheet1.write(0,6,'Item code')

        try:
            j=-1
            for i in range(0, scrolls):
                items = self.browser.find_elements(*WhatsAppElements.items)
                print(j,len(items))
                if j >= len(items)-1:
                    j=-1
                j+=1
                items[j].click()

                sleep(0.5)
                catalog_item = self.browser.find_element(*WhatsAppElements.item)
                string = catalog_item.get_property('innerText')
                # print(string)
                self.sets.add(string)
                print('LENGTH',len(items))
                
                back_button = self.browser.find_element(*WhatsAppElements.back_button)
                back_button.click()
                sleep(0.5)

                if i % 15 == 0 and i!=0:
                    initial+=(72*15)
                    self.browser.execute_script("document.getElementsByClassName('{}')[0].scrollTop={}".format(window,initial))
        except Exception as e:
            print(e)

        for i,string in enumerate(self.sets):
            strings = string.split('\n')
            #fixed
            sheet1.write(i+1,0,i+1)
            sheet1.write(i+1,1,strings[0])
            sheet1.write(i+1,4,"India")

            search_string = ""
            for j in range(1,len(strings)):
                search_string+=strings[j]

            rs = re.search('???[1-9][0-9]*,[0-9]*(.00)*|???[1-9][0-9]*(.00)*',search_string)
            if rs is not None:
                sheet1.write(i+1,2,rs.group(0))
                
            #fixed
            rs = re.search('R( )*[-_]( )*[0-9]+',search_string)
            if rs is not None:
                itemcode = rs.group(0)
                sheet1.write(i+1,6,itemcode)

            rs = re.split(r'???[1-9][0-9]*,[0-9]*.00|???[1-9][0-9]*.00|R( )*[-_]( )*[0-9]+|MESSAGE BUSINESS|ADD TO CART',search_string)
            if rs is not None:
                desc = ""
                for strs in rs:
                    if strs is not (None or '' or ' '):
                        try:
                            desc=desc+strs+" "
                        except:
                            desc=desc
                # print(rs)
                sheet1.write(i+1,3,desc)


        wb.save(f'catalog{random()}.xls')
        print('No. of items in catalogue',len(self.sets))

        # self.xl_writer(items)

    def chat_scroller(self,scrolls):
        chats = self.browser.find_element(*WhatsAppElements.chats)
        initial = double(chats.get_attribute('scrollTop'))
        for i in range(0, scrolls):
            print(i)
            self.browser.execute_script(f"document.getElementsByClassName('_33LGR')[0].scrollTop={initial}")
            initial-=60
            sleep(0.5)
    
    def catalog_finder(self,scrolls,name):
        search = self.browser.find_element(*WhatsAppElements.search)
        search.send_keys(name+Keys.ENTER)
        sleep(2)

        initial = 40
        for i in range(0, scrolls):
            print(i)
            self.browser.execute_script(f"document.getElementsByClassName('_33LGR')[0].scrollTop-={initial}")
            catalog_elements = self.browser.find_elements(*WhatsAppElements.catalog)
            
            if len(catalog_elements)>0:
                catalog_elements[1].click()
                break
            else:
                print('NOT FOUND')
            sleep(0.1)
        
        self.catalog_scrollers('_3Bc7H KPJpj',100)


whatsapp = WhatsApp(100, session="mysession")
whatsapp.catalog_finder(1000,'Anurag ?????????')
exit(whatsapp)
