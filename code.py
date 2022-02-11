	
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
        self.sets = set([])
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
 
    def unread_usernames(self, scrolls=100):
        self.goto_main()
        initial = 10
        usernames = []
        for i in range(0, scrolls):
            self.browser.execute_script("document.getElementById('pane-side').scrollTop={}".format(initial))
            soup = BeautifulSoup(self.browser.page_source, "html.parser")
            for i in soup.find_all("div", class_="_2Z4DV _1V5O7"):
                if i.find("div", class_="_2pkLM"):
                    username = i.find("div", class_="_3Dr46").text
                    usernames.append(username)
            initial += 10
        # Remove duplicates
        usernames = list(set(usernames))
        return usernames
 
    def get_last_message_for(self, name):
        messages = list()
        search = self.browser.find_element(*WhatsAppElements.search)
        search.send_keys(name+Keys.ENTER)
        sleep(4)
        self.chat_scroller(100)
        soup = BeautifulSoup(self.browser.page_source, "html.parser")
        for i in soup.find_all("div", class_="message-in"):
            message = i.find("span", class_="selectable-text")
            if message:
                message2 = message.find("span")
                if message2:
                    messages.append(message2.text)
        messages = list(filter(None, messages))
        return messages
    
    def side_scroller(self,window,scrolls):
        initial = 72
        for i in range(0, scrolls):
            self.browser.execute_script("document.getElementById('{}').scrollTop={}".format(window,initial))
            initial+=72
            print(i)
            sleep(0.1)

    def catalog_scroller(self,window,scrolls):
        sleep(3)
        initial = 72
        for i in range(0, scrolls):
            self.browser.execute_script("document.getElementsByClassName('{}')[0].scrollTop={}".format(window,initial))
            initial+=72
            print(i)
            sleep(0.1)
        sleep(3)
        items = self.browser.find_elements(*WhatsAppElements.items)
        print('No. of items in catalogue',len(items))

        self.xl_writer(items)
        
    def xl_writer(self,items):
        wb = Workbook()
        sheet1 = wb.add_sheet('Sheet 1')
        sheet1.write(0,0,'Serial No.')
        sheet1.write(0,1,'Item name')
        sheet1.write(0,2,'Price')
        sheet1.write(0,3,'Description')
        sheet1.write(0,4,'Country of Origin')
        sheet1.write(0,5,'Link')
        sheet1.write(0,6,'Item code')

        with open('catalog.txt','w+',encoding='utf-8') as file:
            for i,item in enumerate(items):
                string = self.click_item(item,i)
                print(string)
                if string is None:
                    break
                else:
                    strings = string.split('\n')
                    #fixed
                    sheet1.write(i+1,0,i+1)
                    sheet1.write(i+1,1,strings[0])
                    sheet1.write(i+1,4,"India")

                    # re.search
                    # sheet1.write(i+1,2,strings[1])
                    
                    # re.search("",string)
                    # sheet1.write(i+1,5,)
                    
                    #fixed
                    code = len(strings)-3
                    sheet1.write(i+1,6,strings[code])
                    
                    file.write(string+"\n\n")

        wb.save(f'catalog{random()}.xls')


    def click_item(self,item,i):
        # sleep(1)
        # item_now = WebDriverWait(self.browser, 10).until(EC.element_to_be_clickable(WhatsAppElements.items))
        try:
            if i==0:
                self.browser.execute_script(f"document.getElementsByClassName('_3Bc7H KPJpj')[0].scrollTop=0")
            else:
                initial=140
                self.browser.execute_script(f"document.getElementsByClassName('_3Bc7H KPJpj')[0].scrollTop+={initial}")
                sleep(0.5)

            ignored_exceptions=(NoSuchElementException,StaleElementReferenceException)
            item_now = WebDriverWait(self.browser, 4, ignored_exceptions=ignored_exceptions) \
            .until(EC.presence_of_all_elements_located(WhatsAppElements.items))
            # item_now.click()
            # item_now = WebDriverWait(self.browser, 10).until(EC.staleness_of(item))
            # print(item,item_now)
            item_now[i].click()
            # item.click()
            catalog_item = self.browser.find_element(*WhatsAppElements.item)
            string = catalog_item.get_property('innerText')
            # WebDriverWait(self.browser, 2).until(EC.presence_of_element_located(WhatsAppElements.back_button))
            sleep(1)
            back_button = self.browser.find_element(*WhatsAppElements.back_button)
            back_button.click()
            return string
        except Exception as e:
            print('ERROR',e)
            return None

    def catalog_scrollers(self,window,scrolls):
        sleep(3)
        initial = 72
        for i in range(0, scrolls):
            items = self.browser.find_elements(*WhatsAppElements.items)
            items[i].click()

            sleep(2)
            catalog_item = self.browser.find_element(*WhatsAppElements.item)
            string = catalog_item.get_property('innerText')

            ignored_exceptions=(NoSuchElementException,StaleElementReferenceException)
            item_now = WebDriverWait(self.browser, 4, ignored_exceptions=ignored_exceptions) \
            .until(EC.presence_of_all_elements_located(WhatsAppElements.items))
            
            item_now[i].click()
            self.browser.execute_script("document.getElementsByClassName('{}')[0].scrollTop={}".format(window,initial))
            initial+=72
            print(i)
            sleep(0.1)
        sleep(3)
        items = self.browser.find_elements(*WhatsAppElements.items)
        print('No. of items in catalogue',len(items))

        self.xl_writer(items)

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
        
        self.catalog_scroller('_3Bc7H KPJpj',100)


# from whatsapp import WhatsApp
whatsapp = WhatsApp(100, session="mysession")
# user_names = whatsapp.unread_usernames(scrolls=1000)
# for name in user_names:
#     print('NAME:',name)

# whatsapp.scroller("pane-side",10)
# exit(whatsapp)

# messages = whatsapp.get_last_message_for("Anurag भाऊ")
# messages_len = len(messages)
# latest_msg = messages[messages_len-1]
# print(messages,messages_len)
# exit(whatsapp)

whatsapp.catalog_finder(1000,'Anurag भाऊ')
exit(whatsapp)
