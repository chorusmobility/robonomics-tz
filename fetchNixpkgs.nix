{ rev    ? "0d0826481c1e3329ae034c3fe1c3dec55af56d66"             # The Git revision of nixpkgs to fetch
, sha256 ? "1rvp3d779f0i17qlla1jwdp21237h0pxx1p5h8g7nvm72z46bag8" # The SHA256 of the downloaded data
}:

builtins.fetchTarball {
  url = "https://github.com/airalab/airapkgs/archive/${rev}.tar.gz";
  inherit sha256;
}
