# DO NOT RUN IT AS A SCRIPT!
# Copy and paste line by line into shell
# For documentation purpose only
from pytezos import pytezos

SECRET_KEY = "" # don't forget to insert a secret key
CONTRACT_ADDRESS = "KT1CkArDT3YjY6GJFuxjhqeY6pBkyQZ2MVA2"

mnet = pytezos.using(key=SECRET_KEY, shell="mainnet")
ci = mnet.contract(CONTRACT_ADDRESS)

### Calling demand()
ci.demand(order_model="63", order_objective="63", order_cost=5).operation_group.sign().inject()

# Response:
# {
#    'chain_id':'NetXdQprcVkpaWU',
#    'hash':'opSBGhRn5ftmQaUnZQTZCTx1NUjGa5XPm7BVSzWT9L6mw4c2ahd',
#    'protocol':'PsBabyM1eUXZseaJdmXFApDSBqj8YBfwELoxZHHW77EMcAbbwAS',
#    'branch':'BLEprQFdYU5KkqbLs8jhNZtAogLnP6Jc8iJVhzTbsUaTB7M8hoe',
#    'contents':[
#       {
#          'kind':'transaction',
#          'source':'tz1i2DjzrA5rtzSWeUHpoevnTZuv3WC2hvMK',
#          'fee':'40298',
#          'counter':'2333835',
#          'gas_limit':'400000',
#          'storage_limit':'60000',
#          'amount':'0',
#          'destination':'KT1CkArDT3YjY6GJFuxjhqeY6pBkyQZ2MVA2',
#          'parameters':{
#             'entrypoint':'demand',
#             'value':{
#                'prim':'Pair',
#                'args':[
#                   {
#                      'bytes':'63'
#                   },
#                   {
#                      'prim':'Pair',
#                      'args':[
#                         {
#                            'bytes':'63'
#                         },
#                         {
#                            'int':'1'
#                         }
#                      ]
#                   }
#                ]
#             }
#          }
#       }
#    ],
#    'signature':'sigetA79oZqn2Rworst4Cpn59wEHc1aTvrRCh7iH4hQhTjAuA6t9RshZie8BEXjp2GJCocPFqV3d3iZrhe5Zw8bfNTbPK2Xz'
# }

### Calling offer()
ci.offer(order_model="63", order_objective="63", order_cost=1).operation_group.sign().inject()

# Response
# {
#    'chain_id':'NetXdQprcVkpaWU',
#    'hash':'opSBGhRn5ftmQaUnZQTZCTx1NUjGa5XPm7BVSzWT9L6mw4c2ahd',
#    'protocol':'PsBabyM1eUXZseaJdmXFApDSBqj8YBfwELoxZHHW77EMcAbbwAS',
#    'branch':'BLEprQFdYU5KkqbLs8jhNZtAogLnP6Jc8iJVhzTbsUaTB7M8hoe',
#    'contents':[
#       {
#          'kind':'transaction',
#          'source':'tz1i2DjzrA5rtzSWeUHpoevnTZuv3WC2hvMK',
#          'fee':'40298',
#          'counter':'2333835',
#          'gas_limit':'400000',
#          'storage_limit':'60000',
#          'amount':'0',
#          'destination':'KT1CkArDT3YjY6GJFuxjhqeY6pBkyQZ2MVA2',
#          'parameters':{
#             'entrypoint':'demand',
#             'value':{
#                'prim':'Pair',
#                'args':[
#                   {
#                      'bytes':'63'
#                   },
#                   {
#                      'prim':'Pair',
#                      'args':[
#                         {
#                            'bytes':'63'
#                         },
#                         {
#                            'int':'1'
#                         }
#                      ]
#                   }
#                ]
#             }
#          }
#       }
#    ],
#    'signature':'sigetA79oZqn2Rworst4Cpn59wEHc1aTvrRCh7iH4hQhTjAuA6t9RshZie8BEXjp2GJCocPFqV3d3iZrhe5Zw8bfNTbPK2Xz'
# }

