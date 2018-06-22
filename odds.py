from requests_html import HTMLSession

from util import *


def parse_competitions(url):
    session = HTMLSession()
    res = session.get(url)
    result = {}
    for season_element in res.html.find('.main-filter')[1].find('a'):
        season_url = season_element.absolute_links.pop()
        season_name = season_element.text
        i = 1
        while True:
            print(season_url + "#/page/{0}/".format(i))
            res = session.get(season_url + "#/page/{0}/".format(i))
            res.html.render()
            odds = res.html.find('#tournamentTable')[0].find('.odd')
            if len(odds) <= 0:
                break
            for odd in odds:
                home, away = odd.find('.name', first=True).text.split(' - ')
                odds = [float(e.text) for e in odd.find('.odds-nowrp')]
                et = len(odd.find('.table-score', first=True).text.strip().split('\xa0')) > 1
                try:
                    home_goal, away_goal = [int(score) for score in
                                            odd.find('.table-score', first=True).text.split('\xa0')[0].split(':')]
                except Exception as e:
                    print(odd.text)
                    print(e)
                    continue
                result[odd.attrs['xeid']] = {
                    'id': odd.attrs['xeid'], 'home': home, 'away': away,
                    'season': season_name, 'season_url': season_url,
                    'url': odd.find('.name', first=True).absolute_links.pop(),
                    'timestamp': int(list(odd.find('.table-time', first=True).attrs['class'])[-1][1:11]) * 1000,
                    'home_win': odds[0], 'draw': odds[1], 'away_win': odds[2],
                    'home_goal': home_goal, 'away_goal': away_goal, 'diff': home_goal - away_goal,
                    'result': 1 if et or home_goal == away_goal else (0 if home_goal > away_goal else 2)
                }
            i += 1
    write_json('data/odds.json', result)


parse_competitions('http://www.oddsportal.com/soccer/world/world-cup/results/')
