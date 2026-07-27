import os, time, math, logging
from datetime import datetime
from binance.client import Client
from dotenv import load_dotenv

logging.basicConfig(filename="bot.log", level=logging.INFO, format="%(asctime)s | %(message)s")
LG = logging.getLogger()

class BotTrading:
    def __init__(self, cfg=None):
        self.cfg = cfg or {}
        self.carregar_config(self.cfg)
        self.rodando = False
        self.saldo_atual = 0.0
        self.total_operacoes = 0
        self.historico = []
        self.regras = {}
        self.callback_notificacao = None
        load_dotenv()
        self.api_key = self.cfg.get("api_key") or os.getenv("BINANCE_API_KEY","")
        self.api_secret = self.cfg.get("api_secret") or os.getenv("BINANCE_API_SECRET","")
        self.cli = None
        if self.api_key and self.api_secret:
            try:
                self.cli = Client(self.api_key, self.api_secret)
                try: self.cli.futures_change_position_mode(dualSidePosition=False)
                except: pass
                self.carregar_regras()
                LG.info("✅ Bot carregado")
            except Exception as e:
                LG.error(f"❌ Conexao: {e}")

    def carregar_config(self, cfg):
        self.risco = float(cfg.get("risco", 0.05))
        self.alv_ini = int(cfg.get("alv_ini", 10))
        self.alv_max = int(cfg.get("alv_max", 125))
        self.excluir = cfg.get("excluir", ["BTCUSDT","ETHUSDT","SOLUSDT"])
        self.min_not = float(cfg.get("min_not", 5.0))
        self.intervalo = int(cfg.get("intervalo", 30))

    def carregar_regras(self):
        try:
            info = self.cli.futures_exchange_info()
            for s in info["symbols"]:
                if s["quoteAsset"]!="USDT": continue
                pq, mn = 0, 0.0
                for f in s["filters"]:
                    if f["filterType"]=="LOT_SIZE":
                        st=float(f["stepSize"]); pq=max(0,int(round(-math.log10(st),0))); mn=float(f["minQty"])
                self.regras[s["symbol"]]={"pq":pq,"mn":mn,"alv_max":min(int(s.get("maxLeverage",125)),self.alv_max)}
        except: pass

    def saldo_real(self):
        try:
            self.saldo_atual = float(self.cli.futures_account()["availableBalance"])
            return self.saldo_atual
        except: return 0.0

    def ema(self,p,pr):
        e=sum(p[:pr])/pr; m=2/(pr+1)
        for x in p[pr:]: e=x*m+e*(1-m)
        return e

    def rsi(self,p,pr=14):
        g,zz=[],[]
        for i in range(1,len(p)):
            d=p[i]-p[i-1]; g.append(d if d>0 else 0); zz.append(-d if d<0 else 0)
        mg=sum(g[-pr:])/pr; mp=sum(zz[-pr:])/pr
        if mp==0: return 100
        return 100-100/(1+mg/mp)

    def sinal(self,par):
        try:
            v=self.cli.futures_klines(symbol=par,interval="1h",limit=100)
            f=[float(x[4]) for x in v]; pr=f[-1]
            e20,e50=self.ema(f,20),self.ema(f,50); r=self.rsi(f)
            sc,dr=0,0
            if pr>e20 and e20>e50: sc,dr=1,1
            elif pr<e20 and e20<e50: sc,dr=1,-1
            if r<30: sc+=1
            if r>70: sc+=1
            return sc,dr,pr
        except: return 0,0,0

    def abrir(self,par,dr,pr):
        if par not in self.regras: return False
        r=self.regras[par]; pq=r["pq"]; mn=r["mn"]; am=r["alv_max"]
        sd=self.saldo_real()
        if sd<1: return False
        vr=sd*self.risco
        alvs=[]; a=self.alv_ini
        while a<=am: alvs.append(a); a+=5 if a<50 else 10
        for alv in alvs:
            try:
                self.cli.futures_change_leverage(symbol=par,leverage=alv)
                q=(vr*alv)/pr
                va=q*pr
                if va<self.min_not: q*=(self.min_not*1.03)/va
                q=round(q,pq)
                if q<mn: q=mn
                if q*pr<self.min_not: continue
                LG.info(f"🔄 {par} {alv}x Qtd={q}")
                if dr==1: self.cli.futures_create_order(symbol=par,type="MARKET",side="BUY",quantity=q)
                else: self.cli.futures_create_order(symbol=par,type="MARKET",side="SELL",quantity=q)
                self.historico.append({"par":par,"dir":dr,"alv":alv,"preco":pr,"qtd":q,"hora":datetime.now().strftime("%d/%m %H:%M"),"aberta":True})
                self.total_operacoes+=1
                txt=f"{'COMPRA' if dr==1 else 'VENDA'} {par} {alv}x ${pr:.6f}"
                LG.info(f"✅✅✅ {txt}")
                if self.callback_notificacao: self.callback_notificacao("ENTRADA REAL ABERTA!", txt)
                return True
            except Exception as e:
                LG.warning(f"⚠️ {par} {alv}x: {str(e)[:60]}")
        return False

    def iniciar(self):
        if not self.cli: LG.error("❌ Sem conexao Binance"); return
        self.rodando=True
        LG.info("🚀 BOT INICIADO VIA APP")
        pares=[p for p in self.regras if p not in self.excluir]
        while self.rodando:
            LG.info("🔍 Buscando oportunidades...")
            tops=[]
            for p in pares:
                sc,dr,pr=self.sinal(p)
                if sc>=2: tops.append((-sc,p,dr,pr))
            if tops:
                tops.sort(); _,p,dr,pr=tops[0]
                LG.info(f"🎯 SINAL: {p}")
                ok=self.abrir(p,dr,pr)
                if ok: time.sleep(180)
            for _ in range(self.intervalo):
                if not self.rodando: break
                time.sleep(1)
        LG.info("🛑 BOT PARADO")

    def parar(self):
        self.rodando=False
