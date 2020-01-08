#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2019, 2020 Kairo de Araujo
#
import pytest
from unittest import mock

from kodaksmarthome.api import KodakSmartHome
from kodaksmarthome.constants import HTTP_CODE
from tests.conftest import MockRequestsResponse
from tests.json_responses import (
    auth_response, devices_response, events_response
)


class TestKodakSmartHome:
    def test_unsupported_region(self):

        with pytest.raises(AttributeError):
            KodakSmartHome("fake_user", "fake_pass", region="BR")


@mock.patch("kodaksmarthome.api.KodakSmartHome._http_request")
def test__options(mock__http_request):

    mock__http_request.return_value = True
    test_ksh = KodakSmartHome("fake_user", "fake_pass")

    assert test_ksh._options()


@mock.patch("kodaksmarthome.api.KodakSmartHome._http_request")
def test__options_exception(mock__http_request):

    mock__http_request.side_effect = [ConnectionError]
    test_ksh = KodakSmartHome("fake_user", "fake_pass")

    with pytest.raises(ConnectionError):
        test_ksh._options()


@mock.patch("kodaksmarthome.api.KodakSmartHome._http_request")
def test__token(mock__http_request):

    mock__http_request.return_value = {
        "access_token": "access_token",
        "token_type": "token_type",
        "refresh_token": "refresh_token",
        "expires_in": "expires_in",
        "scope": "scope",
        "account_info": "account_info",
        "web_urls": "web_urls",
    }

    test_ksh = KodakSmartHome("fake_user", "fake_pass")

    assert test_ksh._token()
    assert test_ksh.token == "access_token"


@mock.patch("kodaksmarthome.api.KodakSmartHome._http_request")
def test__get_token_exception(mock__http_request):

    mock__http_request.side_effect = [ConnectionError]
    test_ksh = KodakSmartHome("fake_user", "fake_pass")

    with pytest.raises(ConnectionError):
        test_ksh._token()


@mock.patch("kodaksmarthome.api.requests")
@mock.patch("kodaksmarthome.api.KodakSmartHome._http_request")
def test__authentication(mock_requests, mock__http_request):
    mocked_response = MockRequestsResponse(devices_response, HTTP_CODE.OK)

    mock__http_request.return_value = auth_response
    mock_requests.Session.return_value = mock.MagicMock(
        get=mock.MagicMock(return_value=mocked_response)
    )

    test_ksh = KodakSmartHome("fake_user", "fake_pass")

    assert test_ksh._authentication()


@mock.patch("kodaksmarthome.api.KodakSmartHome._http_request")
def test__authentication_exception(mock__http_request):
    mock__http_request.side_effect = [ConnectionError]
    test_ksh = KodakSmartHome("fake_user", "fake_pass")

    with pytest.raises(ConnectionError):
        test_ksh._authentication()


@mock.patch("kodaksmarthome.api.KodakSmartHome._http_request")
def test__get_devices(mock__http_request):

    mock__http_request.return_value = devices_response
    test_ksh = KodakSmartHome("fake_user", "fake_pass")
    test_ksh.is_connected = True

    test_devices = test_ksh._get_devices()

    assert test_devices == devices_response["data"]


@mock.patch("kodaksmarthome.api.KodakSmartHome._http_request")
def test__get_devices_exception(mock__http_request):
    mock__http_request.side_effect = [ConnectionError]
    test_ksh = KodakSmartHome("fake_user", "fake_pass")
    test_ksh.is_connected = True

    with pytest.raises(ConnectionError):
        test_ksh._get_devices()


@mock.patch("kodaksmarthome.api.KodakSmartHome._http_request")
def test__get_events(mock__http_request):

    mock__http_request.return_value = events_response
    test_ksh = KodakSmartHome("fake_user", "fake_pass")
    test_ksh.devices = devices_response["data"]["devices"]
    test_ksh.is_connected = True
    test_events = test_ksh._get_events()

    expected_result = [
        {
            "device_id": devices_response["data"]["devices"][0]["device_id"],
            "events": events_response["data"]["events"]
        }
    ]

    assert test_events == expected_result


