// SPDX-License-Identifier: MIT
// ENVELOP (NIFTSY) protocol for NFT. MultiMinter
pragma solidity 0.8.10;

//import "./WrapperWithERC20Collateral.sol";
import "@openzeppelin/contracts/access/Ownable.sol";
import "../interfaces/IERC721Mintable.sol";
import "../interfaces/IWrapperCollateralWrap.sol";
import "@openzeppelin/contracts/token/ERC20/utils/SafeERC20.sol";
import "@openzeppelin/contracts/token/ERC721/utils/ERC721Holder.sol";


/**
 * @title ERC-721 Non-Fungible Token Wrapper 
 * @dev For multiMint erc721
 */
contract MultiWrapper721 is Ownable, ERC721Holder {
    using SafeERC20 for IERC20;
    
    struct ERC20Collateral {
        address erc20Token;
        uint256 amount;
    }
    
    mapping(address => bool) public distributors;
    IWrapperCollateralWrap public wrapper;

    constructor () 
    {
        distributors[msg.sender] = true;

    }

    function WrapAndDistrib721Batch(
        address _original721, 
        address[] memory _receivers,
        uint256[] memory _tokenIds, 
        ERC20Collateral[] memory _forDistrib,
        uint256 _unwrapAfter
    ) public payable 
    {
        require(distributors[msg.sender], "Only for distributors");
        //require(_receivers.length <= 256, "Not more 256");
        require(_receivers.length == _tokenIds.length, "Not equal arrays");
        // topup this contract with erc20 that would be added in collateral
        for (uint8 i = 0; i < _forDistrib.length; i ++) {
            IERC20(_forDistrib[i].erc20Token).safeTransferFrom(
                msg.sender, 
                address(this), 
                _forDistrib[i].amount * _receivers.length
            );
            // Set approve from this  multiwraper to distributor
            IERC20(_forDistrib[i].erc20Token).approve(
                address(wrapper), 
                IERC20(_forDistrib[i].erc20Token).balanceOf(msg.sender)
            );
        }

        IERC721Mintable(_original721).setApprovalForAll(address(wrapper), true);

        uint256 _wNFTTokenId;
        uint256 etherPerwNFT = msg.value / _receivers.length; // native blockchain asset
        for (uint8 i = 0; i < _receivers.length; i ++) {

            // Wrap
            _wNFTTokenId = wrapper.wrap721(
                _original721,   // _underlineContract, 
                _tokenIds[i],   // _tokenId, 
                _unwrapAfter,
                0,              // _transferFee,
                address(0),     //  _royaltyBeneficiary,
                0,              // _royaltyPercent,
                0,              // _unwraptFeeThreshold,
                address(0)     // _transferFeeToken
            );

            // Add erc20 collateral
            for (uint8 j = 0; j < _forDistrib.length; j ++) {
                wrapper.addERC20Collateral(
                    _wNFTTokenId, 
                    _forDistrib[j].erc20Token, 
                    _forDistrib[j].amount
                );
            }
            
            // Add native collateral
            if (etherPerwNFT > 0) {
                wrapper.addNativeCollateral{value: etherPerwNFT}(_wNFTTokenId); 
            }

            // Transfer WNFT if _receiver[i] != msg.sender
            if (_receivers[i] != msg.sender) {
                wrapper.transferFrom(address(this), _receivers[i], _wNFTTokenId);
            }
            
        }
    }

    function AddManyCollateralToBatch(
        uint256[] memory _tokenIds, 
        ERC20Collateral[] memory _forAdd
    ) public payable 
    {
        require(distributors[msg.sender], "Only for distributors");
        // topup this contract with erc20 that would be added in collateral
        for (uint8 i = 0; i < _forAdd.length; i ++) {
            IERC20(_forAdd[i].erc20Token).safeTransferFrom(
                msg.sender, 
                address(this), 
                _forAdd[i].amount * _tokenIds.length
            );
        }

        uint256 etherPerwNFT = msg.value / _tokenIds.length; // native blockchain asset
        for (uint8 i = 0; i < _tokenIds.length; i ++) {
            // 3.Add erc20 collateral
            for (uint8 j = 0; j < _forAdd.length; j ++) {
                wrapper.addERC20Collateral(
                    _tokenIds[i], 
                    _forAdd[j].erc20Token, 
                    _forAdd[j].amount
                );
            }

            if (etherPerwNFT > 0) {
                wrapper.addNativeCollateral{value: etherPerwNFT}(_tokenIds[i]); 
            }
            
        }
    }

    //  !!!! No topup inside function
    //  Please do it before
    //  No ether  can be added this way
    function AddOneCollateralToBatch(
        uint256[] memory _tokenIds, 
        ERC20Collateral[] memory _forAdd
    ) public payable 
    {
        require(distributors[msg.sender], "Only for distributors");
        require(_tokenIds.length == _forAdd.length, "Not equal arrays");

        for (uint8 i = 0; i < _tokenIds.length; i ++) {
            // 3.Add erc20 collateral
            wrapper.addERC20Collateral(
                _tokenIds[i], 
                _forAdd[i].erc20Token, 
                _forAdd[i].amount
            );

        }
    }
   


    ////////////////////////////////////////////////////////////////
    //////////     Admins                                     //////
    ////////////////////////////////////////////////////////////////

    function setDistributorState(address _user, bool _state) external onlyOwner {
        distributors[_user] = _state;
    }

    function setWrapper(address _wrapperContract) external onlyOwner {
        wrapper = IWrapperCollateralWrap(_wrapperContract);
    }

    function claimNFT(address _erc721, uint256 _tokenId) external onlyOwner {
         IERC721Mintable(_erc721).transferFrom(address(this), owner(), _tokenId);
    }

    function proxySetApprovalForAll(address _erc721, address _operator, bool _isApproved) external onlyOwner {
         IERC721Mintable(_erc721).setApprovalForAll(_operator, _isApproved);
    }
    ////////////////////////////////////////////////////////////////

   
}

