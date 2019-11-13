from os.path import basename, dirname, join, exists, expanduser
from pprint import pformat

from pytezos.operation.result import OperationResult
from pytezos.michelson.contract import Contract
from pytezos.michelson.converter import convert
from pytezos.michelson.micheline import skip_nones
from pytezos.michelson.formatter import micheline_to_michelson
from pytezos.operation.group import OperationGroup
from pytezos.operation.content import format_mutez
from pytezos.interop import Interop
from pytezos.tools.docstring import get_class_docstring


class ContractCallResult(OperationResult):

    @classmethod
    def from_contract_call(cls, operation_group: dict, address, contract: Contract):
        results = cls.from_operation_group(operation_group, kind='transaction', destination=address)
        assert len(results) == 1, results
        result = results[0]

        return cls(
            parameters=contract.parameter.decode(data=result.parameters),
            storage=contract.storage.decode(result.storage),
            big_map_diff=contract.storage.big_map_diff_decode(result.big_map_diff),
            operations=result.operations
        )

    @classmethod
    def from_code_run(cls, code_run: dict, parameters, contract: Contract):
        return cls(
            parameters=contract.parameter.decode(parameters),
            storage=contract.storage.decode(code_run['storage']),
            big_map_diff=contract.storage.big_map_diff_decode(code_run.get('big_map_diff', [])),
            operations=code_run.get('operations', [])
        )


class ContractCall(Interop):

    def __init__(self, parameters,
                 address=None, contract: Contract = None, factory=Contract, amount=0, shell=None, key=None):
        super(ContractCall, self).__init__(shell=shell, key=key)
        self.parameters = parameters
        self.address = address
        self.amount = amount

        if contract is None:
            assert address is not None
            contract = factory.from_micheline(self.shell.contracts[address].code())

        self.contract = contract

    def _spawn(self, **kwargs):
        return ContractCall(
            parameters=self.parameters,
            address=self.address,
            contract=self.contract,
            amount=kwargs.get('amount', self.amount),
            shell=kwargs.get('shell', self.shell),
            key=kwargs.get('key', self.key)
        )

    def __repr__(self):
        res = [
            super(ContractCall, self).__repr__(),
            f'.address  # {self.address}',
            f'.amount  # {self.amount}',
            '\nParameters',
            pformat(self.parameters),
            '\nHelpers',
            get_class_docstring(self.__class__)
        ]
        return '\n'.join(res)

    def with_amount(self, amount):
        """
        Send funds to the contract too.
        :param amount: amount in microtez (int) or tez (Decimal)
        :return: ContractCall
        """
        return self._spawn(amount=amount)

    @property
    def operation_group(self) -> OperationGroup:
        """
        Show generated operation group.
        :return: OperationGroup
        """
        return OperationGroup(shell=self.shell, key=self.key) \
            .transaction(destination=self.address,
                         amount=self.amount,
                         parameters=self.parameters) \
            .fill()

    def inject(self):
        """
        Autofill, sign and inject resulting operation group.
        """
        return self.operation_group.autofill().sign().inject()

    def cmdline(self):
        """
        Generate command line for tezos client.
        :return: str
        """
        arg = micheline_to_michelson(self.parameters['value'], inline=True)
        source = self.key.public_key_hash()
        amount = format_mutez(self.amount)
        entrypoint = self.parameters['entrypoint']
        return f'transfer {amount} from {source} to {self.address} "' \
               f'--entrypoint "{entrypoint}" --arg "{arg}"'

    def result(self, storage=None, source=None, sender=None, gas_limit=None):
        """
        Simulate operation and parse the result.
        :param storage: Python object only. If storage is specified, `run_code` is called instead of `run_operation`.
        :param source: Can be specified for unit testing purposes
        :param sender: Can be specified for unit testing purposes,
        see https://tezos.gitlab.io/whitedoc/michelson.html#operations-on-contracts for the difference
        :param gas_limit: Specify gas limit (default is gas hard limit)
        :return: ContractCallResult
        """
        chain_id = self.shell.chains.main.chain_id()
        if storage is not None:
            query = skip_nones(
                script=self.contract.code,
                storage=self.contract.storage.encode(storage),
                entrypoint=self.parameters['entrypoint'],
                input=self.parameters['value'],
                amount=format_mutez(self.amount),
                chain_id=chain_id,
                source=sender,
                payer=source,
                gas=gas_limit
            )
            code_run_res = self.shell.head.helpers.scripts.run_code.post(query)
            return ContractCallResult.from_code_run(
                code_run_res, parameters=self.parameters, contract=self.contract)
        else:
            opg_with_metadata = self.operation_group.fill().run()
            return ContractCallResult.from_contract_call(
                opg_with_metadata, address=self.address, contract=self.contract)

    def view(self):
        """
        Get return value of a view method.
        :return: object
        """
        opg_with_metadata = self.operation_group.fill().run()
        view_operation = OperationResult.get_contents(opg_with_metadata, source=self.address)[0]
        view_contract = Contract.from_micheline(self.shell.contracts[view_operation['destination']].code())
        return view_contract.parameter.decode(view_operation['parameters'])


