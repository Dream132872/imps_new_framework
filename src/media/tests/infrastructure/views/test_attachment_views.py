"""Unit tests for attachment views.

These tests focus on permission checks only.
Integration tests cover the full flow in test_attachment_views_integration.py
"""

import pytest

from media.infrastructure.views import (
    CreateAttachmentView,
    DeleteAttachmentView,
    UpdateAttachmentView,
)

pytestmark = [
    pytest.mark.infrastructure,
    pytest.mark.unit,
]


class TestCreateAttachmentView:
    """Tests for CreateAttachmentView - permissions only."""

    def test_permission_required(self):
        """Test that view requires correct permissions."""
        view = CreateAttachmentView()
        assert "media_infrastructure.add_attachment" in view.permission_required


class TestUpdateAttachmentView:
    """Tests for UpdateAttachmentView - permissions only."""

    def test_permission_required(self):
        """Test that view requires correct permissions."""
        view = UpdateAttachmentView()
        assert "media_infrastructure.change_attachment" in view.permission_required


class TestDeleteAttachmentView:
    """Tests for DeleteAttachmentView - permissions only."""

    def test_permission_required(self):
        """Test that view requires correct permissions."""
        view = DeleteAttachmentView()
        assert "media_infrastructure.delete_attachment" in view.permission_required
