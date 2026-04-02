import pytest
from unittest.mock import MagicMock, patch
from app.extractor import extract_text_from_pdf, extract_inventor_name, process_document

def test_extract_inventor_name():
    text = "Some random text.\nInventor: Dr. Priya Sharma\nMore text."
    assert extract_inventor_name(text) == "Dr. Priya Sharma"
    
    text_with_spaces = "INVENTOR : John Doe\nAddress: 123 Street"
    assert extract_inventor_name(text_with_spaces) == "John Doe"
    
    no_inventor = "This document does not list an author."
    assert extract_inventor_name(no_inventor) is None
    
    empty_text = ""
    assert extract_inventor_name(empty_text) is None

@patch("pdfplumber.open")
def test_extract_text_from_pdf_success(mock_open):
    # Mocking the PDF structure
    mock_pdf = MagicMock()
    mock_page = MagicMock()
    mock_page.extract_text.return_value = "Extracted text content."
    mock_pdf.pages = [mock_page]
    mock_open.return_value.__enter__.return_value = mock_pdf
    
    result = extract_text_from_pdf("fake.pdf")
    assert result == "Extracted text content."
    mock_open.assert_called_once_with("fake.pdf")

@patch("pdfplumber.open")
def test_extract_text_from_pdf_failure(mock_open):
    mock_open.side_effect = Exception("File not found")
    
    # Should not raise exception because of try-except block
    result = extract_text_from_pdf("missing.pdf")
    assert result == ""

@patch("app.extractor.extract_text_from_pdf")
def test_process_document(mock_extract):
    mock_extract.return_value = "Inventor: Dr. Priya Sharma\nDescription: Solar purifier."
    
    result = process_document("fake.pdf")
    
    assert isinstance(result, dict)
    assert result["inventor_name"] == "Dr. Priya Sharma"
    assert "extracted_text_preview" in result
    assert result["extracted_text_preview"].startswith("Inventor: Dr. Priya Sharma")
