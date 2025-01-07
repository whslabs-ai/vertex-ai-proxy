let
  pkgs = import <nixpkgs> {};
in
  pkgs.mkShell {
    packages = [
      pkgs.black
      (pkgs.python3.withPackages (ps: [
        ps.fastapi
        ps.google-auth
        ps.httpx
        ps.pydantic
        ps.requests
        ps.uvicorn
      ]))
    ];
  }