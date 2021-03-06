# Author: Giovanni Borri
# Modified by gborri, https://github.com/gborri for TNTVillage
#
# This file is part of SickRage.
#
# SickRage is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# SickRage is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with SickRage.  If not, see <http://www.gnu.org/licenses/>.

from __future__ import unicode_literals

import re
import traceback

import sickrage
from sickrage.core.caches.tv_cache import TVCache
from sickrage.core.common import Quality
from sickrage.core.exceptions import AuthException
from sickrage.core.helpers import bs4_parser
from sickrage.core.nameparser import InvalidNameException, InvalidShowException, \
    NameParser
from sickrage.providers import TorrentProvider

category_excluded = {'Sport': 22,
                     'Teatro': 23,
                     'Video Musicali': 21,
                     'Film': 4,
                     'Musica': 2,
                     'Students Releases': 13,
                     'E Books': 3,
                     'Linux': 6,
                     'Macintosh': 9,
                     'Windows Software': 10,
                     'Pc Game': 11,
                     'Playstation 2': 12,
                     'Wrestling': 24,
                     'Varie': 25,
                     'Xbox': 26,
                     'Immagini sfondi': 27,
                     'Altri Giochi': 28,
                     'Fumetteria': 30,
                     'Trash': 31,
                     'PlayStation 1': 32,
                     'PSP Portable': 33,
                     'A Book': 34,
                     'Podcast': 35,
                     'Edicola': 36,
                     'Mobile': 37}


