// SPDX-License-Identifier: MIT
// NIFTSY protocol for NFT. Wrapper - main protocol contract
pragma solidity ^0.8.4;

import "OpenZeppelin/openzeppelin-contracts@4.1.0/contracts/access/Ownable.sol";
import "OpenZeppelin/openzeppelin-contracts@4.1.0/contracts/token/ERC20/IERC20.sol";
import "OpenZeppelin/openzeppelin-contracts@4.1.0/contracts/token/ERC721/extensions/ERC721Enumerable.sol";
import "OpenZeppelin/openzeppelin-contracts@4.1.0/contracts/token/ERC20/utils/SafeERC20.sol";
/**
 * @title ERC-721 Non-Fungible Token Wrapper
 * @dev For wrpap existing ERC721 and ERC1155(now only 721)
 */
contract Wrapper721 is ERC721Enumerable, Ownable {
    using SafeERC20 for IERC20;

    
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

    struct ERC20Collateral {
        address erc20Token;
        uint256 amount;
    }

    uint256 constant public MAX_ROYALTY_PERCENT = 50;
    uint256 constant public MAX_TIME_TO_UNWRAP = 365 days;
    uint256 constant public MAX_FEE_THRESHOLD_PERCENT = 1; //percent from project token tottallSypply 
    uint16   constant public MAX_ERC20_COUNT = 400; //max coins type count in collateral  

    uint256 public protokolFee = 0;
    uint256 public chargeFeeAfter = type(uint256).max;
    uint256 public protokolFeeRaised;

    address public projectToken;
    
    // Map from wrapped token id => NFT record 
    mapping(uint256 => NFT) public wrappedTokens; //Private in Production

    //Map from wrapped token id to array  with erc20 collateral balances
    mapping(uint256 => ERC20Collateral[]) public erc20Collateral;

    uint256 public lastWrappedNFTId; 

    event Wrapped(
        address underlineContract, 
        uint256 tokenId, 
        uint256 indexed wrappedTokenId
    );

    event UnWrapped(
        uint256 indexed wrappedId, 
        address indexed owner, 
        uint256 nativeCollateralAmount,
        uint256 feeAmount 
    );
    event NewFee(uint256 feeAmount, uint256 startDate);
    event NiftsyProtocolTransfer(
        uint256 indexed wrappedTokenId, 
        address indexed royaltyBeneficiary,
        uint256 transferFee, 
        uint256 royalty 
    );
    event PartialUnWrapp(uint256 wrappedId, address owner);

    constructor(address _erc20) ERC721("Wrapped NFT Protocol v1.0.1", "NIFTSY") {
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
            require(_unwraptFeeThreshold == 0, "Cant set Threshold without transferFee");

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
        require(ownerOf(_wrappedTokenId) != address(0));
        NFT storage nft = wrappedTokens[_wrappedTokenId];
        nft.backedValue += msg.value;
    }

    /**
     * @dev Function for add arbitrary ERC20 collaterals 
     *
     * @param _wrappedTokenId  NFT id from thgis contarct
     * @param _erc20 address of erc20 collateral for add
     * @param _amount amount erc20 collateral for add  
     */
    function addERC20Collateral(uint256 _wrappedTokenId, address _erc20, uint256 _amount) external {
        require(ownerOf(_wrappedTokenId) != address(0));
        require(
            IERC20(_erc20).balanceOf(msg.sender) >= _amount,
            "Low balance for add collateral"
        );
        require(
            IERC20(_erc20).allowance(msg.sender, address(this)) >= _amount,
            "Please approve first"
        );

        IERC20(_erc20).safeTransferFrom(msg.sender, address(this), _amount);

        ERC20Collateral[] storage e = erc20Collateral[_wrappedTokenId];
        for (uint256 i = 0; i < e.length; i ++) {
            if (e[i].erc20Token == _erc20) {
                e[i].amount += _amount;
                return;
            }
        }
        //We can add more tokens if limit not exccedd
        if (e.length < MAX_ERC20_COUNT){
            e.push(ERC20Collateral({
              erc20Token: _erc20, 
              amount: _amount
            }));
        }
        
    }

    /**
     * @dev Function for unwrap protocol token. If wrapped  NFT
     * has many erc20 collateral tokens it possible call this method
     * more than once, until unwrapped
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

        //First we need release erc20 collateral, because erc20 transfers are
        // can be expencive
        ERC20Collateral[] storage e = erc20Collateral[_tokenId];
        if (e.length > 0) { 
            uint256 n = _getTransferBatchCount();
            if (e.length <= n) {
                n = e.length;
            } 
            
            for (uint256 i = n; i > 0; i --){
                IERC20(e[i-1].erc20Token).safeTransfer(msg.sender,  e[i-1].amount);
                e.pop();
            }

            // If not all erc20 collateral were transfered
            // we just exit.  User can finish unwrap with next tx
            if  (e.length > 0 ) {
                emit PartialUnWrapp(_tokenId, msg.sender);
                return;
            }
        }
        /////////////////////////////////////////////// 
        
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
        emit UnWrapped(
            _tokenId, 
            msg.sender, 
            nft.backedValue,
            nft.backedTokens 
        );
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

    function getERC20Collateral(uint256 _wrappedId) external view returns (ERC20Collateral[] memory) {
        return erc20Collateral[_wrappedId];
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
        super._beforeTokenTransfer(from, to, tokenId);
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

    function _getTransferBatchCount() internal view returns (uint256){
        // It can be modified in future protocol version
        return block.gaslimit / 50000; //average erc20 transfer cost 
    }

}