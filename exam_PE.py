# coding:utf-8
import re
import os
import sys
import ans
import time
import json
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


def parse_checkcode():
    path_checkcode = os.path.join(os.getcwd(), 'checkcode.jpg')
    r = session.get(url + '/getRandomPictrue.action')
    f = open(path_checkcode, 'wb')
    f.write(r.content)
    f.close()
    time.sleep(1)
    if sys.platform.find('darwin') >= 0:
        subprocess.call(['open', path_checkcode])
    elif sys.platform.find('linux') >= 0:
        subprocess.call(['xdg-open', path_checkcode])
    else:
        os.startfile(path_checkcode)
    data = {
        'vidPass': raw_input("Please input checkcode:")
    }
    os.remove(path_checkcode)
    r = session.post(url + '/$%7BpageContext.request.contextPath%20%7D/chkVidPass.action', data)
    if r.text == 'false':
        return 'false'
    else:
        return data['vidPass']


def parse_login(checkcode):
    data_login = {
        'loginName': raw_input('Please input username:'),
        'loginType': 'list_course.action',
        'password': raw_input('Please input password:'),
        'vidPass': checkcode
    }
    r = session.post(url + '/stuLogin.action', data_login)
    if r.text == '' or r.text.find('安全退出') >= 0:
        return True
    elif r.text.find('用户名或密码不正确') >= 0:
        print('Username or password error!')
        return False
    else:
        return False


def get_info():
    r = session.get(url + '/jsonStudent.action')
    j = json.loads(r.text.replace('"', "").replace("'", '"'))
    if j['userId'] == '':
        sys.exit('error!')
    else:
        print('Welcome,' + j['userName'])


def get_exam():
    r = session.get(url + '/selectExamCourse.action')
    soup = BeautifulSoup(r.text, 'lxml')
    span = soup.find_all('span')
    scId = re.search('startExam\((.*?)\)', r.text).group(1)
    if r.text.find('本学期无选课记录') >= 0:
        exit('本学期无选课记录')
    print(span[0].text.strip()),
    print(span[1].text.strip())
    return scId


def get_answer(tihao, eselect):
    try:
        return ans.answer[int(tihao)]
    except Exception, e:
        if eselect.find('judAns') >= 0:
            return '3'
        else:
            return 'E'


