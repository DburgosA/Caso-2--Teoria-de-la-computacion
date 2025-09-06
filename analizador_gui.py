import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import os
from mini_py_lexer import MiniPyLexer, TokenType

class AnalizadorLexicoGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Analizador Léxico Mini-Python")
        self.root.geometry("800x600")
        self.root.configure(bg='#f0f0f0')
        
        self.archivo_actual = ""
        self.tokens = []
        
        self.crear_interfaz()
        
    def crear_interfaz(self):
        # Título
        titulo = tk.Label(
            self.root,
            text="Analizador Léxico para Mini-Python",
            font=('Arial', 16, 'bold'),
            bg='#2c3e50',
            fg='white',
            pady=10
        )
        titulo.pack(fill='x')
        
        # Frame principal
        main_frame = tk.Frame(self.root, bg='#f0f0f0')
        main_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Sección de selección de archivo
        file_frame = tk.LabelFrame(
            main_frame,
            text="Seleccionar Archivo Python",
            font=('Arial', 12, 'bold'),
            bg='#f0f0f0'
        )
        file_frame.pack(fill='x', pady=(0, 10))
        
        # Entrada de archivo
        input_frame = tk.Frame(file_frame, bg='#f0f0f0')
        input_frame.pack(fill='x', padx=10, pady=10)
        
        self.archivo_entry = tk.Entry(
            input_frame,
            font=('Arial', 10),
            width=60
        )
        self.archivo_entry.pack(side='left', fill='x', expand=True, padx=(0, 5))
        
        examinar_btn = tk.Button(
            input_frame,
            text="Examinar",
            command=self.seleccionar_archivo,
            font=('Arial', 10),
            bg='#3498db',
            fg='white'
        )
        examinar_btn.pack(side='right')
        
        # Botón de análisis
        analizar_btn = tk.Button(
            file_frame,
            text="Analizar Archivo",
            command=self.analizar_archivo,
            font=('Arial', 12, 'bold'),
            bg='#27ae60',
            fg='white',
            pady=5
        )
        analizar_btn.pack(pady=(0, 10))
        
        # Área de resultados
        resultados_frame = tk.LabelFrame(
            main_frame,
            text="Tokens Encontrados",
            font=('Arial', 12, 'bold'),
            bg='#f0f0f0'
        )
        resultados_frame.pack(fill='both', expand=True)
        
        # Tabla de tokens
        columns = ('No.', 'Tipo', 'Valor', 'Línea', 'Columna')
        self.tabla_tokens = ttk.Treeview(
            resultados_frame,
            columns=columns,
            show='headings',
            height=15
        )
        
        # Configurar columnas
        self.tabla_tokens.heading('#1', text='No.')
        self.tabla_tokens.heading('#2', text='Tipo de Token')
        self.tabla_tokens.heading('#3', text='Valor')
        self.tabla_tokens.heading('#4', text='Línea')
        self.tabla_tokens.heading('#5', text='Columna')
        
        self.tabla_tokens.column('#1', width=50, anchor='center')
        self.tabla_tokens.column('#2', width=120, anchor='center')
        self.tabla_tokens.column('#3', width=150, anchor='w')
        self.tabla_tokens.column('#4', width=60, anchor='center')
        self.tabla_tokens.column('#5', width=60, anchor='center')
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(
            resultados_frame,
            orient='vertical',
            command=self.tabla_tokens.yview
        )
        self.tabla_tokens.configure(yscrollcommand=scrollbar.set)
        
        # Empaquetar tabla y scrollbar
        self.tabla_tokens.pack(side='left', fill='both', expand=True, padx=(10, 0), pady=10)
        scrollbar.pack(side='right', fill='y', padx=(0, 10), pady=10)
        
        # Barra de estado
        self.estado = tk.Label(
            self.root,
            text="Seleccione un archivo Python para analizar",
            font=('Arial', 10),
            bg='#ecf0f1',
            anchor='w',
            padx=10
        )
        self.estado.pack(fill='x', side='bottom')
        
    def seleccionar_archivo(self):
        """Abrir diálogo para seleccionar archivo"""
        archivo = filedialog.askopenfilename(
            title="Seleccionar archivo Python",
            filetypes=[
                ("Archivos Python", "*.py"),
                ("Archivos de texto", "*.txt"),
                ("Todos los archivos", "*.*")
            ]
        )
        
        if archivo:
            self.archivo_actual = archivo
            self.archivo_entry.delete(0, tk.END)
            self.archivo_entry.insert(0, archivo)
            self.estado.config(text=f"Archivo seleccionado: {os.path.basename(archivo)}")
            
    def analizar_archivo(self):
        """Analizar el archivo seleccionado"""
        if not self.archivo_actual:
            messagebox.showwarning("Advertencia", "Por favor seleccione un archivo primero.")
            return
            
        try:
            # Leer archivo
            with open(self.archivo_actual, 'r', encoding='utf-8') as file:
                contenido = file.read()
            
            # Crear lexer y analizar
            lexer = MiniPyLexer(contenido)
            self.tokens = lexer.tokenize()
            
            # Mostrar resultados
            self.mostrar_tokens()
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al analizar el archivo:\n{str(e)}")
            
    def mostrar_tokens(self):
        """Mostrar tokens en la tabla"""
        # Limpiar tabla
        for item in self.tabla_tokens.get_children():
            self.tabla_tokens.delete(item)
        
        # Filtrar tokens relevantes (sin NEWLINE, EOF)
        tokens_mostrar = [
            t for t in self.tokens 
            if t.type not in [TokenType.NEWLINE, TokenType.EOF]
        ]
        
        # Insertar tokens en la tabla
        for i, token in enumerate(tokens_mostrar, 1):
            self.tabla_tokens.insert('', 'end', values=(
                i,
                token.type.value,
                token.value if token.value else '(vacío)',
                token.line,
                token.column
            ))
        
        # Actualizar estado
        total_tokens = len(tokens_mostrar)
        errores = len([t for t in self.tokens if t.type == TokenType.ERROR])
        
        if errores > 0:
            estado_text = f"Análisis completado: {total_tokens} tokens encontrados, {errores} errores"
        else:
            estado_text = f"Análisis exitoso: {total_tokens} tokens encontrados sin errores"
            
        self.estado.config(text=estado_text)

def main():
    root = tk.Tk()
    app = AnalizadorLexicoGUI(root)
    
    # Centrar ventana
    root.update_idletasks()
    x = (root.winfo_screenwidth() // 2) - (root.winfo_width() // 2)
    y = (root.winfo_screenheight() // 2) - (root.winfo_height() // 2)
    root.geometry(f"+{x}+{y}")
    
    root.mainloop()

if __name__ == "__main__":
    main()