@mock.patch("kodaksmarthome.api.KodakSmartHome._http_request")
def test__get_events_none(mock__http_request):
    events_response_none = {
        "status": HTTP_CODE.OK,
        "msg": "Success",
        "total_pages": 0,
        "data": {
            'total_events': 0,
            'total_pages': 0,
            "events": [],
        }
    }

    mock__http_request.return_value = events_response_none

    test_ksh = KodakSmartHome("fake_user", "fake_pass")
    test_ksh.devices = devices_response["data"]["devices"]
    test_ksh.token = "abcdef0123456789"
    test_ksh.is_connected = True
    test_events = test_ksh._get_events()

    expected_result = [
        {
            "device_id": devices_response["data"]["devices"][0]["device_id"],
            "events": events_response_none["data"]["events"]
        }
    ]

    assert test_events == expected_result


@mock.patch("kodaksmarthome.api.KodakSmartHome._http_request")
def test__get_events_exception(mock__http_request):

    mock__http_request.side_effect = [ConnectionError]
    test_ksh = KodakSmartHome("fake_user", "fake_pass")
    test_ksh.devices = devices_response["data"]["devices"]
    test_ksh.token = "abcdef0123456789"

    with pytest.raises(ConnectionError):
        test_ksh._get_events()


@mock.patch("kodaksmarthome.api.KodakSmartHome._options")
@mock.patch("kodaksmarthome.api.KodakSmartHome._token")
@mock.patch("kodaksmarthome.api.KodakSmartHome._authentication")
@mock.patch("kodaksmarthome.api.KodakSmartHome._get_devices")
@mock.patch("kodaksmarthome.api.KodakSmartHome._get_events")
def test_connect(
    mock__options,
    mock__token,
    mock__authentication,
    mock__get_devices,
    mock__get_events
):
    mock__options.return_value = True
    mock__token.return_value = True
    mock__authentication.return_value = True
    mock__get_devices.return_value = True
    mock__get_events.return_value = True

    test_ksh = KodakSmartHome("fake_user", "fake_pass")

    assert test_ksh.connect() is None


@mock.patch("kodaksmarthome.api.requests")
def test_disconnect(mock_requests, requests_session_mock_ok):

    mock_requests.Session.return_value = requests_session_mock_ok
    test_ksh = KodakSmartHome("fake_user", "fake_pass")
    test_ksh.disconnect()

    assert test_ksh.is_connected is False


def test_list_devices():
    test_ksh = KodakSmartHome("fake_user", "fake_pass")
    test_ksh.is_connected = True
    test_ksh.devices = devices_response["data"]

    assert test_ksh.list_devices == devices_response["data"]


def test_list_devices_disconnected():
    test_ksh = KodakSmartHome("fake_user", "fake_pass")

    with pytest.raises(ConnectionError):
        test_ksh.list_devices()


def test_get_events():
    test_ksh = KodakSmartHome("fake_user", "fake_pass")
    test_ksh.is_connected = True
    test_ksh.devices = devices_response["data"]
    test_ksh.events = events_response["data"]["events"]

    assert test_ksh.get_events == events_response["data"]["events"]


def test_get_events_disconnected():
    test_ksh = KodakSmartHome("fake_user", "fake_pass")

    with pytest.raises(ConnectionError):
        test_ksh.get_events()


def test__filter_event_type():
    test_ksh = KodakSmartHome("fake_user", "fake_pass")
    test_ksh.is_connected = True
    test_ksh.events = [
        {
            "device_id": devices_response["data"]["devices"][0]["device_id"],
            "events": events_response["data"]["events"]
        }
    ]
    test_ksh.devices = devices_response["data"]["devices"]

    test_result = test_ksh._filter_event_type(device_id="FAKEDEVICEID")

    assert len(test_result) == 2


