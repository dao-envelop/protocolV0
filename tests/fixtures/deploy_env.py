import pytest
from brownie import chain

############ Mocks ########################
@pytest.fixture(scope="module")
def dai(accounts, TokenMock):
    dai = accounts[0].deploy(TokenMock,"DAI MOCK Token", "DAI")
    yield dai

@pytest.fixture(scope="module")
def weth(accounts, TokenMock):
    weth = accounts[0].deploy(TokenMock,"WETH MOCK Token", "WETH")
    yield weth

@pytest.fixture(scope="module")
def pft(accounts, TokenMock):
    pft = accounts[0].deploy(TokenMock,"PF MOCK Token", "PFT")
    yield pft

@pytest.fixture(scope="module")
def erc721mock(accounts, Token721Mock):
    """
    Simple NFT with URI
    """
    t = accounts[0].deploy(Token721Mock, "Simple NFT with URI", "XXX")
    #t.setURI(0, 'https://maxsiz.github.io/')
    yield t    

@pytest.fixture(scope="module")
def fakeERC721mock(accounts, Token721Mock):
    """
    Simple NFT with URI
    """
    b = accounts[0].deploy(Token721Mock, "Fake NFT with URI", "FXX")
    #t.setURI(0, 'https://maxsiz.github.io/')
    yield b
############################################


@pytest.fixture(scope="module")
def niftsy20(accounts, Niftsy):
    erc20 = accounts[0].deploy(Niftsy, accounts[0])
    yield erc20 

@pytest.fixture(scope="module")
def techERC20(accounts, TechToken):
    erc20 = accounts[0].deploy(TechToken)
    yield erc20     

@pytest.fixture(scope="module")
def wrapper(accounts, WrapperWithERC20Collateral, techERC20, dai, weth):
    t = accounts[0].deploy(WrapperWithERC20Collateral, techERC20.address)
    #niftsy20.addMinter(t.address, {'from':accounts[0]})
    t.setCollateralStatus(dai.address, True)
    t.setCollateralStatus(weth.address, True)
    techERC20.addMinter(t.address, {'from': accounts[0]})
    yield t 

@pytest.fixture(scope="module")
def trmodel(accounts, TransferRoyaltyModel01, wrapper, niftsy20):
    t = accounts[0].deploy(TransferRoyaltyModel01, wrapper.address)
    wrapper.editPartnersItem(niftsy20.address, True, t.address, False,{'from': accounts[0]})
    yield t 



@pytest.fixture(scope="module")
def mockHacker(accounts, MaliciousTokenMock):
    h = accounts[0].deploy(MaliciousTokenMock,"Hacker Malicious Token", "KLR")
    yield h

@pytest.fixture(scope="module")
def distributor(accounts, WrapperDistributor721, techERC20):
    t = accounts[0].deploy(WrapperDistributor721, techERC20.address)
    #niftsy20.addMinter(t.address, {'from':accounts[0]})
    techERC20.addMinter(t.address, {'from': accounts[0]})
    yield t  

@pytest.fixture(scope="module")
def ERC721Distr(accounts, ERC721Distribution, distributor):
    """
    Simple NFT with URI
    """
    b = accounts[0].deploy(ERC721Distribution, "Envelop Distribution NFT", "dNIFTSY")
    b.setMinterStatus(distributor.address, True, {"from": accounts[0]})
    #t.setURI(0, 'https://maxsiz.github.io/')
    yield b

@pytest.fixture(scope="module")
def launcpad(accounts, distributor, LaunchpadWNFT, niftsy20):
    l = accounts[0].deploy(LaunchpadWNFT, distributor.address, niftsy20.address, 0)
    yield l


@pytest.fixture(scope="module")
def farming(accounts, WrapperFarming, techERC20, niftsy20):
    t = accounts[0].deploy(
        WrapperFarming, 
        techERC20.address,
        niftsy20 
    )
    #niftsy20.addMinter(t.address, {'from':accounts[0]})
    techERC20.addMinter(t.address, {'from': accounts[0]})
    t.addRewardSettingsSlot(niftsy20, 100, 1000, {'from': accounts[0]})
    t.addRewardSettingsSlot(niftsy20, 200, 2000, {'from': accounts[0]})
    t.addRewardSettingsSlot(niftsy20, 300, 3000, {'from': accounts[0]})
    t.addRewardSettingsSlot(niftsy20, 400, 4000, {'from': accounts[0]})
    yield t  


