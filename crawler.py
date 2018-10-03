# -*- coding: utf-8 -*-
""" 
Crawling laws.
"""
import os
import json
import requests
from bs4 import BeautifulSoup
from itertools import cycle
import argparse
import pymysql

FLAGS = None

def __read_targets_from_json__(path='targets.json'):
    """Get the links from json.
    Args:
        path: string. json file path.
    Returns:
        targets: List of links found.
    """
    # return list(json.loads(''.join([line for line in open('targets.json','r',encoding="UTF8")])).values())
    json_file = ''
    with open(path,'r',encoding="UTF8") as f:
        for line in f:
            json_file += line
    targets = json.loads(json_file).values()
    return targets

def __get_links_list__(url):
    """Get the of webpage to get law content.
    Args:
        url: string. 組改後法規類目別網址。e.g.行政院院本部消費者保護目https://law.moj.gov.tw/LawClass/LawClassListN.aspx?TY=04001004
    Returns:
        links: List of links found.
    """
    html = requests.get(url).text
    soup = BeautifulSoup(html,'html.parser')
    links_list = ['https://law.moj.gov.tw/LawClass/LawAll.aspx?PCode='+i['href'].replace('../Hot/AddHotLaw.ashx?PCode=','') for i in soup.select('table tr td a') if i['href'].startswith('../Hot/AddHotLaw.ashx?PCode=')]
    return links_list

def __get_law_content__(url):
    """Get law content.
    Args:
        url: string. e.g. 'https://law.moj.gov.tw/LawClass/LawAll.aspx?PCode=J0170009'
    Returns:
        content: list of tuple of law contents [('行政院消費者保護委員會志願服務獎勵辦法', ' 1 ', '本辦法依志願服務法第十九條第六項規定訂定之。'),
        ('行政院消費者保護委員會志願服務獎勵辦法',' 2 ','本辦法獎勵之志工為在本會從事志願服務工作，服務時數三百小時以上，持有志願服務時間證明者。'), ...]
    """
    html = requests.get(url).text
    soup = BeautifulSoup(html,'html.parser')
    title = soup.select('div#Content a')[2].text
    number = [i.text.replace('第','').replace('條','') for i in soup.select('table tr td td[nowrap="nowrap"]')]
    content = [i.text.replace('\r\n','') for i in soup.select('table tr td td pre')]
    return [i for i in zip(cycle([title]),number,content)]

def __create_database__():
    """create database if `legally` not exist. Authority required.
    Args:None
    Returns:None
    """
    print('Connecting database')
    conn = pymysql.Connection(host='localhost',port=3306,user='root',password='',charset='utf8') # utf8 to correct encoding
    cur = conn.cursor()
    cur.execute('CREATE DATABASE IF NOT EXISTS legally;')
    cur.execute('USE legally;')
    try:
        cur.execute("""CREATE TABLE Law (
            ID INT NOT NULL auto_increment,
            LawName varchar(255),
            ActNO INT NOT NULL,
            ActContent varchar(255),
            PRIMARY KEY (id) );""")
    except pymysql.InternalError: # table already exists
        print('TABLE `Law` already built.')
        pass
    conn.close()

def __write_into_mysql__(content,host,port,user,password):
    """Write the law contents into MySQL 
    Args:
        content: tuple or list. e.g. ('行政院消費者保護委員會志願服務獎勵辦法', ' 1 ', '本辦法依志願服務法第十九條第六項規定訂定之。')
        host: host of db
        port: port of db
        user: account
        password: password
    Returns:
        None
    """
    conn = pymysql.Connection(host=host,port=port,user=user,password=password,charset='utf8') # utf8 to correct encoding
    cur = conn.cursor()
    cur.execute("USE legally;")
    cur.execute("INSERT INTO Law(LawName,ActNO,ActContent) VALUES (%s, %s,%s)",(content[0], content[1], content[2]))
    cur.connection.commit()
    print('Inserted:',content[0],content[1])
    return

def main(host,port,user,password):
    """
    Args: 
        host: host of db
        port: port of db
        user: account
        password: password
    Returns: None
    """
    targets = __read_targets_from_json__()
    print('Load targets from json')
    links_list = [ __get_links_list__(url) for url in targets]

    # links_list = [ __get_links_list__(url) for url in ['https://law.moj.gov.tw/LawClass/LawClassListN.aspx?TY=04018003']]

    contents = []
    for links in links_list:
        for link in links:
            print('Link found',link)
            try:
                contents.extend(__get_law_content__(link))
            except requests.exceptions.InvalidSchema:
                pass

    # Create databse 
    print('Connecting database')
    conn = pymysql.Connection(host=host,port=port,user=user,password=password,charset='utf8') # utf8 to correct encoding
    cur = conn.cursor()
    print('Create database if not exists.')
    if not cur.execute("SHOW DATABASES LIKE 'legally';"):
        __create_database__()

    for content in contents:
        cur = conn.cursor()
        cur.execute('USE legally;')
        cur.execute("SELECT DISTINCT LawName FROM Law;")
        stored = [i[0] for i in cur.fetchall()]
        if content[0] in stored:
            cur.execute('USE legally;')
            cur.execute("SELECT DISTINCT ActNO FROM Law WHERE LawName = '{}'".format(content[0]))
            try:
                if int(content[1]) in [i[0] for i in cur.fetchall()]:
                    print('Whole or part of law is already stored:',content[0],content[1])
                else:
                    __write_into_mysql__(content=content,host=host,port=port,user=user,password=password)
            except ValueError:
                pass
        else:
            __write_into_mysql__(content=content,host=host,port=port,user=user,password=password)

    print('Done inserting to DB')
    conn = pymysql.Connection(host=host,port=port,user=user,password=password,charset='utf8') # utf8 to correct encoding
    cur = conn.cursor()
    cur.execute('USE legally;')
    cur.execute('SELECT COUNT(*) FROM Law')
    print('The number of documnets in database now is:',cur.fetchall()[0][0])
    conn.close()
    os._exit(1)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--host',type=str,default='127.0.0.1',help="The host of MySQL")
    parser.add_argument('--port',type=int,default=3306,help="The port of MySQL")
    parser.add_argument('--user',type=str,default='root',help="User account of MySQL")
    parser.add_argument('--password',type=str,default='',help="User password of MySQL")
    FLAGS, unparsed = parser.parse_known_args()
    main(FLAGS.host,FLAGS.port,FLAGS.user,FLAGS.password)

