import io
import os
from unittest.mock import patch

from workflows.meeting_notes_generator_workflow.nodes.extract_text_node import (
    extract_text_node as extract_meeting_text,
)
from workflows.resume_analyzer_workflow.nodes.extract_text_node import (
    extract_text_node as extract_resume_text,
)
from workflows.utils.storage import temporary_storage_file


class _FakeStorage:
    def __init__(self, data):
        self._data = data

    def exists(self, key):
        return key in self._data

    def open(self, key, mode="rb"):
        return io.BytesIO(self._data[key])


def test_temporary_storage_file_stages_and_cleans_up(monkeypatch):
    fake_storage = _FakeStorage({"uploads/sample.txt": b"hello world"})
    monkeypatch.setattr("workflows.utils.storage.default_storage", fake_storage)

    with temporary_storage_file("uploads/sample.txt") as temp_path:
        assert os.path.exists(temp_path)
        with open(temp_path, "rb") as file:
            assert file.read() == b"hello world"

    assert not os.path.exists(temp_path)


@patch(
    "workflows.resume_analyzer_workflow.nodes.extract_text_node.default_storage.exists",
    return_value=True,
)
@patch("workflows.resume_analyzer_workflow.nodes.extract_text_node.load_documents")
def test_resume_extract_text_uses_storage_key(mock_load_documents, mock_exists):
    mock_load_documents.return_value = [{"content": "resume text"}]

    state = {"file_path": "resume_uploads/resume.pdf"}

    result = extract_resume_text(state)

    assert result["raw_text"] == "resume text"
    assert result["extraction_error"] is None
    mock_exists.assert_called_once_with("resume_uploads/resume.pdf")
    mock_load_documents.assert_called_once_with(["resume_uploads/resume.pdf"])


@patch(
    "workflows.meeting_notes_generator_workflow.nodes.extract_text_node.default_storage.exists",
    return_value=True,
)
@patch(
    "workflows.meeting_notes_generator_workflow.nodes.extract_text_node.default_storage.open"
)
def test_meeting_extract_text_reads_vtt_from_storage(mock_open, mock_exists):
    mock_open.return_value = io.BytesIO(
        b"WEBVTT\n\n1\n00:00:01.000 --> 00:00:02.000\nHello world\n"
    )

    state = {"file_path": "meeting_notes_uploads/meeting.vtt"}

    result = extract_meeting_text(state)

    assert result["raw_transcript"] == "Hello world"
    assert result["extraction_error"] is None
    mock_exists.assert_called_once_with("meeting_notes_uploads/meeting.vtt")
    mock_open.assert_called_once_with("meeting_notes_uploads/meeting.vtt", "rb")
