from scripts import _01_fetch_logo as fetch_logo


def test_locate_logo_url_picks_header_img():
    html = '''
    <html><head><title>X</title></head>
    <body>
      <header><img src="/wp-content/uploads/logo.png" alt="Deccan Fine Chemicals"></header>
    </body></html>
    '''
    url = fetch_logo.find_logo_url(html, base_url="https://deccanchemicals.com")
    assert url == "https://deccanchemicals.com/wp-content/uploads/logo.png"


def test_locate_logo_url_falls_back_to_alt_text():
    html = '''
    <html><body>
      <div><img src="https://cdn.example.com/site/dc-logo.png" alt="Deccan Fine Chemicals Logo"></div>
    </body></html>
    '''
    url = fetch_logo.find_logo_url(html, base_url="https://deccanchemicals.com")
    assert url == "https://cdn.example.com/site/dc-logo.png"


def test_locate_logo_url_falls_back_to_logo_in_class():
    html = '''
    <html><body>
      <img class="site-logo brand" src="/assets/logo.svg" alt="">
    </body></html>
    '''
    url = fetch_logo.find_logo_url(html, base_url="https://deccanchemicals.com")
    assert url == "https://deccanchemicals.com/assets/logo.svg"


def test_locate_logo_url_returns_none_when_no_logo():
    html = "<html><body><p>no images</p></body></html>"
    url = fetch_logo.find_logo_url(html, base_url="https://deccanchemicals.com")
    assert url is None
