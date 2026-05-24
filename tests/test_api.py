# @generated [partially] Gemini: comments
import pytest
from pathlib import Path
from geochange.api.sentinel_client import SentinelClient


def test_authenticate_success(mocker):
    """
    Test that SentinelClient correctly parses the access token from a successful API response
    We mock 'requests.post' to prevent actual network calls
    """

    # 1. Create a fake response object that behaves like requests.Response
    mock_response = mocker.Mock()
    mock_response.json.return_value = {"access_token": "super_secret_fake_token_1337"}
    mock_response.raise_for_status.return_value = None  # No error

    # 2. Tell pytest to intercept ANY call to 'requests.post' and return our fake response
    mocker.patch("requests.post", return_value=mock_response)

    # 3. Run the actual code
    client = SentinelClient()
    client.authenticate()

    # 4. Verify the client saved the token correctly
    assert client.token == "super_secret_fake_token_1337"


def test_download_image_success(mocker, tmp_path):
    """
    Test that download_image correctly saves the binary content to a file
    """
    # 1. Fake the response for downloading an image
    mock_response = mocker.Mock()
    mock_response.status_code = 200
    mock_response.content = b"fake_image_bytes_from_space"

    mocker.patch("requests.post", return_value=mock_response)

    # 2. Setup the client and manually set a fake token so it doesn't try to authenticate
    client = SentinelClient()
    client.token = "fake_token_already_authenticated"

    # 3. Create a temporary path for the output file
    fake_output_path = tmp_path / "test_mask.png"

    # 4. Call the method
    client.download_image(
        coords=(50.08, 14.42),
        year=2020,
        output_path=fake_output_path,
        options={"image_type": "water_mask", "use_mosaic": False}
    )

    # 5. Verify the file was created and contains our fake bytes
    assert fake_output_path.exists()

    with open(fake_output_path, "rb") as f:
        saved_bytes = f.read()

    assert saved_bytes == b"fake_image_bytes_from_space"