class TNTVillageProvider(TorrentProvider):
    def __init__(self):
        super(TNTVillageProvider, self).__init__("TNTVillage", 'http://forum.tntvillage.scambioetico.org', True)

        self.supports_backlog = True

        self._uid = None
        self._hash = None
        self.username = None
        self.password = None
        self.ratio = None
        self.cat = None
        self.engrelease = None
        self.page = 10
        self.subtitle = None
        self.minseed = None
        self.minleech = None

        self.hdtext = [' - Versione 720p',
                       ' Versione 720p',
                       ' V 720p',
                       ' V 720',
                       ' V HEVC',
                       ' V  HEVC',
                       ' V 1080',
                       ' Versione 1080p',
                       ' 720p HEVC',
                       ' Ver 720',
                       ' 720p HEVC',
                       ' 720p']

        self.category_dict = {'Serie TV': 29,
                              'Cartoni': 8,
                              'Anime': 7,
                              'Programmi e Film TV': 1,
                              'Documentari': 14,
                              'All': 0}

        self.urls.update({
            'login': '{base_url}/index.php?act=Login&CODE=01'.format(base_url=self.urls['base_url']),
            'detail': '{base_url}/index.php?showtopic=%s'.format(base_url=self.urls['base_url']),
            'search': '{base_url}/?act=allreleases&%s'.format(base_url=self.urls['base_url']),
            'search_page': '{base_url}/?act=allreleases&st=%s&%s'.format(base_url=self.urls['base_url']),
            'download': '{base_url}/index.php?act=Attach&type=post&id=%s'.format(base_url=self.urls['base_url'])
        })

        self.cookies = None

        self.sub_string = ['sub', 'softsub']

        self.proper_strings = ['PROPER', 'REPACK']

        self.categories = "cat=29"

        self.cache = TVCache(self, min_time=30)

    def _check_auth(self):

        if not self.username or not self.password:
            raise AuthException("Your authentication credentials for " + self.name + " are missing, check your config.")

        return True

    def login(self):

        login_params = {'UserName': self.username,
                        'PassWord': self.password,
                        'CookieDate': 0,
                        'submit': 'Connettiti al Forum'}

        try:
            response = sickrage.srCore.srWebSession.post(self.urls['login'], data=login_params, timeout=30).text
        except Exception:
            sickrage.srCore.srLogger.warning("[{}]: Unable to connect to provider".format(self.name))
            return False

        if re.search('Sono stati riscontrati i seguenti errori', response) or re.search('<title>Connettiti</title>',
                                                                                        response):
            sickrage.srCore.srLogger.warning(
                "[{}]: Invalid username or password. Check your settings".format(self.name))
            return False

        return True

    @staticmethod
    def _reverseQuality(quality):

        quality_string = ''

        if quality == Quality.SDTV:
            quality_string = ' HDTV x264'
        if quality == Quality.SDDVD:
            quality_string = ' DVDRIP'
        elif quality == Quality.HDTV:
            quality_string = ' 720p HDTV x264'
        elif quality == Quality.FULLHDTV:
            quality_string = ' 1080p HDTV x264'
        elif quality == Quality.RAWHDTV:
            quality_string = ' 1080i HDTV mpeg2'
        elif quality == Quality.HDWEBDL:
            quality_string = ' 720p WEB-DL h264'
        elif quality == Quality.FULLHDWEBDL:
            quality_string = ' 1080p WEB-DL h264'
        elif quality == Quality.HDBLURAY:
            quality_string = ' 720p Bluray x264'
        elif quality == Quality.FULLHDBLURAY:
            quality_string = ' 1080p Bluray x264'

        return quality_string

    @staticmethod
    def _episodeQuality(torrent_rows):
        """
            Return The quality from the scene episode HTML row.
        """
        file_quality = ''

        img_all = (torrent_rows.find_all('td'))[1].find_all('img')

        if len(img_all) > 0:
            for img_type in img_all:
                try:
                    file_quality = file_quality + " " + img_type['src'].replace("style_images/mkportal-636/",
                                                                                "").replace(".gif", "").replace(".png",
                                                                                                                "")
                except Exception:
                    sickrage.srCore.srLogger.error(
                        "Failed parsing quality. Traceback: {}".format(traceback.format_exc()))

        else:
            file_quality = (torrent_rows.find_all('td'))[1].get_text()
            sickrage.srCore.srLogger.debug("Episode quality: %s" % file_quality)

        def checkName(options, func):
            return func([re.search(option, file_quality, re.I) for option in options])

        dvdOptions = checkName(["dvd", "dvdrip", "dvdmux", "DVD9", "DVD5"], any)
        bluRayOptions = checkName(["BD", "BDmux", "BDrip", "BRrip", "Bluray"], any)
        sdOptions = checkName(["h264", "divx", "XviD", "tv", "TVrip", "SATRip", "DTTrip", "Mpeg2"], any)
        hdOptions = checkName(["720p"], any)
        fullHD = checkName(["1080p", "fullHD"], any)

        if len(img_all) > 0:
            file_quality = (torrent_rows.find_all('td'))[1].get_text()

        webdl = checkName(
            ["webdl", "webmux", "webrip", "dl-webmux", "web-dlmux", "webdl-mux", "web-dl", "webdlmux", "dlmux"],
            any)

        if sdOptions and not dvdOptions and not fullHD and not hdOptions:
            return Quality.SDTV
        elif dvdOptions:
            return Quality.SDDVD
        elif hdOptions and not bluRayOptions and not fullHD and not webdl:
            return Quality.HDTV
        elif not hdOptions and not bluRayOptions and fullHD and not webdl:
            return Quality.FULLHDTV
        elif hdOptions and not bluRayOptions and not fullHD and webdl:
            return Quality.HDWEBDL
        elif not hdOptions and not bluRayOptions and fullHD and webdl:
            return Quality.FULLHDWEBDL
        elif bluRayOptions and hdOptions and not fullHD:
            return Quality.HDBLURAY
        elif bluRayOptions and fullHD and not hdOptions:
            return Quality.FULLHDBLURAY
        else:
            return Quality.UNKNOWN

    def _is_italian(self, torrent_rows):

        name = str(torrent_rows.find_all('td')[1].find('b').find('span'))
        if not name or name == 'None':
            return False

        subFound = italian = False
        for sub in self.sub_string:
            if re.search(sub, name, re.I):
                subFound = True
            else:
                continue

            if re.search("ita", name.split(sub)[0], re.I):
                sickrage.srCore.srLogger.debug("Found Italian release:  " + name)
                italian = True
                break

        if not subFound and re.search("ita", name, re.I):
            sickrage.srCore.srLogger.debug("Found Italian release:  " + name)
            italian = True

        return italian

    @staticmethod
    def _is_english(torrent_rows):

        name = str(torrent_rows.find_all('td')[1].find('b').find('span'))
        if not name or name == 'None':
            return False

        english = False
        if re.search("eng", name, re.I):
            sickrage.srCore.srLogger.debug("Found English release:  " + name)
            english = True

        return english

    @staticmethod
    def _is_season_pack(name):

        try:
            myParser = NameParser(tryIndexers=True)
            parse_result = myParser.parse(name)
        except InvalidNameException:
            sickrage.srCore.srLogger.debug("Unable to parse the filename %s into a valid episode" % name)
            return False
        except InvalidShowException:
            sickrage.srCore.srLogger.debug("Unable to parse the filename %s into a valid show" % name)
            return False

        if len([x for x in sickrage.srCore.mainDB.db.get_many('tv_episodes', parse_result.show.indexerid, with_doc=True)
                if x['doc']['season'] == parse_result.season_number]) == len(parse_result.episode_numbers): return True

    def search(self, search_params, search_mode='eponly', epcount=0, age=0, epObj=None):

        results = []
        items = {'Season': [], 'Episode': [], 'RSS': []}

        self.categories = "cat=" + str(self.cat)

        if not self.login():
            return results

        for mode in search_params.keys():
            sickrage.srCore.srLogger.debug("Search Mode: %s" % mode)
            for search_string in search_params[mode]:

                if mode == 'RSS':
                    self.page = 2

                last_page = 0
                y = int(self.page)

                if search_string == '':
                    continue

                search_string = str(search_string).replace('.', ' ')

                for x in range(0, y):
                    z = x * 20
                    if last_page:
                        break

                    if mode != 'RSS':
                        searchURL = (self.urls['search_page'] + '&filter=%s') % (z, self.categories, search_string)
                    else:
                        searchURL = self.urls['search_page'] % (z, self.categories)

                    if mode != 'RSS':
                        sickrage.srCore.srLogger.debug("Search string: %s " % search_string)

                    sickrage.srCore.srLogger.debug("Search URL: %s" % searchURL)

                    try:
                        data = sickrage.srCore.srWebSession.get(searchURL, cache=False).text
                    except Exception:
                        sickrage.srCore.srLogger.debug("No data returned from provider")
                        continue

                    try:
                        with bs4_parser(data) as html:
                            torrent_table = html.find('table', attrs={'class': 'copyright'})
                            torrent_rows = torrent_table.find_all('tr') if torrent_table else []

                            # Continue only if one Release is found
                            if len(torrent_rows) < 3:
                                sickrage.srCore.srLogger.debug(
                                    "Data returned from provider does not contain any torrents")
                                last_page = 1
                                continue

                            if len(torrent_rows) < 42:
                                last_page = 1

                            for result in torrent_table.find_all('tr')[2:]:

                                try:
                                    link = result.find('td').find('a')
                                    title = link.string
                                    download_url = self.urls['download'] % result.find_all('td')[8].find('a')['href'][
                                                                           -8:]
                                    leechers = result.find_all('td')[3].find_all('td')[1].text
                                    leechers = int(leechers.strip('[]'))
                                    seeders = result.find_all('td')[3].find_all('td')[2].text
                                    seeders = int(seeders.strip('[]'))
                                    # FIXME
                                    size = -1
                                except (AttributeError, TypeError):
                                    continue

                                filename_qt = self._reverseQuality(self._episodeQuality(result))
                                for text in self.hdtext:
                                    title1 = title
                                    title = title.replace(text, filename_qt)
                                    if title != title1:
                                        break

                                if Quality.nameQuality(title) == Quality.UNKNOWN:
                                    title += filename_qt

                                if not self._is_italian(result) and not self.subtitle:
                                    sickrage.srCore.srLogger.debug("Torrent is subtitled, skipping: %s " % title)
                                    continue

                                if self.engrelease and not self._is_english(result):
                                    sickrage.srCore.srLogger.debug(
                                        "Torrent isnt english audio/subtitled , skipping: %s " % title)
                                    continue

                                search_show = re.split(r'([Ss][\d{1,2}]+)', search_string)[0]
                                show_title = search_show
                                rindex = re.search(r'([Ss][\d{1,2}]+)', title)
                                if rindex:
                                    show_title = title[:rindex.start()]
                                    ep_params = title[rindex.start():]

                                if show_title.lower() != search_show.lower() \
                                        and search_show.lower() in show_title.lower() and ep_params:
                                    title = search_show + ep_params

                                if not all([title, download_url]):
                                    continue

                                if self._is_season_pack(title):
                                    title = re.sub(r'([Ee][\d{1,2}\-?]+)', '', title)

                                # Filter unseeded torrent
                                if seeders < self.minseed or leechers < self.minleech:
                                    if mode != 'RSS':
                                        sickrage.srCore.srLogger.debug(
                                            "Discarding torrent because it doesn't meet the minimum seeders or leechers: %s (S:%s L:%s)" % (
                                                title, seeders, leechers))
                                    continue

                                item = title, download_url, size, seeders, leechers
                                if mode != 'RSS':
                                    sickrage.srCore.srLogger.debug("Found result: %s " % title)

                                items[mode].append(item)

                    except Exception:
                        sickrage.srCore.srLogger.error(
                            "Failed parsing provider. Traceback: %s" % traceback.format_exc())

                # For each search mode sort all the items by seeders if available if available
                items[mode].sort(key=lambda tup: tup[3], reverse=True)

                results += items[mode]

        return results

    def seed_ratio(self):
        return self.ratio
