{ nixpkgs ? import ./fetchNixpkgs.nix { }
, system ? builtins.currentSystem
}:

let
  pkgs = import nixpkgs { inherit system; };

in rec {
  ros_tutorials = pkgs.callPackage ./ros_tutorials.nix { };
  package = pkgs.callPackage ./default.nix { inherit ros_tutorials; };
}
