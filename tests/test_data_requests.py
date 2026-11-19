"""
Data requests (RQ1) are optional, for SoundFont mode where no JD-Xi answers.
Switched off, they are left out of what is sent; parameter changes still go
out, and an explicit Read still asks. Until chosen, the setting follows the
mode: off with Use SoundFont List, on with the JD-Xi lists.

QSettings is replaced by a dict, so the user's own settings are not touched.
"""

from unittest.mock import MagicMock, patch

import pytest

import jdxi_editor.midi.io.data_requests as data_requests
import jdxi_editor.midi.io.delay as delay

RQ1 = "F0 41 10 00 00 00 0E 11 19 42 00 00 00 00 00 40 65 F7"
RQ1_B = bytes.fromhex("F0 41 10 00 00 00 0E 11 18 00 00 00 00 00 00 40 28 F7")
DT1 = bytes.fromhex("F0 41 10 00 00 00 0E 12 19 42 00 00 01 02 22 F7")


class _Settings:
    store: dict = {}

    def __init__(self, *_args):
        pass

    def value(self, key, default=None):
        return self.store.get(key, default)

    def setValue(self, key, value):
        self.store[key] = value

    def sync(self):
        pass


@pytest.fixture
def settings():
    _Settings.store = {}
    with patch.object(data_requests, "QSettings", _Settings):
        yield _Settings.store


@pytest.fixture
def soundfont_mode():
    state = {"on": False}
    with patch(
        "jdxi_editor.ui.editors.pattern.preset_list_provider.get_use_soundfont_list",
        lambda: state["on"],
    ):
        yield state


def test_requests_are_recognised_in_hex_and_bytes():
    assert data_requests.is_data_request(RQ1)
    assert data_requests.is_data_request(RQ1_B)
    assert not data_requests.is_data_request(DT1)
    assert not data_requests.is_data_request([0xC0, 0x05])
    assert not data_requests.is_data_request("not hex")
    assert data_requests.without_data_requests([RQ1, DT1, RQ1_B, ""]) == [DT1]


def test_until_chosen_requests_follow_the_mode(settings, soundfont_mode):
    assert data_requests.stored_data_requests_setting() is None
    assert data_requests.data_requests_enabled()
    soundfont_mode["on"] = True
    assert not data_requests.data_requests_enabled()


def test_a_saved_choice_wins_over_the_mode(settings, soundfont_mode):
    soundfont_mode["on"] = True
    data_requests.set_data_requests_enabled(True)
    assert data_requests.data_requests_enabled()
    soundfont_mode["on"] = False
    data_requests.set_data_requests_enabled(False)
    assert not data_requests.data_requests_enabled()
    settings[data_requests.DATA_REQUESTS_KEY] = "false"  # as QSettings may store it
    assert not data_requests.data_requests_enabled()


@pytest.fixture
def device():
    dev = MagicMock()
    with patch.object(delay, "device_for", return_value=dev):
        yield dev


def test_with_requests_on_everything_is_queued(device):
    with patch.object(delay, "data_requests_enabled", return_value=True):
        delay.send_with_delay(object(), [RQ1, DT1])
    device.request.assert_called_once_with([RQ1, DT1])


def test_with_requests_off_only_the_requests_are_left_out(device):
    with patch.object(delay, "data_requests_enabled", return_value=False):
        delay.send_with_delay(object(), [RQ1, DT1, RQ1_B])
    device.request.assert_called_once_with([DT1])


def test_with_requests_off_a_list_of_requests_sends_nothing(device):
    with patch.object(delay, "data_requests_enabled", return_value=False):
        delay.send_with_delay(object(), [RQ1, RQ1_B])
    device.request.assert_not_called()


def test_an_explicit_read_is_sent_even_with_requests_off(device):
    with patch.object(delay, "data_requests_enabled", return_value=False):
        delay.send_with_delay(object(), [RQ1], force=True)
    device.request.assert_called_once_with([RQ1])
