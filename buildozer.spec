      - name: Conserta bug do Buildozer
        run: |
          python3 << 'PYEOF'
          import os, re
          caminho = os.path.expanduser("~/.local/lib/python3.10/site-packages/buildozer/__init__.py")
          with open(caminho, "r") as f:
              conteudo = f.read()

          funcao_nova = '''    def download(self, url, filename, report_hook):
        import requests
        print("Downloading " + url)
        resp = requests.get(url, stream=True, timeout=600)
        resp.raise_for_status()
        total = int(resp.headers.get("content-length", 0))
        baixado = 0
        with open(filename, "wb") as arq:
            for parte in resp.iter_content(chunk_size=65536):
                if parte:
                    arq.write(parte)
                    baixado += len(parte)
                    if report_hook:
                        try:
                            report_hook(baixado // 65536, 65536, total)
                        except Exception:
                            pass
        return filename
'''
          padrao = re.compile(r'    def download\(self, url, filename, report_hook\):.*?(?=\n    def |\nclass |\Z)', re.DOTALL)
          novo = padrao.sub(funcao_nova, conteudo, count=1)

          with open(caminho, "w") as f:
              f.write(novo)

          if "requests.get" in open(caminho).read():
              print("BUG CONSERTADO COM SUCESSO")
          else:
              print("ERRO AO CONSERTAR BUG")
              raise SystemExit(1)
          PYEOF
