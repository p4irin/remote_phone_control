import unittest
import time
import os
from dotenv import load_dotenv
from remote_phone_control.snom import Snom


load_dotenv()


class SnomTests(unittest.TestCase):
    """Basic call flows with SNOMs"""

    class _TestData:

        class SnomA:
            ip_address = os.getenv('SNOM_A__IP_ADDRESS')
            action_server_ip_address = os.getenv(
                'SNOM_A__ACTION_SERVER_IP_ADDRESS'
            )
            action_server_port = int(
                os.getenv('SNOM_A__ACTION_SERVER_PORT')
            )
            username = os.getenv('SNOM_A__USERNAME')
            password = os.getenv('SNOM_A__PASSWORD')
            outgoing_uri = os.getenv('SNOM_A__OUTGOING_URI')
            extension = os.getenv('SNOM_A__EXTENSION')

        class SnomB:
            ip_address = os.getenv('SNOM_B__IP_ADDRESS')
            action_server_ip_address = os.getenv(
                'SNOM_B__ACTION_SERVER_IP_ADDRESS'
            )
            action_server_port = int(
                os.getenv('SNOM_B__ACTION_SERVER_PORT')
            )
            username = os.getenv('SNOM_B__USERNAME')
            password = os.getenv('SNOM_B__PASSWORD')
            outgoing_uri = os.getenv('SNOM_B__OUTGOING_URI')
            extension = os.getenv('SNOM_B__EXTENSION')

        pstn_number_to_call = os.getenv('PSTN_NUMBER_TO_CALL')

    @classmethod
    def setUpClass(cls) -> None:

        cls.snom_a = Snom(
            cls._TestData.SnomA.ip_address,
            cls._TestData.SnomA.action_server_ip_address,
            cls._TestData.SnomA.action_server_port,
            cls._TestData.SnomA.username,
            cls._TestData.SnomA.password,
            cls._TestData.SnomA.outgoing_uri,
            cls._TestData.SnomA.extension
        )

        cls.snom_b = Snom(
            cls._TestData.SnomB.ip_address,
            cls._TestData.SnomB.action_server_ip_address,
            cls._TestData.SnomB.action_server_port,
            cls._TestData.SnomB.username,
            cls._TestData.SnomB.password,
            cls._TestData.SnomB.outgoing_uri,
            cls._TestData.SnomB.extension
        )

        disable_speakers = os.getenv('DISABLE_SPEAKERS')
        cls.snom_a.set_disable_speaker(disable_speakers)
        cls.snom_b.set_disable_speaker(disable_speakers)

    def setUp(self) -> None:
        pass

    def tearDown(self) -> None:
        pass

    @classmethod
    def tearDownClass(cls) -> None:

        cls.snom_a.stop()
        cls.snom_b.stop()

    @staticmethod
    def call_duration(duration: int) -> None:

        time.sleep(duration)

    def test_001__call_a_pstn_number(self):
        """Call a PSTN number, callee answers, we end the call
        
        For this test, make sure the callee has auto answer enabled
        """
        self.assertTrue(
            self.snom_a.callout(self._TestData.pstn_number_to_call)
        )
        self.assertTrue(self.snom_a.expect('connect'))
        self.call_duration(5)
        self.assertTrue(self.snom_a.hangup())
        self.assertTrue(self.snom_a.expect('disconnect'))

    def test_002__a_calls_b_b_ends_the_call(self):
        """A calls B, B answers, call is established, B ends the call"""

        self.snom_a.callout(self.snom_b.extension)
        self.assertTrue(self.snom_b.expect('incoming'))
        self.snom_b.pickup()
        self.assertTrue(self.snom_b.expect('connect'))
        self.call_duration(5)
        self.snom_b.hangup()
        self.assertTrue(self.snom_b.expect('disconnect'))

    def test_003__a_calls_b_b_rejects_the_call(self):
        """A calls B, B rejects the call"""
    
        self.snom_a.callout(self.snom_b.extension)
        self.assertTrue(self.snom_b.expect('incoming'))
        # Reject incoming call
        self.snom_b.hangup()
        self.assertTrue(self.snom_a.expect('disconnect'))
