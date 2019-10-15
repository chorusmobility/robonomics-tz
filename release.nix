{ pkgs ? import (builtins.fetchTarball https://github.com/airalab/airapkgs/archive/nixos-unstable.tar.gz) { }
}:

rec {
  ros_tutorials = pkgs.callPackage ./ros_tutorials.nix { };
  package = pkgs.callPackage ./default.nix { inherit ros_tutorials; };
}
