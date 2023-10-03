# -*- coding: utf-8 -*-
"""
Created on Tue Jun 20 07:38:28 2023

@author: brgris
"""
# import time
import pandas as pd
from tkinter import filedialog
from selenium import webdriver
from selenium.webdriver.common.by import By
import tkinter as tk
from tkinter import ttk
from selenium.webdriver.chrome.options import Options

# Configurar as opções do Chrome
chrome_options = Options()
chrome_options.add_argument('--headless')  # Configurar o modo sem cabeçalho


def submit():
    global navegador
    login = login_entry.get()
    password = password_entry.get()
    login_password.append(login)
    login_password.append(password)
    navegador = webdriver.Chrome(options=chrome_options)
    link = "https://chi597a.itaipu.binacional/aplicacoes/sno.nsf/Frame?OpenFrameset&login"
    navegador.get(link)
    login_input = navegador.find_element(By.XPATH,'//*[@id="Username_A"]')
    login_input.send_keys(login)
    password_input = navegador.find_element(By.XPATH,'//*[@id="Password_A"]')
    password_input.send_keys(password)
    login_button = navegador.find_element(By.XPATH,'//*[@id="submitB"]')
    login_button.click()

def extrair_hist():
    navegador = webdriver.Chrome(options=chrome_options)
    # link_hist = "https://chi597a.itaipu.binacional/aplicacoes/sno.nsf/formViewSN_RevCodigoBrasil?OpenForm"
    link_hist = "https://chi597a.itaipu.binacional/aplicacoes/sno.nsf/SN_RevTipo?SearchView&Query=AO"

    navegador.get(link_hist)
    total_elements = len(navegador.find_elements(By.XPATH, '//*[@id="celView"]/div/table/tbody/tr[2]/td[2]/table/tbody/tr'))
    # Create empty lists to store the extracted texts
    doc_num = []
    doc_descr = []
    doc_motivo = []
    doc_data_aprov = []
    doc_data_ultima_rev = []
    doc_data_cancel = []

    def extrair_dados(i):
        global df
        nonlocal doc_num, doc_descr, doc_motivo, doc_data_aprov, doc_data_ultima_rev, doc_data_cancel
        num_xpath = f'//*[@id="celView"]/div/table/tbody/tr[2]/td[2]/table/tbody/tr[{i}]/td[6]'
        descr_xpath = f'//*[@id="celView"]/div/table/tbody/tr[2]/td[2]/table/tbody/tr[{i}]/td[7]'
        motivo_xpath = f'//*[@id="celView"]/div/table/tbody/tr[2]/td[2]/table/tbody/tr[{i}]/td[8]'
        data_aprov_xpath = f'//*[@id="celView"]/div/table/tbody/tr[2]/td[2]/table/tbody/tr[{i}]/td[9]'
        data_ultima_rev_xpath = f'//*[@id="celView"]/div/table/tbody/tr[2]/td[2]/table/tbody/tr[{i}]/td[10]'
        data_cancel_xpath = f'//*[@id="celView"]/div/table/tbody/tr[2]/td[2]/table/tbody/tr[{i}]/td[11]'
        
        num_element = navegador.find_element(By.XPATH, num_xpath)
        descr_element = navegador.find_element(By.XPATH, descr_xpath)
        motivo_element = navegador.find_element(By.XPATH, motivo_xpath)
        data_aprov_element = navegador.find_element(By.XPATH, data_aprov_xpath)
        data_ultima_rev_element = navegador.find_element(By.XPATH, data_ultima_rev_xpath)
        data_cancel_element = navegador.find_element(By.XPATH, data_cancel_xpath)
        
        num_text = num_element.text
        # print(num_text)
        descr_text = descr_element.text
        motivo_text =  motivo_element.text
        data_aprov_text = data_aprov_element.text
        data_ultima_rev_text = data_ultima_rev_element.text
        data_cancel_text = data_cancel_element.text
        
        doc_num.append(num_text)
        doc_descr.append(descr_text)
        doc_motivo.append(motivo_text)
        doc_data_aprov.append(data_aprov_text)
        doc_data_ultima_rev.append(data_ultima_rev_text)
        doc_data_cancel.append(data_cancel_text)
        
        progress = (i - 2) / (total_elements - 2) * 100
        progress_bar['value'] = progress
        dialog_box.update_idletasks()
        
        if i < total_elements:
            dialog_box.after(10, lambda: extrair_dados(i + 1))
        else:
            navegador.quit()
            df = pd.DataFrame({'Documento': doc_num, 'Descrição': doc_descr, 'Motivo': doc_motivo, 'Data_aprovação': doc_data_aprov, 'Data_última_revisão': doc_data_ultima_rev, 'Data_cancelamento': doc_data_cancel})
            # Faça o que precisar com o DataFrame df
            # return df
    # Iniciar extração de dados
    extrair_dados(2)


