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

let hash_order o = Crypto.sha256 (
    Bytes.concat [
      Crypto.sha256 o.model;
      Crypto.sha256 o.objective;
      Crypto.sha256 (Bytes.pack o.cost);
    ]
  )

let check_sender m =
  let encoded = encode_order m.lot in
  if not (Crypto.check m.sender m.signature encoded) then
    failwith "Wrong message signature"
  else
    Crypto.hash_key m.sender 

(* Main *)

let%entry main ((demand : message), (offer : message)) storage =
  if hash_order demand.lot <> hash_order offer.lot then 
    failwith "Demand/Offer mismatch"
  else
    let (promisee, promisor) = (check_sender demand, check_sender offer) in
    let liability = { params = demand.lot; promisee; promisor; result = None; } in
    ([], liability :: storage)
