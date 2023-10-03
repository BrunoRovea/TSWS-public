import pandas as pd
from tkinter import Tk, Button, Entry, Text

def executar():
    pass

def selecionar_arquivo_soperm():
    pass

def selecionar_arquivo_dados():
    pass


def display_dataframe():
    # Create a sample DataFrame
    df = pd.DataFrame({'Column 1': [1, 2, 3], 'Column 2': ['A', 'B', 'C']})

    # Clear the text widget
    text_widget.delete(1.0, "end")

    # Insert the DataFrame into the text widget
    text_widget.insert("end", df.to_string())

# Create the main Tkinter window
janela = Tk()
janela.geometry("700x400")

# Create the buttons
botao_selecionar = Button(janela, text="Selecionar arquivo soperm", command=selecionar_arquivo_soperm, width=40)
botao_selecionar.grid(row=2, column=1, padx=10, pady=10)

botao_selecionar = Button(janela, text="Selecionar historico sartre", command=selecionar_arquivo_dados, width=40)
botao_selecionar.grid(row=3, column=1, padx=10, pady=10)

botao_executar = Button(janela, text="Executar", command=executar, width=40)
botao_executar.grid(row=5, column=1, padx=10, pady=10)

# Create the text widget
text_widget = Text(janela, height=10, width=50)
text_widget.grid(row=6, column=0, columnspan=2, padx=10, pady=10)

# Create the function to display the DataFrame
display_button = Button(janela, text="Display DataFrame", command=display_dataframe, width=40)
display_button.grid(row=7, column=1, padx=10, pady=10)

# Start the Tkinter event loop
janela.mainloop()


