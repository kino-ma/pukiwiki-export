{ pkgs, ... }:

let
  pname = "pandoc";
  version = "2.4";
in

pkgs.python310Packages.buildPythonPackage {
  inherit pname version;
  src = pkgs.fetchPypi {
    inherit pname version;
    sha256 = "sha256-7NH4y7f0GAxrXbShenwadN9RmZX18Ybvgc5yqcvQ3Zo=";
  };

  propagatedBuildInputs = with pkgs.python310Packages; [
    pkgs.pandoc
    plumbum
    ply
  ];

  doCheck = false;
}
