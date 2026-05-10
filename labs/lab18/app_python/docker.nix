{ pkgs ? import (fetchTarball "https://github.com/NixOS/nixpkgs/archive/23.11.tar.gz") {} }:

let
  app = pkgs.callPackage ./default.nix {};
in
pkgs.dockerTools.buildImage {
  name = "devops-info-service-nix";
  tag = "1.0.0";

  copyToRoot = [ app ];

  config = {
    Cmd = [ "${app}/bin/devops-info-service" ];
    Env = [ "DATA_DIR=/data" ];
    ExposedPorts = { "5000/tcp" = {}; };
    Volumes = { "/data" = {}; };
  };
}