class ContractEntrypoint(Interop):

    def __init__(self, name, address=None, contract: Contract = None, factory=Contract, shell=None, key=None):
        super(ContractEntrypoint, self).__init__(shell=shell, key=key)
        if contract is None:
            assert address is not None
            code = self.shell.contracts[address].code()
            contract = factory.from_micheline(code)

        self.contract = contract
        self.name = name
        self.address = address

    def _spawn(self, **kwargs):
        return ContractEntrypoint(
            name=self.name,
            contract=self.contract,
            address=self.address,
            shell=kwargs.get('shell', self.shell),
            key=kwargs.get('key', self.key),
        )

    def __repr__(self):
        res = [
            super(ContractEntrypoint, self).__repr__(),
            f'.address  # {self.address}',
            f'\n{self.__doc__}'
        ]
        return '\n'.join(res)

    def __call__(self, *args, **kwargs):
        if args:
            if len(args) == 1:
                data = args[0]
            else:
                data = list(args)
        elif kwargs:
            data = kwargs
        else:
            data = []

        if self.name:
            data = {self.name: data} if data else self.name

        parameters = self.contract.parameter.encode(data)
        return ContractCall(
            parameters=parameters,
            address=self.address,
            contract=self.contract,
            shell=self.shell,
            key=self.key,
        )


class ContractInterface(Interop):
    __default_entry__ = 'call'

    def __init__(self, address=None, contract: Contract = None, factory=Contract, shell=None, key=None):
        super(ContractInterface, self).__init__(shell=shell, key=key)
        if contract is None:
            assert address is not None
            code = self.shell.contracts[address].code()
            contract = factory.from_micheline(code)

        self.contract = contract
        self.address = address

        for entry_name, docstring in contract.parameter.entries(default=self.__default_entry__):
            entry_point = ContractEntrypoint(
                name=entry_name if entry_name != self.__default_entry__ else None,
                address=self.address,
                contract=contract,
                shell=self.shell,
                key=self.key
            )
            entry_point.__doc__ = docstring
            setattr(self, entry_name, entry_point)

    def _spawn(self, **kwargs):
        return ContractInterface(
            address=self.address,
            contract=self.contract,
            shell=kwargs.get('shell', self.shell),
            key=kwargs.get('key', self.key)
        )

    def __repr__(self):
        entrypoints, _ = zip(*self.contract.parameter.entries(default=self.__default_entry__))
        res = [
            super(ContractInterface, self).__repr__(),
            f'.address  # {self.address}',
            '\nEntrypoints',
            *list(map(lambda x: f'.{x}()', entrypoints)),
            '\nHelpers',
            get_class_docstring(self.__class__,
                                attr_filter=lambda x: not x.startswith('_') and x not in entrypoints)
        ]
        return '\n'.join(res)

    @classmethod
    def create_from(cls, source, shell=None, factory=Contract):
        if isinstance(source, str) and exists(expanduser(source)):
            contract = factory.from_file(source)
        else:
            contract = factory(convert(source, output='micheline'))

        return ContractInterface(contract=contract, shell=shell)

    def big_map_get(self, path, block_id='head'):
        """
        Get BigMap entry as Python object by plain key and block height
        :param path: Json path to the key (or just key to access default BigMap location)
        :param block_id: Block height / hash / offset to use, default is `head`
        :return: object
        """
        key = basename(path)
        big_map_path = dirname(path)
        big_map_path = join('/', big_map_path) if big_map_path else None
        query = self.contract.storage.big_map_query(key, big_map_path)
        value = self.shell.blocks[block_id].context.contracts[self.address].big_map_get.post(query)
        return self.contract.storage.big_map_decode(value, big_map_path)

    def storage(self, block_id='head'):
        """
        Get storage as Pythons object at specified block height.
        :param block_id: Block height / hash / offset to use, default is `head`
        :return: object
        """
        storage = self.shell.blocks[block_id].context.contracts[self.address].storage()
        return self.contract.storage.decode(storage)

    def operation_result(self, operation_group: dict) -> ContractCallResult:
        """
        Get operation parameters, storage and big_map_diff as Python objects.
        Can locate operation inside operation groups with multiple contents and/or internal operations.
        :param operation_group: {'branch', 'protocol', 'contents', 'signature'}
        :return: ContractCallResult
        """
        return ContractCallResult.from_contract_call(
            operation_group, address=self.address, contract=self.contract)

    def manager(self):
        """
        Get contract manager address (tz)
        :return: str
        """
        return self.shell.block.context.contracts[self.address].manager()
