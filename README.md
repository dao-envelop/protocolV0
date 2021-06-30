## NIFTSY protocol
Collateral-backed and price discovery cross-chain protocol to provide NFT with
 inner value and liquidity.

### Protocol Conractcts
`WrapperBase` - main protocol contract with Wrapp and UnWrapp functionality.  
Features:
 - ability add native chain collateral(ETH, BNB, ...);
 - ability add each-transfer-accumulated fee;
 - author royalty from each erc721 token transfer;  

`WrapperWithERC20Collateral` - extending for `WrapperBase`, add features for 
ability add whitelisted ERC20 collateral to wrapped NFT.

### Deployments Info
Deploy is very simple. You can find workflow in 
[fixtures](./tests/fixtures/deploy_env.py) 

### Deploy 20210627 Rinkeby ALFA-2-AUDIT
#### WrapperWithERC20Collateral  
https://rinkeby.etherscan.io/address/0xB9401FeB33fd7b13f549a1992A18E771a52A9e65#code

#### Niftsy ERC20
https://rinkeby.etherscan.io/address/0x1E991eA872061103560700683991A6cF88BA0028#code

#### ERC721MOck
https://rinkeby.etherscan.io/address/0x50FFDdCA76f4Eba021F701e6c400347A8c4bde55#code

----


### Deploy 20210627 Rinkeby ALFA
#### WrapperWithERC20Collateral  
https://rinkeby.etherscan.io/address/0x937DbB747f69df066e0BA60cf673feB082c3514a#code

#### Niftsy ERC20
https://rinkeby.etherscan.io/address/0x1E991eA872061103560700683991A6cF88BA0028#code

#### ERC721MOck
https://rinkeby.etherscan.io/address/0xB71e481C0EB22A3f6Bb54C11128bC673C47a68E5#code



### Deploy 20210609 Rinkeby v1.0.1
#### wrapper  
https://rinkeby.etherscan.io/address/0xfe6d84794169c3794d9842695b2969db96cb19ee#code

#### Niftsy ERC20
https://rinkeby.etherscan.io/address/0x1E991eA872061103560700683991A6cF88BA0028#code

#### ERC721MOck
https://rinkeby.etherscan.io/address/0xB71e481C0EB22A3f6Bb54C11128bC673C47a68E5#code



#### 20210421 Testnet Binance Smart Chain
##### wrapper
https://testnet.bscscan.com/address/0x45198c41fb63Ad4119E52587ACc968944633254D#code

##### NIFTSY ERC20
https://testnet.bscscan.com/address/0xCEFe82aDEd5e1f8c2610256629d651840601EAa8#code

##### ERC721MOck
https://testnet.bscscan.com/address/0x3ddaeC66470Ca68eb20dfBfC8f3287B94e4320a8#code


----

#### Deploy v0.0.2 20210330
##### wrapper  
https://rinkeby.etherscan.io/address/0x510CC3fB0E685Ff20768298d62b231a1A1df35c6#code

##### ERC721MOck
https://rinkeby.etherscan.io/address/0xB71e481C0EB22A3f6Bb54C11128bC673C47a68E5#code
