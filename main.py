from kivymd.app import MDApp
from kivymd.uix.screenmanager import MDScreenManager
from kivymd.uix.screen import MDScreen
from kivymd.uix.card import MDCard
from kivymd.uix.label import MDLabel
from kivymd.uix.button import MDFillRoundFlatIconButton
from kivymd.uix.textfield import MDTextField
from kivymd.uix.list import MDList, TwoLineListItem
from kivymd.uix.tab import MDTabsBase
from kivymd.uix.floatlayout import MDFloatLayout
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.toolbar import MDTopAppBar
from kivy.clock import Clock, mainthread
from kivy.core.window import Window
from kivy.utils import get_color_from_hex
from kivy.metrics import dp
from plyer import notification
import threading, json, os, sys
from bot_trading import BotTrading

COR_FUNDO = "#0B0E11"
COR_CARD = "#1E2329"
COR_PRIMARIA = "#F0B90B"
COR_SUCESSO = "#0ECB81"
COR_ERRO = "#F6465D"
COR_TEXTO = "#EAECEF"
COR_TEXTO_MUDO = "#848E9C"

Window.softinput_mode = "below_target"

class Tab(MDFloatLayout, MDTabsBase): pass

class DashboardScreen(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.app = MDApp.get_running_app()
        self.build_ui()
        Clock.schedule_interval(self.atualizar, 2)

    def build_ui(self):
        ly = MDBoxLayout(orientation="vertical", padding=dp(16), spacing=dp(12), md_bg_color=get_color_from_hex(COR_FUNDO))
        g = MDBoxLayout(orientation="horizontal", spacing=dp(8), size_hint_y=None, height=dp(100))
        self.cs=self.card("STATUS","DESLIGADO",COR_ERRO); self.cd=self.card("SALDO","$0.00",COR_PRIMARIA); self.co=self.card("OPS","0",COR_TEXTO)
        for c in [self.cs,self.cd,self.co]: g.add_widget(c)
        ly.add_widget(g)
        self.cpl = MDCard(style="outlined", radius=dp(12), padding=dp(16), size_hint_y=None, height=dp(70), md_bg_color=get_color_from_hex(COR_CARD))
        self.lpl = MDLabel(text="P/L DO DIA: $0.00", theme_text_color="Custom", text_color=get_color_from_hex(COR_SUCESSO), font_style="H5", halign="center")
        self.cpl.add_widget(self.lpl); ly.add_widget(self.cpl)
        ly.add_widget(MDLabel(text="ULTIMA OPERACAO", theme_text_color="Custom", text_color=get_color_from_hex(COR_TEXTO_MUDO), font_style="Caption"))
        self.cu = MDCard(style="outlined", radius=dp(12), padding=dp(16), size_hint_y=None, height=dp(80), md_bg_color=get_color_from_hex(COR_CARD))
        self.lu = MDLabel(text="Aguardando primeira entrada...", theme_text_color="Custom", text_color=get_color_from_hex(COR_TEXTO))
        self.cu.add_widget(self.lu); ly.add_widget(self.cu)
        self.btn = MDFillRoundFlatIconButton(text="LIGAR BOT", icon="play", font_size=dp(16), size_hint_y=None, height=dp(56), md_bg_color=get_color_from_hex(COR_SUCESSO))
        self.btn.bind(on_press=lambda x: self.app.toggle_bot())
        ly.add_widget(self.btn)
        self.add_widget(ly)

    def card(self, t, v, c):
        cd = MDCard(style="outlined", radius=dp(12), padding=dp(8), size_hint=(0.33,1), md_bg_color=get_color_from_hex(COR_CARD))
        b = MDBoxLayout(orientation="vertical")
        b.add_widget(MDLabel(text=t, theme_text_color="Custom", text_color=get_color_from_hex(COR_TEXTO_MUDO), font_style="Caption", halign="center"))
        b.add_widget(MDLabel(text=v, theme_text_color="Custom", text_color=get_color_from_hex(c), font_style="H6", halign="center"))
        cd.add_widget(b); return cd

    @mainthread
    def atualizar(self, dt):
        if not self.app.bot: return
        b=self.app.bot
        self.cd.children[0].children[0].text = f"${b.saldo_atual:.2f}"
        self.co.children[0].children[0].text = str(b.total_operacoes)
        st="RODANDO" if b.rodando else "DESLIGADO"
        cr=COR_SUCESSO if b.rodando else COR_ERRO
        self.cs.children[0].children[0].text=st; self.cs.children[0].children[0].text_color=get_color_from_hex(cr)
        self.btn.text="DESLIGAR" if b.rodando else "LIGAR BOT"
        self.btn.icon="stop" if b.rodando else "play"
        self.btn.md_bg_color=get_color_from_hex(COR_ERRO if b.rodando else COR_SUCESSO)
        if b.historico:
            u=b.historico[-1]
            self.lu.text=f"{u['par']} | {'C' if u['dir']==1 else 'V'} | {u['alv']}x | {u['hora']}"

class OperacoesScreen(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.app=MDApp.get_running_app()
        self.lista=MDList()
        ly=MDBoxLayout(orientation="vertical", padding=dp(16), md_bg_color=get_color_from_hex(COR_FUNDO))
        ly.add_widget(MDLabel(text="HISTORICO DE OPERACOES", theme_text_color="Custom", text_color=get_color_from_hex(COR_PRIMARIA), font_style="H6", padding=dp(0,0,0,8))))
        ly.add_widget(self.lista); self.add_widget(ly)
        Clock.schedule_interval(self.atualizar,3)

    @mainthread
    def atualizar(self, dt):
        if not self.app.bot: return
        self.lista.clear_widgets()
        for op in reversed(self.app.bot.historico[-40:]):
            c=COR_SUCESSO if op['dir']==1 else COR_ERRO
            self.lista.add_widget(TwoLineListItem(
                text=f"{op['par']} - {'LONG' if op['dir']==1 else 'SHORT'} @ {op['alv']}x",
                secondary_text=f"{op['hora']} | ${op['preco']:.6f}",
                theme_text_color="Custom", text_color=get_color_from_hex(c),
                secondary_theme_text_color="Custom", secondary_text_color=get_color_from_hex(COR_TEXTO_MUDO)))

class ConfigScreen(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.app=MDApp.get_running_app()
        ly=MDBoxLayout(orientation="vertical", padding=dp(16), spacing=dp(10), md_bg_color=get_color_from_hex(COR_FUNDO))
        self.r=MDTextField(text="0.05", hint_text="Risco por operacao (0.05 = 5%)", mode="outlined", line_color_focus=get_color_from_hex(COR_PRIMARIA))
        self.ai=MDTextField(text="10", hint_text="Alavancagem Inicial", mode="outlined")
        self.am=MDTextField(text="125", hint_text="Alavancagem Maxima", mode="outlined")
        self.ex=MDTextField(text="BTCUSDT,ETHUSDT,SOLUSDT", hint_text="Excluir (virgula)", mode="outlined")
        self.mn=MDTextField(text="5.0", hint_text="Valor minimo ordem USDT", mode="outlined")
        self.ak=MDTextField(text="", hint_text="BINANCE API KEY", mode="outlined", password=True)
        self.as_=MDTextField(text="", hint_text="BINANCE API SECRET", mode="outlined", password=True)
        self.sv=MDFillRoundFlatIconButton(text="SALVAR", icon="content-save", md_bg_color=get_color_from_hex(COR_PRIMARIA), text_color=get_color_from_hex("#000000"))
        self.sv.bind(on_press=self.salvar)
        for w in [self.r,self.ai,self.am,self.ex,self.mn,self.ak,self.as_,self.sv]: ly.add_widget(w)
        self.add_widget(ly); self.carregar()

    def salvar(self, i):
        cfg={"risco":float(self.r.text),"alv_ini":int(self.ai.text),"alv_max":int(self.am.text),
             "excluir":[x.strip() for x in self.ex.text.split(",") if x.strip()],"min_not":float(self.mn.text),
             "api_key":self.ak.text,"api_secret":self.as_.text}
        with open("config.json","w") as f: json.dump(cfg,f,indent=2)
        if self.app.bot: self.app.bot.carregar_config(cfg)
        try: notification.notify(title="CONFIG SALVA", message="Pronto!")
        except: pass

    def carregar(self):
        if os.path.exists("config.json"):
            with open("config.json") as f: c=json.load(f)
            self.r.text=str(c.get("risco",0.05)); self.ai.text=str(c.get("alv_ini",10))
            self.am.text=str(c.get("alv_max",125)); self.ex.text=",".join(c.get("excluir",["BTCUSDT","ETHUSDT","SOLUSDT"]))
            self.mn.text=str(c.get("min_not",5.0)); self.ak.text=c.get("api_key",""); self.as_.text=c.get("api_secret","")

class LogsScreen(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        ly=MDBoxLayout(md_bg_color=get_color_from_hex("#000000"), padding=dp(8))
        self.l=MDLabel(text="Logs em tempo real...", theme_text_color="Custom", text_color=get_color_from_hex(COR_SUCESSO), font_size=dp(11))
        ly.add_widget(self.l); self.add_widget(ly)
        Clock.schedule_interval(self.atualizar,1)

    @mainthread
    def atualizar(self, dt):
        if os.path.exists("bot.log"):
            with open("bot.log") as f: self.l.text="".join(f.readlines()[-100:])

class AppBot(MDApp):
    def build(self):
        self.theme_cls.theme_style="Dark"
        self.theme_cls.primary_palette="Amber"
        self.bot=None; self.th=None
        self.sm=MDScreenManager()
        self.sm.add_widget(DashboardScreen(name="dash"))
        self.sm.add_widget(OperacoesScreen(name="ops"))
        self.sm.add_widget(ConfigScreen(name="cfg"))
        self.sm.add_widget(LogsScreen(name="log"))
        ly=MDBoxLayout(orientation="vertical")
        tb=MDTopAppBar(title="BOT TRADING PRO", md_bg_color=get_color_from_hex(COR_CARD), specific_text_color=get_color_from_hex(COR_PRIMARIA))
        self.tabs=MDTabs(tab_display_mode="text", background_color=get_color_from_hex(COR_CARD), text_color_active=get_color_from_hex(COR_PRIMARIA))
        self.tabs.bind(on_tab_switch=self.mudar)
        for n in ["DASHBOARD","OPERACOES","CONFIG","LOGS"]: self.tabs.add_widget(Tab(tab_label_text=n))
        ly.add_widget(tb); ly.add_widget(self.tabs); ly.add_widget(self.sm)
        return ly

    def mudar(self, t, tab, x, y):
        self.sm.current={"DASHBOARD":"dash","OPERACOES":"ops","CONFIG":"cfg","LOGS":"log"}.get(tab.tab_label_text,"dash")

    def on_start(self):
        cfg={}
        if os.path.exists("config.json"):
            with open("config.json") as f: cfg=json.load(f)
        self.bot=BotTrading(cfg)
        self.bot.callback_notificacao=lambda t,m: self.notif(t,m)

    def toggle_bot(self):
        if not self.bot: return
        if self.bot.rodando: self.bot.parar()
        else:
            self.th=threading.Thread(target=self.bot.iniciar, daemon=True)
            self.th.start()

    @mainthread
    def notif(self, t, m):
        try: notification.notify(title=t, message=m, app_name="BotTradingPro")
        except: pass

if __name__=="__main__":
    AppBot().run()
