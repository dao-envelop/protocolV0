// SPDX-License-Identifier: MIT
// NIFTSY protocol for NFT
pragma solidity ^0.8.6;

import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/token/ERC721/ERC721.sol";

//v0.0.1
contract ERC721Distribution is ERC721, Ownable {
    
    mapping(address => bool) public trustedMinter;
    
    constructor(string memory name_,
        string memory symbol_) ERC721(name_, symbol_)  {
        trustedMinter[msg.sender] = true;

    }

    function mint(address _to, uint256 _tokenId) external {
        require(trustedMinter[msg.sender], "Trusted address only");
        _mint(_to, _tokenId);
    }
    
    
    function baseURI() external view  returns (string memory) {
        return _baseURI();
    }

    function _baseURI() internal view  override returns (string memory) {
        return 'https://envelop.is/distribmetadata/';
    }

    function setMinterStatus(address _minter, bool _isTrusted) external onlyOwner {
        trustedMinter[_minter] = _isTrusted;
    }
}
