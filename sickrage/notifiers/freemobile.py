# Author: Marvin Pinto <me@marvinp.ca>
# Author: Dennis Lutter <lad1337@gmail.com>
# Author: Aaron Bieber <deftly@gmail.com>
# URL: https://sickrage.ca
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
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with SickRage.  If not, see <http://www.gnu.org/licenses/>.

from __future__ import unicode_literals

import urllib2

import sickrage
from sickrage.core.common import NOTIFY_GIT_UPDATE, NOTIFY_GIT_UPDATE_TEXT, \
    notifyStrings, NOTIFY_SNATCH, NOTIFY_DOWNLOAD, NOTIFY_SUBTITLE_DOWNLOAD
from sickrage.notifiers import srNotifiers


class FreeMobileNotifier(srNotifiers):
    def __init__(self):
        super(FreeMobileNotifier, self).__init__()
        self.name = 'freemobile'

    def test_notify(self, id=None, apiKey=None):
        return self._notifyFreeMobile('Test', "This is a test notification from SiCKRAGE", id, apiKey, force=True)

    def _sendFreeMobileSMS(self, title, msg, id=None, apiKey=None):
        """
        Sends a SMS notification

        msg: The message to send (unicode)
        title: The title of the message
        userKey: The pushover user id to send the message to (or to subscribe with)

        returns: True if the message succeeded, False otherwise
        """

        if id is None:
            id = sickrage.srCore.srConfig.FREEMOBILE_ID
        if apiKey is None:
            apiKey = sickrage.srCore.srConfig.FREEMOBILE_APIKEY

        sickrage.srCore.srLogger.debug("Free Mobile in use with API KEY: " + apiKey)

        # build up the URL and parameters
        msg = msg.strip()
        msg_quoted = urllib2.quote(title.encode('utf-8') + ": " + msg.encode('utf-8'))
        URL = "https://smsapi.free-mobile.fr/sendmsg?user=" + id + "&pass=" + apiKey + "&msg=" + msg_quoted

        req = urllib2.Request(URL)
        # send the request to Free Mobile
        try:
            urllib2.urlopen(req)
        except IOError as e:
            if hasattr(e, 'code'):
                if e.code == 400:
                    message = "Missing parameter(s)."
                    sickrage.srCore.srLogger.error(message)
                    return False, message
                if e.code == 402:
                    message = "Too much SMS sent in a short time."
                    sickrage.srCore.srLogger.error(message)
                    return False, message
                if e.code == 403:
                    message = "API service isn't enabled in your account or ID / API key is incorrect."
                    sickrage.srCore.srLogger.error(message)
                    return False, message
                if e.code == 500:
                    message = "Server error. Please retry in few moment."
                    sickrage.srCore.srLogger.error(message)
                    return False, message
        except Exception as e:
            message = "Error while sending SMS: {0}".format(e.message)
            sickrage.srCore.srLogger.error(message)
            return False, message

        message = "Free Mobile SMS successful."
        sickrage.srCore.srLogger.info(message)
        return True, message

    def _notify_snatch(self, ep_name, title=notifyStrings[NOTIFY_SNATCH]):
        if sickrage.srCore.srConfig.FREEMOBILE_NOTIFY_ONSNATCH:
            self._notifyFreeMobile(title, ep_name)

    def _notify_download(self, ep_name, title=notifyStrings[NOTIFY_DOWNLOAD]):
        if sickrage.srCore.srConfig.FREEMOBILE_NOTIFY_ONDOWNLOAD:
            self._notifyFreeMobile(title, ep_name)

    def _notify_subtitle_download(self, ep_name, lang, title=notifyStrings[NOTIFY_SUBTITLE_DOWNLOAD]):
        if sickrage.srCore.srConfig.FREEMOBILE_NOTIFY_ONSUBTITLEDOWNLOAD:
            self._notifyFreeMobile(title, ep_name + ": " + lang)

    def _notify_version_update(self, new_version="??"):
        if sickrage.srCore.srConfig.USE_FREEMOBILE:
            update_text = notifyStrings[NOTIFY_GIT_UPDATE_TEXT]
            title = notifyStrings[NOTIFY_GIT_UPDATE]
            self._notifyFreeMobile(title, update_text + new_version)

    def _notifyFreeMobile(self, title, message, id=None, apiKey=None, force=False):
        """
        Sends a SMS notification

        title: The title of the notification to send
        message: The message string to send
        id: Your Free Mobile customer ID
        apikey: Your Free Mobile API key
        force: Enforce sending, for instance for testing
        """

        if not sickrage.srCore.srConfig.USE_FREEMOBILE and not force:
            sickrage.srCore.srLogger.debug("Notification for Free Mobile not enabled, skipping this notification")
            return False, "Disabled"

        sickrage.srCore.srLogger.debug("Sending a SMS for " + message)

        return self._sendFreeMobileSMS(title, message, id, apiKey)
