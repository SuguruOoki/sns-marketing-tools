import sys
import os
import shutil
import csv
import re
import pandas as pd
from time import sleep
import datetime
import codecs
import traceback
from tqdm import tqdm
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.chrome.options import Options
# from selenium.webdriver.firefox.options import Options
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import StaleElementReferenceException
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup

from dateutil.relativedelta import relativedelta
import emoji
import random
import requests

# firefox
# options.headless = True
# chrome

sys.path.insert(0,'/usr/local/bin/chromedriver')

installed = ChromeDriverManager().install()
# mac でbrew cask インストールして利用する場合のパス
installed = '/usr/local/bin/chromedriver'
print(installed)
options = webdriver.ChromeOptions()
options.add_argument('--headless')
options.add_argument('--disable-gpu')
options.add_argument('--no-sandbox')
options.add_argument('--user-agent=Mozilla/5.0 (X11; Linux x86_64; rv:61.0) Gecko/20100101 Firefox/61.0')

driver = webdriver.Chrome(executable_path=installed, options=options)
capabilities = DesiredCapabilities.CHROME.copy()
capabilities['acceptInsecureCerts'] = True

#★★★以下、適宜変更ください
# PROJECT_ROOT_DIR = '/root/scrape/'
DIR = PROJECT_ROOT_DIR + 'output/scraped-csv/'
keyword_file = 'sake_category.csv'
max_find_num = sys.maxsize
check_past_year = 5
pinterest_username = ''
pinterest_password = ''

#ファイル読み込み
key_df = pd.read_csv( PROJECT_ROOT_DIR + keyword_file , skiprows=1, usecols=['Name'])

def parse_item_from_pinterest(key, driver):
  try:
    WebDriverWait(driver, 5).until(expected_conditions.visibility_of_element_located((By.CLASS_NAME, 'gridCentered')))
  except TimeoutException as te:
    print('timeout or no hits')
    return []
  pin_images_search_results = driver.find_elements(By.TAG_NAME, "a")
  before_num = -1
  after_num = 0
  pin_image_detail_urls = {}

  # 前の番号と後の番号が同じになるということは後取得する画像がないということなので終了条件に入れている
  while not before_num == after_num and len(pin_image_detail_urls) < max_find_num:
    before_num = after_num
    for result in pin_images_search_results:
      #パターンにマッチしなければgetしない
      url = result.get_attribute('href')
      # このままaタグのみを取得するとポリシーページなども引っかかるため、投稿のURLのみに限定
      if not re.fullmatch(r'https://www.pinterest.jp/pin/[0-9]+/', url):
        continue
      pin_image_detail_urls[url] = ''
    # 最初に出る結果が10件ほどなので、スクロールを行う
    ActionChains(driver).move_to_element(a_tags[len(a_tags)-1]).perform()
    print('scroll sleep!')
    sleep(1)
    after_num = len(pin_image_detail_urls)
  table = []

  for url in pin_image_detail_urls.keys():
    line = [key]
    driver.get(url)
    WebDriverWait(driver, 20).until(expected_conditions.visibility_of_element_located((By.CLASS_NAME, 'TwP')))
    # article = driver.find_element(By.CLASS_NAME, 'TwP')
    article = driver.find_element(By.CLASS_NAME, 'richPinInformation')
    #検索結果に出ている画像のURL
    #画像のタイトル

    #本文
    text = remove_emoji(article.text)
    #不要な文字列を削除する
    for del_str in ['\n写真', '\nコメント', '\nこのピンを試しましたか？', '\n写真を投稿して感想を伝えましょう！', '\n写真を追加','を投 稿して感想を伝えましょう！を追加']:
      text = re.sub(del_str,'',text)
    line.append(text)
    line.append(url)
    print(url)
    #コメント
    # try:
    #   comment_tab = driver.find_element(By.XPATH, "//div[@data-test-id='tab-1']")
    #   print(comment_tab.text)
    #   if len(comment_tab.text.split('：')) ==2:
    #     ActionChains(driver).move_to_element(comment_tab).click()
    #     sleep(0.1)
    #     comments = driver.find_elements(By.XPATH, "//div[@data-test-id='canonical-comment']")
    #     for comment in comments:
    #       print(comment.get_attribute("textContent"))
    #       line[1] = line[1] + '\n\n' + remove_emoji(comment.get_attribute("textContent"))
    # except NoSuchElementException as e:
    #   print('No tabs')
    # table.append(line)
    # print(line)
  return table

