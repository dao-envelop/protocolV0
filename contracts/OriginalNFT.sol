// SPDX-License-Identifier: MIT
pragma solidity ^0.8.6;

import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/token/ERC721/extensions/ERC721Enumerable.sol";
import "@openzeppelin/contracts/utils/Strings.sol";


contract OrigNFT is ERC721Enumerable, Ownable {
    using Strings for uint256;
    using Strings for uint160;
    
    string  internal baseurl;
    uint256 public lastNFTId;
    
    constructor(
        string memory name_,
        string memory symbol_,
        string memory _baseurl
    ) 
        ERC721(name_, symbol_)  
    {
        baseurl = baseurl = string(
            abi.encodePacked(
                _baseurl,
                block.chainid.toString(),
                "/",
                uint160(address(this)).toHexString(),
                "/"
            )
        );
    }

    function mint(address _to) external {
        lastNFTId += 1;
        _mint(_to, lastNFTId);
    }
    
    function baseURI() external view  returns (string memory) {
        return baseurl;
    }

    function tokenURI(uint256 _tokenId) public view override returns (string memory) {
        return baseurl;
    }
}
