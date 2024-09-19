{
  description = "pukiwiki-to-growi";

  inputs = {
    nixpkgs = { url = "github:NixOS/nixpkgs/nixpkgs-unstable"; };
    flake-utils = { url = "github:numtide/flake-utils"; };
  };

  outputs = inputs@{ self, nixpkgs, flake-utils, ... }:
    flake-utils.lib.eachDefaultSystem (system:
      let
        inherit (nixpkgs.lib) optional;
        pkgs = import nixpkgs { inherit system; };

        pandoc-py = pkgs.callPackage ./nix/pandoc-python { };
      in
      {
        devShell = pkgs.mkShell {
          buildInputs = with pkgs; [
            pandoc
            pandoc-py
            python310
            python310Packages.black
          ];
        };
      });
}
