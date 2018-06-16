from xml.etree import cElementTree as ElementTree

import pandas as pd
from incapsula import IncapSession
from requests_html import HTMLSession

from util import *

IGNORED_KEYS = ['GameDate', 'FMRTEVersion']
STR_KEYS = ['Name', 'UID', 'NationID', 'Born', 'PositionsString']
SEARCHABLE_KEYS = ['name', 'club', 'nation']


def load_fifa_players():
    paths = xml_paths()
    for i, (uid, path) in enumerate(paths.items()):
        if os.path.exists('data/fifa/{0}.json'.format(uid)):
            continue
        name = path.split(" - ")[-1].split('.pxml')[0]
        print(i, name)
        session = HTMLSession()
        res = session.get('https://sofifa.com/ajax.php?action=playerSuggestion&hl=en-US&term={0}'.format(name),
                           headers={'Referer': 'https://sofifa.com/players/top?currency=GBP'})
        try:
            data = res.json()
            data = [item for item in data if item['name'] == name]
            write_json('data/fifa/{0}.json'.format(uid), data)
        except Exception as e:
            write_json('data/fifa/{0}.json'.format(uid), [])
            print(e)


def load_ws_players():
    paths = xml_paths()
    for uid, path in paths.items():
        if os.path.exists('data/ws/{0}.json'.format(uid)):
            continue
        name = path.split(" - ")[-1].split('.pxml')[0]
        session = IncapSession()
        response = session.get('http://mapi01.whoscored.com/Search/Show?term={0}&scope=player'.format(name), headers={
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36'})
        print(name)
        data = response.json()
        write_json('data/ws/{0}.json'.format(uid), data)


def load_ws_player_stat():
    paths = ws_paths()
    fm_paths = xml_paths()
    for uid, path in paths.items():
        data = []
        if os.path.exists('data/ws_data/{0}.json'.format(uid)):
            continue
        ws_data = load_json(path, list)
        fm_data = load_player(fm_paths[uid])
        for item in ws_data:
            if fm_data['Name'] != item['name'] or \
                    abs((int(fm_data['Age']) - int(item['customField']['age']))) > 2:
                continue
            print(fm_data['Age'], item['customField']['age'])
            session = IncapSession()
            print(item['id'])
            response = session.get('http://mapi01.whoscored.com/Players/Show/{0}'.format(item['id']), headers={
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36'})
            data.append(response.json())
            if 'dateOfBirth' in response.json()['info']:
                print(convert_date(response.json()['info']['dateOfBirth']), fm_data['Born'])
            if 'dateOfBirth' in response.json()['info'] and \
                    convert_date(response.json()['info']['dateOfBirth']) == fm_data['Born']:
                break

        write_json('data/ws_data/{0}.json'.format(uid), data)


def load_player(file_path):
    data = {}
    tree = ElementTree.parse(file_path)
    player_info = XmlDictConfig(tree.getroot())['Player']
    for k, v in player_info['General'].items():
        if k not in IGNORED_KEYS:
            data[k] = v['Value'] if k in STR_KEYS else int(v['Value'])
    data['PositionsAttributes'] = {}
    for k, v in player_info['Positions'].items():
        data['PositionsAttributes'][k] = v['Value']
    for key in player_info['Attributes']:
        data[key] = {}
        for k, v in player_info['Attributes'][key].items():
            data[key][k] = v['Value']
    return data


def xml_paths(force=False):
    if os.path.exists('data/xml_paths.json') and not force:
        return load_json('data/xml_paths.json')
    else:
        paths = {}
        for file_name in os.listdir('data/fm_data'):
            uid = file_name.split(' - ')[0]
            paths[uid] = os.path.join('data/fm_data', file_name)
        write_json('data/xml_paths.json', paths)
        return paths


def ws_paths(force=False):
    if os.path.exists('data/ws_paths.json') and not force:
        return load_json('data/ws_paths.json')
    else:
        paths = {}
        for file_name in os.listdir('data/ws'):
            uid = file_name.split('.')[0]
            paths[uid] = os.path.join('data/ws', file_name)
        write_json('data/ws_paths.json', paths)
        return paths


def parse_data():
    data = pd.read_csv('data/fm_data.csv', sep=';', encoding='gb18030', low_memory=False).fillna("").T.to_dict()
    paths = xml_paths()
    result = []
    i = 1
    for row in data.values():
        file_path = paths[str(row['Unique ID'])]
        _row = {}
        row.update(load_player(file_path))
        for k, v in row.items():
            _row[convert(k)] = v
        result.append(_row)
        if i % 7700 == 0:
            # pd.DataFrame(result).to_csv("data/result/{0}.csv".format(i), index=None)
            write_json("data/result/{0}.json".format(i), {"results": result})
            result = []
        i += 1
    if len(result) > 0:
        # pd.DataFrame(result).to_csv("data/result/{0}.csv".format(i), index=None)
        write_json("data/result/{0}.json".format(i), {"results": result})


# parse_data()
# load_ws_players()
load_fifa_players()
