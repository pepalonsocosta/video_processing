import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from main import app

client = TestClient(app)

class TestConverter:
    @patch("main.H265.encode")
    @patch("main.os.path.exists")
    def test_convert_h265(self, mock_exists, mock_encode):
        mock_exists.return_value = True
        request_data = {"video_path": "test.mp4"}
        
        response = client.post("/process/h265", json=request_data)
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert "output_path" in data

    @patch("main.VP8.encode")
    @patch("main.os.path.exists")
    def test_convert_vp8_webm_extension(self, mock_exists, mock_encode):
        mock_exists.return_value = True
        request_data = {"video_path": "test.mp4"}
        
        response = client.post("/process/vp8", json=request_data)
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert data["output_path"].endswith(".webm")

    @patch("main.AV1.encode")
    @patch("main.os.path.exists")
    def test_convert_av1(self, mock_exists, mock_encode):
        mock_exists.return_value = True
        request_data = {"video_path": "test.mp4"}
        
        response = client.post("/process/av1", json=request_data)
        assert response.status_code == 200

    def test_invalid_codec(self):
        request_data = {"video_path": "test.mp4"}
        response = client.post("/process/invalid", json=request_data)
        assert response.status_code == 400
        assert "Unsupported codec" in response.json()["detail"]

