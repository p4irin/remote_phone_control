"""SNOM Remote Phone Control"""

from typing import Literal
import requests
from remote_phone_control import ActionServer


class Snom(object):
    """Remote control a snom phone and handle its events"""

    event_wait_timeout = 15

    def __init__(
            self, snom_ip: str,
            action_server_ip: str,
            action_server_port: int,
            username:str,
            passwd:str,
            outgoing_uri:str,
            extension: str,
            **kwargs: dict
            ):
        
        self._ip = snom_ip
        self._credentials = (username, passwd)
        self._command_url = f'http://{snom_ip}/command.htm'
        self._setting_url = f'http://{snom_ip}/dummy.htm'
        self._advanced_update_url = f'http://{snom_ip}/advanced_update.htm'
        self._outgoing_uri = outgoing_uri
        self.extension = extension
        self._action_server_ip = action_server_ip
        self._action_server_port = action_server_port
        self._action_server = ActionServer(action_server_port)
        self._action_server.start()
        self._set_action_urls()

    def _set_action_urls(self) -> None:
        """Set Action URLs on a phone

        Point the Action URLs to the Action server provided by this
        Snom instance. Do this regardless of whether it's set or not
        """
        base_action_url_path = f'http://{self._action_server_ip}:{self._action_server_port}/event?'
        self.set_setting(
            'action_incoming_url',
            f'{base_action_url_path}ip=$phone_ip&event=incoming&local=$local&remote=$remote'
        )
        self.set_setting(
            'action_connected_url',
            f'{base_action_url_path}ip=$phone_ip&event=connected&local=$local&remote=$remote'
        )
        self.set_setting(
            'action_disconnected_url',
            f'{base_action_url_path}ip=$phone_ip&event=disconnected&local=$local&remote=$remote'
        )

    def callout(self, number: str) -> bool:
        request_params = {
            'number': number, 'outgoing_uri': self._outgoing_uri
        }
        return requests.get(
            self._command_url, params=request_params,
            auth=self._credentials,
            allow_redirects=False
        ).status_code == 302    # Snom behavior here is to redirect to index.htm

    def pickup(self) -> bool:
        request_params = {'key': 'ENTER'}
        return requests.get(
            self._command_url, params=request_params,
            auth=self._credentials
        ).status_code == 200

    def hangup(self) -> bool:
        """
        X-button is used to hangup a standing call or reject an incoming call.
        Hanging up a standing call triggers an 'On Disconnected' action-url.
        Rejecting an incoming call does NOT trigger an action-url!
        """
        request_params = {'key': 'CANCEL'}
        return requests.get(
            self._command_url, params=request_params,
            auth=self._credentials
        ).status_code == 200

    def hangup_onhook(self) -> bool:
        request_params = {'key': 'ONHOOK'}
        return requests.get(
            self._command_url, params=request_params,
            auth=self._credentials
        ).status_code == 200

    def hangup_all(self) -> bool:
        return requests.get(
            self._command_url + '?RELEASE_ALL_CALLS',
            auth = self._credentials
        ).status_code == 200

    def senddtmf(self, digits: str) -> bool:
        """
        Inband dtmf
        """

        request_params = {'key_dtmf': digits}
        return requests.get(
            self._command_url, params=request_params,
            auth=self._credentials
        ).status_code == 200

    def senddtmf_sipinfo(self, digits: str) -> bool:
        """
        Send dtmf using SIP-INFO, simply by pressing digits and *, #
        on the keypad.
        """

        time = 100 # in milliseconds
        pause = 100
        value = ''
        for digit in digits:
            value += '%s,%s,%s;' % (digit, time, pause)
        value = value[0:-1] # ditch last semicolon
            
        request_params = {'key': value}
        return requests.get(
            self._command_url, params=request_params,
            auth=self._credentials
        ).status_code == 200
    
    def expect(self, event: Literal['incoming', 'connect', 'disconnect'],
                 timeout: int = event_wait_timeout) -> bool:
        
        action_server = self._action_server.server
        
        if event == 'incoming':
            result = action_server.event_incoming_call.wait(timeout)
            action_server.event_incoming_call.clear()
        if event == 'connect':
            result = action_server.event_connect.wait(timeout)
            action_server.event_connect.clear()
        if event == 'disconnect':
            result = action_server.event_disconnect.wait(timeout)
            action_server.event_disconnect.clear()
        return result

    def clear_events(self) -> None:
        self._action_server.server.event_connect.clear()
        self._action_server.server.event_disconnect.clear()
        self._action_server.server.event_incoming_call.clear()

    def set_disable_speaker(self, value: Literal['on', 'off']) -> bool:
        """
        Turn this setting 'on' to disable your speaker.
        value: 'on' | 'off'
        """

        request_params = {'settings': 'save', 'disable_speaker': value}
        return requests.get(
            self._setting_url, params=request_params,
            auth=self._credentials
        ).status_code == 200

    def set_setting(self, setting: str, value: str) -> bool:
        """
        Generic set setting method

        setting: one of settings on the snom Settings page
                 reference: <http://snom_ip/settings.htm
        value: valid value for setting
                 reference: <http://wiki.snom.com/Category:Setting:V8>

        For this to work, setting must have write permission flag for
        user.
        """

        request_params = {
            'settings': 'save',
            setting: value,
            'store_settings': 'save' # permanently write to Snom's flash memeory
        }
        return requests.get(
            self._setting_url, params=request_params,
            auth=self._credentials
        ).status_code == 200

    def press_px(self, x: str) -> bool:
        """
        simulates pressing free programmable function keys
        """

        request_params = {'key': f'p{x}'}
        return requests.get(
            self._command_url, params=request_params,
            auth=self._credentials
        ).status_code == 200

    def transfer(self) -> bool:

        request_params = {'key': 'TRANSFER'}
        return requests.get(
            self._command_url, params=request_params,
            auth=self._credentials
        ).status_code == 200

    def reboot(self) -> bool:

        request_params = {'reboot': 'Reboot'}
        return requests.get(
            self._advanced_update_url, params = request_params,
            auth = self._credentials
        ).status_code == 200
    
    def stop(self) -> None:
        """
        Stop the Action Server
        """
        self._action_server.stop()
