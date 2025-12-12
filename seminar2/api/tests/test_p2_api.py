import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, mock_open, MagicMock, AsyncMock
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from p2_api import app

client = TestClient(app)

@pytest.fixture
def mock_file():
    return MagicMock(filename="test.mp4", file=MagicMock())

@pytest.fixture
def mock_uuid():
    with patch("p2_api.uuid.uuid4", return_value=MagicMock(hex="test-uuid")):
        yield

class TestHealth:
    def test_health_endpoint(self):
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json() == {"status": "ok"}

class TestConvertVideo:
    @patch("p2_api.os.path.exists")
    @patch("p2_api.httpx.AsyncClient")
    @patch("p2_api.shutil.copyfileobj")
    @patch("p2_api.os.makedirs")
    @patch("builtins.open", new_callable=mock_open)
    @patch("p2_api.os.remove")
    def test_convert_video_success(self, mock_remove, mock_file_open, mock_makedirs, mock_copy, mock_client, mock_exists, mock_uuid):
        mock_exists.return_value = True
        mock_response = MagicMock()
        mock_response.json = AsyncMock(return_value={"output_path": "converted_test.mp4"})
        mock_response.raise_for_status = MagicMock()
        
        mock_http_client = AsyncMock()
        mock_http_client.post = AsyncMock(return_value=mock_response)
        mock_client_instance = MagicMock()
        mock_client_instance.__aenter__ = AsyncMock(return_value=mock_http_client)
        mock_client_instance.__aexit__ = AsyncMock(return_value=None)
        mock_client.return_value = mock_client_instance
        
        files = {"file": ("test.mp4", b"fake video content", "video/mp4")}
        response = client.post("/api/video/convert/h265", files=files)
        
        assert response.status_code == 200

    def test_convert_video_invalid_codec(self):
        files = {"file": ("test.mp4", b"fake video content", "video/mp4")}
        response = client.post("/api/video/convert/invalid", files=files)
        assert response.status_code == 400
        assert "Unsupported codec" in response.json()["detail"]

class TestEncodingLadder:
    @patch("p2_api.os.path.exists")
    @patch("p2_api.httpx.AsyncClient")
    @patch("p2_api.shutil.copyfileobj")
    @patch("p2_api.os.makedirs")
    @patch("builtins.open", new_callable=mock_open)
    @patch("p2_api.os.remove")
    def test_encoding_ladder_success(self, mock_remove, mock_file_open, mock_makedirs, mock_copy, mock_client, mock_exists, mock_uuid):
        mock_response = MagicMock()
        mock_response.json = AsyncMock(return_value={"status": "success", "ladder": []})
        mock_response.raise_for_status = MagicMock()
        
        mock_http_client = AsyncMock()
        mock_http_client.post = AsyncMock(return_value=mock_response)
        mock_client_instance = MagicMock()
        mock_client_instance.__aenter__ = AsyncMock(return_value=mock_http_client)
        mock_client_instance.__aexit__ = AsyncMock(return_value=None)
        mock_client.return_value = mock_client_instance
        
        files = {"file": ("test.mp4", b"fake video content", "video/mp4")}
        data = {"codec": "vp9", "resolutions": "480p,720p"}
        response = client.post("/api/video/encoding-ladder", files=files, data=data)
        
        assert response.status_code == 200

    def test_encoding_ladder_invalid_codec(self):
        files = {"file": ("test.mp4", b"fake video content", "video/mp4")}
        data = {"codec": "invalid", "resolutions": "480p"}
        response = client.post("/api/video/encoding-ladder", files=files, data=data)
        assert response.status_code == 400
        assert "Unsupported codec" in response.json()["detail"]

