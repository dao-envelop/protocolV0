export WEB3_INFURA_PROJECT_ID=79f3c18a7d394279b3bc877fa2610caf
export ETHERSCAN_TOKEN=K7HHHZ89N7Y1D13ICA1AA9HGHDYVVNSZ55
export MYTHX_API_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJqdGkiOiJmMjQxNTkxMC0xMTEzLTRiZjEtYjk2Mi05MGQwNWNmYWU4ZDkiLCJpYXQiOjE2MTU5NTQ0MDQuOTU2LCJpc3MiOiJNeXRoWCBBUEkiLCJleHAiOjE5MzE1MzA0MDQuOTQ2LCJ1c2VySWQiOiI2MDUxODE2ZmZhZmU2OTAwMTk3ZDUxZDUifQ.jNc0955ilHga4aWH0HM9mcFgLXnvO8DIeNWYN1qytXg

```python
accounts.add('2cdbeadae3122f6b30a67733fd4f0fb6c27ccd85c3c68de97c8ff534c87603c8')
accounts.add('3c2c9898bd1df57f9fc16a547cf0ffc4014006b863e0b2a8be0cb63e74542b9c')



niftsyERC20=TokenMock.deploy('NIFTSY ERC20 Token','NIFTSY', {'from':accounts[0]}, publish_source=True)
erc721=Token721Mock.deploy('Simple NFT with URI','ZZZ',{'from':accounts[0]}, publish_source=True)
erc721.setURI(0, 'https://maxsiz.github.io/', {'from': accounts[0]})
wrapper = Wraped721.deploy(niftsyERC20, {'from': accounts[0]}, publish_source=True)

wrapper = Wraped721.at('0xf90223Ba129Ba829a4A08979920de1452938aCA1') 
niftsyERC20 = TokenMock.at('0x27E0fF339A2053Ee31093026571f4037419E5c63')
erc721=Token721Mock.at('0xc7Cc26d14Ed6d3beBF69C1eDAC2bCFbC810093a2')


erc721.mintWithURI(accounts[1],1,'degenfarm/V1/creatures/1',{'from':accounts[0]})
erc721.approve(wrapper.address, 0, {'from':accounts[0]})
wrapper.wrap721(erc721.address,0,{'from':accounts[0], 'value':'1 ether'})
wrapper.ownerOf(1)
niftsyERC20.approve(wrapper.address, 1e25,{'from':accounts[0]})
wrapper.transferFrom(accounts[0], accounts[1], wrapper.ourId(), {'from':accounts[0]})
wrapper.transferFrom(accounts[1], accounts[0], wrapper.ourId(), {'from':accounts[1]})
wrapper.unWrap721(wrapper.ourId(), {'from':accounts[1]})
```
### Deploy v0.0.2 20210330
#### wrapper  
https://rinkeby.etherscan.io/address/0x510CC3fB0E685Ff20768298d62b231a1A1df35c6#code

#### ERC721MOck
https://rinkeby.etherscan.io/address/0xB71e481C0EB22A3f6Bb54C11128bC673C47a68E5#code

wrapped id=2
https://rinkeby.etherscan.io/tx/0x513e70bef2f29c2a1599da10b05809303c7fe8513c5ff735bdd6b641301cd513
```python
accounts.add('3d56389d912cea65a9f243e7a63089a882c8ea1347c6cf778a7f59da1859c13d')
accounts.add('3c2c9898bd1df57f9fc16a547cf0ffc4014006b863e0b2a8be0cb63e74542b9c')

wrapper = Wraped721.at('0x510CC3fB0E685Ff20768298d62b231a1A1df35c6')
erc721=Token721Mock.at('0xB71e481C0EB22A3f6Bb54C11128bC673C47a68E5')
```
