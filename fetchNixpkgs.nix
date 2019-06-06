{ rev    ? "98e6ca4f09c08028466e444398cef669fb40be3b"             # The Git revision of nixpkgs to fetch
, sha256 ? "0f5ivv30jqk9qswl24afi26x92j9pavqjvdrhf8cz5ina7amgzl5" # The SHA256 of the downloaded data
}:

builtins.fetchTarball {
  url = "https://github.com/airalab/airapkgs/archive/${rev}.tar.gz";
  inherit sha256;
}
