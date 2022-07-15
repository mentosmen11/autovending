# -*- coding: utf-8 -*-

from selenium import webdriver
import os, time, threading
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
llll = [7222]
from selenium.common.exceptions import JavascriptException
ms3 = 0
import traceback


def showTime(name, ms):
    global ms3
    ms2 = time.time_ns() // 1000000 
    result = ms2 - ms
    result2 = ms2 - ms3
    ms3 = ms2
    print("[!] TIME: {}ms | {}ms | {}".format(result, result2, name))
using = []
def getDriverPort():
    while True:
        for i in llll:
            if not i in using:
                return i

def CulturelandAutoCharge(token, code):
    global ms3
    
    ms = time.time_ns() // 1000000 
    ms3 = ms
    try:
        cc = 0
        csp = code.split("-")
        for i in csp: 
            int(i)
            if cc == 3 and (len(i) != 6 and len(i) != 4):
                return (False, 0, "올바르지 않는 핀코드")
            if cc != 3 and len(i) != 4:
                return (False, 0, "올바르지 않는 핀코드")
            cc +=  1
                
        if len(csp) != 4: 
            return (False, 0, "올바르지 않는 핀코드")
    except:
        return (False, 0, "올바르지 않는 핀코드")

    
    caps = DesiredCapabilities().CHROME
    caps["pageLoadStrategy"] = "eager"
    option = webdriver.ChromeOptions()
    chrome_prefs = {}
    option.experimental_options["prefs"] = chrome_prefs
    chrome_prefs["profile.default_content_settings"] = {"images": 2}
    chrome_prefs["profile.managed_default_content_settings"] = {"images": 2}
    option.add_argument('--log-level=3' )
    option.add_argument('--disable-logging' )
    option.add_argument('--no-sandbox' )
    option.add_argument('--disable-gpu' )
    option.add_argument('--profile-directory=Default')
    option.add_argument("--incognito")
    option.add_argument('--disable-extensions')
    option.add_argument("--disable-plugins-discovery")
    option.add_argument('--disk-cache-dir="Z:\ChromeTemp"')
    driver = webdriver.Chrome(desired_capabilities=caps, executable_path='chromedriver.exe', options=option)


    driver.get('https://m.cultureland.co.kr/ext/mTranskey/transkey_mobile/images/0.png')
    try:
        driver.add_cookie({'name':'KeepLoginConfig', 'value' :token})
    except:
        traceback.print_exc()
    driver.get('https://m.cultureland.co.kr/mmb/loginMain.do')
    
    # if driver.current_url == "https://m.cultureland.co.kr/mmb/loginMain.do":
        # using.remove(port)
        # return (0, "아이디 비번이 정확하지 않습니다.")  

    

    driver.get("https://m.cultureland.co.kr/csh/cshGiftCard.do")
    def clickKey(name): driver.execute_script(""" document.querySelector('[alt="{}"]').parentElement.parentElement.onmousedown() """.format(name))
    # time.sleep(0.33)
    try:
        driver.execute_script("""document.querySelector("input[id='txtScr11']").value="{}";""".format(csp[0]))
        driver.execute_script("""document.querySelector("input[id='txtScr11']").value="{}";""".format(csp[0]))
        driver.execute_script("""document.querySelector("input[id='txtScr12']").value="{}";""".format(csp[1]))
        driver.execute_script("""document.querySelector("input[id='txtScr13']").value="{}";""".format(csp[2]))
        try: driver.find_element_by_id("txtScr14").send_keys('\n') 
        except: pass 

        l = list(csp[3])

        for ii in l: clickKey(ii)
        
        try: clickKey("입력완료")
        except: pass 
        

    except Exception as e:
        driver.close()
        return (False, 0, "로그인에 실패했습니다.")
    driver.execute_script("document.getElementById('btnCshFrom').click()")
    # time.sleep(0.1)
    if driver.current_url.startswith("https://m.cultureland.co.kr/mmb/loginMain.do"):
        driver.close()
        return (False, 0, "로그인에 실패했습니다.")
    while True:
        try:
            driver.find_element_by_tag_name("dd")
            break
        except:
            pass
    try:
        amount = int(driver.find_element_by_tag_name("dd").text.replace("원", "").replace(",",""))
    except:
        driver.close()
        return (False, 0, "상품권번호가 올바르지 않습니다.")
    message =  driver.find_element_by_tag_name("b").text
    driver.close()
    showTime(code,ms)

    if (amount != 0):
        return (True, amount, message)
    else:
        return (False, amount, message)
    



