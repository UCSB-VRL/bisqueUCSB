{ pkgs ? import <nixpkgs> {} }:

pkgs.mkShell {
  packages = with pkgs; [
    k3d
    kubectl
    kubernetes-helm
    kustomize
    kubeconform
    docker
    curl
    jq
    yq-go
  ];

  shellHook = ''
    echo "BisQue k3d example shell"
    echo "Run: source ./env.example"
    echo "Docker daemon must be running."
  '';
}
