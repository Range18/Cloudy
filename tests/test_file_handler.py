import pytest
from unittest.mock import MagicMock
from src.app.file_handler import FileHandler
from src.core.types.app_mode_enum import AppMode


class DummyEvent:
    def __init__(self, src_path, is_dir=False, dest_path=None):
        self.src_path = src_path
        self.is_directory = is_dir
        self.dest_path = dest_path


@pytest.fixture
def mock_cloud():
    return MagicMock()


@pytest.fixture
def handler_dev(mock_cloud):
    return FileHandler("/base", AppMode.DEV, mock_cloud)


@pytest.fixture
def handler_prod(mock_cloud):
    return FileHandler("/base", AppMode.PROD, mock_cloud)


def test_on_modified_file(handler_dev, mock_cloud, capsys):
    event = DummyEvent("/base/file.txt")
    handler_dev.on_modified(event)
    out = capsys.readouterr().out
    assert "Modified: /base/file.txt" in out
    mock_cloud.update.assert_called_once()


def test_on_modified_dir_ignored(handler_dev, mock_cloud):
    event = DummyEvent("/base/dir", is_dir=True)
    assert handler_dev.on_modified(event) is None
    mock_cloud.update.assert_not_called()


def test_on_modified_tempfile_ignored(handler_dev, mock_cloud):
    event = DummyEvent("/base/~temp.txt")
    assert handler_dev.on_modified(event) is None
    mock_cloud.update.assert_not_called()


def test_on_created_file(handler_dev, mock_cloud, capsys):
    event = DummyEvent("/base/newfile.txt")
    handler_dev.on_created(event)
    out = capsys.readouterr().out
    assert "Created: /base/newfile.txt" in out
    mock_cloud.create_file.assert_called_once()


def test_on_created_dir(handler_dev, mock_cloud):
    event = DummyEvent("/base/newdir", is_dir=True)
    handler_dev.on_created(event)
    mock_cloud.make_dir.assert_called_once()


def test_on_deleted(handler_dev, mock_cloud, capsys):
    event = DummyEvent("/base/oldfile.txt")
    handler_dev.on_deleted(event)
    out = capsys.readouterr().out
    assert "Deleted: /base/oldfile.txt" in out
    mock_cloud.remove_file_or_dir.assert_called_once()


def test_on_moved(handler_dev, mock_cloud, capsys):
    event = DummyEvent("/base/a.txt", dest_path="/base/b.txt")
    handler_dev.on_moved(event)
    out = capsys.readouterr().out
    assert "Moved: from /base/a.txt to /base/b.txt" in out
    mock_cloud.move.assert_called_once()


def test_ignored_tempfile_in_all_handlers(handler_prod, mock_cloud):
    for method in ["on_modified", "on_created", "on_deleted", "on_moved"]:
        mock_cloud.reset_mock()
        event = DummyEvent("/base/~temp", dest_path="/base/target")
        getattr(handler_prod, method)(event)
        assert not any(call[0] for call in mock_cloud.method_calls)