def test__filter_event_type_none():
    test_ksh = KodakSmartHome("fake_user", "fake_pass")
    test_ksh.is_connected = True
    test_ksh.events = [
        {
            "device_id": devices_response["data"]["devices"][0]["device_id"],
            "events": events_response["data"]["events"]
        }
    ]
    test_ksh.devices = devices_response["data"]["devices"]

    test_result = test_ksh._filter_event_type(device_id=None)

    assert len(test_result) == 2


def test__filter_event_type_disconnected():
    test_ksh = KodakSmartHome("fake_user", "fake_pass")
    test_ksh.is_connected = False

    with pytest.raises(ConnectionError):
        test_ksh._filter_event_type(device_id=None)


def test_get_motion_events():
    test_ksh = KodakSmartHome("fake_user", "fake_pass")
    test_ksh.is_connected = True
    test_ksh.events = [
        {
            "device_id": devices_response["data"]["devices"][0]["device_id"],
            "events": events_response["data"]["events"]
        }
    ]
    test_ksh.devices = devices_response["data"]["devices"]

    assert len(test_ksh.get_motion_events(device_id="FAKEDEVICEID")) == 2


def test_get_motion_events_invalid_device_id():
    test_ksh = KodakSmartHome("fake_user", "fake_pass")
    test_ksh.is_connected = True
    test_ksh.events = [
        {
            "device_id": devices_response["data"]["devices"][0]["device_id"],
            "events": events_response["data"]["events"]
        }
    ]
    test_ksh.devices = devices_response["data"]["devices"]

    assert len(test_ksh.get_motion_events(device_id="INVALID")) == 0


def test_get_motion_events_disconnected():
    test_ksh = KodakSmartHome("fake_user", "fake_pass")

    with pytest.raises(ConnectionError):
        test_ksh.get_motion_events()


def test_get_battery_events():
    test_ksh = KodakSmartHome("fake_user", "fake_pass")
    test_ksh.is_connected = True
    test_ksh.events = [
        {
            "device_id": devices_response["data"]["devices"][0]["device_id"],
            "events": events_response["data"]["events"]
        }
    ]
    test_ksh.devices = devices_response["data"]["devices"]

    assert len(test_ksh.get_battery_events(device_id="FAKEDEVICEID")) == 3


def test_get_battery_events_disconnected():
    test_ksh = KodakSmartHome("fake_user", "fake_pass")

    with pytest.raises(ConnectionError):
        test_ksh.get_battery_events()


def test_get_battery_events_invalid_device_id():
    test_ksh = KodakSmartHome("fake_user", "fake_pass")
    test_ksh.is_connected = True
    test_ksh.events = [
        {
            "device_id": devices_response["data"]["devices"][0]["device_id"],
            "events": events_response["data"]["events"]
        }
    ]
    test_ksh.devices = devices_response["data"]["devices"]

    assert len(test_ksh.get_battery_events(device_id="INVALID")) == 0


def test_get_sound_events():
    test_ksh = KodakSmartHome("fake_user", "fake_pass")
    test_ksh.is_connected = True
    test_ksh.events = [
        {
            "device_id": devices_response["data"]["devices"][0]["device_id"],
            "events": events_response["data"]["events"]
        }
    ]
    test_ksh.devices = devices_response["data"]["devices"]

    assert len(test_ksh.get_sound_events(device_id="FAKEDEVICEID")) == 1


def test_get_sound_events_disconnected():
    test_ksh = KodakSmartHome("fake_user", "fake_pass")

    with pytest.raises(ConnectionError):
        test_ksh.get_sound_events()


def test_get_sound_events_invalid_device_id():
    test_ksh = KodakSmartHome("fake_user", "fake_pass")
    test_ksh.is_connected = True
    test_ksh.events = [
        {
            "device_id": devices_response["data"]["devices"][0]["device_id"],
            "events": events_response["data"]["events"]
        }
    ]
    test_ksh.devices = devices_response["data"]["devices"]

    assert len(test_ksh.get_sound_events(device_id="INVALID")) == 0
