{ stdenv
, ros_comm
, mkRosPackage
, python3Packages
, python3
, libsodium
}:

mkRosPackage rec {
  name = "${pname}-${version}";
  pname = "robonomics_tz";
  version = "master";

  src = ./.;

  propagatedBuildInputs = with python3Packages;
  [ ros_comm secp256k1
    simplejson pysodium fastecdsa pyblake2 base58
    requests pendulum ply tqdm ];

  meta = with stdenv.lib; {
    description = "Robonomics on Tezos";
    homepage = http://github.com/akru/robonomics_tz;
    license = licenses.mit;
    maintainers = [ maintainers.akru ];
  };
}
