// SPDX-License-Identifier: MIT
// ENVELOP (NIFTSY) protocol for NFT. Wrapper & Distributor contract
pragma solidity ^0.8.6;

// import "./WrapperWithERC20Collateral.sol";
// import "../interfaces/IERC721Mintable.sol";
import "./WrapperDistributor.sol";

/**
 * @title ERC-721 Non-Fungible Token Wrapper 
 * @dev For wrpap existing ERC721 with ability add ERC20 collateral
 */
contract WrapperDistributor721Saft is WrapperDistributor721 {
    using Strings for uint256;
    using Strings for uint160;
    
    string  internal baseurl;
    
    constructor(
        string memory _baseurl,
        address _erc20
    ) 
        WrapperDistributor721(_erc20)  
    {
        baseurl = string(
            abi.encodePacked(
                _baseurl,
                block.chainid.toString(),
                "/",
                uint160(address(this)).toHexString(),
                "/"
            )
        );

    }

    function baseURI() external view  returns (string memory) {
        return _baseURI();
    }

    function _baseURI() internal view  override(WrapperDistributor721) returns (string memory) {
        return baseurl;
    }

}

