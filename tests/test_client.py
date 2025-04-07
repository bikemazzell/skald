import pytest
import socket
import json
import sys
from unittest.mock import MagicMock, patch
from bin.client import send_command

class TestClient:
    @pytest.fixture
    def mock_socket(self, mocker):
        # Create a context manager mock that returns itself
        mock_sock = mocker.MagicMock()
        mock_sock.__enter__.return_value = mock_sock
        mock_sock.recv.return_value = json.dumps({"status": "OK"}).encode()

        # Patch socket.socket to return our mock
        mocker.patch('socket.socket', return_value=mock_sock)

        return mock_sock

    @patch('sys.exit')
    def test_send_command_success(self, mock_exit, mock_socket):
        mock_socket.recv.return_value = json.dumps({"status": "OK"}).encode()

        send_command("start")

        mock_socket.connect.assert_called_once()
        mock_socket.send.assert_called_once()
        mock_exit.assert_not_called()

    @patch('sys.exit')
    def test_send_command_timeout(self, mock_exit, mock_socket):
        mock_socket.connect.side_effect = socket.timeout

        send_command("start")

        mock_exit.assert_called_once()

    @patch('sys.exit')
    def test_send_command_invalid_response(self, mock_exit, mock_socket):
        mock_socket.recv.return_value = b"invalid json"

        send_command("start")

        mock_exit.assert_called_once()