from unittest.mock import MagicMock
from fastapi.security import HTTPAuthorizationCredentials
from src.frame_finder.data.classes.supabase_auth_provider import SupabaseAuthProvider
import pytest


class MockAuthError(Exception):
    def __init__(self, code: str):
        self.code = code


@pytest.fixture
def mock_client():
    return MagicMock()


@pytest.fixture
def provider(mock_client):
    return SupabaseAuthProvider(mock_client)


def test_sign_in_returns_auth_result(
    provider,
    mock_client,
):
    response = MagicMock()

    response.user.id = "user-123"
    response.user.email = "alice@example.com"

    response.session.access_token = "access-token"
    response.session.refresh_token = "refresh-token"

    mock_client.auth.sign_in_with_password.return_value = response

    result = provider.sign_in(
        email="alice@example.com",
        password="password123",
    )

    assert result.success is True
    assert result.user_id == "user-123"
    assert result.email == "alice@example.com"
    assert result.access_token == "access-token"
    assert result.refresh_token == "refresh-token"

    mock_client.auth.sign_in_with_password.assert_called_once_with(
        {
            "email": "alice@example.com",
            "password": "password123",
        }
    )


@pytest.mark.parametrize(
    ("error_code", "expected_message"),
    [
        (
            "invalid_credentials",
            "Invalid email or password.",
        ),
        (
            "email_not_confirmed",
            (
                "Please confirm your email address "
                "before signing in."
            ),
        ),
    ],
)
def test_sign_in_returns_known_error(
    provider,
    mock_client,
    error_code,
    expected_message,
):
    mock_client.auth.sign_in_with_password.side_effect = (
        MockAuthError(error_code)
    )

    result = provider.sign_in(
        email="alice@example.com",
        password="password123",
    )

    assert result.success is False
    assert result.error_code == error_code
    assert result.error_message == expected_message


def test_sign_in_returns_default_error_for_unknown_error(
    provider,
    mock_client,
):
    mock_client.auth.sign_in_with_password.side_effect = (
        MockAuthError("something_unknown")
    )

    result = provider.sign_in(
        email="alice@example.com",
        password="password123",
    )

    assert result.success is False
    assert result.error_code == "something_unknown"
    assert result.error_message == (
        "Something went wrong. Please try again."
    )


def test_sign_up_returns_auth_result(
    provider,
    mock_client,
):
    response = MagicMock()

    response.user.id = "user-123"
    response.user.email = "alice@example.com"

    mock_client.auth.sign_up.return_value = response

    result = provider.sign_up(
        email="alice@example.com",
        password="password123",
    )

    assert result.success is True
    assert result.user_id == "user-123"
    assert result.email == "alice@example.com"

    mock_client.auth.sign_up.assert_called_once_with(
        {
            "email": "alice@example.com",
            "password": "password123",
        }
    )


@pytest.mark.parametrize(
    ("error_code", "expected_message"),
    [
        (
            "user_already_exists",
            "An account with this email already exists.",
        ),
        (
            "weak_password",
            "Password should be at least 6 characters",
        ),
    ],
)
def test_sign_up_returns_known_error(
    provider,
    mock_client,
    error_code,
    expected_message,
):
    mock_client.auth.sign_up.side_effect = (
        MockAuthError(error_code)
    )

    result = provider.sign_up(
        email="alice@example.com",
        password="password123",
    )

    assert result.success is False
    assert result.error_code == error_code
    assert result.error_message == expected_message


def test_sign_up_returns_default_error_for_unknown_error(
    provider,
    mock_client,
):
    mock_client.auth.sign_up.side_effect = (
        MockAuthError("something_unknown")
    )

    result = provider.sign_up(
        email="alice@example.com",
        password="password123",
    )

    assert result.success is False
    assert result.error_code == "something_unknown"
    assert result.error_message == (
        "Something went wrong. Please try again."
    )


def test_get_current_user_returns_user(
    provider,
    mock_client,
):
    response = MagicMock()

    response.user.id = "user-123"
    response.user.email = "alice@example.com"

    mock_client.auth.get_user.return_value = response

    credentials = HTTPAuthorizationCredentials(
        scheme="Bearer",
        credentials="access-token",
    )

    user = provider.get_current_user(credentials)

    assert user.id == "user-123"
    assert user.email == "alice@example.com"

    mock_client.auth.get_user.assert_called_once_with(
        "access-token"
    )

def test_refresh_returns_new_tokens(
    provider,
    mock_client,
):
    response = MagicMock()

    response.session.access_token = "new-access-token"
    response.session.refresh_token = "new-refresh-token"
    response.user.email = "alice@example.com"

    mock_client.auth.refresh_session.return_value = response

    result = provider.refresh("old-refresh-token")

    assert result.access_token == "new-access-token"
    assert result.refresh_token == "new-refresh-token"
    assert result.email == "alice@example.com"

    mock_client.auth.refresh_session.assert_called_once_with(
        "old-refresh-token"
    )

def test_sign_in_returns_default_error_for_exception_without_code(
    provider,
    mock_client,
):
    mock_client.auth.sign_in_with_password.side_effect = (
        Exception("Network error")
    )

    result = provider.sign_in(
        email="alice@example.com",
        password="password123",
    )

    assert result.success is False
    assert result.error_code is None
    assert result.error_message == (
        "Something went wrong. Please try again."
    )