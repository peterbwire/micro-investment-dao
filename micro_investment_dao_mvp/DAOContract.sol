// contracts/DAOContract.sol

// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract DAOContract {
    struct Proposal {
        uint id;
        string description;
        uint amount;
        uint voteCountYes;
        uint voteCountNo;
        bool executed;
        mapping(address => bool) voters;
    }

    struct Group {
        string name;
        address[] members;
        uint balance;
        mapping(uint => Proposal) proposals;
        uint proposalCount;
    }

    mapping(uint => Group) public groups;
    uint public groupCount = 0;

    event GroupCreated(uint groupId, string name);
    event ContributionMade(uint groupId, address contributor, uint amount);
    event ProposalCreated(uint groupId, uint proposalId, string description, uint amount);
    event VoteCast(uint groupId, uint proposalId, address voter, bool support);
    event ProposalExecuted(uint groupId, uint proposalId);

    function createGroup(string memory name) public {
        Group storage g = groups[groupCount];
        g.name = name;
        g.members.push(msg.sender);
        groupCount++;
        emit GroupCreated(groupCount - 1, name);
    }

    function contribute(uint groupId) public payable {
        Group storage g = groups[groupId];
        g.balance += msg.value;
        g.members.push(msg.sender);
        emit ContributionMade(groupId, msg.sender, msg.value);
    }

    function proposeInvestment(uint groupId, string memory description, uint amount) public {
        Group storage g = groups[groupId];
        Proposal storage p = g.proposals[g.proposalCount];
        p.id = g.proposalCount;
        p.description = description;
        p.amount = amount;
        g.proposalCount++;
        emit ProposalCreated(groupId, p.id, description, amount);
    }

    function vote(uint groupId, uint proposalId, bool support) public {
        Proposal storage p = groups[groupId].proposals[proposalId];
        require(!p.voters[msg.sender], "Already voted");
        p.voters[msg.sender] = true;
        if (support) {
            p.voteCountYes++;
        } else {
            p.voteCountNo++;
        }
        emit VoteCast(groupId, proposalId, msg.sender, support);
    }

    function executeProposal(uint groupId, uint proposalId) public {
        Group storage g = groups[groupId];
        Proposal storage p = g.proposals[proposalId];
        require(!p.executed, "Already executed");
        require(p.voteCountYes > p.voteCountNo, "Not enough yes votes");
        require(p.amount <= g.balance, "Insufficient balance");

        p.executed = true;
        g.balance -= p.amount;
        payable(msg.sender).transfer(p.amount);
        emit ProposalExecuted(groupId, proposalId);
    }

    function getGroupMembers(uint groupId) public view returns (address[] memory) {
        return groups[groupId].members;
    }

    function getGroupBalance(uint groupId) public view returns (uint) {
        return groups[groupId].balance;
    }
}
