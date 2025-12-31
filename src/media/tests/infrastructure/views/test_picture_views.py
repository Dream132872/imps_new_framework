"""Unit tests for picture views.

These tests focus on permission checks only.
Integration tests cover the full flow in test_picture_views_integration.py
"""

import pytest

from media.infrastructure.views import (
    CreatePictureView,
    DeletePictureView,
    UpdatePictureView,
)

pytestmark = [
    pytest.mark.django_db,
    pytest.mark.unit,
    pytest.mark.infrastructure,
]


class TestCreatePictureView:
    """Tests for CreatePictureView - permissions only."""

    def test_permission_required(self):
        """Test that view requires correct permissions."""
        view = CreatePictureView()
        assert "media_infrastructure.add_picture" in view.permission_required


class TestUpdatePictureView:
    """Tests for UpdatePictureView - permissions only."""

    def test_permission_required(self):
        """Test that view requires correct permissions."""
        view = UpdatePictureView()
        assert "media_infrastructure.change_picture" in view.permission_required


class TestDeletePictureView:
    """Tests for DeletePictureView - permissions only."""

    def test_permission_required(self):
        """Test that view requires correct permissions."""
        view = DeletePictureView()
        assert "media_infrastructure.delete_picture" in view.permission_required
