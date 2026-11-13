{ pkgs ? import <nixpkgs> {} }:
pkgs.mkShell {
packages = [ pkgs.python3 pkgs.python3Packages.pillow pkgs.python3Packages.tkinter ];
}
