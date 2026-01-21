import streamlit as st
import cv2
from ultralytics import YOLO
import serial
import time
import numpy as np
import threading
from PIL import Image
import hashlib 

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Control de Tráfico IA", page_icon="🚦", layout="wide")

# ==========================================
# 🔐 MÓDULO DE SEGURIDAD (NIVEL 1)
# ==========================================

def make_hashes(password):
    return hashlib.sha256(str.encode(password)).hexdigest()

def check_hashes(password, hashed_text):
    if make_hashes(password) == hashed_text:
        return True
    return False

# Inicializar estado de login
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False

# BLOQUEO DE PANTALLA
if not st.session_state['logged_in']:
    st.markdown("""
    <style>
        .stApp { background-color: #0e1117; }
        .login-box { background-color: #1e1e1e; padding: 20px; border-radius: 10px; border: 1px solid #333; }
    </style>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        st.title("🔒 Acceso Restringido")
        st.markdown("Sistema de Control de Tráfico IoT")
        st.markdown("<div class='login-box'>", unsafe_allow_html=True)
        
        username = st.text_input("Usuario")
        password = st.text_input("Contraseña", type='password')
        
        if st.button("Ingresar al Sistema", type="primary"):
            # Hash de la contraseña "12345"
            hash_real = '5994471abb01112afcc18159f6cc74b4f511b99806da59b3caf5a9c173cacfc5'
            
            if username == 'admin' and check_hashes(password, hash_real):
                st.session_state['logged_in'] = True
                st.success("Acceso concedido...")
                time.sleep(1)
                st.rerun()
            else:
                st.error("❌ Credenciales incorrectas")
        
        st.markdown("</div>", unsafe_allow_html=True)
    
    st.stop() # 🛑 DETIENE TODO EL CÓDIGO SI NO HAY LOGIN

# ==========================================
# 🚦 SISTEMA PRINCIPAL (Solo carga si pasó el login)
# ==========================================

# --- ESTILOS CSS ---
st.markdown("""
<style>
    .stApp { background: radial-gradient(circle at 50% 0%, #1c202b 0%, #0e1117 100%); background-attachment: fixed; }
    h1, h2, h3 { color: #FFFFFF !important; text-shadow: 0px 0px 10px rgba(0, 255, 239, 0.3); font-weight: bold !important; }
    h4 { color: #FFFFFF !important; background-color: rgba(0, 0, 0, 0.4); padding: 8px; border-radius: 8px; text-align: center; border: 1px solid #404040; margin-bottom: 10px; font-family: 'Segoe UI', sans-serif; text-transform: uppercase; letter-spacing: 1px; }
    .stMarkdown, p, label { color: #e0e0e0 !important; }
    
    div[data-testid="stMetric"] { background-color: #1e1e1e !important; border: 1px solid #333 !important; border-left: 5px solid #00FFEF !important; padding: 10px !important; border-radius: 8px !important; box-shadow: 0 4px 6px rgba(0,0,0,0.3); }
    label[data-testid="stMetricLabel"] { color: #00FFEF !important; font-size: 16px !important; font-weight: bold !important; }
    div[data-testid="stMetricValue"] { color: #FFFFFF !important; font-size: 30px !important; }

    div[data-testid="stImage"] img { border: 2px solid #00FFEF; border-radius: 10px; transition: transform 0.3s ease; }
    div[data-testid="stImage"] img:hover { transform: scale(1.02); box-shadow: 0 0 20px rgba(0, 255, 239, 0.5); cursor: pointer; }
    section[data-testid="stSidebar"] { background-color: #11131a; border-right: 1px solid #333; }

    button[kind="primary"] {
        background: linear-gradient(90deg, #00C9FF 0%, #92FE9D 100%);
        color: #FFFFFF !important; text-shadow: 0px 1px 3px rgba(0,0,0,0.6); 
        font-weight: bold !important; border: none; border-radius: 8px; padding: 0.5rem 1rem;
        transition: transform 0.2s ease;
    }
    button[kind="primary"]:hover { transform: scale(1.05); box-shadow: 0 0 15px rgba(0, 201, 255, 0.7); }
    div.stButton > button:first-child { min-width: 150px; }
</style>
""", unsafe_allow_html=True)

# --- CLASE ANTI-LAG ---
class CamaraRapida:
    def __init__(self, url):
        self.url = url
        self.cap = cv2.VideoCapture(url)
        self.frame = None
        self.ret = False
        self.running = True
        self.thread = threading.Thread(target=self.update, args=())
        self.thread.daemon = True
        self.thread.start()

    def update(self):
        while self.running:
            try:
                if self.cap.isOpened():
                    ret, frame = self.cap.read()
                    if ret:
                        self.ret = ret
                        self.frame = frame
                    else:
                        time.sleep(0.1)
                else:
                    time.sleep(0.1)
            except Exception:
                time.sleep(0.1)
        if self.cap.isOpened():
            self.cap.release()

    def read(self):
        return self.ret, self.frame

    def stop(self):
        self.running = False
        if self.thread.is_alive():
            self.thread.join(timeout=0.5)

# --- CLASE CEREBRO (SISTEMA PRINCIPAL) ---
class SistemaTrafico:
    def __init__(self):
        self.running = False
        self.lock = threading.Lock()
        
        self.imgs_display = [np.zeros((240, 320, 3), dtype=np.uint8)] * 4
        self.conteos = [0, 0, 0, 0]
        self.tiempo_restante = 0
        self.estado_actual = 0
        
        self.param_tiempo_base = 20
        self.param_tiempo_auto = 3
        self.param_tiempo_max = 60
        self.param_confianza = 0.45
        
        self.thread = None

    def iniciar(self):
        if not self.running:
            self.running = True
            self.thread = threading.Thread(target=self._proceso_principal, daemon=True)
            self.thread.start()

    def detener(self):
        self.running = False
        if self.thread:
            self.thread.join(timeout=1.0)

    def _proceso_principal(self):
        CAMS_URLS = [
            "http://192.168.0.100:81/stream", 
            "http://192.168.0.101:81/stream", 
            "http://192.168.0.102:81/stream", 
            "http://192.168.0.103:81/stream"  
        ]
        
        model = YOLO('best.pt')
        caps = [CamaraRapida(url) for url in CAMS_URLS]
        time.sleep(1.5) 
        
        try:
            arduino = serial.Serial('COM5', 9600, timeout=1)
            time.sleep(2)
        except:
            arduino = None

        def enviar(cmd):
            if arduino: 
                try: arduino.write(cmd.encode()) 
                except: pass

        estado = 0
        enviar('V')
        inicio_fase = time.time()
        duracion_fase = self.param_tiempo_base

        while self.running:
            temp_imgs = []
            temp_conteos = []
            
            for cap in caps:
                ret, frame = cap.read()
                c = 0
                if ret and frame is not None:
                    try:
                        frame_proc = frame.copy() 
                        frame_proc = cv2.resize(frame_proc, (320, 240))
                        
                        results = model(frame_proc, stream=True, conf=self.param_confianza, verbose=False)
                        for r in results:
                            for box in r.boxes:
                                c += 1
                                x1, y1, x2, y2 = map(int, box.xyxy[0])
                                cv2.rectangle(frame_proc, (x1, y1), (x2, y2), (0, 255, 0), 2)
                        frame_proc = cv2.cvtColor(frame_proc, cv2.COLOR_BGR2RGB)
                    except:
                        frame_proc = np.zeros((240, 320, 3), dtype=np.uint8)
                else:
                    frame_proc = np.zeros((240, 320, 3), dtype=np.uint8)
                
                temp_imgs.append(frame_proc)
                temp_conteos.append(c)

            with self.lock:
                self.imgs_display = temp_imgs
                self.conteos = temp_conteos
                self.estado_actual = estado
                self.tiempo_restante = int(duracion_fase - (time.time() - inicio_fase))
                if self.tiempo_restante < 0: self.tiempo_restante = 0

            if time.time() - inicio_fase >= duracion_fase:
                if estado == 0:
                    enviar('v'); duracion_fase = 6; estado = 1
                elif estado == 1:
                    total = temp_conteos[1] + temp_conteos[3]
                    t = self.param_tiempo_base + (total * self.param_tiempo_auto)
                    if t > self.param_tiempo_max: t = self.param_tiempo_max
                    enviar('H'); duracion_fase = t; estado = 2
                elif estado == 2:
                    enviar('h'); duracion_fase = 6; estado = 3
                elif estado == 3:
                    total = temp_conteos[0] + temp_conteos[2]
                    t = self.param_tiempo_base + (total * self.param_tiempo_auto)
                    if t > self.param_tiempo_max: t = self.param_tiempo_max
                    enviar('V'); duracion_fase = t; estado = 0
                inicio_fase = time.time()

        enviar('R')
        if arduino: 
            try: arduino.close()
            except: pass
        for c in caps: 
            c.stop()

# --- INICIALIZACIÓN ---
if 'sistema' not in st.session_state:
    st.session_state.sistema = SistemaTrafico()

sistema = st.session_state.sistema

# --- SIDEBAR (CON BOTÓN DE LOGOUT) ---
st.sidebar.title("⚙️ Configuración")

# Botón de Cerrar Sesión
st.sidebar.markdown(f"👤 **Admin** Conectado")
if st.sidebar.button("🔒 Cerrar Sesión"):
    st.session_state['logged_in'] = False
    st.rerun()

st.sidebar.divider()
sistema.param_tiempo_base = st.sidebar.slider("Tiempo Base (Min)", 10, 30, 20)
sistema.param_tiempo_auto = st.sidebar.slider("Segundos por Auto", 1, 5, 3)
sistema.param_tiempo_max = st.sidebar.slider("Tiempo Máximo (Max)", 30, 90, 60)
sistema.param_confianza = st.sidebar.slider("Confianza IA", 0.1, 1.0, 0.45)
st.sidebar.info("Proyecto IT Gestion de Control de Trafico Vehicular.")

# --- UI PRINCIPAL ---
st.title("🚦 Sistema de Tráfico Inteligente - Dashboard")

col_estado, col_tiempo, col_autos_v, col_autos_h = st.columns(4)
metric_estado = col_estado.empty()
metric_tiempo = col_tiempo.empty()
metric_autos_v = col_autos_v.empty()
metric_autos_h = col_autos_h.empty()

st.divider()

col1, col2 = st.columns(2)
with col1:
    st.markdown("#### ⬆️ Calle 1 (Norte)")
    cam1 = st.empty()
    st.markdown("#### ⬇️ Calle 3 (Sur)")
    cam3 = st.empty()
with col2:
    st.markdown("#### ➡️ Calle 2 (Este)")
    cam2 = st.empty()
    st.markdown("#### ⬅️ Calle 4 (Oeste)")
    cam4 = st.empty()

placeholders = [cam1, cam2, cam3, cam4]
st.markdown("<br>", unsafe_allow_html=True)

col_btn1, col_btn2, _ = st.columns([0.15, 0.15, 0.7])

with col_btn1:
    if st.button("▶️ INICIAR SISTEMA", type="primary"):
        sistema.iniciar()
        st.rerun()

with col_btn2:
    if st.button("⏹️ DETENER SISTEMA"):
        sistema.detener()
        st.rerun()

# --- BUCLE VISUALIZACIÓN ---
if sistema.running:
    try:
        while True:
            with sistema.lock:
                imgs = sistema.imgs_display
                cnts = sistema.conteos
                est = sistema.estado_actual
                t_rest = sistema.tiempo_restante
            
            for i, ph in enumerate(placeholders):
                ph.image(imgs[i], channels="RGB", use_container_width=True)
            
            metric_tiempo.metric("⏳ Tiempo Restante", f"{t_rest} s")
            metric_autos_v.metric("🚗 Autos Vertical (1+3)", cnts[0] + cnts[2])
            metric_autos_h.metric("🚙 Autos Horizontal (2+4)", cnts[1] + cnts[3])
            
            if est == 0: metric_estado.markdown("### Estado: <span style='color:#00FF00'>VERDE VERTICAL</span>", unsafe_allow_html=True)
            elif est == 1: metric_estado.markdown("### Estado: <span style='color:#FFFF00'>AMARILLO VERTICAL</span>", unsafe_allow_html=True)
            elif est == 2: metric_estado.markdown("### Estado: <span style='color:#00FF00'>VERDE HORIZONTAL</span>", unsafe_allow_html=True)
            elif est == 3: metric_estado.markdown("### Estado: <span style='color:#FFFF00'>AMARILLO HORIZONTAL</span>", unsafe_allow_html=True)
            
            time.sleep(0.05)
            
    except Exception:
        pass
else:
    st.warning("Sistema Detenido. Presiona Iniciar.")