def extrair_vigentes():
    navegador = webdriver.Chrome(options=chrome_options)
    # link_hist = "https://chi597a.itaipu.binacional/aplicacoes/sno.nsf/formViewSN_RevCodigoBrasil?OpenForm"
    link_vigentes = "https://chi597a.itaipu.binacional/aplicacoes/sno.nsf/SN_ViewTP_Doc?OpenForm&TP=AO"
    navegador.get(link_vigentes)
    
    total_elements = len(navegador.find_elements(By.XPATH, '//*[@id="tabview"]/table/tbody/tr'))
    # Create empty lists to store the extracted texts
    doc_num = []
    doc_descr = []
    doc_descr_es= []
    doc_data_aprov = []
    doc_data_cancel = []

    def extrair_dados(i):
        global df_vigentes
        nonlocal doc_num, doc_descr, doc_descr_es, doc_data_aprov, doc_data_cancel
        num_xpath = f'//*[@id="tabview"]/table/tbody/tr[{i}]/td[6]'
        descr_xpath = f'//*[@id="tabview"]/table/tbody/tr[{i}]/td[7]'
        descr_es_xpath = f'//*[@id="tabview"]/table/tbody/tr[{i}]/td[8]'
        data_aprov_xpath = f'//*[@id="tabview"]/table/tbody/tr[{i}]/td[9]'
        data_cancel_xpath = f'//*[@id="tabview"]/table/tbody/tr[{i}]/td[10]'
        
        num_element = navegador.find_element(By.XPATH, num_xpath)
        descr_element = navegador.find_element(By.XPATH, descr_xpath)
        descr_es_element = navegador.find_element(By.XPATH, descr_es_xpath)
        data_aprov_element = navegador.find_element(By.XPATH, data_aprov_xpath)
        data_cancel_element = navegador.find_element(By.XPATH, data_cancel_xpath)
        
        num_text = num_element.text
        descr_text = descr_element.text
        descr_es_text =  descr_es_element.text
        data_aprov_text = data_aprov_element.text
        data_cancel_text = data_cancel_element.text
        
        doc_num.append(num_text)
        doc_descr.append(descr_text)
        doc_descr_es.append(descr_es_text)
        doc_data_aprov.append(data_aprov_text)
        doc_data_cancel.append(data_cancel_text)
        
        progress = (i - 2) / (total_elements - 2) * 100
        progress_bar_vig['value'] = progress
        dialog_box.update_idletasks()
        
        if i < total_elements:
            dialog_box.after(10, lambda: extrair_dados(i + 1))
        else:
            navegador.quit()
            df_vigentes = pd.DataFrame({'Documento': doc_num, 'Descrição': doc_descr, 'Descrição_es': doc_descr_es, 'Data_aprovação': doc_data_aprov,'Data_cancelamento': doc_data_cancel})
            # Faça o que precisar com o DataFrame df
            # return df
    # Iniciar extração de dados
    extrair_dados(3)


def exportar_result():
    pasta_destino = filedialog.askdirectory()
    df_result = pd.concat([df,df_vigentes])
    if pasta_destino:
        caminho_arquivo = pasta_destino + '/Dados_SNO.xlsx'
        df_result.to_excel(caminho_arquivo, index=False)
        print("Resultado salvo como Excel em:", caminho_arquivo)


def close_window():
    dialog_box.quit()
    dialog_box.destroy()

dialog_box = tk.Tk()
dialog_box.title("Login and Password")
dialog_box.geometry("300x500")

login_label = tk.Label(dialog_box, text="Login:")
login_label.pack()
login_entry = tk.Entry(dialog_box)
login_entry.pack()

password_label = tk.Label(dialog_box, text="Password:")
password_label.pack()
password_entry = tk.Entry(dialog_box, show="*")
password_entry.pack()

submit_button = tk.Button(dialog_box, text="Submit", command=submit)
submit_button.pack(pady=10)

exec_button = tk.Button(dialog_box, text="Extrair dados AO_historicos", command=extrair_hist)
exec_button.pack(pady=10)

progress_bar = ttk.Progressbar(dialog_box, length=200, mode='determinate')
progress_bar.pack(pady=10)

exec_button = tk.Button(dialog_box, text="Extrair dados AO_vigentes", command=extrair_vigentes)
exec_button.pack(pady=10)

progress_bar_vig = ttk.Progressbar(dialog_box, length=200, mode='determinate')
progress_bar_vig.pack(pady=10)

botao_salvar = tk.Button(dialog_box, text="Salvar DataFrame", command=exportar_result)
botao_salvar.pack(pady=10)

close_button = tk.Button(dialog_box, text="Fechar", command=close_window, width=20)
close_button.pack(pady=10)

login_password = []

dialog_box.protocol("WM_DELETE_WINDOW", close_window)  # Handle window close event
dialog_box.mainloop()









# wait = WebDriverWait(driver, 10)
# element = wait.until(EC.visibility_of_element_located((By.XPATH, '//*[@id="RicoTree_Desc_tree1_normativostra"]')))


# hist = navegador.find_element(By.XPATH,'//*[@id="RicoTree_Desc_tree1_normativostra"]')
# hist.click()

# opse_hist = navegador.find_element(By.XPATH,'//*[@id="RicoTree_Desc_tree1_docrevogadosOPSE"]')
# opse_hist.click()