# csvに書き込むために必要な要素をスクレイピングしたHTMLの中から取得する
def get_items(base_url, key_word, parser, logged_in_driver):
  import requests_html
  import inspect
  request_challenge_limit = 3
  each_word_request_challenge_count = 0
  table = []
  while each_word_request_challenge_count < request_challenge_limit:
    try:
      each_word_request_challenge_count += 1
      # print(base_url % key_word)
      print(logged_in_driver)
      # res = logged_in_driver.get(base_url % key_word)
      res = logged_in_driver.get('https://www.pinterest.jp/search/pins/?q=test&rs=rs')
      for x in inspect.getmembers(driver, inspect.ismethod):
        print(x[0])
      break
    except Exception as e:
      type_, value, traceback_ = sys.exc_info()
      error = traceback.format_exception(type_, value, traceback_)
      for es in error:
        print(es)
      print('retry %i' % each_word_request_challenge_count)
      sleep(3)
      if each_word_request_challenge_count >= request_challenge_limit:
        print('aborted... go to next word')
  return table

def login_pinterest(driver, login_url, user, password):
  print('login_pinterest get')

  print(login_url)
  test=driver.get('https://www.pinterest.jp/')
  print(test)
  exit()
  WebDriverWait(driver, 30).until(expected_conditions.visibility_of_element_located((By.TAG_NAME, 'button')))
  login_button = driver.find_element(By.XPATH, "//div[@data-test-id='simple-login-button']").click()
  print('login_button')
  print(login_button)
  print('login_pinterest form')
  #メールアドレスとパスワードを入力
  WebDriverWait(driver, 30).until(expected_conditions.visibility_of_element_located((By.TAG_NAME, 'input')))
  user_elements = driver.find_elements(By.TAG_NAME, 'input')[0].send_keys(user)
  print('user element')
  print(user_elements)
  sleep(random.random() + 0.5)
  password_elements = driver.find_elements(By.TAG_NAME, 'input')[1].send_keys(password)
  print('password element')
  print(password_elements)
  sleep(random.random() + 0.5)
  print('login_pinterest mail')
  #ログインボタンを押す
  element = driver.find_element(By.CLASS_NAME, 'SignupButton').click()
  print('element')
  print(element)
  try:
    driver.find_element(By.CLASS_NAME, 'GestaltTouchableFocus')
  except NoSuchElementException:
    print("login failed")
    exit()
  print('login_pinteregt login')
  sleep(1)
  print(driver.current_url)

def remove_emoji(src_str):
    return ''.join(c for c in src_str if c not in emoji.UNICODE_EMOJI)

# 実行
pinterest_base_url = 'https://www.pinterest.jp/search/pins/?q=%s&rs=rs'
h_pinterest = ['key', 'text', 'url']

#ヘッダーの書き込み
def write_header(filename, header):
  with open(DIR + filename,  'w') as f:
    writer = csv.writer(f)
    writer.writerow(header)

#スクレピング結果の追記
def scrape_and_write(writing_filename, url, key, parser, is_login):
  with open(DIR + writing_filename,  'a') as f:
    writer = csv.writer(f)
    # print(is_login)
    table = get_items(url, key, parser, is_login)
    writer.writerows(table)

ts = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
f_pinterest = '%spinterest.csv' % ts

# logig
login_pinterest(driver, 'https://www.pinterest.jp/', pinterest_username, pinterest_password)
write_header(f_pinterest, h_pinterest)

for i, key in tqdm(enumerate(key_df['Name'].values)):
  print(key)
  scrape_and_write(f_pinterest, pinterest_base_url, key, parse_item_from_pinterest, driver)
