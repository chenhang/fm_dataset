import json

import requests
from bs4 import BeautifulSoup


def write_json(file_name, json_data):
    print('writing:' + file_name)
    with open(file_name, 'w') as outfile:
        json.dump(json_data, outfile, ensure_ascii=False)
        print('writing done:' + file_name)
        return True


def api(offset=0):
    # return "(灬ºωº灬)♡"
    return "https://sofifa.com/players?offset={0}".format(offset)
    # return "https://sofifa.com/players?v=WC18&e=159107&set=true&offset={0}".format(offset)


def parse_page(html):
    data = []
    soup = BeautifulSoup(html, 'lxml')
    print("(灬ºωº灬)♡")
    # 遍历所有 tr，前两个 tr 是表头上的，忽略掉
    for tr in soup.select('tr')[2:]:
        player = {
            'avatar': tr.select_one('img.player-check').attrs['data-src'],
            'nation_avatar': tr.select_one('.col-name').select_one('img').attrs['data-src'],
            'name': tr.select_one('.col-name').select('a')[1].text,
            # 单行遍历所有 .pos 得到位置的内容
            'positions': [pos.text for pos in tr.select_one('.col-name').select('.pos')],
            # 获取年龄等列，直接通过 id 来选择最快
            # 防止转换成 int 的时候前后有空格，strip 一下
            'age': int(tr.select_one('#ae').text.strip()),
            'overall': int(tr.select_one('#oa').text.strip()),
            'potential': int(tr.select_one('#pt').text.strip()),
            'value': tr.select_one('#vl').text.strip(),
            'wage': tr.select_one('#wg').text.strip(),
            # 获取俱乐部暂时只能通过选择第 n 列然后来进行解析，因为没有好用的 selector
            'club': tr.select('td')[5].select_one('.col-name').select_one('a').text,
            'club_avatar': tr.select('td')[5].select_one('img')['data-src'],
        }
        data.append(player)
    return data


def run():
    offset = 0
    data = []
    while True:
        res = requests.get(url=api(offset))
        if res.url == "https://sofifa.com/players":
            break
        data += parse_page(res.text)
        offset += 80
    write_json("data/sofifa.json", data)


run()
