// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

contract SteganographyRegistry {
    struct ImageRecord {
        string ipfsHash;
        string metadataHash;
        uint256 timestamp;
        address owner;
        bool exists;
    }
    
    mapping(string => ImageRecord) public imageRecords;
    mapping(address => string[]) public userImages;
    
    event ImageStored(
        string indexed imageId,
        string ipfsHash,
        string metadataHash,
        address indexed owner
    );
    
    function storeImageRecord(
        string memory imageId,
        string memory ipfsHash,
        string memory metadataHash
    ) public {
        require(!imageRecords[imageId].exists, "Image already exists");
        
        imageRecords[imageId] = ImageRecord({
            ipfsHash: ipfsHash,
            metadataHash: metadataHash,
            timestamp: block.timestamp,
            owner: msg.sender,
            exists: true
        });
        
        userImages[msg.sender].push(imageId);
        
        emit ImageStored(imageId, ipfsHash, metadataHash, msg.sender);
    }
    
    function getImageRecord(string memory imageId) 
        public view returns (ImageRecord memory) {
        require(imageRecords[imageId].exists, "Image not found");
        return imageRecords[imageId];
    }
    
    function getUserImages(address user) 
        public view returns (string[] memory) {
        return userImages[user];
    }
    
    function verifyImageOwnership(string memory imageId, address user) 
        public view returns (bool) {
        return imageRecords[imageId].owner == user && imageRecords[imageId].exists;
    }
}