(* Type definitions *)

type order = { 
  model     : bytes;
  objective : bytes;
  cost      : nat;
}

type message = {
  lot       : order;
  sender    : key;
  signature : signature;
}

type liability = {
  params   : order;
  promisee : key_hash;
  promisor : key_hash;
  result   : bytes option;
}

type storage = liability list

(* Functions *)

let encode_order o =
  Bytes.concat [ o.model; o.objective; Bytes.pack o.cost]

let check_sender m =
  let encoded = encode_order m.lot in
  if not (Crypto.check m.sender m.signature encoded) then
    failwith "Wrong message signature"
  else
    Crypto.hash_key m.sender

(* Main *)

let%entry main ((demand : message), (offer : message)) storage =
  let (promisee, promisor) = (check_sender demand, check_sender offer) in
  let liability = { params = demand.lot; promisee; promisor; result = None; } in
  ([], liability :: storage)