op = mnet.shell.blocks[-20:].find_operation('opSBGhRn5ftmQaUnZQTZCTx1NUjGa5XPm7BVSzWT9L6mw4c2ahd')

# {
#    'protocol':'PsBabyM1eUXZseaJdmXFApDSBqj8YBfwELoxZHHW77EMcAbbwAS',
#    'chain_id':'NetXdQprcVkpaWU',
#    'hash':'opSBGhRn5ftmQaUnZQTZCTx1NUjGa5XPm7BVSzWT9L6mw4c2ahd',
#    'branch':'BLEprQFdYU5KkqbLs8jhNZtAogLnP6Jc8iJVhzTbsUaTB7M8hoe',
#    'contents':[
#       {
#          'kind':'transaction',
#          'source':'tz1i2DjzrA5rtzSWeUHpoevnTZuv3WC2hvMK',
#          'fee':'40298',
#          'counter':'2333835',
#          'gas_limit':'400000',
#          'storage_limit':'60000',
#          'amount':'0',
#          'destination':'KT1CkArDT3YjY6GJFuxjhqeY6pBkyQZ2MVA2',
#          'parameters':{
#             'entrypoint':'demand',
#             'value':{
#                'prim':'Pair',
#                'args':[
#                   {
#                      'bytes':'63'
#                   },
#                   {
#                      'prim':'Pair',
#                      'args':[
#                         {
#                            'bytes':'63'
#                         },
#                         {
#                            'int':'1'
#                         }
#                      ]
#                   }
#                ]
#             }
#          },
#          'metadata':{
#             'balance_updates':[
#                {
#                   'kind':'contract',
#                   'contract':'tz1i2DjzrA5rtzSWeUHpoevnTZuv3WC2hvMK',
#                   'change':'-40298'
#                },
#                {
#                   'kind':'freezer',
#                   'category':'fees',
#                   'delegate':'tz1XfAjZyaLdceHnZxbMYop7g7kWKPut4PR7',
#                   'cycle':169,
#                   'change':'40298'
#                }
#             ],
#             'operation_result':{
#                'status':'applied',   # <-- operation result!
#                'storage':{
#                   'prim':'Pair',
#                   'args':[
#                      [
#                         {
#                            'prim':'Elt',
#                            'args':[
#                               {
#                                  'bytes':'9275387b3780c5933e0ac5f1c0e65df616e311d54246004625aac59dd5853e1a'
#                               },
#                               {
#                                  'prim':'Pair',
#                                  'args':[
#                                     {
#                                        'prim':'Pair',
#                                        'args':[
#                                           {
#                                              'bytes':'63'
#                                           },
#                                           {
#                                              'prim':'Pair',
#                                              'args':[
#                                                 {
#                                                    'bytes':'63'
#                                                 },
#                                                 {
#                                                    'int':'1'
#                                                 }
#                                              ]
#                                           }
#                                        ]
#                                     },
#                                     {
#                                        'bytes':'0000f58524659f5f467272c570ad033ba5b2c3a3e238'
#                                     }
#                                  ]
#                               }
#                            ]
#                         }
#                      ],
#                      {
#                         'prim':'Pair',
#                         'args':[
#                            [
#
#                            ],
#                            [
#
#                            ]
#                         ]
#                      }
#                   ]
#                },
#                'balance_updates':[
#                   {
#                      'kind':'contract',
#                      'contract':'tz1i2DjzrA5rtzSWeUHpoevnTZuv3WC2hvMK',
#                      'change':'-86000'
#                   }
#                ],
#                'consumed_gas':'93181',
#                'storage_size':'4634',
#                'paid_storage_size_diff':'86'
#             }
#          }
#       }
#    ],
#    'signature':'sigetA79oZqn2Rworst4Cpn59wEHc1aTvrRCh7iH4hQhTjAuA6t9RshZie8BEXjp2GJCocPFqV3d3iZrhe5Zw8bfNTbPK2Xz'
# }

op['contents'][0]['metadata']['operation_result']['status']
