import pytest
from src.reality.social.pinterest.browser import PinterestBrowserProvider

def test_mock_pin_deletion(mock_pin_page_path):
    """
    Testa se o Playwright consegue interagir e excluir o Pin na página mockada offline (Sprint P3 - Passo 3.2).
    """
    provider = PinterestBrowserProvider()
    
    # Passa o URI do arquivo local como content_id
    mock_url = mock_pin_page_path.resolve().as_uri()
    
    deleted = provider.archive_content(mock_url)
    
    assert deleted is True
