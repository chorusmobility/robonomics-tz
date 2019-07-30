type order = { 
  order_model     : bytes;
  order_objective : bytes;
  order_cost      : nat;
}

type report = {
  report_ix        : nat;
  report_data      : bytes;
}

type liability = {
  liability_params   : order;
  liability_promisee : address;
  liability_promisor : address;
  liability_report   : bytes option;
}

type storage = {
  asks  : (bytes, (order * address)) map;
  bids  : (bytes, (order * address)) map;
  deals : (nat, liability) map;
}

let hash_order o = Crypto.blake2b (
    Bytes.concat [
      Crypto.blake2b o.order_model;
      Crypto.blake2b o.order_objective;
      Crypto.blake2b (Bytes.pack o.order_cost);
    ]
  )
    
let new_liability order promisee promisor = {
  liability_params   = order;
  liability_promisee = promisee;
  liability_promisor = promisor;
  liability_report   = None;
}

let%init storage = {
  asks = Map;
  bids = Map;
  deals = Map;
}
  
let%entry demand (order : order) storage =
  let demand_hash = hash_order order in
  match Map.find demand_hash storage.bids with
  | None -> 
      [], storage.asks <- Map.add demand_hash (order, Current.sender ()) storage.asks
  | Some (_, promisor) -> 
      let liability = new_liability order (Current.sender ()) promisor in
      let storage = storage.deals <- Map.add (Map.size storage.deals) liability storage.deals in
      let storage = storage.bids <- Map.remove demand_hash storage.bids in
      [], storage
      
let%entry offer (order : order) storage =
  let offer_hash = hash_order order in
  match Map.find offer_hash storage.asks with
  | None -> 
      [], storage.bids <- Map.add offer_hash (order, Current.sender ()) storage.bids
  | Some (_, promisee) -> 
      let liability = new_liability order promisee (Current.sender ()) in
      let storage = storage.deals <- Map.add (Map.size storage.deals) liability storage.deals in
      let storage = storage.asks <- Map.remove offer_hash storage.asks in
      [], storage

let%entry finalize report storage =
  match Map.find report.report_ix storage.deals with
  | None -> failwith "Wrong liability index"
  | Some l ->
      match l.liability_report with
      | None -> failwith "Liability already finalized"
      | _ ->
          if l.liability_promisor <> Current.sender () then
            failwith "Wrong report sender"
          else
            let l = l.liability_report <- Some report.report_data in
            [], storage.deals <- Map.update report.report_ix (Some l) storage.deals
