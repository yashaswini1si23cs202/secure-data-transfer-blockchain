// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

/// @title Ledger
/// @notice Stores a SHA-256 file hash on-chain against a filename, so
///         any later change to the file can be detected by comparing
///         a freshly computed hash against the one recorded here.
///         This is the on-chain replacement for backend/ledger.py's
///         JSON-file stub used in Phase 1.
contract Ledger {
    // filename -> SHA-256 hash (hex string)
    mapping(string => string) private fileHashes;

    // filename -> address that stored the hash (who uploaded it)
    mapping(string => address) private uploader;

    // Emitted every time a hash is stored, so it shows up in Ganache's
    // transaction/event log — useful to point at during your viva.
    event HashStored(string filename, string fileHash, address indexed uploadedBy);

    /// @notice Record a file's hash. Called once per uploaded file.
    function storeHash(string memory filename, string memory fileHash) public {
        fileHashes[filename] = fileHash;
        uploader[filename] = msg.sender;
        emit HashStored(filename, fileHash, msg.sender);
    }

    /// @notice Retrieve the recorded hash for a filename.
    ///         Returns an empty string if nothing was ever stored.
    function getHash(string memory filename) public view returns (string memory) {
        return fileHashes[filename];
    }

    /// @notice Retrieve which blockchain account originally stored
    ///         the hash for a filename (useful for an audit trail).
    function getUploader(string memory filename) public view returns (address) {
        return uploader[filename];
    }
}
