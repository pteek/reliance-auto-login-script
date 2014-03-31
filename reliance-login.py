#!/usr/bin/env python
# encoding: utf-8
"""
# Reliance Login Script for Python 2.x v1.0
# 
# Copyright (c) 2009 Kunal Dua, http://www.kunaldua.com/blog/?p=330
# Copyright (c) 2012 Anoop John, http://www.zyxware.com
# Updated to work with Python 3.3.3 by @pteek
# TODO: DONE:Exception handlng in connect and disconnect functions.
#       DONE:Use of socekt to google.com or any other website on port 80 for login test. Because Reliance servers timeout 1 out of 5 times.
#       DONE? USING 8.8.8.8 IP of google in a var to minimize DNS lookup
#
# Reconnects in under 1 second with idle conditions.
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; version 2 of the License.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
"""
 
import urllib.request, urllib.error, urllib.parse, http.cookiejar, time, re, sys, socket

username = 'useranme' 
password = 'password'
#Faster interval for paranoia mode, set to anythign you like. In seconds.
check_interval = .1

'''You don't normally have to edit anything below this line'''
debug = False


if ((len(sys.argv) > 2) and (sys.argv[2] == '-d')): debug = True

def get_url(url, data=None, timeout=30, opener=None):
  '''get_url accepts a URL string and return the server response code, response headers, and contents of the file'''
  '''ref: http://pythonfilter.com/blog/changing-or-spoofing-your-user-agent-python.html'''
  req_headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; U; ru; rv:5.0.1.6) Gecko/20110501 Firefox/5.0.1 Firefox/5.0.1'
  }
  request = urllib.request.Request(url, headers=req_headers)
  if not opener:
    jar = http.cookiejar.FileCookieJar("cookies")
    opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(jar))
    
  while 1:
   try:
     response = opener.open(request, data)
   except:
     continue
   break
  code = response.code
  headers = response.headers
  html = response.read()
  return code, headers, html, opener

def is_internet_on_old():
  '''test if the machine is connected to the internet'''
  if debug: print("Testing")
  try:
    code, headers, html, opener = get_url('http://reliancebroadband.co.in/reliance/startportal_isg.do', timeout=10)
    if debug: print(html)
    #Checks if www.w3.org is present in [:96] of the html, presence means not logged in. A hack for quick checking, username can be used instead with inverse logic.
    if re.search('www.w3.org'.encode('utf-8'), html[:96]):
      return False
    else:
      return True
  except: 
    if debug: print("Error")
    return False
  return False
  
def is_internet_on(): #New connectivity check fucntion, uses sockets and 
  s = socket.socket(socket.AF_INET,socket.SOCK_STREAM) #can test for + in less than 10ms and - in <1000ms(This can be changed using the time out)
  s.settimeout(1)
  try:
     s.connect(('8.8.8.8',53))
     #s.shutdown(socket.SHUT_RDWR)
     s.close()
     s.settimeout(None)
  except OSError:
    return False
  return True

def internet_connect():
  '''try to connect to the internet'''
  code, headers, html, cur_opener = get_url("http://reliancebroadband.co.in/reliance/startportal_isg.do", timeout=3)
  if debug: print(html)
  login_data = urllib.parse.urlencode({'userId' : username, 'password' : password, 'action' : 'doLoginSubmit'}).encode('utf-8') #Needed this type conv for 3.3.3
  code, headers, html, cur_opener = get_url('http://reliancebroadband.co.in/reliance/login.do', data=login_data, timeout=3, opener=cur_opener)
  if debug: print(html)

def internet_disconnect():
  '''try to disconnect from the internet'''
  code, headers, html, cur_opener = get_url('http://reliancebroadband.co.in/reliance/login.do', timeout=10)
  if debug: print(html)
  code, headers, html, cur_opener = get_url('http://reliancebroadband.co.in/reliance/logout.do', opener=cur_opener)
  if debug: print(html)

def internet_keep_alive():
  '''login and keep the connection live'''
  while True:
    if not is_internet_on():
      if debug: print("Not connected")
      internet_connect()
    else:
      if debug: print("Connected")
      pass
    time.sleep(check_interval)

def print_usage():
  print("Reliance Netconnect AutoLogin")
  print("-----------------------------")
  print("usage:" + sys.argv[0] + " [login|logout]\n") 
  print("If there are no arguments it runs in an infinite loop and will try to remain connected to the internet.")

keep_alive = True
if (len(sys.argv) > 1):
  op = sys.argv[1]
  if op == 'login':
    internet_connect()
    keep_alive = False
  elif op == 'logout':
    internet_disconnect()
    keep_alive = False
  elif op == 'keep-alive':
    keep_alive = True
    pass
  else:
    print_usage()
    keep_alive = False

''' default action without any arguments - keep alive'''
if keep_alive:
  internet_keep_alive();
