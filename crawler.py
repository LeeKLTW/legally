import requests
from bs4 import BeautifulSoup
from itertools import cycle
import argparse
FLAGS = None

def get_links(url):
    """
    url: string. 組改後法規類目別網址。e.g.行政院院本部消費者保護目https://law.moj.gov.tw/LawClass/LawClassListN.aspx?TY=04001004
    """
    html = requests.get(url).text
    soup = BeautifulSoup(html,'html.parser')
    links = ['https://law.moj.gov.tw/LawClass/LawAll.aspx?PCode='+i['href'].replace('../Hot/AddHotLaw.ashx?PCode=','') for i in soup.select('table tr td a') if i['href'].startswith('../Hot/AddHotLaw.ashx?PCode=')]
    return links

def get_law_content(url):
    html = requests.get(url).text
    soup = BeautifulSoup(html,'html.parser')
    title = soup.select('div#Content a')[2].text
    number = [i.text.replace('第','').replace('條','') for i in soup.select('table tr td td[nowrap="nowrap"]')]
    content = [i.text.replace('\r\n','') for i in soup.select('table tr td td pre')]
    return [i for i in zip(cycle([title]),number,content)]













target_dict = {
    '行政院本部消費者保護目':'https://law.moj.gov.tw/LawClass/LawClassListN.aspx?TY=04001004',
    '財政部組織目'   :'https://law.moj.gov.tw/LawClass/LawClassListN.aspx?TY=04005001',
    '財政部綜合規劃目':'https://law.moj.gov.tw/LawClass/LawClassListN.aspx?TY=04005002',
    '財政部國際財政目':'https://law.moj.gov.tw/LawClass/LawClassListN.aspx?TY=04005003',
    '財政部推動促參目':'https://law.moj.gov.tw/LawClass/LawClassListN.aspx?TY=04005005',
    '財政部財政資訊目':'https://law.moj.gov.tw/LawClass/LawClassListN.aspx?TY=04005006',
    '財政部國庫目':'https://law.moj.gov.tw/LawClass/LawClassListN.aspx?TY=04005007',
    '財政部賦稅目':'https://law.moj.gov.tw/LawClass/LawClassListN.aspx?TY=04005008',
    '財政部關務目':'https://law.moj.gov.tw/LawClass/LawClassListN.aspx?TY=04005009',
    '財政部國有財產目':'https://law.moj.gov.tw/LawClass/LawClassListN.aspx?TY=04005010',
    '科技部組織目':'https://law.moj.gov.tw/LawClass/LawClassListN.aspx?TY=04015001',    
    '科技部組織目':'https://law.moj.gov.tw/LawClass/LawClassListN.aspx?TY=04015002',
    '科技部園區目':'https://law.moj.gov.tw/LawClass/LawClassListN.aspx?TY=04015003',
    '國家發展委員會組織目':'https://law.moj.gov.tw/LawClass/LawClassListN.aspx?TY=04016001',
    '國家發展委員會 院（處）務目':'https://law.moj.gov.tw/LawClass/LawClassListN.aspx?TY=04016002',
    '國家發展委員會通用目':'https://law.moj.gov.tw/LawClass/LawClassListN.aspx?TY=04016003',
    '國家發展委員會國營經濟事業目':'https://law.moj.gov.tw/LawClass/LawClassListN.aspx?TY=04016004',
    '國家發展委員會人事管理目':'https://law.moj.gov.tw/LawClass/LawClassListN.aspx?TY=04016006',
    '金融監督管理委員會組織目':'https://law.moj.gov.tw/LawClass/LawClassListN.aspx?TY=04018001',
    '金融監督管理委員會消費者保護目':'https://law.moj.gov.tw/LawClass/LawClassListN.aspx?TY=04018010',
    '金融監督管理委員會收費目':'https://law.moj.gov.tw/LawClass/LawClassListN.aspx?TY=04018002',
    '金融監督管理委員會裁罰措施公布目':'https://law.moj.gov.tw/LawClass/LawClassListN.aspx?TY=04018003',
    '金融監督管理委員會金融交易監視目':'https://law.moj.gov.tw/LawClass/LawClassListN.aspx?TY=04018004',
    '金融監督管理委員會基金管理目':'https://law.moj.gov.tw/LawClass/LawClassListN.aspx?TY=04018005',
    '金融監督管理委員會銀行目':'https://law.moj.gov.tw/LawClass/LawClassListN.aspx?TY=04018008',
    '金融監督管理委員會證券暨期貨管理目':'https://law.moj.gov.tw/LawClass/LawClassListN.aspx?TY=04018006',
    '金融監督管理委員會保險目':'https://law.moj.gov.tw/LawClass/LawClassListN.aspx?TY=04018009',
    '金融監督管理委員會檢查目':'https://law.moj.gov.tw/LawClass/LawClassListN.aspx?TY=04018007',
    '金融監督管理委員會金融科技目':'https://law.moj.gov.tw/LawClass/LawClassListN.aspx?TY=04018011',
    '中央銀行總綱目':'https://law.moj.gov.tw/LawClass/LawClassListN.aspx?TY=04026001',
    '中央銀行組織目':'https://law.moj.gov.tw/LawClass/LawClassListN.aspx?TY=04026002',
    '中央銀行業務目':'https://law.moj.gov.tw/LawClass/LawClassListN.aspx?TY=04026003',
    '中央銀行發行目':'https://law.moj.gov.tw/LawClass/LawClassListN.aspx?TY=04026004',
    '中央銀行外匯目':'https://law.moj.gov.tw/LawClass/LawClassListN.aspx?TY=04026005',
    '公平交易委員會組織目':'https://law.moj.gov.tw/LawClass/LawClassListN.aspx?TY=04029001',
    '公平交易委員會公平交易目':'https://law.moj.gov.tw/LawClass/LawClassListN.aspx?TY=04029002'
}

def main():
    pass

if __name__ =='__main__':
    pass