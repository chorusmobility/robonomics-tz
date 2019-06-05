type order = {
  order_model     : bytes;
  order_objective : bytes;
  order_cost      : nat;
}

type message = {
  message_order     : order;
  message_sender    : key;
  message_signature : signature;
}

type report = {
  report_ix        : nat;
  report_data      : bytes;
  report_sender    : key;
  report_signature : signature;
}

type liability = {
  liability_params   : order;
  liability_promisee : key_hash;
  liability_promisor : key_hash;
  liability_report   : bytes option;
}

type storage = (nat, liability) map

let check_sender hash sender signature =
  if not (Crypto.check sender signature hash) then
    failwith "Wrong message signature"
  else
    Crypto.hash_key sender

let hash_order o = Crypto.sha256 (
    Bytes.concat [
      Crypto.sha256 o.order_model;
      Crypto.sha256 o.order_objective;
      Crypto.sha256 (Bytes.pack o.order_cost);
    ]
  )

let hash_report r = Crypto.sha256 (
    Bytes.concat [
      Crypto.sha256 (Bytes.pack r.report_ix);
      Crypto.sha256 r.report_data;
    ]
  ) 

let check_order_sender m =
  check_sender (hash_order m.message_order) m.message_sender m.message_signature

let check_report_sender m =
  check_sender (hash_report m) m.report_sender m.report_signature 

let%init storage = Map

let%entry create ((demand : message), (offer : message)) storage =
  if hash_order demand.message_order <> hash_order offer.message_order then
    failwith "Demand/Offer mismatch"
  else
    let (promisee, promisor) = (check_order_sender demand, check_order_sender offer) in
    let liability = {
      liability_params = demand.message_order;
      liability_promisee = promisee;
      liability_promisor = promisor;
      liability_report = None;
    } in [], Map.add (Map.size storage) liability storage

let%entry finalize msg storage =
  let promisor = check_report_sender msg in
  match Map.find msg.report_ix storage with
  | None -> failwith "Wrong liability ix"
  | Some l ->
      if promisor <> l.liability_promisor then
        failwith "Wrong report signer"
      else
        let l = l.liability_report <- Some msg.report_data in
        [], Map.update msg.report_ix (Some l) storage