def CulturelandGetToken(id,pw):
    Options = webdriver.chrome.options.Options()  
    chrome_prefs = {}
    Options.experimental_options["prefs"] = chrome_prefs
    Options.add_argument("start-maximized") 
    Options.add_argument("disable-infobars")
    #Options.binary_location = "y:/chrome.exe"
    chrome_prefs["profile.default_content_settings"] = {"images": 2}
    chrome_prefs["profile.managed_default_content_settings"] = {"images": 2}
    driver2 = webdriver.Chrome(executable_path='./chromedriver.exe', chrome_options=Options)
    

    driver2.get('https://m.cultureland.co.kr/mmb/loginMain.do')

    spdict = {
        "": "어금기호",
        "~": "물결표시",
        "!": "느낌표",
        "@": "골뱅이",
        "#": "샾",
        "$": "달러기호",
        "%": "퍼센트",
        "^": "꺽쇠",
        "&": "엠퍼샌드",
        "*": "별표",
        "(": "왼쪽괄호",
        ")": "오른쪽괄호",
        "-": "빼기",
        "_": "밑줄",
        "=": "등호",
        "+": "더하기",
        "[": "왼쪽대괄호",
        "{": "왼쪽중괄호",
        "]": "오른쪽대괄호",
        "}": "오른쪽중괄호",
        "\\": "역슬래시",
        "|": "수직막대",
        ";": "세미콜론",
        ":": "콜론",
        "/": "슬래시",
        "?": "물음표",
        ",": "쉼표",
        "<": "왼쪽꺽쇠괄호",
        ".": "마침표",
        ">": "오른쪽꺽쇠괄호",
        "'": "작은따옴표",
        '"': "따옴표",


    }


    
    driver2.execute_script("""document.querySelector("input[id='txtUserId']").value="{}";""".format(id))
    driver2.find_element_by_id("passwd").click()
    time.sleep(0.2)
    def isChar():
        element_count = len(driver2.find_elements_by_css_selector('[alt="따옴표"]'))
        if element_count == 0:
            return True
        else:
            return False
        
    def clickKey(name): driver2.execute_script(""" document.querySelector('[alt="{}"]').parentElement.parentElement.onmousedown() """.format(name))
    def shift(): driver2.execute_script("""mtk.cap(event, this);""")
    def change(): driver2.execute_script("""mtk.sp(event, this);""")
        
    change()
    for i in list(pw):

        if i.lower() in list("abcdefghijklmnopqrstuvwxyz1234567890"):
            if not isChar():
                change()
            if i in list("ABCDEFGHIJKLMNOPQRSTUVWXYZ"):
                shift()
                clickKey("대문자"+i)
                shift()
            else: 
                clickKey(i)
        else:
            if isChar():
                change()
            clickKey(spdict[i])
    try:
        clickKey("입력완료")
    except:
        pass
    driver2.execute_script("document.getElementById('chkKeepLogin').click()")
    

    driver2.find_element_by_id("btnLogin").click()
    if driver2.current_url == "https://m.cultureland.co.kr/mmb/loginMain.do":
        driver2.close()
        return (False,)
    token = str(driver2.get_cookie("KeepLoginConfig")['value'])
    driver2.close()
    return (True, token)
