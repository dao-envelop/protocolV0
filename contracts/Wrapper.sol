// SPDX-License-Identifier: MIT
// NIFTSY protocol for NFT. Wrapper - main protocol contract
pragma solidity ^0.8.4;
import "OpenZeppelin/openzeppelin-contracts@4.1.0/contracts/token/ERC721/extensions/ERC721Enumerable.sol";
import "OpenZeppelin/openzeppelin-contracts@4.1.0/contracts/token/ERC20/IERC20.sol";
import "OpenZeppelin/openzeppelin-contracts@4.1.0/contracts/access/Ownable.sol";
/**
 * @title ERC-721 Non-Fungible Token Wrapper
 * @dev For wrpap existing ERC721 and ERC1155(now only 721)
 */
contract Wrapper721 is ERC721Enumerable, Ownable {

    
    struct NFT {
        address tokenContract;      //Address of wrapping token  contract
        uint256 tokenId;            //Wrapping tokenId
        uint256 backedValue;        //ETH
        uint256 backedTokens;       //native project tokens
        uint256 unwrapAfter;        //Freez date
        uint256 transferFee;        //transferFee amount with decimals i.e. 20e18
        address royaltyBeneficiary; //Royalty payments receiver
        uint256 royaltyPercent;     //% from transferFee
        uint256 unwraptFeeThreshold;//unwrap possiple only after backedTokens achive this amount
    }

    uint256 constant public MAX_ROYALTY_PERCENT = 50;
    uint256 constant public MAX_TIME_TO_UNWRAP = 365 days;
    uint256 constant public MAX_FEE_THRESHOLD_PERCENT = 10; //percent from project token tottallSypply

    uint256 public protokolFee = 0;
    uint256 public chargeFeeAfter = type(uint256).max;
    uint256 public protokolFeeRaised;

    address public projectToken;

    mapping(uint256 => NFT) public wrappedTokens; //Private in Production

    uint256 public lastWrappedNFTId; //Private in Production...will think

    event Wrapped(
        address underlineContract, 
        uint256 tokenId, 
        uint256 indexed wrappedTokenId
    );
    event NewFee(uint256 feeAmount, uint256 startDate);
    event NiftsyProtocolTransfer(
        uint256 indexed wrappedTokenId, 
        address indexed royaltyBeneficiary,
        uint256 transferFee, 
        uint256 royalty 
    );

    constructor(address _erc20) ERC721("Wrapped NFT Protocol v0.2.0", "NIFTSY") {
        projectToken = _erc20; 
    }

    /**
     * @dev Function for wrap existing ERC721 
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
        uint256 _transferFee,
        address _royaltyBeneficiary,
        uint256 _royaltyPercent,
        uint256 _unwraptFeeThreshold
    ) 
        external 
        payable
        returns (uint256) 
    {
        
        /////////////////Sanity checks////////////////////////
        //1. ERC allowance
        require(
            IERC721(_underlineContract).getApproved(_tokenId) == address(this), 
            "Please call approve in your NFT contract"
        );

        //2. Logik around transfer fee
        if  (_transferFee > 0) {
            require(_royaltyPercent <= MAX_ROYALTY_PERCENT, "Royalty percent too big");     

        } else {
            require(_royaltyPercent == 0, "Royalty source is transferFee");
            require(_royaltyBeneficiary == address(0), "No Royalty without transferFee");
        }

        //3. MAX time to UNWRAP
        require( _unwrapAfter <= block.timestamp + MAX_TIME_TO_UNWRAP,
            "Too long Wrap"
        );

        //4. 
        require(
            _unwraptFeeThreshold  <
            IERC20(projectToken).totalSupply() * MAX_FEE_THRESHOLD_PERCENT / 100,
            "Too much threshold"
        );
        //////////////////////////////////////////////////////
        //Protokol fee can be not zero in the future       //
        if  (_getProtokolFeeAmount() > 0) {
            require(
                _chargeFee(msg.sender, _getProtokolFeeAmount()), 
                "Cant charge protokol fee"
            );
        }

        ////////////////////////
        ///   WRAP LOGIC    ////
        IERC721(_underlineContract).transferFrom(msg.sender, address(this), _tokenId);
        lastWrappedNFTId += 1;
        _mint(msg.sender, lastWrappedNFTId);
        wrappedTokens[lastWrappedNFTId] = NFT(
            _underlineContract, 
            _tokenId, 
            msg.value, 
            0, 
            _unwrapAfter, 
            _transferFee,
            _royaltyBeneficiary,
            _royaltyPercent,
            _unwraptFeeThreshold
        );
        emit Wrapped(_underlineContract, _tokenId, lastWrappedNFTId);
        return lastWrappedNFTId;
    }

    /**
     * @dev Function add native(eth, bnb) collateral to wrapped token
     *
     * @param _wrappedTokenId id of protocol token fo add
     */
    function addNativeCollateral(uint256 _wrappedTokenId) external payable {
        require(
            ownerOf(_wrappedTokenId) == msg.sender, 
            "Only current owner can add collateral"
        );
        NFT storage nft = wrappedTokens[_wrappedTokenId];
        nft.backedValue += msg.value;
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
            require(nft.unwrapAfter <= block.timestamp, "Cant unwrap before day X");    
        }

        if (nft.unwraptFeeThreshold > 0){
            require(nft.backedTokens >= nft.unwraptFeeThreshold, "Cant unwrap due Fee Threshold");
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

    function tokenURI(uint256 tokenId) public view override returns (string memory) {
        NFT storage nft = wrappedTokens[tokenId];
        return IERC721Metadata(nft.tokenContract).tokenURI(nft.tokenId);
    }

    function getTokenValue(uint256 tokenId) external view returns (uint256, uint256) {
        NFT storage nft = wrappedTokens[tokenId];
        return (nft.backedValue, nft.backedTokens);
    }

    function getWrappedToken(uint256 tokenId) external view returns (NFT memory) {
        return wrappedTokens[tokenId];
    }

    
    /////////////////////////////////////////////////////////////////////
    //                    Admin functions                              //
    /////////////////////////////////////////////////////////////////////
    function setFee(uint256 _fee, uint256 _startDate) external onlyOwner {
        protokolFee = _fee;
        chargeFeeAfter = _startDate;
        emit NewFee(_fee, _startDate);
    }


    /////////////////////////////////////////////////////////////////////

    /////////////////////////////////////////////////////////////////////
    /////////////   Internals     ///////////////////////////////////////
    /////////////////////////////////////////////////////////////////////
    function _beforeTokenTransfer(address from, address to, uint256 tokenId) 
        internal 
        virtual 
        override 
    {
        //Not for mint and burn
        if (to != address(0) && from !=address(0)) {
            NFT storage nft = wrappedTokens[tokenId];
            //Transfer fee charge
            if  (nft.transferFee > 0) {
                uint256 rAmount;
                if (_chargeFee(from, nft.transferFee) == true) {
                    //Royalty send   
                    if  (nft.royaltyPercent > 0 ) {
                        rAmount = nft.royaltyPercent * nft.transferFee / 100;
                        IERC20(projectToken).transfer(
                            nft.royaltyBeneficiary,
                            rAmount
                        );
                    }
                    nft.backedTokens += nft.transferFee - rAmount;
                }
                emit NiftsyProtocolTransfer(tokenId, nft.royaltyBeneficiary, nft.transferFee, rAmount);
            }
        }
    }

    function _chargeFee(address _payer, uint256 _amount) internal returns(bool) {
        require(
            IERC20(projectToken).balanceOf(_payer) >= _amount, 
                    "insufficient NIFTSY balance for fee"
        );
        IERC20(projectToken).transferFrom(_payer, address(this), _amount);
        return true;
    }

    function _getProtokolFeeAmount() internal view returns (uint256) {
        if (block.timestamp >= chargeFeeAfter) {
            return protokolFee;
        } else {
            return 0;
        }
    }

}