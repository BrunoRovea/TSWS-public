""" 
    Itaipu Binacional - Operação de Usina e Subestações (OPUO.DT)
    Autores: Bruno Rovea, Bruno Gris 
    Foz do Iguaçú, 28/Setembro/2023
    V1.0

    
    U10*TOMADA_DAGUA AGUAS EQUILIBRADAS*SV
    U10*TOMADA_DAGUA*SV
    *U05*excit*Corr*Av*

    Problemas com o tag_search


"""

#%%
import tkinter as tk
from tkinter import *
from tkinter import ttk
from tkinter import filedialog
import glob
from GSSLibs import TSWS, log
import pandas as pd
import datetime 
from time import sleep
import threading
import re
from time import sleep



# Cria a janela, mas logo em seguida a fecha
root = Tk()



# Classe das funcionalidade dos botões
class Funcs():
    # Limpa os campos das entrys especificadas
    def limpa_tela(self):
        # Nome destas entrys deve estar igual as entrys da def widgets
        self.step_amount_entry.delete(0, END)
        self.filtro_entry.delete(0, END)
        self.dinicio_entry.delete(0, END)
        self.dfim_entry.delete(0, END)
        self.nomep_entry.delete(0, END)

    def conectTSWS(self):
        # Setup na biblioteca
        if (not(log.setup('GSSLib_test'))):
            print('Conectado ao TSWS no modo desenvolvimento')
        else:
            print('Falha ao conectar-se ao TSWS')
        # Inicializa no modo desenvolvimento
        self.tsws = TSWS.setup('./config.json')

    def toogle_snapshot(self):
        if not self.snapshot_running:
            self.snapshot_running = True
            self.bt_snapshot.config(text="Parar Snapshot")
            self.start_snapshot_thread()
        else:
            self.snapshot_running = False
            self.bt_snapshot.config(text="Iniciar Snapshot")

    def start_snapshot_thread(self):
        self.snapshot_thread = threading.Thread(target=self.snapshot_loop)
        self.snapshot_thread.start()

    def stop_snapshot_thread(self):
        self.snapshot_running = False

    def snapshot_loop(self):
        # Colocar isso aqui em loop ñ é trivial
        # O botão trava a thread da janela, crashando o programa

        # Limpa a lista
        self.listaEvt.delete(*self.listaEvt.get_children())
        
        # Especificação da Tag a ser procurada (entrada do usuário), padrão Pi
        # entry.get() irá coletar a informação contida na entry na hora da execução desta linha
        
        query = self.filtro_entry.get()

        # Cria uma lista vazia que será appendada no for
        response_list = []

        if self.snapshot_running:
            # Caso ñ preencha o filtro, o arquivo lista_evt existe e foi carregado do excel
            if query == '':
                # Percorre a lista carregada do excel
                for tag in self.tag_list:
                    # Retorna o último valor registrado na tagname (rápido)
                    value    = self.tsws.get.time_series_snapshot(tag)

                    # Extrai o que interessa do json retornado pelo time_series_snapshot
                    response = value.json()['timeSeriesResponse']

                    # appenda a lista vazia criada anteriormente, em cada iteração do for
                    response_list.append(response)

                # Transforma a lista appendada no for em um dataframe a ser escrito na tela do tkinter
                events = pd.DataFrame.from_dict(response_list)
            else:
                # Caso o campo do filtro esteja preenchido, procurar snapshot pelo filtro do usuário
                tag_name = self.tsws.get.tag_search(query).json()['tagResponse'][0]['tagName']

                # O dicionário contendo os dados do snapshot
                value    = self.tsws.get.time_series_snapshot(tag_name)
                response = value.json()['timeSeriesResponse']

                # Força response a ser uma lista e converte-o para df
                # Nesse caso, response é apenas um valor
                events   = pd.DataFrame([response])



            # Estabelece os índices do df segundo a lista do frame 3
            events['Índice'] = pd.Series(events.index)
            events['Data'] = events['timestamp'].str[:10]
            events['Hora'] = events['timestamp'].str[12:19]
            events['Local'] = events['tagName'].str[:8]
            events['Evento'] = events['tagName'].str[9:]
            events['Estado'] = events['value']

            # Definir as colunas que serão utilizadas
            columns = ['Índice', 'Data', 'Hora', 'Local', 'Evento', 'Estado']

            # Remover a coluna 'value' do DataFrame
            # Categoriza o dataframe 
            self.events = events[columns]

            # Especifica o nome de cada coluna
            self.listaEvt.heading("#0", text="")
            self.listaEvt.heading("#1", text='Índice')
            self.listaEvt.heading("#2", text='Data')
            self.listaEvt.heading("#3", text='Hora')
            self.listaEvt.heading("#4", text='Local')
            self.listaEvt.heading("#5", text='Alarme')
            self.listaEvt.heading("#6", text='Estado')
            
            # Isso aq é meio confuso, divide o número 500 nas proporções de cada coluna
            self.listaEvt.column("#0", width=1)
            self.listaEvt.column("#1", width=60)
            self.listaEvt.column("#2", width=100)
            self.listaEvt.column("#3", width=100)
            self.listaEvt.column("#4", width=100)
            self.listaEvt.column("#5", width=300)
            self.listaEvt.column("#6", width=100)

            # Adiciona o df events na lista criada no frame 3
            # Adiciona lunha por linha, percorrendo as row
            # lista.insert        
            for index, row in events.iterrows():
                self.listaEvt.insert("", "end", values=(row['Índice'], row['Data'], row['Hora'], row['Local'], row['Evento'], row['Estado']))



            # Verifica se o botão "Snapshot" foi pressionado novamente
            if not self.snapshot_running:
                return

            self.root.after(5000, self.snapshot_loop)

    def buscar_evt(self):
       # Função para detecção dos eventos qye possuem a string ' RET - ' na coluna Estado
        def contem_RET(texto):
            # Filtrar por RET -
            #return bool(re.search(r' RET - ', texto, flags=re.IGNORECASE))
            return bool(re.search(r' RET - | RECON - ', texto, flags=re.IGNORECASE))
        
        # Limpa a lista
        self.listaEvt.delete(*self.listaEvt.get_children())



        # Especificação da Tag a ser procurada (entrada do usuário), padrão Pi
        # entry.get() irá coletar a informação contida na entry na hora da execução desta linha
        query = self.filtro_entry.get()



        # Especificação do range de data a ser procurado no formato especificado
        # YYYY/MM/DD hh:mm:ss
        # Na entry deve ser dd:mm:yyyy hh:mm:ss
        startTime = self.dinicio_entry.get()
        stopTime =  self.dfim_entry.get()
          
        # str2datetime
        # Formato que o TSWS entende
        startTime = datetime.datetime.strptime(startTime, "%d/%m/%Y %H:%M:%S")
        stopTime  = datetime.datetime.strptime(stopTime, "%d/%m/%Y %H:%M:%S")

        step_amount = self.step_amount_entry.get()


        if step_amount != '':
            # programar condição para quando o usuário não preenche step_amount
            # step_amount = 5
            step_amount = int(step_amount)
            print(step_amount)
            step = 'MINUTE'
            tag_name = self.tsws.get.tag_search(query).json()['tagResponse'][0]['tagName']
            response = self.tsws.get.time_series_fixed_step_range(tag_name,step,step_amount,startTime,stopTime)
            response = response.json()['timeSeriesResponse']
            
            # Transforma response em DataFrame
            events   = pd.DataFrame.from_dict(response)
            events['índice'] = pd.Series(events.index)
            
            # Remove eventos identicos do df
            self.events = events.drop_duplicates()
            


            # Especifica o nome de cada coluna
            self.listaEvt.heading("#0", text="")
            self.listaEvt.heading("#1", text='índice')
            self.listaEvt.heading("#2", text='Un Eng')
            self.listaEvt.heading("#3", text='Valor Numérico')
            self.listaEvt.heading("#4", text='Nome da TAG')
            self.listaEvt.heading("#5", text='Data/Hora')
            self.listaEvt.heading("#6", text='Valor')
            
            # Isso aq é meio confuso, divide o número 500 nas proporções de cada coluna
            self.listaEvt.column("#0", width=1)
            self.listaEvt.column("#1", width=60)
            self.listaEvt.column("#2", width=60)
            self.listaEvt.column("#3", width=150)
            self.listaEvt.column("#4", width=300)
            self.listaEvt.column("#5", width=150)
            self.listaEvt.column("#6", width=150)

            for index, row in events.iterrows():
                # self.listaEvt.insert("", "end", values=(row['engUnit'], row['numericValue'], row['tagName'], row['timestamp'], row['value']))
                self.listaEvt.insert("", "end", values=(row['índice'],row['engUnit'], row['numericValue'], row['tagName'], row['timestamp'], row['value']))     
        else:
            # Extrai os dados nas condições anteriormente especificadas, isso é um dicionário
            # Função feita pelo GSS
            response = self.tsws.get.time_series_events(query, startTime, stopTime)
            # No final das contas, response é um dicionário 
            response = response.json()['timeSeriesResponse']

            # Transforma response em DataFrame
            events   = pd.DataFrame.from_dict(response)

            # Especifica a coluna índice do dataframe
            # Extrair as informações de Data, Hora, Local, Evento e Estado
            events['índice'] = pd.Series(events.index)
            events['Data']   = events['value'].str[:12]
            events['Hora']   = events['value'].str[12:21]
            events['Local']  = events['value'].str[21:30]
            events['Evento'] = events['value'].str[30:79]
            events['Estado'] = events['value'].str[79:]

            # Contém True em todos os índices onde contém a string "- RET "
            mascara = events['Estado'].apply(contem_RET)

            # Nas linhas que contém - RET  tratar as colunas Hora Local e Evento de maneira adequada
            events.loc[mascara, 'Hora']  = events.loc[mascara, 'Local'] + ' - ' + events.loc[mascara, 'Hora']
            events.loc[mascara, 'Local'] = events.loc[mascara, 'Evento'].str[:9]
            events.loc[mascara, 'Evento'] = events.loc[mascara, 'Evento'].str.slice(9)

            # Definir as colunas que serão utilizadas
            columns = ['índice', 'Data', 'Hora', 'Local', 'Evento', 'Estado']

            # Categoriza o dataframe 
            self.events = events[columns]

            # Remove eventos identicos do df
            self.events = events.drop_duplicates()



            # Especifica o nome de cada coluna
            self.listaEvt.heading("#0", text="")
            self.listaEvt.heading("#1", text='Índice')
            self.listaEvt.heading("#2", text='Data')
            self.listaEvt.heading("#3", text='Hora')
            self.listaEvt.heading("#4", text='Local')
            self.listaEvt.heading("#5", text='Alarme')
            self.listaEvt.heading("#6", text='Estado')
            
            # Isso aq é meio confuso, divide o número 500 nas proporções de cada coluna
            self.listaEvt.column("#0", width=1)
            self.listaEvt.column("#1", width=60)
            self.listaEvt.column("#2", width=100)
            self.listaEvt.column("#3", width=100)
            self.listaEvt.column("#4", width=100)
            self.listaEvt.column("#5", width=300)
            self.listaEvt.column("#6", width=500)
            
            for index, row in events.iterrows():
                self.listaEvt.insert("", "end", values=(row['índice'], row['Data'], row['Hora'], row['Local'], row['Evento'], row['Estado']))

    def export(self):
        # Exporta o dataframe events para xlsx
        # Segundo o nome especificado
        nome_pesquisa = self.nomep_entry.get()
        self.events_sem_indice = self.events.reset_index(drop=True)
        self.events_sem_indice = self.events_sem_indice.drop('índice', axis=1)
        self.events_sem_indice.to_excel(nome_pesquisa +'.xlsx', index=False) 


        # Limpa a lista
        self.listaEvt.delete(*self.listaEvt.get_children())



        # Especificação da Tag a ser procurada (entrada do usuário), padrão Pi
        # entry.get() irá coletar a informação contida na entry na hora da execução desta linha
        query = self.filtro_entry.get()



        # Especificação do range de data a ser procurado no formato especificado
        # YYYY/MM/DD hh:mm:ss
        # Na entry deve ser dd:mm:yyyy hh:mm:ss
        startTime = self.dinicio_entry.get()
        stopTime =  self.dfim_entry.get()
          
        # str2datetime
        # Formato que o TSWS entende
        startTime = datetime.datetime.strptime(startTime, "%d/%m/%Y %H:%M:%S")
        stopTime  = datetime.datetime.strptime(stopTime, "%d/%m/%Y %H:%M:%S")



        # programar condição para quando o usuário não preenche step_amount
        # step_amount = 5
        step_amount = self.step_amount_entry.get()
        step_amount = int(step_amount)
        step = 'MINUTE'

        tag_name = self.tsws.get.tag_search(query).json()['tagResponse'][0]['tagName']
        response = self.tsws.get.time_series_fixed_step_range(tag_name,step,step_amount,startTime,stopTime)
        response = response.json()['timeSeriesResponse']
        
        # Transforma response em DataFrame
        events   = pd.DataFrame.from_dict(response)
        events['índice'] = pd.Series(events.index)
        
        # Remove eventos identicos do df
        self.events = events.drop_duplicates()
        


        # Especifica o nome de cada coluna
        self.listaEvt.heading("#0", text="")
        self.listaEvt.heading("#1", text='índice')
        self.listaEvt.heading("#2", text='Un Eng')
        self.listaEvt.heading("#3", text='Valor Numérico')
        self.listaEvt.heading("#4", text='Nome da TAG')
        self.listaEvt.heading("#5", text='Data/Hora')
        self.listaEvt.heading("#6", text='Valor')
        
        # Isso aq é meio confuso, divide o número 500 nas proporções de cada coluna
        self.listaEvt.column("#0", width=1)
        self.listaEvt.column("#1", width=60)
        self.listaEvt.column("#2", width=60)
        self.listaEvt.column("#3", width=150)
        self.listaEvt.column("#4", width=300)
        self.listaEvt.column("#5", width=150)
        self.listaEvt.column("#6", width=150)

        for index, row in events.iterrows():
            # self.listaEvt.insert("", "end", values=(row['engUnit'], row['numericValue'], row['tagName'], row['timestamp'], row['value']))
            self.listaEvt.insert("", "end", values=(row['índice'],row['engUnit'], row['numericValue'], row['tagName'], row['timestamp'], row['value']))     

    def load_list(self):
        # Limpa a entry do filtro
        self.filtro_entry.delete(0, END)
        
        # Janela para localizar a lista
        caminho_list = tk.filedialog.askopenfilename(filetypes=[('Todos os arquivos', '*.*')])

        
        arquivos = glob.glob(caminho_list)
        lista_evt = pd.read_excel(arquivos[0])

        lista_evt['tag_name'] = '*' + lista_evt['SUBNAM'] + '*' + lista_evt['PNTNAM']        
        
        lista_evt.drop('SUBNAM', axis=1, inplace=True)
        lista_evt.drop('PNTNAM', axis=1, inplace=True)
        
        self.tag_list = []
        for index, row in lista_evt.iterrows():
            print(index)
            tag_name = self.tsws.get.tag_search(row.to_string(index=False)[1:47]).json()['tagResponse'][0]['tagName']           
            self.tag_list.append(tag_name)

        print('Lista de tags carregadas')






