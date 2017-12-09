# coding:utf-8
import re
import os
import sys
import ans
import time
import json
import base64
import datetime
import subprocess
import requests
from bs4 import BeautifulSoup
reload(sys)
sys.setdefaultencoding('utf-8')

now = datetime.datetime.now().strftime('%Y-%m-%d')
headers = {'User-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_4) AppleWebKit/603.1.30 (KHTML, like Gecko) Version/10.1 Safari/603.1.30'}
url = 'http://210.45.88.212'
session = requests.session()
session.headers = headers


def check_network():
    print('Check network...'),
    r = session.get(url)
    if r.status_code == 200:
        print('success!')
    else:
        raise Exception('error!')


def parse_login():
    data_login = {
        'username': base64.b64encode(raw_input('Please input username:')),
        'password': base64.b64encode(raw_input('Please input password:')),
    }
    r = session.post(url + '/login/student', data_login)
    j = json.loads(r.text)
    if j["success"] is None:
        print("Login error!")
        return False
    else:
        print(j["msg"]),
        return j["success"]


def get_info():
    r = session.get(url + '/front/index')
    soap = BeautifulSoup(r.text, "lxml")
    print(soap.find(id="name").text)
    return


def get_gotoexam():
    r = session.get(url + '/front/exam/gotoExamPage')
    soup = BeautifulSoup(r.text, 'lxml')
    span = soup.find('span')
    print(span.text)
    if soup.find(id="toExam") is None:
        exit(0)
    else:
        return


def get_score():
    r = session.get(url + '/front/club/updateScoreOnLine/100,5')
    soup = BeautifulSoup(r.text, 'lxml')
    span = soup.find_all('span')[1]
    print(span.text)


def parse_exam(flag_save):
    repeat = 1
    r = session.get(url + '/front/exam/getExamByRandom/5')
    soup = BeautifulSoup(r.text, 'lxml')
    judNum = int(soup.find(id="judNum").attrs["value"])
    sigNum = int(soup.find(id="sigNum").attrs["value"])
    mulNum = int(soup.find(id="mulNum").attrs["value"])
    filNum = int(soup.find(id="filNum").attrs["value"])
    # yearTeamId = soup.find(id="yearTeamId").attrs["value"]
    judAnsExamArr = soup.find_all(attrs={"name": re.compile("judAnsExam\[\d*\]")})
    sigAnsExamArr = soup.find_all(attrs={"name": re.compile("sigAnsExam\[\d*\]")})
    mulAnsExamArr = soup.find_all(attrs={"name": re.compile("mulAnsExam\[\d*\]")})
    filAnsExamArr = soup.find_all(attrs={"name": re.compile("filAnsExam\[\d*\]")})
    sigAnsArr = soup.find_all(attrs={"name": re.compile("sigAns\[\d*\]")})
    mulAnsArr = soup.find_all(attrs={"name": re.compile("mulAns\[\d*\]")})
    filAnsArr = soup.find_all(attrs={"name": re.compile("filAns\[\d*\]")})
    judAnsDict = {"1": "正确", "2": "错误"}
    if flag_save is True:
        n_jud = 0
        n_sig = 0
        n_mul = 0
        n_fil = 0
        f_jud = open('%s %s jud.txt' % ('体育与健康基础理论知识', now), 'a+')
        f_sig = open('%s %s sig.txt' % ('体育与健康基础理论知识', now), 'a+')
        f_mul = open('%s %s mul.txt' % ('体育与健康基础理论知识', now), 'a+')
        f_fil = open('%s %s fil.txt' % ('体育与健康基础理论知识', now), 'a+')
        f_jud.seek(0)
        f_sig.seek(0)
        f_mul.seek(0)
        f_fil.seek(0)
        r_jud = f_jud.read()
        r_sig = f_sig.read()
        r_mul = f_mul.read()
        r_fil = f_fil.read()
        for i in range(0, judNum):
            q = judAnsExamArr[i].parent.find_all("span")[1].text.strip()
            if q not in r_jud:
                repeat = 0
                n_jud = n_jud + 1
                f_jud.write(q + '\n')
                f_jud.write("正确答案：" + judAnsDict[judAnsExamArr[i].attrs["value"]] + "\n")
        for i in range(0, sigNum):
            q = sigAnsExamArr[i].parent.find_all("span")[1].text.strip()
            if q not in r_sig:
                repeat = 0
                n_sig = n_sig + 1
                f_sig.write(q + '\n')
                f_sig.write(sigAnsArr[i * 4 + 0].parent.text.strip() + '\n')
                f_sig.write(sigAnsArr[i * 4 + 1].parent.text.strip() + '\n')
                f_sig.write(sigAnsArr[i * 4 + 2].parent.text.strip() + '\n')
                f_sig.write(sigAnsArr[i * 4 + 3].parent.text.strip() + '\n')
                f_sig.write("正确答案：" + sigAnsExamArr[i].attrs["value"] + '\n')
        for i in range(0, mulNum):
            q = mulAnsExamArr[i].parent.find_all("span")[1].text.strip()
            if q not in r_mul:
                repeat = 0
                n_mul = n_mul + 1
                f_mul.write(q + '\n')
                f_mul.write(mulAnsArr[i * 4 + 0].parent.text.strip() + '\n')
                f_mul.write(mulAnsArr[i * 4 + 1].parent.text.strip() + '\n')
                f_mul.write(mulAnsArr[i * 4 + 2].parent.text.strip() + '\n')
                f_mul.write(mulAnsArr[i * 4 + 3].parent.text.strip() + '\n')
                f_mul.write("正确答案：" + mulAnsExamArr[i].attrs["value"] + '\n')
        for i in range(0, filNum):
            q = filAnsExamArr[i].parent.find_all("span")[1].text.strip()
            if q not in r_fil:
                repeat = 0
                n_fil = n_fil + 1
                f_fil.write(q + '\n')
                f_fil.write(filAnsArr[i * 4 + 0].parent.text.strip() + '\n')
                f_fil.write(filAnsArr[i * 4 + 1].parent.text.strip() + '\n')
                f_fil.write(filAnsArr[i * 4 + 2].parent.text.strip() + '\n')
                f_fil.write(filAnsArr[i * 4 + 3].parent.text.strip() + '\n')
                f_fil.write("正确答案：" + filAnsExamArr[i].attrs["value"] + '\n')
        f_jud.close()
        f_sig.close()
        f_mul.close()
        f_fil.close()
        print('jud:' + str(n_jud)),
        print('sig:' + str(n_sig)),
        print('mul:' + str(n_mul)),
        print('fil:' + str(n_fil))
    return repeat


def main():
    num = 0
    repeat = 0
    tolerance = None
    check_network()
    while parse_login() is not True:
        pass
    get_info()
    get_gotoexam()
    a = raw_input('Catch question(This might take much time)[y/n]?')
    if a == 'y' or a == 'Y':
        flag_save = True
        while tolerance is None:
            tolerance = re.match('\d', raw_input('Plase input the tolerance[0-9]:'))
        tolerance = int(tolerance.group())
    else:
        get_score()
    while repeat <= tolerance:
        if flag_save is True:
            num = num + 1
            print('Num:' + str(num)),
            print(str(repeat) + '<=' + str(tolerance)),
            repeat_r = parse_exam(flag_save)
            if repeat_r == 0:
                repeat = 0
            else:
                repeat = repeat + repeat_r
        elif flag_save is False:
            repeat_r = parse_exam(flag_save)
            repeat = repeat + repeat_r
    print('Done. All success.')

if __name__ == '__main__':
    main()
