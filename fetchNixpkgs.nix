{ rev    ? "7618e2b48902bc2adc4c06629b2704d5c7e89c15"             # The Git revision of nixpkgs to fetch
, sha256 ? "1ms6i7ksml9cri6vw3sxxfxw16nj2z1qiggj4jk76vjwaks9198m" # The SHA256 of the downloaded data
}:

builtins.fetchTarball {
  url = "https://github.com/airalab/airapkgs/archive/${rev}.tar.gz";
  inherit sha256;
}
