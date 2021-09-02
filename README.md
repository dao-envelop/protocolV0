## NIFTSY protocol
Collateral-backed and price discovery cross-chain protocol to provide NFT with
 inner value and liquidity.

### Protocol Conracts
`WrapperBase` - main protocol contract with Wrapp and UnWrapp functionality.  
Features:
 - ability add native chain collateral(ETH, BNB, ...);
 - ability add each-transfer-accumulated fee;
 - author royalty from each erc721 token transfer;  

`WrapperWithERC20Collateral` - extending for `WrapperBase`, add features for 
ability add whitelisted ERC20 collateral to wrapped NFT.

### Tests
We use Brownie framework for developing and unit test. For run tests
first please [install it](https://eth-brownie.readthedocs.io/en/stable/install.html)

```bash
brownie pm install OpenZeppelin/openzeppelin-contracts@4.1.0
brownie test
```
In `./tests` directory you can find test case file `long_test_wrapper_unWrap721_2.py` 
which **is not** run with `brownie test` command becaus it take  along time (5..10 min).
But for  run it please use : `brownie test ./tests/long_test_wrapper_unWrap721_2.py`


Don't forget [ganache-cli](https://www.npmjs.com/package/ganache-cli)

### Deployments Info
Deploy is very simple. You can find workflow in 
[fixtures](./tests/fixtures/deploy_env.py) 

### Ethereum Mainnet deploy ALFA 
**NIFTSY ERC20 token**  
https://etherscan.io/address/0x7728cd70b3dD86210e2bd321437F448231B81733#code

**WrapperWithERC20Collateral**   
https://etherscan.io/address/0xc2571eBbc8F2af4f832bB8a2D3A4b0932Ce24773#code

**techERC20**  
https://etherscan.io/address/0x6426Bc3F86E554f44bE7798c8D1f3482Fb7BB68C#code

**TransferRoyaltyModel01**  
https://etherscan.io/address/0x6664c8118284b3F5ECB47c2105cAa544Ab0Cf75B#code


----
### Deploy 20210830 Rinkeby Pre Prod Deploy
**WrapperWithERC20Collateral**  
https://rinkeby.etherscan.io/address/0x6d3e28b5Fa8d13A08Cbbf8151D86f77829977c34#code  

**techERC20**
https://rinkeby.etherscan.io/address/0xbbe47167666100eC33de9079c1EE7B150cCbD874#code  


**TransferRoyaltyModel01**
https://rinkeby.etherscan.io/address/0x64820a2cB3367C9b1416a101682e3CAc7E7392a9#code  



#### Gas Consumption Info
```
WrapperWithERC20Collateral <Contract>
   ├─ constructor                -  avg : 4145117  low: 4145117  high: 4145117
   ├─ wrap721                    -  avg :  372649  low:   24713  high:  429754
   ├─ transferFrom               -  avg :  114051  low:   23486  high:  177410
   ├─ unWrap721                  -  avg :  122923  low:   28379  high:  233867
   ├─ addERC20Collateral         -  avg :  103729  low:   29117  high:  123936
   ├─ setFee                     -  avg :   67448  low:   23069  high:   70191
   ├─ approve                    -  avg :   46901  low:   46894  high:   46906
   ├─ setCollateralStatus        -  avg :   44723  low:   23077  high:   45254
   ├─ editPartnersItem           -  avg :   37254  low:   14771  high:   44794
   ├─ addNativeCollateral        -  avg :   29972  low:   22525  high:   43430
   └─ setMaxERC20CollateralCount -  avg :   29588  low:   22535  high:   29588


```

----


### Deploy 20210627 Rinkeby ALFA
#### WrapperWithERC20Collateral  
https://rinkeby.etherscan.io/address/0x937DbB747f69df066e0BA60cf673feB082c3514a#code

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

---
