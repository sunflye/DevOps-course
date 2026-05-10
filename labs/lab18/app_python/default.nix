{ pkgs ? import (fetchTarball "https://github.com/NixOS/nixpkgs/archive/23.11.tar.gz") {} }:

pkgs.python311.pkgs.buildPythonApplication {
  pname = "devops-info-service";
  version = "1.0.0";

  src = ./.;

  propagatedBuildInputs = with pkgs.python311.pkgs; [
    flask
    prometheus-client
  ];

  # Говорим Nix, что это не стандартный пакет с setup.py
  format = "other";

  # Указываем, как "установить" наше приложение
  installPhase = ''
    mkdir -p $out/bin
    cp app.py $out/bin/devops-info-service
    chmod +x $out/bin/devops-info-service
  '';

  doCheck = false;
}