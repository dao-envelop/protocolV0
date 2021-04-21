import pytest


@pytest.fixture(scope="module")
def dai(accounts, TokenMock):
    dai = accounts[0].deploy(TokenMock,"DAI MOCK Token", "DAI")
    yield dai



@pytest.fixture(scope="module")
def wrapper(accounts, Wraped721):
    t = accounts[0].deploy(Wraped721)
    yield t    

@pytest.fixture(scope="module")
def niftsy20(accounts, Niftsy, wrapper):
    mkr = accounts[0].deploy(Niftsy, wrapper.address)
    wrapper.setProjectToken(mkr.address, {'from':accounts[0]})
    yield mkr


@pytest.fixture(scope="module")
def erc721mock(accounts, Token721Mock):
    """
    Simple NFT with URI
    """
    t = accounts[0].deploy(Token721Mock, "Simple NFT with URI", "XXX")
    #t.setURI(0, 'https://maxsiz.github.io/')
    yield t 