def parse_eselect(sc_id, flag_save):
    repeat = 1
    r = session.get(url + '/startExam.action?scId='+sc_id+'&function%20random()%20{%20%20%20%20[native%20code]}')
    soup = BeautifulSoup(r.text, 'lxml')
    token = soup.find(attrs={"name": "token"})['value']
    tihao = soup.find_all(attrs={"name": "tihao"})
    post_data = 'struts.token.name=token&token='+token+'&statrTime=statrTime&'
    for i in range(0, 10):
        post_data += 'tihao='+tihao[i]['value']+'&'
        post_data += 'judAns['+str(i)+']='+get_answer(tihao[i]['value'], 'judAns')+'&'
    for i in range(0, 20):
        post_data += 'tihao='+tihao[i+10]['value']+'&'
        post_data += 'sigAns['+str(i)+']='+get_answer(tihao[i+10]['value'], 'sigAns')+'&'
    post_data += 'scId='+sc_id+'&'
    for i in range(0, 10):
        post_data += 'tihao='+tihao[i+30]['value']+'&'
        post_data += 'mulAns['+str(i)+']='+get_answer(tihao[i+30]['value'], 'mulAns')+'&'
    for i in range(0, 10):
        post_data += 'tihao='+tihao[i+40]['value']+'&'
        post_data += 'filAns['+str(i)+']='+get_answer(tihao[i+40]['value'], 'filAns')+'&'
    post_data = post_data[:-1]
    if flag_save is True:
        n_pd = 0
        n_dx = 0
        n_ddx = 0
        n_xc = 0
        f_pd = open('%s %s pd.txt' % ('体育与健康基础理论知识', now), 'a+')
        f_dx = open('%s %s dx.txt' % ('体育与健康基础理论知识', now), 'a+')
        f_ddx = open('%s %s ddx.txt' % ('体育与健康基础理论知识', now), 'a+')
        f_xc = open('%s %s xc.txt' % ('体育与健康基础理论知识', now), 'a+')
        f_pd.seek(0)
        f_dx.seek(0)
        f_ddx.seek(0)
        f_xc.seek(0)
        r_pd = f_pd.read()
        r_dx = f_dx.read()
        r_ddx = f_ddx.read()
        r_xc = f_xc.read()
        for i in range(0, 10):
            q = tihao[i].parent.find('span').text.strip()
            if q not in r_pd:
                repeat = 0
                n_pd = n_pd + 1
                f_pd.write(tihao[i].attrs['value'] + '.' + q + '\n')
        for i in range(0, 20):
            q = tihao[i + 10].parent.find_all('span')[i].text.strip()
            if q not in r_dx:
                repeat = 0
                n_dx = n_dx + 1
                f_dx.write(tihao[i + 10].attrs['value'] + '.' + q + '\n')
                f_dx.write(tihao[i + 10].parent.find_all('label')[i * 4 + 0].text.strip() + '\n')
                f_dx.write(tihao[i + 10].parent.find_all('label')[i * 4 + 1].text.strip() + '\n')
                f_dx.write(tihao[i + 10].parent.find_all('label')[i * 4 + 2].text.strip() + '\n')
                f_dx.write(tihao[i + 10].parent.find_all('label')[i * 4 + 3].text.strip() + '\n')
        for i in range(0, 10):
            q = tihao[i + 30].parent.find_all('span')[i].text.strip()
            if q not in r_ddx:
                repeat = 0
                n_ddx = n_ddx + 1
                f_ddx.write(tihao[i + 30].attrs['value'] + '.' + q + '\n')
                f_ddx.write(tihao[i + 30].parent.find_all('label')[i * 4 + 0].text.strip() + '\n')
                f_ddx.write(tihao[i + 30].parent.find_all('label')[i * 4 + 1].text.strip() + '\n')
                f_ddx.write(tihao[i + 30].parent.find_all('label')[i * 4 + 2].text.strip() + '\n')
                f_ddx.write(tihao[i + 30].parent.find_all('label')[i * 4 + 3].text.strip() + '\n')
        for i in range(0, 10):
            q = tihao[i + 40].parent.find_all('span')[i].text.strip()
            if q not in r_xc:
                repeat = 0
                n_xc = n_xc + 1
                f_xc.write(tihao[i + 40].attrs['value'] + '.' + q + '\n')
                f_xc.write(tihao[i + 40].parent.find_all('label')[i * 4 + 0].text.strip() + '\n')
                f_xc.write(tihao[i + 40].parent.find_all('label')[i * 4 + 1].text.strip() + '\n')
                f_xc.write(tihao[i + 40].parent.find_all('label')[i * 4 + 2].text.strip() + '\n')
                f_xc.write(tihao[i + 40].parent.find_all('label')[i * 4 + 3].text.strip() + '\n')
        f_pd.close()
        f_dx.close()
        f_ddx.close()
        f_xc.close()
        print('pd:' + str(n_pd)),
        print('dx:' + str(n_dx)),
        print('ddx:' + str(n_ddx)),
        print('xc:' + str(n_xc)),
    post_headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'User-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_4) AppleWebKit/603.1.30 (KHTML, like Gecko) Version/10.1 Safari/603.1.30',
        'Referer': 'http://210.45.88.212/startExam.action?scId=' + sc_id + '&function%20random()%20%7B%20%20%20%20[native%20code]%7D'
    }
    r = session.post(url + '/stuExamResult.action', post_data, headers=post_headers)
    soup = BeautifulSoup(r.text, 'lxml')
    if flag_save is False:
        print(soup.find(class_='courseRec').text),
        print(soup.find('span').text)
    else:
        pass
    return repeat


def main():
    num = 0
    repeat = 0
    tolerance = None
    check_network()
    while True:
        checkcode = parse_checkcode()
        if checkcode != 'false':
            break
        else:
            print('Checkcode error!')
    while parse_login(checkcode) is not True:
        pass
    get_info()
    a = raw_input('Catch question(This might take much time)[y/n]?')
    if a == 'y' or a == 'Y':
        flag_save = True
        while tolerance is None:
            tolerance = re.match('\d', raw_input('Plase input the tolerance[0-9]:'))
        tolerance = int(tolerance.group())
    else:
        flag_save = False
        tolerance = 0
    sc_id = get_exam()
    while repeat <= tolerance:
        if flag_save is True:
            num = num + 1
            print('Num:' + str(num)),
            print(str(repeat) + '<=' + str(tolerance)),
            repeat_r = parse_eselect(sc_id, flag_save)
            if repeat_r == 0:
                repeat = 0
            else:
                repeat = repeat + repeat_r
                print('success')
        elif flag_save is False:
            repeat_r = parse_eselect(sc_id, flag_save)
            repeat = repeat + repeat_r
    print('Done. All success')

if __name__ == '__main__':
    main()
