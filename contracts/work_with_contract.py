from pytezos import pytezos

SECRET_KEY = "" # don't forget to insert a secret key
CONTRACT_ADDRESS = "KT1CkArDT3YjY6GJFuxjhqeY6pBkyQZ2MVA2"

mnet = pytezos.using(key=SECRET_KEY, shell="mainnet")
ci = mnet.contract(CONTRACT_ADDRESS)
