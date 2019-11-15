import pendulum
from pendulum.parsing.exceptions import ParserError
from datetime import datetime
from itertools import count
from typing import Iterator

from pytezos.tools.docstring import get_attr_docstring
from pytezos.rpc.search import BlockSliceQuery
from pytezos.rpc.query import RpcQuery
from pytezos.encoding import is_bh, is_ogh


def to_timestamp(v):
    try:
        v = pendulum.parse(v)
    except ParserError:
        pass
    if isinstance(v, datetime):
        v = int(v.timestamp())
    return v


class BlocksQuery(RpcQuery, path='/chains/{}/blocks'):

    def __call__(self, length=1, head=None, min_date=None):
        """
        Lists known heads of the blockchain sorted with decreasing fitness.
        Optional arguments allows to returns the list of predecessors for known heads
        or the list of predecessors for a given list of blocks.
        :param length: The requested number of predecessors to returns (per requested head).
        :param head: An empty argument requests blocks from the current heads.
        A non empty list allow to request specific fragment of the chain.
        :param min_date: When `min_date` is provided, heads with a timestamp before `min_date` are filtered out
        :return: list[list[str]]
        """
        if isinstance(head, str) and not is_bh(head):
            head = self.__getitem__(head).calculate_hash()

        if min_date and not isinstance(min_date, int):
            min_date = to_timestamp(min_date)

        return super(BlocksQuery, self).__call__(
            length=length, head=head, min_date=min_date)

    def __getitem__(self, block_id):
        """
        Construct block query or get a block range.
        :param block_id: Block identity or block range
          int: Block level or offset from the head if negative;
          str: Block hash (base58) or special names (head, genesis), expressions like `head~1` etc;
          slice [:]: First value (start) must be int, second (stop) can be any Block ID or empty.
        :return: BlockQuery or BlockSliceQuery
        """
        if isinstance(block_id, slice):
            if not isinstance(block_id.start, int):
                raise NotImplementedError('Slice start should be an integer.')

            return BlockSliceQuery(
                start=block_id.start,
                stop=block_id.stop,
                node=self.node,
                path=self._wild_path,
                params=self._params
            )

        if isinstance(block_id, int) and block_id < 0:
            return self.blocks[f'head~{block_id}']

        return super(BlocksQuery, self).__getitem__(block_id)

    @property
    def current_voting_period(self):
        """
        Get block range for the current voting period.
        :return: BlockSliceQuery
        """
        metadata = self.head.metadata()
        return BlockSliceQuery(
            start=metadata['level']['level'] - metadata['level']['voting_period_position'],
            stop='head',
            node=self.node,
            path=self._wild_path,
            params=self._params
        )

    @property
    def current_cycle(self):
        """
        Get block range for the current cycle.
        :return: BlockSliceQuery
        """
        metadata = self.head.metadata()
        return BlockSliceQuery(
            start=metadata['level']['level'] - metadata['level']['cycle_position'],
            stop='head',
            node=self.node,
            path=self._wild_path,
            params=self._params
        )


class BlockQuery(RpcQuery, path='/chains/{}/blocks/{}'):

    def __init__(self, *args, **kwargs):
        super(BlockQuery, self).__init__(*args, **kwargs)
        self._caching = self._caching or 'head' not in self._params

    @property
    def predecessor(self):
        """
        Query previous block.
        :return: BlockQuery
        """
        return self._parent[self.header()['predecessor']]

    @property
    def baker(self):
        """
        Query block producer (baker).
        :return: ContractQuery
        """
        return self.context.contracts[self.metadata()['baker']]

    def voting_period(self):
        """
        Get voting period for this block from metadata.
        """
        return self.metadata()['level']['voting_period']

    def level(self) -> int:
        """
        Get level for this block from metadata.
        """
        return self.metadata()['level']['level']

    def cycle(self) -> int:
        """
        Get cycle for this block from metadata.
        """
        return self.metadata()['level']['cycle']


class ContractQuery(RpcQuery, path='/chains/{}/blocks/{}/context/contracts/{}'):

    def public_key(self) -> str:
        """
        Retrieve the contract manager's public key (base58 encoded)
        """
        pkh = self._params[-1]
        if pkh.startswith('KT'):
            pkh = self.manager_key().get('manager')

        pk = self._parent[pkh].manager_key().get('key')
        if not pk:
            raise ValueError('Public key is not revealed.')

        return pk

    def count(self) -> Iterator:
        """
        Get contract counter iterator: it returns incremented value on each call.
        """
        return count(start=int(self.counter()) + 1, step=1)

    def code(self):
        """
        Get contract code
        :return: Micheline expression
        """
        return self().get('script', {}).get('code')


class BigMapGetQuery(RpcQuery, path='/chains/{}/blocks/{}/context/contracts/{}/big_map_get'):

    def post(self, query: dict):
        """
        Access the value associated with a key in the big map storage of the michelson.
        :param query: {
            key: { $key_type : <key> },
            type: { "prim" : $key_prim }
        }
        $key_type: Provided key encoding, e.g. "string", "bytes" for hex-encoded string, "int"
        key_prim: Expected high-level data type, e.g. "address", "nat", "mutez" (see storage section in code)
        :return: Micheline expression
        """
        return self._post(json=query)


