import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import threading
import queue
import os
import sys
from datetime import datetime
import pandas as pd

# Importar las clases existentes
try:
    from Query import Query
    from read_data import EmssanarDataReader
    from read_cups_data import CupsDataReader
    from cups_query import CupsQuery
except ImportError as e:
    CupsDataReader = None
    CupsQuery = None
    if "Query" in str(e) or "read_data" in str(e):
        messagebox.showerror("Error", "No se encontraron los archivos Query.py y read_data.py")
        sys.exit(1)


class EmssanarGUI:
    """Interfaz gráfica para el sistema de migración de datos Clinizad."""
    
    # Paleta de colores
    COLORES = {
        'azul_principal': "#2563EB",
        'azul_oscuro': "#1D4ED8",
        'azul_claro': "#EFF6FF",
        'azul_medio': "#3B82F6",
        'blanco': "#FFFFFF",
        'gris_claro': "#F8FAFC",
        'gris_medio': "#E2E8F0",
        'fondo_seccion': "#F1F5F9",
        'texto': "#1E293B",
        'texto_secundario': "#64748B",
        'exito': "#10B981",
        'error': "#EF4444",
        'advertencia': "#F59E0B",
    }
    
    VERSION = "v1.0.0"
    
    # Usuarios válidos
    USUARIOS_VALIDOS = {
        "admin": "admin123",
        "clinizad": "clinizad2024",
        "usuario": "password"
    }

    def __init__(self, root):
        self.root = root
        self._configurar_ventana()
        self._inicializar_variables()
        self._configurar_estilos()
        self._crear_widgets()
        self._verificar_cola()
    
    def _configurar_ventana(self):
        """Configura la ventana principal."""
        self.root.title("Clinizad - Sistema de Migración de Datos")
        self.root.geometry("1100x750")
        self.root.configure(bg=self.COLORES['blanco'])
        self.root.minsize(900, 600)
        
        # Establecer icono de la ventana
        self._establecer_icono()
    
    def _establecer_icono(self):
        """Establece el icono de la ventana."""
        try:
            # Buscar el icono en diferentes ubicaciones
            posibles_rutas = [
                os.path.join(os.path.dirname(os.path.abspath(__file__)), "icono.ico"),
                os.path.join(os.path.dirname(sys.executable), "icono.ico"),
                "icono.ico"
            ]
            
            for ruta in posibles_rutas:
                if os.path.exists(ruta):
                    self.root.iconbitmap(ruta)
                    break
        except Exception:
            pass  # Si no se puede cargar el icono, continuar sin él
    
    def _inicializar_variables(self):
        """Inicializa todas las variables de la aplicación."""
        # Configuración BD
        self.archivo_excel = tk.StringVar()
        self.host_db = tk.StringVar(value="192.168.9.177")
        self.puerto_db = tk.StringVar(value="5432")
        self.nombre_db = tk.StringVar(value="practica")
        self.usuario_db = tk.StringVar(value="postgres")
        self.password_db = tk.StringVar(value="postgres")
        
        # Login
        self.usuario_app = tk.StringVar()
        self.password_app = tk.StringVar()
        self.login_exitoso = False
        self.usuario_actual = None
        
        # Estado
        self.en_proceso = False
        self.cancelar = False
        self.queue = queue.Queue()
        
        # Cache
        self._cache_excel = None
        self._cache_archivo = None
        
        # Animación
        self._animacion_activa = False
        self._animacion_contador = 0
        
        # CUPS
        self.en_proceso_cups = False
    
    def _configurar_estilos(self):
        """Configura los estilos de la interfaz."""
        style = ttk.Style()
        style.theme_use('clam')
        
        c = self.COLORES  # Alias para brevedad
        
        # Botones
        style.configure("TButton", background=c['azul_principal'], foreground=c['blanco'],
                       borderwidth=0, focuscolor='none', padding=(15, 10), font=("Segoe UI", 9, "bold"))
        style.map("TButton", background=[("active", c['azul_oscuro']), ("pressed", c['azul_medio']), ("disabled", "#94A3B8")])
        
        # LabelFrame
        style.configure("TLabelframe", background=c['fondo_seccion'], borderwidth=1, relief="solid")
        style.configure("TLabelframe.Label", background=c['fondo_seccion'], foreground=c['texto'],
                       font=("Segoe UI", 11, "bold"), padding=(10, 5))
        
        # Frame
        style.configure("TFrame", background=c['blanco'])
        
        # Notebook
        style.configure("TNotebook", background=c['blanco'], borderwidth=0, tabmargins=[5, 5, 5, 0])
        style.configure("TNotebook.Tab", background=c['gris_claro'], foreground=c['texto_secundario'],
                       padding=[25, 12], font=("Segoe UI", 10, "bold"))
        style.map("TNotebook.Tab",
                 background=[("selected", c['azul_principal']), ("active", c['azul_claro'])],
                 foreground=[("selected", c['blanco']), ("active", c['azul_principal'])],
                 expand=[("selected", [0, 0, 0, 2])])
        
        # Entry
        style.configure("TEntry", fieldbackground=c['blanco'], borderwidth=2, relief="flat",
                       padding=10, font=("Segoe UI", 10))
        style.map("TEntry", bordercolor=[("focus", c['azul_principal']), ("!focus", c['gris_medio'])])
        
        # Progressbar
        style.configure("TProgressbar", background=c['azul_principal'], borderwidth=0,
                       troughcolor=c['gris_medio'], thickness=8)
        
        # Treeview
        style.configure("Treeview", background=c['blanco'], foreground=c['texto'],
                       fieldbackground=c['blanco'], borderwidth=0, rowheight=28, font=("Segoe UI", 9))
        style.configure("Treeview.Heading", background=c['azul_principal'], foreground=c['blanco'],
                       font=("Segoe UI", 9, "bold"), relief="flat", padding=8)
        style.map("Treeview", background=[("selected", c['azul_claro'])], foreground=[("selected", c['texto'])])

    def _crear_label(self, parent, text, font_size=10, bold=False, fg=None, bg=None, **kwargs):
        """Crea un Label con configuración común."""
        font = ("Segoe UI", font_size, "bold" if bold else "normal")
        return tk.Label(parent, text=text, font=font, 
                       bg=bg or self.COLORES['fondo_seccion'],
                       fg=fg or "#333333", **kwargs)

    def _crear_frame_campo(self, parent, label_text, variable, width=45, show=None, placeholder=None):
        """Crea un campo de entrada con label."""
        frame = tk.Frame(parent, bg=self.COLORES['fondo_seccion'])
        frame.pack(fill=tk.X, pady=8)
        
        label = self._crear_label(frame, label_text, width=15, anchor="w")
        label.pack(side=tk.LEFT, padx=(0, 15))
        
        entry = ttk.Entry(frame, textvariable=variable, width=width, show=show or "")
        entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        return entry

    def _crear_widgets(self):
        """Crea todos los widgets de la interfaz."""
        self._crear_header()
        self._crear_contenido_principal()
        self._crear_footer()
    
    def _crear_header(self):
        """Crea el encabezado de la aplicación."""
        c = self.COLORES
        
        header_frame = tk.Frame(self.root, bg=c['azul_principal'])
        header_frame.pack(fill=tk.X, side=tk.TOP)
        
        header_content = tk.Frame(header_frame, bg=c['azul_principal'])
        header_content.pack(fill=tk.X, padx=25, pady=12)
        
        # Título
        tk.Label(header_content, text="CLINIZAD", font=("Segoe UI", 20, "bold"),
                bg=c['azul_principal'], fg=c['blanco']).pack(side=tk.LEFT)
        
        tk.Label(header_content, text="  |  ", font=("Segoe UI", 14),
                bg=c['azul_principal'], fg="#93C5FD").pack(side=tk.LEFT)
        
        tk.Label(header_content, text="Sistema de Migración de Datos", font=("Segoe UI", 11),
                bg=c['azul_principal'], fg="#DBEAFE").pack(side=tk.LEFT)
        
        # Usuario
        user_container = tk.Frame(header_content, bg=c['azul_principal'])
        user_container.pack(side=tk.RIGHT)
        
        self.btn_cerrar_sesion = tk.Button(user_container, text="Cerrar Sesión", command=self._cerrar_sesion,
            bg="#1E40AF", fg=c['blanco'], activebackground="#1E3A8A", activeforeground=c['blanco'],
            font=("Segoe UI", 8), relief="flat", cursor="hand2", padx=10, pady=2, bd=0)
        
        self.user_indicator = tk.Label(user_container, text="", font=("Segoe UI", 9),
                                       bg=c['azul_principal'], fg="#BFDBFE")
        self.user_indicator.pack(side=tk.LEFT, padx=(0, 10))
        
        # Línea decorativa
        tk.Frame(self.root, bg=c['azul_oscuro'], height=3).pack(fill=tk.X, side=tk.TOP)
    
    def _crear_contenido_principal(self):
        """Crea el contenido principal con pestañas."""
        main_frame = tk.Frame(self.root, bg=self.COLORES['blanco'])
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self._crear_pestaña_configuracion()
        self._crear_pestaña_migracion()
        
        if CupsDataReader and CupsQuery:
            try:
                self._crear_pestaña_codigos_cups()
            except Exception as e:
                print(f"Error al crear pestaña CUPS: {e}")
    
    def _crear_footer(self):
        """Crea la barra de estado."""
        c = self.COLORES
        
        tk.Frame(self.root, bg=c['gris_medio'], height=1).pack(fill=tk.X, side=tk.BOTTOM)
        
        footer = tk.Frame(self.root, bg=c['gris_claro'], height=28)
        footer.pack(fill=tk.X, side=tk.BOTTOM)
        footer.pack_propagate(False)
        
        tk.Label(footer, text=f"Clinizad {self.VERSION}", font=("Segoe UI", 8),
                bg=c['gris_claro'], fg=c['texto_secundario']).pack(side=tk.LEFT, padx=15)
        
        self.footer_datetime = tk.Label(footer, text="", font=("Segoe UI", 8),
                                        bg=c['gris_claro'], fg=c['texto_secundario'])
        self.footer_datetime.pack(side=tk.RIGHT, padx=15)
        
        self.footer_status = tk.Label(footer, text="Sin conexión", font=("Segoe UI", 8),
                                      bg=c['gris_claro'], fg=c['texto_secundario'])
        self.footer_status.pack(side=tk.RIGHT, padx=15)
        
        self.footer_session = tk.Label(footer, text="No autenticado", font=("Segoe UI", 8),
                                       bg=c['gris_claro'], fg=c['texto_secundario'])
        self.footer_session.pack(side=tk.RIGHT, padx=15)
        
        self._actualizar_hora_footer()
    
    def _actualizar_hora_footer(self):
        """Actualiza la hora en el footer cada segundo."""
        self.footer_datetime.config(text=datetime.now().strftime("%d/%m/%Y  %H:%M:%S"))
        self.root.after(1000, self._actualizar_hora_footer)
    
    def _actualizar_estado_footer(self):
        """Actualiza el estado de sesión en el footer."""
        if self.login_exitoso:
            self.footer_session.config(text=f"Sesión: {self.usuario_actual}", fg=self.COLORES['exito'])
        else:
            self.footer_session.config(text="No autenticado", fg=self.COLORES['texto_secundario'])

    # === ANIMACIÓN ===
    
    def _iniciar_animacion_carga(self, label_widget, texto_base="Procesando"):
        """Inicia animación de puntos en un label."""
        self._animacion_activa = True
        self._animacion_contador = 0
        self._animar_texto(label_widget, texto_base)
    
    def _detener_animacion_carga(self):
        """Detiene la animación de carga."""
        self._animacion_activa = False
    
    def _animar_texto(self, label_widget, texto_base):
        """Anima el texto con puntos suspensivos."""
        if not self._animacion_activa:
            return
        
        puntos = "." * (self._animacion_contador % 4)
        try:
            label_widget.config(text=f"{texto_base}{puntos}")
        except tk.TclError:
            return
        
        self._animacion_contador += 1
        self.root.after(400, lambda: self._animar_texto(label_widget, texto_base))

    # === PESTAÑA CONFIGURACIÓN ===
    
    def _crear_pestaña_configuracion(self):
        """Pestaña de configuración con login."""
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text=" Configuración ")
        
        self.main_container_config = tk.Frame(frame, bg=self.COLORES['blanco'])
        self.main_container_config.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)
        
        self._crear_login_card()
        self._crear_frame_db()
    
    def _crear_login_card(self):
        """Crea el card de login."""
        c = self.COLORES
        
        self.frame_login_container = tk.Frame(self.main_container_config, bg=c['blanco'])
        self.frame_login_container.pack(expand=True)
        
        # Sombras
        shadow_outer = tk.Frame(self.frame_login_container, bg="#D1D5DB")
        shadow_outer.pack(padx=4, pady=4)
        shadow_mid = tk.Frame(shadow_outer, bg="#E5E7EB")
        shadow_mid.pack(padx=2, pady=2)
        shadow_inner = tk.Frame(shadow_mid, bg="#F3F4F6")
        shadow_inner.pack(padx=1, pady=1)
        
        login_card = tk.Frame(shadow_inner, bg=c['blanco'], relief="flat", bd=0)
        login_card.pack()
        
        # Header
        login_header = tk.Frame(login_card, bg=c['azul_principal'], height=55)
        login_header.pack(fill=tk.X)
        login_header.pack_propagate(False)
        tk.Label(login_header, text="Inicio de Sesión", font=("Segoe UI", 13, "bold"),
                bg=c['azul_principal'], fg=c['blanco']).pack(expand=True)
        
        # Contenido
        login_content = tk.Frame(login_card, bg=c['blanco'])
        login_content.pack(fill=tk.BOTH, expand=True, padx=40, pady=30)
        
        tk.Label(login_content, text="Bienvenido al sistema", font=("Segoe UI", 10),
                bg=c['blanco'], fg="#666666").pack(pady=(0, 20))
        
        # Usuario
        container_usuario = tk.Frame(login_content, bg=c['blanco'])
        container_usuario.pack(fill=tk.X, pady=8)
        tk.Label(container_usuario, text="Usuario:", font=("Segoe UI", 10),
                bg=c['blanco'], fg="#333333").pack(anchor="w", pady=(0, 5))
        self.entry_usuario_app = ttk.Entry(container_usuario, textvariable=self.usuario_app, width=30, font=("Segoe UI", 11))
        self.entry_usuario_app.pack(fill=tk.X, ipady=5)
        self.entry_usuario_app.bind('<Return>', lambda e: self._intentar_login())
        
        # Contraseña
        container_password = tk.Frame(login_content, bg=c['blanco'])
        container_password.pack(fill=tk.X, pady=8)
        tk.Label(container_password, text="Contraseña:", font=("Segoe UI", 10),
                bg=c['blanco'], fg="#333333").pack(anchor="w", pady=(0, 5))
        self.entry_password_app = ttk.Entry(container_password, textvariable=self.password_app, width=30, show="●", font=("Segoe UI", 11))
        self.entry_password_app.pack(fill=tk.X, ipady=5)
        self.entry_password_app.bind('<Return>', lambda e: self._intentar_login())
        
        self.label_estado_login = tk.Label(login_content, text="", font=("Segoe UI", 9),
                                           bg=c['blanco'], fg=c['error'])
        self.label_estado_login.pack(pady=10)
        
        ttk.Button(login_content, text="  Iniciar Sesión  ", command=self._intentar_login).pack(pady=10, ipadx=20, ipady=5)
    
    def _crear_frame_db(self):
        """Crea el frame de conexión a base de datos."""
        c = self.COLORES
        
        self.frame_db = ttk.LabelFrame(self.main_container_config, text="Conexión a Base de Datos", padding=20)
        
        campos_container = tk.Frame(self.frame_db, bg=c['fondo_seccion'])
        campos_container.pack(fill=tk.BOTH, expand=True)
        
        campos = [
            ("Host:", self.host_db, None),
            ("Puerto:", self.puerto_db, None),
            ("Base de datos:", self.nombre_db, None),
            ("Usuario:", self.usuario_db, None),
            ("Contraseña:", self.password_db, "*")
        ]
        
        for label, variable, show in campos:
            self._crear_frame_campo(campos_container, label, variable, show=show)
        
        frame_botones = tk.Frame(self.frame_db, bg=c['fondo_seccion'])
        frame_botones.pack(fill=tk.X, pady=(15, 5))
        ttk.Button(frame_botones, text="Probar Conexión", command=self._probar_conexion).pack(side=tk.LEFT)
        
        self.label_estado_db = tk.Label(self.frame_db, text="", font=("Segoe UI", 9),
                                        bg=c['fondo_seccion'], fg=c['azul_principal'], anchor="w")
        self.label_estado_db.pack(fill=tk.X, pady=(10, 0), padx=5)
    
    def _intentar_login(self):
        """Intenta autenticar al usuario."""
        usuario = self.usuario_app.get().strip()
        password = self.password_app.get()
        
        if not usuario or not password:
            self.label_estado_login.config(text="Por favor ingrese usuario y contraseña", fg=self.COLORES['error'])
            return
        
        if usuario in self.USUARIOS_VALIDOS and self.USUARIOS_VALIDOS[usuario] == password:
            self.login_exitoso = True
            self.usuario_actual = usuario
            self.user_indicator.config(text=f"Usuario: {usuario}")
            self.btn_cerrar_sesion.pack(side=tk.LEFT)
            self.frame_login_container.pack_forget()
            self.frame_db.pack(fill=tk.BOTH, expand=True)
            self._actualizar_estado_footer()
            messagebox.showinfo("Bienvenido", f"¡Bienvenido, {usuario}!")
        else:
            self.label_estado_login.config(text="Usuario o contraseña incorrectos", fg=self.COLORES['error'])
            self.password_app.set("")
            self.entry_password_app.focus_set()
    
    def _cerrar_sesion(self):
        """Cierra la sesión actual."""
        if self.en_proceso:
            messagebox.showwarning("Advertencia", "No puede cerrar sesión mientras hay un proceso en ejecución")
            return
        
        if messagebox.askyesno("Cerrar Sesión", "¿Está seguro de que desea cerrar sesión?"):
            self.login_exitoso = False
            self.usuario_actual = None
            self.usuario_app.set("")
            self.password_app.set("")
            self.user_indicator.config(text="")
            self.btn_cerrar_sesion.pack_forget()
            self.frame_db.pack_forget()
            self.frame_login_container.pack(expand=True)
            self.label_estado_login.config(text="")
            self._actualizar_estado_footer()
            self.entry_usuario_app.focus_set()
    
    def _probar_conexion(self):
        """Prueba la conexión a la base de datos."""
        c = self.COLORES
        self.label_estado_db.config(text="⏳ Probando conexión...", fg=c['azul_principal'])
        self.root.update()
        
        try:
            import psycopg2
            conn = psycopg2.connect(
                host=self.host_db.get(),
                port=int(self.puerto_db.get()),
                database=self.nombre_db.get(),
                user=self.usuario_db.get(),
                password=self.password_db.get()
            )
            conn.close()
            self.label_estado_db.config(text="✓ Conexión exitosa", fg=c['exito'])
            self.footer_status.config(text="BD: Conectada", fg=c['exito'])
            messagebox.showinfo("Éxito", "Conexión establecida correctamente")
        except Exception as e:
            self.label_estado_db.config(text=f"✗ Error: {str(e)}", fg=c['error'])
            self.footer_status.config(text="BD: Desconectada", fg=c['error'])
            messagebox.showerror("Error", f"No se pudo conectar:\n{str(e)}")

    # === PESTAÑA MIGRACIÓN ===
    
    def _crear_pestaña_migracion(self):
        """Pestaña de migración de datos."""
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text=" Autorizaciones ")
        
        # Canvas con scrollbar
        canvas = tk.Canvas(frame, bg=self.COLORES['blanco'], highlightthickness=0)
        scrollbar = ttk.Scrollbar(frame, orient="vertical", command=canvas.yview)
        scrollable = tk.Frame(canvas, bg=self.COLORES['blanco'])
        
        scrollable.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas_window = canvas.create_window((0, 0), window=scrollable, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        def on_canvas_configure(event):
            canvas.itemconfig(canvas_window, width=event.width)
        canvas.bind("<Configure>", on_canvas_configure)
        
        # Función para scroll con mouse/touchpad que funciona en toda el área
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
        
        def _bind_mousewheel(widget):
            """Vincula el scroll del mouse a un widget y todos sus hijos recursivamente."""
            widget.bind("<MouseWheel>", _on_mousewheel)
            widget.bind("<Button-4>", lambda e: canvas.yview_scroll(-1, "units"))  # Linux scroll up
            widget.bind("<Button-5>", lambda e: canvas.yview_scroll(1, "units"))   # Linux scroll down
            for child in widget.winfo_children():
                _bind_mousewheel(child)
        
        # Vincular scroll a canvas y frame scrollable
        _bind_mousewheel(canvas)
        _bind_mousewheel(scrollable)
        
        # También vincular cuando se agregan nuevos widgets
        def _on_widget_configure(event):
            _bind_mousewheel(scrollable)
        scrollable.bind("<Map>", _on_widget_configure)
        
        # Guardar referencia para vincular widgets futuros
        self._scrollable_migracion = scrollable
        self._bind_mousewheel_migracion = _bind_mousewheel
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        self._crear_seccion_excel(scrollable)
        self._crear_seccion_control(scrollable)
        self._crear_seccion_estadisticas(scrollable)
        self._crear_seccion_progreso(scrollable)
        self._crear_seccion_log(scrollable)
        self._crear_seccion_consulta(scrollable)
        
        # Vincular scroll del mouse a todos los widgets después de crearlos
        self.root.after(100, lambda: _bind_mousewheel(scrollable))
    
    def _crear_seccion_excel(self, parent):
        """Sección de carga de Excel."""
        c = self.COLORES
        frame = ttk.LabelFrame(parent, text="📄 Carga Autorizaciones", padding=15)
        frame.pack(fill=tk.X, padx=20, pady=10)
        
        container = tk.Frame(frame, bg=c['fondo_seccion'])
        container.pack(fill=tk.X, pady=5)
        
        self._crear_label(container, "Archivo Excel:", width=15, anchor="w").pack(side=tk.LEFT, padx=(0, 10))
        ttk.Entry(container, textvariable=self.archivo_excel, width=55).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        ttk.Button(container, text="Examinar...", command=self._seleccionar_archivo).pack(side=tk.LEFT)
        
        self.label_estado_archivo = tk.Label(frame, text="", font=("Segoe UI", 9),
                                             bg=c['fondo_seccion'], fg=c['azul_principal'], anchor="w")
        self.label_estado_archivo.pack(fill=tk.X, pady=(10, 0), padx=5)
    
    def _crear_seccion_control(self, parent):
        """Sección de control de migración."""
        c = self.COLORES
        frame = ttk.LabelFrame(parent, text="Control de Migración", padding=15)
        frame.pack(fill=tk.X, padx=20, pady=10)
        
        ttk.Button(frame, text="Iniciar Migración", command=self._iniciar_migracion, width=20).pack(side=tk.LEFT, padx=5)
        
        self.btn_cancelar = tk.Button(frame, text="Cancelar", command=self._cancelar_migracion, width=18,
            state=tk.DISABLED, bg=c['error'], fg=c['blanco'], activebackground="#B91C1C",
            activeforeground=c['blanco'], disabledforeground="#D1D5DB", font=("Segoe UI", 9, "bold"),
            relief="flat", cursor="hand2", padx=15, pady=6, bd=0)
        self.btn_cancelar.pack(side=tk.LEFT, padx=(10, 5))
    
    def _crear_seccion_estadisticas(self, parent):
        """Sección de estadísticas."""
        c = self.COLORES
        frame = ttk.LabelFrame(parent, text="Estadísticas", padding=20)
        frame.pack(fill=tk.X, padx=20, pady=10)
        
        container = tk.Frame(frame, bg=c['fondo_seccion'])
        container.pack(fill=tk.X, pady=5)
        
        labels = [
            "Total registros en Excel:", "Registros ya existentes:", "Registros nuevos a insertar:",
            "Registros insertados:", "Errores:"
        ]
        
        self.stats_vars = {}
        for i, label in enumerate(labels):
            self._crear_label(container, label, anchor="w").grid(row=i, column=0, sticky=tk.W, pady=8, padx=10)
            var = tk.StringVar(value="0")
            self.stats_vars[label] = var
            tk.Label(container, textvariable=var, font=("Segoe UI", 10, "bold"),
                    bg=c['fondo_seccion'], fg=c['azul_principal'], anchor="w").grid(row=i, column=1, sticky=tk.W, padx=20, pady=8)
    
    def _crear_seccion_progreso(self, parent):
        """Sección de progreso."""
        c = self.COLORES
        frame = ttk.LabelFrame(parent, text="Progreso", padding=15)
        frame.pack(fill=tk.X, padx=20, pady=10)
        
        self.progreso = ttk.Progressbar(frame, mode='determinate', length=400)
        self.progreso.pack(fill=tk.X, pady=5)
        
        self.label_progreso = tk.Label(frame, text="Esperando...", font=("Segoe UI", 9),
                                       bg=c['fondo_seccion'], fg=c['azul_principal'])
        self.label_progreso.pack(pady=5)
    
    def _crear_seccion_log(self, parent):
        """Sección de log."""
        c = self.COLORES
        frame = ttk.LabelFrame(parent, text="Log de Operaciones", padding=10)
        frame.pack(fill=tk.X, padx=20, pady=10)
        
        self.log_text = scrolledtext.ScrolledText(frame, height=6, width=80, wrap=tk.WORD,
            bg=c['blanco'], fg="#333333", font=("Consolas", 9),
            insertbackground=c['azul_principal'], selectbackground=c['azul_medio'], selectforeground=c['blanco'])
        self.log_text.pack(fill=tk.BOTH, expand=True)
        
        self.log_text.tag_config("exito", foreground=c['exito'], font=("Consolas", 9, "bold"))
        self.log_text.tag_config("error", foreground=c['error'], font=("Consolas", 9, "bold"))
        self.log_text.tag_config("advertencia", foreground="#FF8C00", font=("Consolas", 9, "bold"))
        self.log_text.tag_config("info", foreground=c['azul_principal'], font=("Consolas", 9))
    
    def _crear_seccion_consulta(self, parent):
        """Sección de consulta de autorizaciones."""
        c = self.COLORES
        frame = ttk.LabelFrame(parent, text="Consulta de Autorizaciones", padding=15)
        frame.pack(fill=tk.X, padx=20, pady=10)
        
        container = tk.Frame(frame, bg=c['fondo_seccion'])
        container.pack(fill=tk.X, pady=5)
        
        self._crear_label(container, "Documento del afiliado:").pack(side=tk.LEFT, padx=(0, 10))
        self.doc_busqueda = tk.StringVar()
        entry = ttk.Entry(container, textvariable=self.doc_busqueda, width=35)
        entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        entry.bind('<Return>', lambda e: self._buscar_afiliado())
        ttk.Button(container, text="Buscar", command=self._buscar_afiliado).pack(side=tk.LEFT)
        
        # Treeview
        tree_frame = ttk.Frame(frame)
        tree_frame.pack(fill=tk.BOTH, expand=True, pady=(10, 0))
        
        vsb = ttk.Scrollbar(tree_frame, orient="vertical")
        hsb = ttk.Scrollbar(tree_frame, orient="horizontal")
        
        self.tree_resultados = ttk.Treeview(tree_frame, yscrollcommand=vsb.set, xscrollcommand=hsb.set,
                                            height=6, selectmode="extended")
        vsb.config(command=self.tree_resultados.yview)
        hsb.config(command=self.tree_resultados.xview)
        
        self.tree_resultados.grid(row=0, column=0, sticky='nsew')
        vsb.grid(row=0, column=1, sticky='ns')
        hsb.grid(row=1, column=0, sticky='ew')
        tree_frame.grid_rowconfigure(0, weight=1)
        tree_frame.grid_columnconfigure(0, weight=1)
        
        self.label_info_busqueda = tk.Label(frame, text="Ingrese el documento y presione 'Buscar'",
            font=("Segoe UI", 9), bg=c['fondo_seccion'], fg="#666666", anchor="w")
        self.label_info_busqueda.pack(fill=tk.X, pady=5)
    
    def _seleccionar_archivo(self):
        """Abre diálogo para seleccionar archivo Excel."""
        archivo = filedialog.askopenfilename(
            title="Seleccionar archivo Excel",
            filetypes=[("Archivos Excel", "*.xlsx *.xls"), ("Todos los archivos", "*.*")]
        )
        if archivo:
            self.archivo_excel.set(archivo)
            self._verificar_archivo()
    
    def _verificar_archivo(self):
        """Verifica si el archivo Excel es válido."""
        c = self.COLORES
        archivo = self.archivo_excel.get()
        
        if archivo and os.path.exists(archivo):
            try:
                xls = pd.ExcelFile(archivo)
                self.label_estado_archivo.config(
                    text=f"✓ Archivo válido ({len(xls.sheet_names)} hoja(s))", fg=c['exito'])
            except Exception as e:
                self.label_estado_archivo.config(text=f"✗ Error: {str(e)}", fg=c['error'])
        else:
            self.label_estado_archivo.config(text="✗ Archivo no encontrado", fg=c['error'])
    
    def _agregar_log(self, mensaje, tipo="info"):
        """Agrega un mensaje al log."""
        texto = f"[{datetime.now().strftime('%H:%M:%S')}] {mensaje}\n"
        self.log_text.insert(tk.END, texto, tipo)
        self.log_text.see(tk.END)
        self.root.update()
    
    def _iniciar_migracion(self):
        """Inicia el proceso de migración."""
        if not self.archivo_excel.get():
            messagebox.showerror("Error", "Por favor seleccione un archivo Excel")
            return
        
        if not os.path.exists(self.archivo_excel.get()):
            messagebox.showerror("Error", "El archivo Excel no existe")
            return
        
        if not messagebox.askyesno("Confirmar", "¿Iniciar migración de datos?"):
            return
        
        self.cancelar = False
        self.en_proceso = True
        self.btn_cancelar.config(state=tk.NORMAL)
        self._iniciar_animacion_carga(self.label_progreso, "Procesando")
        self.log_text.delete(1.0, tk.END)
        
        for var in self.stats_vars.values():
            var.set("0")
        
        self.notebook.select(1)
        threading.Thread(target=self._proceso_migracion, daemon=True).start()
    
    def _proceso_migracion(self):
        """Proceso principal de migración (hilo separado)."""
        try:
            self.queue.put(("log", "Iniciando migración...", "info"))
            
            # Cargar Excel
            self.queue.put(("log", f"Leyendo: {os.path.basename(self.archivo_excel.get())}", "info"))
            lector = EmssanarDataReader(self.archivo_excel.get())
            lector._cargar_datos()
            df = lector._df
            
            if df is None or df.empty:
                self.queue.put(("log", "Archivo vacío o sin datos válidos", "error"))
                self.queue.put(("finalizado", False))
                return
            
            total = len(df)
            self.queue.put(("stat", "Total registros en Excel:", str(total)))
            self.queue.put(("log", f"Encontrados {total} registros", "exito"))
            
            df = df.where(pd.notnull(df), None)
            
            # Conectar BD
            self.queue.put(("log", "Conectando a BD...", "info"))
            import psycopg2
            query = Query()
            query.conn.close()
            query.conn = psycopg2.connect(
                host=self.host_db.get(), port=int(self.puerto_db.get()),
                database=self.nombre_db.get(), user=self.usuario_db.get(), password=self.password_db.get()
            )
            self.queue.put(("log", "Conexión establecida", "exito"))
            
            # Verificar existentes
            self.queue.put(("log", "Verificando registros existentes...", "info"))
            existentes = query.obtener_solicitudes_existentes()
            self.queue.put(("stat", "Registros ya existentes:", str(len(existentes))))
            
            # Filtrar nuevos
            df['numero_solicitud_str'] = df['numero_solicitud'].astype(str)
            df_nuevos = df[~df['numero_solicitud_str'].isin(existentes)].copy()
            df_nuevos = df_nuevos.drop(columns=['numero_solicitud_str'])
            
            nuevos = len(df_nuevos)
            self.queue.put(("stat", "Registros nuevos a insertar:", str(nuevos)))
            self.queue.put(("log", f"Nuevos: {nuevos}, Duplicados: {total - nuevos}", "info"))
            
            if nuevos == 0:
                self.queue.put(("log", "No hay registros nuevos", "advertencia"))
                self.queue.put(("finalizado", True))
                query.cerrar_conexion()
                return
            
            # Insertar
            self.queue.put(("log", "Insertando registros...", "info"))
            insertados, errores = 0, 0
            
            for _, row in df_nuevos.iterrows():
                if self.cancelar:
                    self.queue.put(("log", "Cancelado por usuario", "advertencia"))
                    break
                
                try:
                    if query.insertar_solicitud_servicio(row.to_dict(), existentes):
                        insertados += 1
                        progreso = int((insertados / nuevos) * 100)
                        self.queue.put(("progreso", progreso, f"Insertando: {insertados}/{nuevos}"))
                        
                        if insertados % 10 == 0:
                            self.queue.put(("stat", "Registros insertados:", str(insertados)))
                        if insertados % 100 == 0:
                            self.queue.put(("log", f"Procesados {insertados}/{nuevos}...", "info"))
                except Exception as e:
                    errores += 1
                    self.queue.put(("stat", "Errores:", str(errores)))
                    if errores <= 5:
                        self.queue.put(("log", f"Error: {str(e)}", "error"))
            
            self.queue.put(("stat", "Registros insertados:", str(insertados)))
            self.queue.put(("stat", "Errores:", str(errores)))
            query.cerrar_conexion()
            
            self.queue.put(("log", "═" * 50, "info"))
            self.queue.put(("log", f"¡Completado! Insertados: {insertados}", "exito"))
            if errores > 0:
                self.queue.put(("log", f"Errores: {errores}", "error"))
            self.queue.put(("finalizado", True))
            
        except Exception as e:
            self.queue.put(("log", f"Error crítico: {str(e)}", "error"))
            self.queue.put(("finalizado", False))
    
    def _cancelar_migracion(self):
        """Cancela el proceso de migración."""
        if messagebox.askyesno("Cancelar", "¿Cancelar la migración?"):
            self.cancelar = True
            self._agregar_log("Solicitando cancelación...", "advertencia")
    
    def _obtener_lector_excel(self):
        """Obtiene el lector de Excel con cache."""
        archivo = self.archivo_excel.get()
        if self._cache_archivo != archivo or self._cache_excel is None:
            self._cache_excel = EmssanarDataReader(archivo)
            self._cache_archivo = archivo
        return self._cache_excel
    
    def _buscar_afiliado(self):
        """Busca información de un afiliado."""
        c = self.COLORES
        doc = self.doc_busqueda.get().strip()
        
        if not doc:
            messagebox.showwarning("Advertencia", "Ingrese un documento")
            return
        
        if not self.archivo_excel.get():
            messagebox.showerror("Error", "Seleccione un archivo Excel")
            return
        
        try:
            self.tree_resultados.delete(*self.tree_resultados.get_children())
            resultados = self._obtener_lector_excel().consultar_por_afiliado(doc)
            
            if resultados.empty:
                self.label_info_busqueda.config(text=f"⚠ Sin registros para {doc}", fg=c['advertencia'])
                return
            
            columnas = list(resultados.columns)
            self.tree_resultados['columns'] = columnas
            self.tree_resultados['show'] = 'headings'
            
            for col in columnas:
                ancho = min(max(len(str(col)) * 10 + 20, resultados[col].astype(str).str.len().max() * 8 + 20, 80), 300)
                self.tree_resultados.heading(col, text=col, anchor="w")
                self.tree_resultados.column(col, width=int(ancho), minwidth=60, anchor="w")
            
            for _, row in resultados.iterrows():
                self.tree_resultados.insert("", tk.END, values=[str(v) if v is not None else "" for v in row])
            
            self.label_info_busqueda.config(text=f"✓ {len(resultados)} registro(s) para {doc}", fg=c['exito'])
            
        except Exception as e:
            messagebox.showerror("Error", f"Error en búsqueda:\n{str(e)}")
            self.label_info_busqueda.config(text="✗ Error en búsqueda", fg=c['error'])

    # === PESTAÑA CUPS ===
    
    def _crear_pestaña_codigos_cups(self):
        """Pestaña para códigos CUPS."""
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text=" Códigos CUPS ")
        
        # Canvas con scrollbar
        canvas = tk.Canvas(frame, bg=self.COLORES['blanco'], highlightthickness=0)
        scrollbar = ttk.Scrollbar(frame, orient="vertical", command=canvas.yview)
        scrollable = tk.Frame(canvas, bg=self.COLORES['blanco'])
        
        scrollable.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas_window = canvas.create_window((0, 0), window=scrollable, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        def on_canvas_configure(event):
            canvas.itemconfig(canvas_window, width=event.width)
        canvas.bind("<Configure>", on_canvas_configure)
        
        # Función para scroll con mouse/touchpad que funciona en toda el área
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
        
        def _bind_mousewheel(widget):
            """Vincula el scroll del mouse a un widget y todos sus hijos recursivamente."""
            widget.bind("<MouseWheel>", _on_mousewheel)
            widget.bind("<Button-4>", lambda e: canvas.yview_scroll(-1, "units"))  # Linux scroll up
            widget.bind("<Button-5>", lambda e: canvas.yview_scroll(1, "units"))   # Linux scroll down
            for child in widget.winfo_children():
                _bind_mousewheel(child)
        
        # Vincular scroll a canvas y frame scrollable
        _bind_mousewheel(canvas)
        _bind_mousewheel(scrollable)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Contenedor principal dentro del scrollable
        main = tk.Frame(scrollable, bg=self.COLORES['blanco'])
        main.pack(fill=tk.BOTH, expand=True, padx=15, pady=10)
        
        self._crear_seccion_carga_cups(main)
        self._crear_seccion_progreso_cups(main)
        self._crear_seccion_log_cups(main)
        self._crear_seccion_consulta_cups(main)
        
        # Vincular scroll del mouse a todos los widgets después de crearlos
        self.root.after(100, lambda: _bind_mousewheel(scrollable))
    
    def _crear_seccion_carga_cups(self, parent):
        """Sección de carga de archivos CUPS."""
        c = self.COLORES
        frame = ttk.LabelFrame(parent, text="Carga de Códigos CUPS", padding=10)
        frame.pack(fill=tk.X, pady=(0, 10))
        
        # Preparación
        container_prep = tk.Frame(frame, bg=c['fondo_seccion'])
        container_prep.pack(fill=tk.X, pady=3)
        self._crear_label(container_prep, "Preparación:", font_size=9, width=12, anchor="w").pack(side=tk.LEFT, padx=(0, 5))
        self.archivo_preparacion = tk.StringVar()
        ttk.Entry(container_prep, textvariable=self.archivo_preparacion, width=40).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        ttk.Button(container_prep, text="Examinar", command=lambda: self._seleccionar_archivo_cups("preparacion")).pack(side=tk.LEFT)
        
        # Remitidos
        container_rem = tk.Frame(frame, bg=c['fondo_seccion'])
        container_rem.pack(fill=tk.X, pady=3)
        self._crear_label(container_rem, "Remitidos:", font_size=9, width=12, anchor="w").pack(side=tk.LEFT, padx=(0, 5))
        self.archivo_remitidos = tk.StringVar()
        ttk.Entry(container_rem, textvariable=self.archivo_remitidos, width=40).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        ttk.Button(container_rem, text="Examinar", command=lambda: self._seleccionar_archivo_cups("remitidos")).pack(side=tk.LEFT)
        
        # Botones
        container_btns = tk.Frame(frame, bg=c['fondo_seccion'])
        container_btns.pack(fill=tk.X, pady=5)
        self.btn_cargar_cups = ttk.Button(container_btns, text="Cargar Códigos CUPS", command=self._iniciar_carga_cups)
        self.btn_cargar_cups.pack(side=tk.LEFT)
        
        self.label_stats_cups = tk.Label(frame, text="", font=("Segoe UI", 8),
                                         bg=c['fondo_seccion'], fg="#666666", anchor="w")
        self.label_stats_cups.pack(fill=tk.X)
    
    def _crear_seccion_progreso_cups(self, parent):
        """Sección de progreso CUPS."""
        c = self.COLORES
        frame = ttk.LabelFrame(parent, text="Progreso", padding=15)
        frame.pack(fill=tk.X, pady=(0, 10))
        
        self.progreso_cups = ttk.Progressbar(frame, mode='determinate', length=400)
        self.progreso_cups.pack(fill=tk.X, pady=5)
        
        self.label_estado_cups = tk.Label(frame, text="Esperando...", font=("Segoe UI", 9),
                                          bg=c['fondo_seccion'], fg=c['azul_principal'])
        self.label_estado_cups.pack(pady=5)
    
    def _crear_seccion_log_cups(self, parent):
        """Sección de log para operaciones CUPS."""
        c = self.COLORES
        frame = ttk.LabelFrame(parent, text="Log de Operaciones CUPS", padding=10)
        frame.pack(fill=tk.X, pady=(0, 10))
        
        self.log_cups_text = scrolledtext.ScrolledText(frame, height=6, width=80, wrap=tk.WORD,
            bg=c['blanco'], fg="#333333", font=("Consolas", 9),
            insertbackground=c['azul_principal'], selectbackground=c['azul_medio'], selectforeground=c['blanco'])
        self.log_cups_text.pack(fill=tk.BOTH, expand=True)
        
        self.log_cups_text.tag_config("exito", foreground=c['exito'], font=("Consolas", 9, "bold"))
        self.log_cups_text.tag_config("error", foreground=c['error'], font=("Consolas", 9, "bold"))
        self.log_cups_text.tag_config("advertencia", foreground="#FF8C00", font=("Consolas", 9, "bold"))
        self.log_cups_text.tag_config("info", foreground=c['azul_principal'], font=("Consolas", 9))
    
    def _agregar_log_cups(self, mensaje, tipo="info"):
        """Agrega un mensaje al log de CUPS."""
        texto = f"[{datetime.now().strftime('%H:%M:%S')}] {mensaje}\n"
        self.log_cups_text.insert(tk.END, texto, tipo)
        self.log_cups_text.see(tk.END)
        self.root.update()
    
    def _crear_seccion_consulta_cups(self, parent):
        """Sección de consulta CUPS."""
        c = self.COLORES
        frame = ttk.LabelFrame(parent, text="Consulta de Códigos CUPS", padding=10)
        frame.pack(fill=tk.BOTH, expand=True)
        
        # Búsqueda
        frame_busqueda = tk.Frame(frame, bg=c['fondo_seccion'])
        frame_busqueda.pack(fill=tk.X, pady=(0, 10))
        
        self._crear_label(frame_busqueda, "Código:", font_size=9).pack(side=tk.LEFT, padx=(0, 5))
        self.busqueda_codigo_cups = tk.StringVar()
        entry_codigo = ttk.Entry(frame_busqueda, textvariable=self.busqueda_codigo_cups, width=15)
        entry_codigo.pack(side=tk.LEFT, padx=(0, 10))
        entry_codigo.bind('<Return>', lambda e: self._ejecutar_busqueda_cups())
        
        self._crear_label(frame_busqueda, "Nombre:", font_size=9).pack(side=tk.LEFT, padx=(0, 5))
        self.busqueda_nombre_cups = tk.StringVar()
        entry_nombre = ttk.Entry(frame_busqueda, textvariable=self.busqueda_nombre_cups, width=25)
        entry_nombre.pack(side=tk.LEFT, padx=(0, 10))
        entry_nombre.bind('<Return>', lambda e: self._ejecutar_busqueda_cups())
        
        self.filtro_preparacion = tk.BooleanVar()
        ttk.Checkbutton(frame_busqueda, text="Prep. Especial", variable=self.filtro_preparacion).pack(side=tk.LEFT, padx=(0, 5))
        
        self.filtro_remitido = tk.BooleanVar()
        ttk.Checkbutton(frame_busqueda, text="Remitido", variable=self.filtro_remitido).pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Button(frame_busqueda, text="Buscar", command=self._ejecutar_busqueda_cups).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(frame_busqueda, text="Limpiar", command=self._limpiar_busqueda_cups).pack(side=tk.LEFT)
        
        self.label_resultados_cups = tk.Label(frame, text="", font=("Segoe UI", 9),
                                              bg=c['fondo_seccion'], fg="#666666", anchor="w")
        self.label_resultados_cups.pack(fill=tk.X)
        
        # Tabla
        frame_tabla = tk.Frame(frame, bg=c['fondo_seccion'])
        frame_tabla.pack(fill=tk.BOTH, expand=True)
        
        scrollbar_y = ttk.Scrollbar(frame_tabla, orient=tk.VERTICAL)
        scrollbar_y.pack(side=tk.RIGHT, fill=tk.Y)
        scrollbar_x = ttk.Scrollbar(frame_tabla, orient=tk.HORIZONTAL)
        scrollbar_x.pack(side=tk.BOTTOM, fill=tk.X)
        
        self.tree_cups = ttk.Treeview(frame_tabla, columns=("codigo", "nombre", "preparacion", "remitido"),
                                      show="headings", yscrollcommand=scrollbar_y.set,
                                      xscrollcommand=scrollbar_x.set, height=10)
        
        for col, (text, width, anchor) in {
            "codigo": ("Código CUPS", 120, tk.CENTER),
            "nombre": ("Nombre del Estudio", 400, tk.W),
            "preparacion": ("Preparación Especial", 150, tk.CENTER),
            "remitido": ("Remitido", 120, tk.CENTER)
        }.items():
            self.tree_cups.heading(col, text=text)
            self.tree_cups.column(col, width=width, anchor=anchor)
        
        self.tree_cups.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar_y.config(command=self.tree_cups.yview)
        scrollbar_x.config(command=self.tree_cups.xview)
    
    def _seleccionar_archivo_cups(self, tipo):
        """Selecciona archivo para códigos CUPS."""
        archivo = filedialog.askopenfilename(
            title=f"Seleccionar archivo de {tipo}",
            filetypes=[("Archivos Excel", "*.xlsx *.xls"), ("Todos", "*.*")]
        )
        if archivo:
            (self.archivo_preparacion if tipo == "preparacion" else self.archivo_remitidos).set(archivo)
    
    def _iniciar_carga_cups(self):
        """Inicia carga de códigos CUPS."""
        if self.en_proceso_cups:
            messagebox.showwarning("Advertencia", "Ya hay un proceso en ejecución")
            return
        
        archivo_prep = self.archivo_preparacion.get().strip() or None
        archivo_rem = self.archivo_remitidos.get().strip() or None
        
        if not archivo_prep and not archivo_rem:
            messagebox.showerror("Error", "Seleccione al menos un archivo")
            return
        
        self.btn_cargar_cups.config(state=tk.DISABLED)
        self.progreso_cups.config(mode='indeterminate')
        self.progreso_cups.start()
        self.en_proceso_cups = True
        self._iniciar_animacion_carga(self.label_estado_cups, "Cargando datos")
        
        # Limpiar log antes de iniciar
        self.log_cups_text.delete(1.0, tk.END)
        self._agregar_log_cups("Iniciando carga de códigos CUPS...", "info")
        
        if archivo_prep:
            self._agregar_log_cups(f"Archivo preparación: {os.path.basename(archivo_prep)}", "info")
        if archivo_rem:
            self._agregar_log_cups(f"Archivo remitidos: {os.path.basename(archivo_rem)}", "info")
        
        threading.Thread(target=self._procesar_carga_cups, args=(archivo_prep, archivo_rem), daemon=True).start()
    
    def _procesar_carga_cups(self, archivo_prep, archivo_rem):
        """Procesa carga de CUPS (hilo separado)."""
        try:
            self.queue.put(("cups_log", "Leyendo archivos Excel...", "info"))
            reader = CupsDataReader(ruta_preparacion=archivo_prep, ruta_remitidos=archivo_rem)
            
            self.queue.put(("cups_estado", "Cargando archivos Excel..."))
            df = reader.cargar_datos()
            
            if df is None or df.empty:
                self.queue.put(("cups_log", "No se pudieron cargar datos de los archivos", "error"))
                self.queue.put(("cups_error", "No se pudieron cargar datos"))
                return
            
            self.queue.put(("cups_log", f"✓ Datos cargados: {len(df)} registros encontrados", "exito"))
            self.queue.put(("cups_estado", f"Cargados: {len(df)} registros"))
            
            self.queue.put(("cups_log", "Conectando a base de datos...", "info"))
            self.queue.put(("cups_estado", "Conectando a BD..."))
            
            db = CupsQuery(
                host=self.host_db.get(), port=int(self.puerto_db.get()),
                database=self.nombre_db.get(), user=self.usuario_db.get(), password=self.password_db.get()
            )
            
            self.queue.put(("cups_log", f"✓ Conexión establecida ({self.host_db.get()}:{self.puerto_db.get()})", "exito"))
            self.queue.put(("cups_estado", "Procesando datos..."))
            self.queue.put(("cups_log", "Procesando e insertando datos...", "info"))
            
            stats = db.procesar_dataframe(df)
            
            # Log detallado de resultados
            self.queue.put(("cups_log", "═" * 45, "info"))
            self.queue.put(("cups_log", "RESUMEN DE OPERACIÓN:", "info"))
            self.queue.put(("cups_log", f"  • Total procesados: {stats['total']}", "info"))
            self.queue.put(("cups_log", f"  • Registros nuevos insertados: {stats['insertados']}", "exito"))
            self.queue.put(("cups_log", f"  • Registros actualizados: {stats['actualizados']}", "advertencia" if stats['actualizados'] > 0 else "info"))
            
            if stats['errores'] > 0:
                self.queue.put(("cups_log", f"  • Errores: {stats['errores']}", "error"))
            else:
                self.queue.put(("cups_log", f"  • Errores: 0", "exito"))
            
            self.queue.put(("cups_log", "═" * 45, "info"))
            self.queue.put(("cups_log", "¡Proceso completado exitosamente!", "exito"))
            
            mensaje = (f"Total: {stats['total']}\n• Nuevos: {stats['insertados']}\n"
                      f"• Actualizados: {stats['actualizados']}\n• Errores: {stats['errores']}")
            
            self.queue.put(("cups_resultado", mensaje, stats))
            db.cerrar_conexion()
            self.queue.put(("cups_log", "Conexión a BD cerrada", "info"))
            
        except Exception as e:
            self.queue.put(("cups_log", f"Error crítico: {str(e)}", "error"))
            self.queue.put(("cups_error", f"Error: {str(e)}"))
    
    def _ejecutar_busqueda_cups(self):
        """Ejecuta búsqueda de códigos CUPS."""
        codigo = self.busqueda_codigo_cups.get().strip() or None
        nombre = self.busqueda_nombre_cups.get().strip() or None
        prep = self.filtro_preparacion.get() if self.filtro_preparacion.get() else None
        rem = self.filtro_remitido.get() if self.filtro_remitido.get() else None
        
        threading.Thread(target=self._procesar_busqueda_cups, args=(codigo, nombre, prep, rem), daemon=True).start()
    
    def _procesar_busqueda_cups(self, codigo, nombre, prep, rem):
        """Procesa búsqueda CUPS (hilo separado)."""
        try:
            db = CupsQuery(
                host=self.host_db.get(), port=int(self.puerto_db.get()),
                database=self.nombre_db.get(), user=self.usuario_db.get(), password=self.password_db.get()
            )
            
            resultados = db.buscar_con_filtros(codigo_cups=codigo, nombre_busqueda=nombre,
                                               preparacion_especial=prep, remitido=rem, limite=1000)
            total = db.contar_registros(codigo_cups=codigo, nombre_busqueda=nombre,
                                        preparacion_especial=prep, remitido=rem)
            db.cerrar_conexion()
            
            self.queue.put(("cups_busqueda_resultado", resultados, total))
            
        except Exception as e:
            self.queue.put(("cups_busqueda_error", f"Error: {str(e)}"))
    
    def _limpiar_busqueda_cups(self):
        """Limpia campos de búsqueda CUPS."""
        self.busqueda_codigo_cups.set("")
        self.busqueda_nombre_cups.set("")
        self.filtro_preparacion.set(False)
        self.filtro_remitido.set(False)
        
        for item in self.tree_cups.get_children():
            self.tree_cups.delete(item)
        
        self.label_resultados_cups.config(text="Ingrese criterios y presione 'Buscar'", fg="#666666")
    
    def _mostrar_resultados_busqueda_cups(self, resultados, total):
        """Muestra resultados de búsqueda CUPS."""
        c = self.COLORES
        
        for item in self.tree_cups.get_children():
            self.tree_cups.delete(item)
        
        for r in resultados:
            self.tree_cups.insert("", tk.END, values=(
                r['codigo_cups'], r['nombre_estudio'] or "",
                "Sí" if r['preparacion_especial'] else "No",
                "Sí" if r['remitido'] else "No"
            ))
        
        if total > 0:
            self.label_resultados_cups.config(text=f"{len(resultados)} de {total} registros (máx 1000)", fg=c['exito'])
        else:
            self.label_resultados_cups.config(text="Sin resultados", fg=c['error'])

    # === COLA DE MENSAJES ===
    
    def _verificar_cola(self):
        """Verifica la cola de mensajes del hilo de migración."""
        c = self.COLORES
        
        try:
            while True:
                msg = self.queue.get_nowait()
                tipo = msg[0]
                
                if tipo == "log":
                    self._agregar_log(msg[1], msg[2])
                
                elif tipo == "stat":
                    self.stats_vars[msg[1]].set(msg[2])
                
                elif tipo == "progreso":
                    self.progreso['value'] = msg[1]
                    self.label_progreso.config(text=msg[2])
                
                elif tipo == "finalizado":
                    self.en_proceso = False
                    self._detener_animacion_carga()
                    self.btn_cancelar.config(state=tk.DISABLED)
                    self.progreso['value'] = 100
                    self.label_progreso.config(text="Completado")
                    
                    if msg[1]:
                        messagebox.showinfo("Completado", "Migración completada correctamente")
                    else:
                        messagebox.showerror("Error", "Migración terminó con errores")
                
                elif tipo == "cups_estado":
                    self.label_estado_cups.config(text=msg[1], fg=c['azul_principal'])
                
                elif tipo == "cups_log":
                    self._agregar_log_cups(msg[1], msg[2])
                
                elif tipo == "cups_resultado":
                    self._detener_animacion_carga()
                    self.progreso_cups.stop()
                    self.progreso_cups.config(mode='determinate', value=100)
                    self.label_estado_cups.config(text="Carga completada", fg=c['exito'])
                    self.label_stats_cups.config(text=msg[1], fg="#333333")
                    self.en_proceso_cups = False
                    self.btn_cargar_cups.config(state=tk.NORMAL)
                    messagebox.showinfo("Completado", f"Carga completada:\n\n{msg[1]}")
                
                elif tipo == "cups_error":
                    self._detener_animacion_carga()
                    self.progreso_cups.stop()
                    self.progreso_cups.config(mode='determinate', value=0)
                    self.label_estado_cups.config(text="Error", fg=c['error'])
                    self.en_proceso_cups = False
                    self.btn_cargar_cups.config(state=tk.NORMAL)
                    messagebox.showerror("Error", msg[1])
                
                elif tipo == "cups_busqueda_resultado":
                    self._mostrar_resultados_busqueda_cups(msg[1], msg[2])
                
                elif tipo == "cups_busqueda_error":
                    self.label_resultados_cups.config(text=msg[1], fg=c['error'])
                    messagebox.showerror("Error", msg[1])
        
        except queue.Empty:
            pass
        
        self.root.after(100, self._verificar_cola)


def main():
    root = tk.Tk()
    EmssanarGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
