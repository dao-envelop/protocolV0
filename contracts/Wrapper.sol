
// SPDX-License-Identifier: MIT

pragma solidity ^0.7.4;

import "OpenZeppelin/openzeppelin-contracts@3.4.0/contracts/token/ERC721/ERC721.sol";
import "OpenZeppelin/openzeppelin-contracts@3.4.0/contracts/token/ERC20/IERC20.sol";

contract Wraped721 is ERC721 {
    using SafeMath for uint256; 


    struct NFT{
        address tokenContract;
        uint256 tokenId;
        uint256 backedValue;//ETH
        uint256 backedTokens; //native project tokens
    }

    address public projectToken;
    uint256 public constant transferFee = 1e18; 

    mapping(uint256 => NFT) public wrappedTokens; //Private in Production

    uint256 public ourId; //Private in Production

    event Wrapped(address underlineContract, uint256 tokenId);

    constructor(address _erc20) ERC721("Wrapped NFT v0.0.1", "NIFTSY") {
        projectToken = _erc20;
    }

    function wrap721(address underlineContract, uint256 tokenId) external payable{
        //TODO  Check Allowed
        require(IERC721(underlineContract).getApproved(tokenId) == address(this), "Please call approve in your NFT contract.");
        IERC721(underlineContract).transferFrom(msg.sender, address(this), tokenId);
        ourId = ourId.add(1);
        _mint(msg.sender, ourId);
        wrappedTokens[ourId] = NFT(underlineContract, tokenId, msg.value, 0);
        emit Wrapped(underlineContract, tokenId);
    }

    function unWrap721( uint256 tokenId) external {
        require(ownerOf(tokenId) == msg.sender, 'Only owner can unwrap it!');
        //storoge did not work because there is no this var after delete
        NFT memory nft = wrappedTokens[tokenId];

        //TODO  Check Allowed
        _burn(tokenId);
        IERC721(nft.tokenContract).transferFrom(address(this), msg.sender, nft.tokenId);
        delete wrappedTokens[tokenId];
        //Return backed ether
        if  (nft.backedValue > 0) {
            address payable toPayable = payable(msg.sender);
            toPayable.transfer(nft.backedValue);
        }
        //Return backed tokens
        if  (nft.backedTokens > 0) {
            IERC20(projectToken).transfer(msg.sender, nft.backedTokens);
        }
    }

    function _beforeTokenTransfer(address from, address to, uint256 tokenId) internal virtual override {
        //Not for mint and burn
        if (to != address(0) && from !=address(0)) {
            require(IERC20(projectToken).allowance(to, address(this))>=transferFee, "Receiver must approve our ERC20 for fee.");
            IERC20(projectToken).transferFrom(to, address(this), transferFee);
            NFT storage nft = wrappedTokens[tokenId];
            nft.backedTokens = nft.backedTokens.add(transferFee);
        }
    }

    function tokenURI(uint256 tokenId) public view override returns (string memory) {
        NFT storage nft = wrappedTokens[tokenId];
        return IERC721Metadata(nft.tokenContract).tokenURI(nft.tokenId);
    }

    function getTokenValue(uint256 tokenId) external view returns (uint256, uint256) {
        NFT storage nft = wrappedTokens[tokenId];
        return (nft.backedValue, nft.backedTokens);
    }
}