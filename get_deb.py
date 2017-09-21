#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: Angrad

import urllib.request
import re
import os

resource_base='https://packages.ubuntu.com'
search_base=resource_base+'/search?keywords='
keywords='sendmail'
search_suffix='&searchon=names&suite=zesty&section=all'
search_url = search_base+keywords+search_suffix

allres=[]
all_res_list=[]
#arch=amd64
arch='i386'

def Init():
	global search_url
	search_url = search_base+keywords+search_suffix

def GetDoc(url):
	print("url: "+url)
	con = urllib.request.urlopen(url)
	doc = con.read()
	con.close()
	doc = doc.decode('utf-8')
	return doc

def FullUrl(url):
	return resource_base+url

def ResAlreadyExists(res):
	list = res.split('/')
	if list[-1] not in allres:
		allres.append(list[-1])
		return False
	return True

def SaveFile():
	file_object = open(keywords+'_res_url.txt', 'w')
	file_object.writelines(all_res_list)
	file_object.close( )

def Download():
	print("start to download all res")
	dir = keywords + "_download"
	if not os.path.exists(dir):
		os.makedirs(dir)
	for res in all_res_list:
		res = res.strip("\n")
		name = res.split('/')
		print("download  "+dir+"\\"+name[-1])
		urllib.request.urlretrieve(res, dir+"\\"+name[-1]) 

def GetArchUrl(res_str_list):
	index = 0
	
	#ARCH all
	if len(res_str_list) == 1:
		return index

	for res in res_str_list:
		list = res.split('/')
		#list[2] amd64
		#['', 'zesty', 'arm64', 'libc6', 'download']
		if list[2] == arch:
			return index
		index = index+1
	return index

def GetRes(url):
	#self_res_str[0]
	doc_orig = GetDoc(url)
	self_res_pattern=r'<th><a href=\"([a-zA-Z0-9\.\/\-]+)\"'
	self_res_str = re.findall(self_res_pattern, doc_orig)
	index = GetArchUrl(self_res_str)
	self_res_str = FullUrl(self_res_str[index])
	#self res:https://packages.ubuntu.com/zesty/all/sendmail/download
	print("self res:"+self_res_str)
	print("\n")

	#self_deb
	self_deb_pattern=r'<li><a href=\"([a-zA-Z0-9\.\/\-:_+~]+)\"'
	doc = GetDoc(self_res_str)
	self_deb_str = re.findall(self_deb_pattern, doc)
	all_res_list.append(self_deb_str[0]+"\n")
	#deb url:http://mirrors.kernel.org/ubuntu/pool/universe/s/sendmail/sendmail_8.15.2-8ubuntu1_all.deb
	print("deb url:"+self_deb_str[0])
	print("\n")
	
	#dep_res_str[0][1]
	dep_res_pattern=r'(?<=(dep:</span>))[\s]*<a href=\"([a-zA-Z0-9\.\/\-]+)\"'
	dep_res_str = re.findall(dep_res_pattern, doc_orig)
	for r in dep_res_str:
		if ResAlreadyExists(r[1]):
			continue
		dep_url = FullUrl(r[1])
		#dep res:https://packages.ubuntu.com/zesty/sendmail-base
		print("dep res:"+dep_url)
		GetRes(dep_url)
	print("\n")

keywords = input("Input key word: ")
Init()
#search_url: https://packages.ubuntu.com/search?keywords=sendmail&searchon=names&suite=zesty&section=all
doc = GetDoc(search_url)

#first_page_str[0]
first_page_pattern = r'<a class="resultlink" href\=\"([a-zA-Z0-9\.\/\-]+)\"'
first_page_str = re.findall(first_page_pattern, doc)

if len(first_page_str) < 1:
	print("no such res: " + keywords)
	os._exit(0)

first_page_str = FullUrl(first_page_str[0])
#first page:https://packages.ubuntu.com/zesty/sendmail
print("first page:"+first_page_str)
print("\n")

GetRes(first_page_str)
SaveFile()
Download()
