{ stdenv
, mavros
, mkRosPackage
, ros_tutorials
, python3Packages
, pkgs
}:

mkRosPackage rec {
  name = "${pname}-${version}";
  pname = "robonomics_tz";
  version = "master";

  src = ./.;

  propagatedBuildInputs = with python3Packages;
  [ ros_tutorials mavros
    simplejson pysodium fastecdsa pyblake2 base58
    secp256k1 requests pendulum ply tqdm loguru mnemonic pkgs.qt5.full ];

  meta = with stdenv.lib; {
    description = "Robonomics on Tezos";
    homepage = http://github.com/akru/robonomics_tz;
    license = licenses.mit;
    maintainers = [ maintainers.akru ];
  };
}
