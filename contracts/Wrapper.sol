
// SPDX-License-Identifier: MIT

pragma solidity ^0.7.4;

import "OpenZeppelin/openzeppelin-contracts@3.4.0/contracts/token/ERC721/ERC721.sol";
import "OpenZeppelin/openzeppelin-contracts@3.4.0/contracts/token/ERC20/IERC20.sol";

/**
 * @title ERC-721 Non-Fungible Token Wrapper
 * @dev For wrpap existing ERC721 and ERC1155
 */
contract Wraped721 is ERC721 {
    using SafeMath for uint256; 


    struct NFT{
        address tokenContract; //Address of wrapping token  contract
        uint256 tokenId;       //Wrapping tokenId
        uint256 backedValue;   //ETH
        uint256 backedTokens;  //native project tokens
        uint256 unwrapAfter;   //Freez date
        uint256 transferFee;   //transferFee amount with decimals i.e. 20e18
    }

    address public projectToken;
    //uint256 public constant transferFee = 1e18; 

    mapping(uint256 => NFT) public wrappedTokens; //Private in Production

    uint256 public ourId; //Private in Production...will think

    event Wrapped(address underlineContract, uint256 tokenId, uint256 indexed wrappedTokenId);

    constructor(address _erc20) ERC721("Wrapped NFT Protocol v0.0.2", "NIFTSY") {
        projectToken = _erc20;
    }

    /**
     * @dev Function for wrap existing ERC721 and ERC1155 token
     *
     * @param _underlineContract address of native NFT contract
     * @param _tokenId id of NFT that need to be wraped
     * @param _unwrapAfter Unix time value after that token can be unwrapped  
     * @param _transferFee transferFee amount of projectToken with decimals i.e. 20e18 
     * @return uint256 id of new wrapped token that represent old
     */
    function wrap721(
        address _underlineContract, 
        uint256 _tokenId, 
        uint256 _unwrapAfter,
        uint256 _transferFee
    ) 
        external 
        payable
        returns (uint256) 
    {
        require(
            IERC721(_underlineContract).getApproved(_tokenId) == address(this), 
            "Please call approve in your NFT contract."
        );
        IERC721(_underlineContract).transferFrom(msg.sender, address(this), _tokenId);
        ourId = ourId.add(1);
        _mint(msg.sender, ourId);
        wrappedTokens[ourId] = NFT(
            _underlineContract, 
            _tokenId, 
            msg.value, 
            0, 
            _unwrapAfter, 
            _transferFee
        );
        emit Wrapped(_underlineContract, _tokenId, ourId);
        return ourId;
    }

    /**
     * @dev Function for unwrap protocol token
     *
     * @param _tokenId id of protocol token to unwrapp
     */
    function unWrap721( uint256 _tokenId) external {
        require(ownerOf(_tokenId) == msg.sender, 'Only owner can unwrap it!');
        //storoge did not work because there is no this var after delete
        NFT memory nft = wrappedTokens[_tokenId];
        if  (nft.unwrapAfter != 0) {
            require(nft.unwrapAfter <= block.timestamp, "Can't unwrap before day X");    
        }
        
        _burn(_tokenId);
        IERC721(nft.tokenContract).transferFrom(address(this), msg.sender, nft.tokenId);
        delete wrappedTokens[_tokenId];
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

    function _beforeTokenTransfer(address from, address to, uint256 tokenId) 
        internal 
        virtual 
        override 
    {
        //Not for mint and burn
        if (to != address(0) && from !=address(0)) {
            NFT storage nft = wrappedTokens[tokenId];
            if  (nft.transferFee > 0) {
                require(
                    IERC20(projectToken).allowance(to, address(this))>=nft.transferFee, 
                    "Receiver must approve our ERC20 for fee."
                );
                IERC20(projectToken).transferFrom(to, address(this), nft.transferFee);
                nft.backedTokens = nft.backedTokens.add(nft.transferFee);
            }
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

    function getWrappedToken(uint256 tokenId) external view returns (uint256, uint256, uint256, uint256) {
        NFT storage nft = wrappedTokens[tokenId];
        return (nft.backedValue, nft.backedTokens, nft.unwrapAfter, nft.transferFee);
    }
}