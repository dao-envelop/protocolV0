// SPDX-License-Identifier: MIT
// NIFTSY protocol for NFT
pragma solidity ^0.8.2;

import "OpenZeppelin/openzeppelin-contracts@4.1.0/contracts/access/Ownable.sol";
import "OpenZeppelin/openzeppelin-contracts@4.1.0/contracts/token/ERC721/extensions/ERC721URIStorage.sol";

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

    function _baseURI() internal view  override returns (string memory) {
        return 'https://nft.iber.group/degenfarm/V1/creatures/';
    }
}
