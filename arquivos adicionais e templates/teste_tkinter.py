import pandas as pd
import os
import tkinter as tk
from tkinter import filedialog
from datetime import datetime
from datetime import timedelta
from datetime import date
from openpyxl import Workbook, load_workbook
import configparser
import shutil

def select_base_file():
    pass

def select_novos_file():
    pass

def execute_functions():
    pass

def get_current_year():
    return datetime.now().year

# Ler os valores do arquivo pac.ini
config = configparser.ConfigParser()
config.read('pac.ini', encoding='utf-8')
base_file_path = config.get('Arquivo', 'Base_de_dados', fallback='')
novos_file_path = config.get('Arquivo', 'Novos_dados', fallback='')

window = tk.Tk()
window.title("Interface de Usuário")
window.geometry("500x420")

base_frame = tk.Frame(window)
base_frame.pack()

base_file_label = tk.Label(base_frame, text="Arquivo Base:")
base_file_label.pack(side=tk.LEFT)

base_file_entry = tk.Entry(base_frame, width=50)
base_file_entry.insert(tk.END, base_file_path)
base_file_entry.pack(side=tk.LEFT, padx=10)

select_base_file_button = tk.Button(base_frame, text="Selecionar", command=select_base_file)
select_base_file_button.pack(side=tk.LEFT)

novos_frame = tk.Frame(window)
novos_frame.pack()

novos_file_label = tk.Label(novos_frame, text="Novos dados:")
novos_file_label.pack(side=tk.LEFT)

novos_file_entry = tk.Entry(novos_frame, width=50)
novos_file_entry.insert(tk.END, novos_file_path)
novos_file_entry.pack(side=tk.LEFT, padx=10)

select_novos_file_button = tk.Button(novos_frame, text="Selecionar", command=select_novos_file)
select_novos_file_button.pack(side=tk.LEFT)

ano_frame = tk.Frame(window)
ano_frame.pack()

ano_label = tk.Label(ano_frame, text="          Ano:   ")
ano_label.pack(side=tk.LEFT)

ano_entry = tk.Entry(ano_frame, width=5)
ano_entry.insert(tk.END, get_current_year())
ano_entry.pack(side=tk.LEFT)

ano_label = tk.Label(ano_frame, text="                                                                                                           ")
ano_label.pack(side=tk.LEFT)

execute_button = tk.Button(window, text="Executar", command=execute_functions)
execute_button.pack()

console_frame = tk.Frame(window)
console_frame.pack(expand=True, fill=tk.BOTH)

console_label = tk.Label(console_frame, text="Console:")
console_label.pack()

console_text = tk.Text(console_frame, width=40, height=10)
console_text.pack(expand=True, fill=tk.BOTH)

# Botão para fechar a janela e encerrar o programa
def close_window():
    window.destroy()
    window.quit()

close_button = tk.Button(window, text="Fechar", command=close_window)
close_button.pack()

window.mainloop()