class ContextRawBytesQuery(RpcQuery, path='/chains/{}/blocks/{}/context/raw/bytes'):

    def __init__(self, *args, **kwargs):
        kwargs.update(timeout=60)
        super(ContextRawBytesQuery, self).__init__(*args, **kwargs)

    def __call__(self, depth=1) -> dict:
        """
        Return the raw context.
        :param depth: Context is a tree structure, default depth is 1
        """
        return super(ContextRawBytesQuery, self).__call__(depth=depth)


class ContextRawJsonQuery(RpcQuery, path='/chains/{}/blocks/{}/context/raw/json'):

    def __init__(self, *args, **kwargs):
        kwargs.update(timeout=60)
        super(ContextRawJsonQuery, self).__init__(*args, **kwargs)


class ContextSeedQuery(RpcQuery, path='/chains/{}/blocks/{}/context/seed'):

    def post(self):
        """
        Get seed of the cycle to which the block belongs.
        """
        return self._post()


class EndorsingPower(RpcQuery, path='/chains/{}/blocks/{}/endorsing_power'):

    def post(self, endorsement_operation):
        """
        Get the endorsing power of an endorsement operation, that is, the number of slots that the op has
        :param endorsement_operation:
        { "branch": $block_hash,
        "contents": [ $operation.alpha.contents ... ],
        "signature": $Signature }
        """
        return self._post({'sendorsement_operation': endorsement_operation})


class OperationListListQuery(RpcQuery, path=['/chains/{}/blocks/{}/operations']):

    def __getitem__(self, item):
        """
        Find operation by hash
        :param item: Operation group hash (base58)
        :return: OperationQuery
        """
        if isinstance(item, tuple):
            return self[item[0]][item[1]]

        if isinstance(item, str) and is_ogh(item):
            operation_hashes = self._parent.operation_hashes()

            def find_index():
                for i, validation_pass in enumerate(operation_hashes):
                    for j, og_hash in enumerate(validation_pass):
                        if og_hash == item:
                            return i, j
                raise StopIteration('Operation group hash not found')

            return self[find_index()]

        return super(OperationListListQuery, self).__getitem__(item)

    @property
    def endorsements(self):
        """
        Operations with content of type: `endorsement`
        :return: OperationListQuery
        """
        return self[0]

    @property
    def votes(self):
        """
        Operations with content of type: `proposal`, `ballot`
        :return: OperationListQuery
        """
        return self[1]

    @property
    def anonymous(self):
        """
        Operations with content of type: `seed_nonce_revelation`, `double_endorsement_evidence`,
            `double_baking_evidence`, `activate_account`
        :return: OperationListQuery
        """
        return self[2]

    @property
    def managers(self):
        """
        Operations with content of type: `reveal`, `transaction`, `origination`, `delegation`
        :return: OperationListQuery
        """
        return self[3]

    def find_upvotes(self, proposal_id) -> list:
        """
        Find operations of kind `proposal` for given proposal
        :param proposal_id: Proposal hash (base58)
        """
        def is_upvote(op):
            return any(map(
                lambda x: x['kind'] == 'proposal' and proposal_id in x.get('proposals', []),
                op['contents']))
        return list(filter(is_upvote, self.votes()))

    def find_ballots(self, proposal_id=None) -> list:
        """
        Find operations of kind `ballot`
        :param proposal_id: Proposal hash (optional)
        """
        def is_ballot(op):
            return any(map(
                lambda x: x['kind'] == 'ballot' and (proposal_id is None or proposal_id == x.get('proposal')),
                op['contents']))
        return list(filter(is_ballot, self.votes()))

    def find_origination(self, contract_id):
        """
        Find origination of the contract.
        :param contract_id: Contract ID (KT-address)
        """
        def is_origination(op):
            def is_it(x):
                return x['kind'] == 'origination' \
                       and contract_id in x['metadata']['operation_result']['originated_contracts']
            return any(map(is_it, op['contents']))
        return next(filter(is_origination, self.managers()))


class OperationQuery(RpcQuery, path=['/chains/{}/blocks/{}/operations/{}/{}']):

    def unsigned(self) -> dict:
        """
        Get operation group data without metadata and signature.
        """
        data = self()
        return {
            'branch': data['branch'],
            'contents': [
                {k: v for k, v in content.items() if k != 'metadata'}
                for content in data['contents']
            ]
        }


class ProposalQuery(RpcQuery, path='/chains/{}/blocks/{}/votes/proposals/{}'):

    def __call__(self) -> int:
        """
        Roll count for this proposal.
        """
        proposals = self._parent()
        proposal_id = self._params[-1]
        roll_count = next((x[1] for x in proposals if x[0] == proposal_id), 0)
        return roll_count


class ProposalsQuery(RpcQuery, path='/chains/{}/blocks/{}/votes/proposals'):

    def __getitem__(self, proposal_id) -> ProposalQuery:
        """
        Roll count for the selected proposal
        :param proposal_id: Base58-encoded proposal ID
        :return: ProposalQuery
        """
        return ProposalQuery(
            path=self._wild_path + '/{}',
            params=self._params + [proposal_id],
            node=self.node
        )

    def __repr__(self):
        res = [
            super(ProposalsQuery, self).__repr__(),
            f'[]{get_attr_docstring(self.__class__, "__getitem__")}',
        ]
        return '\n'.join(res)