# A classe Application pode utilizar as funções da classe Funcs
class Application(Funcs):
    # Inicialização
    def __init__(self):
        # Isso aq ñ sei o que significa, nem esse self
        self.root = root
        self.tela()
        self.frames_da_tela()
        self.widgets_frame1()
        self.widgets_frame2()
        self.lista_frame3()
        # Coloca a abertura de janela em loop para que se possa interagir com ela
        root.mainloop()

    def tela(self):
        # Cria um título para a janela
        self.root.title("Busca de eventos TSWS")
        
        # Define a cor de fundo para a janela
        # Cores tkinter que ele entende (ggl)
        self.root.configure(background= '#1e3743')

        # Geometria da janela responsiva
        self.root.geometry("1200x800")
        self.root.resizable(True, True)
   
    def frames_da_tela(self):
        self.frame_1 = Frame(self.root, bd = 4, bg = '#dfe3ee', highlightbackground="#759fe6", highlightthickness=3)
        self.frame_1.place(relx = 0.02, rely = 0.02, relwidth = 0.66, relheight = 0.25)

        self.frame_2 = Frame(self.root, bd = 4, bg = '#dfe3ee', highlightbackground="#759fe6", highlightthickness=3)
        self.frame_2.place(relx = 0.70, rely = 0.02, relwidth = 0.28, relheight = 0.25)
            

        # Esse frame começará na metade da janela, rely = 0.5
        self.frame_3 = Frame(self.root, bd = 4, bg = '#dfe3ee', highlightbackground="#759fe6", highlightthickness=3)
        self.frame_3.place(relx = 0.02, rely = 0.28, relwidth = 0.96, relheight = 0.70)

    def widgets_frame1(self):
        self.lb_filtro = Label(self.frame_1, text="Filtro", font=("Arial", 14), bg='#dfe3ee', fg='#107db2')
        self.lb_filtro.place(relx = 0.00, rely = 0.05)

        self.filtro_entry = Entry(self.frame_1)
        self.filtro_entry.place(relx = 0.17, rely = 0.072, relwidth=0.4, relheight=0.12)



        self.lb_inicio = Label(self.frame_1, text="Data de início", font=("Arial", 14), bg='#dfe3ee', fg='#107db2')
        self.lb_inicio.place(relx = 0.00, rely = 0.3)

        self.dinicio_entry = Entry(self.frame_1)
        self.dinicio_entry.place(relx = 0.17, rely = 0.315, relwidth=0.4, relheight=0.12)
        
        data_hora_atual = datetime.datetime.now() - datetime.timedelta(hours=24)

        self.dinicio_entry.insert(0, data_hora_atual.strftime('%d/%m/%Y %H:%M:%S'))



        self.lb_dfim = Label(self.frame_1, text="Data de fim", font=("Arial", 14), bg='#dfe3ee', fg='#107db2')
        self.lb_dfim.place(relx = 0.00, rely = 0.55)

        self.dfim_entry = Entry(self.frame_1)
        self.dfim_entry.place(relx = 0.17, rely = 0.565, relwidth=0.4, relheight=0.12)

        data_hora_atual = datetime.datetime.now() 

        self.dfim_entry.insert(0, data_hora_atual.strftime('%d/%m/%Y %H:%M:%S'))



        self.lb_step_amount = Label(self.frame_1, text="Step_amount", font=("Arial", 14), bg='#dfe3ee', fg='#107db2')
        self.lb_step_amount.place(relx = 0.59, rely = 0.05)

        self.step_amount_entry = Entry(self.frame_1)
        self.step_amount_entry.place(relx = 0.75, rely = 0.05, relwidth=0.2, relheight=0.12)



        # Botões
        self.bt_clear = Button(self.frame_1, text="Limpar", bd=2, bg='#107db2', fg='white', font=('verdana', 8, 'bold'), command=self.limpa_tela)
        self.bt_clear.place(relx=0.50, rely = 0.8, relwidth = 0.1, relheight = 0.15)



        self.bt_conect = Button(self.frame_1, text="Conectar ao TSWS", bd=2, bg='#107db2', fg='white', font=('verdana', 8, 'bold'), command=self.conectTSWS)
        self.bt_conect.place(relx=0.81, rely = 0.8, relwidth = 0.18, relheight = 0.15)



        self.bt_snapshot = Button(self.frame_1, text="Iniciar Snapshot", bd=2, bg='#107db2', fg='white', font=('verdana', 8, 'bold'), command=self.toogle_snapshot)
        self.bt_snapshot.place(relx=0.35, rely = 0.8, relwidth = 0.15, relheight = 0.15)

        self.snapshot_thread = None  # Thread para o loop de snapshot
        self.snapshot_running = False  # Variável de controle para o loop



        self.bt_buscar = Button(self.frame_1, text="Buscar Eventos", bd=2, bg='#107db2', fg='white', font=('verdana', 8, 'bold'), command=self.buscar_evt)
        self.bt_buscar.place(relx=0.0, rely = 0.8, relwidth = 0.15, relheight = 0.15)



        self.bt_get_list = Button(self.frame_1, text="Carregar Lista snap", bd=2, bg='#107db2', fg='white', font=('verdana', 8, 'bold'), command=self.load_list)
        self.bt_get_list.place(relx=0.15, rely = 0.8, relwidth = 0.2, relheight = 0.15)

    def widgets_frame2(self):

        self.lb_filtro = Label(self.frame_2, text="Nome da pesquisa", font=("Arial", 14), bg='#dfe3ee', fg='#107db2')
        self.lb_filtro.place(relx = 0.25, rely = 0.15)

        self.nomep_entry = Entry(self.frame_2)
        self.nomep_entry.place(relx = 0.05, rely = 0.35, relwidth=0.9, relheight=0.12)

        # Botão buscar e label export
        self.bt_buscar = Button(self.frame_2, text="Exportar .xlsx", bd=2, bg='#107db2', fg='white', font=('verdana', 8, 'bold'), command=self.export)
        self.bt_buscar.place(relx=0.3, rely = 0.55, relwidth = 0.4, relheight = 0.15)

    def lista_frame3(self):
        # Especifica qual frame, tamanho vertical e colunas da tabela de pre-view
        self.listaEvt = ttk.Treeview(self.frame_3, height=3, columns=('col1', 'col2', 'col3', 'col4', 'col5', 'col6'))
                
   
        # Posições rlativas deescritas no widgets
        self.listaEvt.place(relx=0.01, rely=0.020, relwidth=0.96, relheight=0.95)
        

        # Crie um scrollbar vertical
        scrollbar_vertical = ttk.Scrollbar(self.frame_3, orient="vertical", command=self.listaEvt.yview)
        scrollbar_vertical.pack(side="right", fill="y")

        # Associe o scrollbar vertical ao Treeview
        self.listaEvt.config(yscrollcommand=scrollbar_vertical.set)

if __name__ == "__main__":
    Application()
# %%