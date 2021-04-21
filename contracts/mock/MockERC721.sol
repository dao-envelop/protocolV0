// SPDX-License-Identifier: MIT
// NIFTSY protocol for NFT
pragma solidity ^0.7.4;

import "./ERC721URIStorage.sol";
import "OpenZeppelin/openzeppelin-contracts@3.4.0/contracts/access/Ownable.sol";

//v0.0.1
contract Token721Mock is ERC721URIStorage, Ownable {

    
    constructor(string memory name_,
        string memory symbol_) ERC721(name_, symbol_)  {
        _mint(msg.sender, 0);
    }

    function mintWithURI(
        address to, 
        uint256 tokenId, 
        string memory _tokenURI 
    ) external onlyOwner {
        
        _mint(to, tokenId);
        _setTokenURI(tokenId, _tokenURI);
    }
    
    //TODO Remove if not usefull
    function setURI(uint256 tokenId, string memory _tokenURI) external {
        require(ownerOf(tokenId) == msg.sender, 'Only owner can changi URI.');
        _setTokenURI(tokenId, _tokenURI);

    }

    function baseURI() public view  override returns (string memory) {
        return 'https://nft.iber.group/degenfarm/V1/creatures/';
    }
}
