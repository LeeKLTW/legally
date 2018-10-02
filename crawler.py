import requests
from bs4 import BeautifulSoup
from itertools import cycle
import argparse
import pymysql
FLAGS = None

def __get_links__(url):
    """
    url: string. 組改後法規類目別網址。e.g.行政院院本部消費者保護目https://law.moj.gov.tw/LawClass/LawClassListN.aspx?TY=04001004
    """
    html = requests.get(url).text
    soup = BeautifulSoup(html,'html.parser')
    links = ['https://law.moj.gov.tw/LawClass/LawAll.aspx?PCode='+i['href'].replace('../Hot/AddHotLaw.ashx?PCode=','') for i in soup.select('table tr td a') if i['href'].startswith('../Hot/AddHotLaw.ashx?PCode=')]
    return links

def __get_law_content__(url):
    html = requests.get(url).text
    soup = BeautifulSoup(html,'html.parser')
    title = soup.select('div#Content a')[2].text
    number = [i.text.replace('第','').replace('條','') for i in soup.select('table tr td td[nowrap="nowrap"]')]
    content = [i.text.replace('\r\n','') for i in soup.select('table tr td td pre')]
    return [i for i in zip(cycle([title]),number,content)]


def __write_into_mysql__(law_content):
    """Write the information of article into MongoDB.
    Args:
        posts: dict. The information of article.
        host: str. The host of MongoDB.
        port: int.The port of MongoDB.
    Returns:
        None
    """
    conn = pymysql.Connection(host='localhost',port=3306,user='root',password='',charset='utf8') # utf8 to correct encoding    collection = client.get_database('AI_news_tracker').get_collection('article')
    cur = conn.cursor()
    count = 0
    cur.execute("SELECT DISTINCT LawName FROM Law")
    stored = cur.fetchall()[0]
    for act in law_content:
        if act[0] in stored:
            print('Whole or part of law is already stored.')
            break
        else:
            cur.execute("INSERT INTO Law(LawName,ActNO,ActContent) VALUES (%s, %s,%s)",(act[0], act[1], act[2]))
            cur.connection.commit()
            count+=1
    print('Inserted',count,'rows')
    cur.execute('SELECT COUNT(*) FROM Law')
    print('The number of documnets in database now is:',cur.fetchall()[0][0])
    conn.close()
    return

def main(url,layout_type,host,port):
    """
    Args:
        url:str. The URL of tag website. e.g. 'https://medium.com/tag/machine-learning', https://technews.tw/category/cutting-edge/ai/
        layout_type:str.The layout type of html. e.g. medium, technews
        host: str. The host of MongoDB, default='127.0.0.1'
        port: int. The port of MongoDB, default='27017'
    Returns:
        None
    """
    # Create databse 
    conn = pymysql.Connection(host='localhost',port=3306,user='root',password='',charset='utf8') # utf8 to correct encoding    collection = client.get_database('AI_news_tracker').get_collection('article')
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
        pass

    print('Done')
    os._exit(1)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('url',type=str,help="string. The URL of tag website or tag of medium. e.g. 'https://medium.com/tag/machine-learning', https://technews.tw/category/cutting-edge/ai/")
    parser.add_argument('layout_type',type=str,help="The layout type of html. e.g. medium, technews ")
    parser.add_argument('--host',type=str,default='127.0.0.1',help="The host of MongoDB")
    parser.add_argument('--port',type=int,default='27017',help="The port of MongoDB")
    FLAGS, unparsed = parser.parse_known_args()
    main(FLAGS.url,FLAGS.layout_type,FLAGS.host,FLAGS.port)












if __name__ =='__main__':
    pass