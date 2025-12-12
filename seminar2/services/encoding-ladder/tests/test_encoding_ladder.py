import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from main import app

client = TestClient(app)

class TestEncodingLadder:
    @patch("main.os.path.getsize")
    @patch("main.os.path.exists")
    @patch("main.AV1.encode")
    def test_create_ladder_av1(self, mock_encode, mock_exists, mock_getsize):
        mock_exists.return_value = True
        mock_getsize.return_value = 1024 * 1024  # 1MB
        
        request_data = {
            "video_path": "test.mp4",
            "codec": "av1",
            "resolutions": ["480p", "720p"]
        }
        
        response = client.post("/process", json=request_data)
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert data["codec"] == "av1"
        assert len(data["ladder"]) == 2

    @patch("main.os.path.getsize")
    @patch("main.os.path.exists")
    @patch("main.VP9.encode")
    def test_create_ladder_vp9(self, mock_encode, mock_exists, mock_getsize):
        mock_exists.return_value = True
        mock_getsize.return_value = 1024 * 1024
        
        request_data = {
            "video_path": "test.mp4",
            "codec": "vp9",
            "resolutions": ["1080p"]
        }
        
        response = client.post("/process", json=request_data)
        assert response.status_code == 200
        data = response.json()
        assert data["codec"] == "vp9"
        assert len(data["ladder"]) == 1

    def test_invalid_codec(self):
        request_data = {
            "video_path": "test.mp4",
            "codec": "invalid",
            "resolutions": ["480p"]
        }
        
        response = client.post("/process", json=request_data)
        assert response.status_code == 400
        assert "Unsupported codec" in response.json()["detail"]

    def test_invalid_resolution(self):
        request_data = {
            "video_path": "test.mp4",
            "codec": "h265",
            "resolutions": ["4k"]
        }
        
        response = client.post("/process", json=request_data)
        assert response.status_code == 400
        assert "Unsupported resolution" in response.json()["detail"]

