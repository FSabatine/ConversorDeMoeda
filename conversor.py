import tkinter as tk
from tkinter import ttk, messagebox
import requests
from PIL import Image, ImageTk
from io import BytesIO

class ConversorMoedas:
    def __init__(self, root):
        self.root = root
        self.root.title("Conversor de Moedas em Tempo Real")
        self.root.geometry("500x350")

        self.api_key = "SUA_CHAVE_API"  # Substitua pela sua chave da API da ExchangeRate-API
        self.moedas = self.carregar_moedas()
        self.fotos_bandeiras = {}

        self.criar_widgets()

    def carregar_moedas(self):
        try:
            url = f"https://v6.exchangerate-api.com/v6/{self.api_key}/codes"
            response = requests.get(url)
            response.raise_for_status()
            dados = response.json()
            # Filtra moedas que não são mais válidas
            return sorted([moeda for moeda in dados['supported_codes'] if "Obsolete" not in moeda[1]], key=lambda x: x[1])
        except requests.exceptions.RequestException as e:
            messagebox.showerror("Erro de Conexão", f"Não foi possível buscar a lista de moedas.\n{e}")
            return []

    def criar_widgets(self):
        frame_principal = ttk.Frame(self.root, padding="10")
        frame_principal.pack(fill=tk.BOTH, expand=True)

        ttk.Label(frame_principal, text="Valor:", font=("Helvetica", 12)).grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.entry_valor = ttk.Entry(frame_principal, width=20, font=("Helvetica", 12))
        self.entry_valor.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(frame_principal, text="De:", font=("Helvetica", 12)).grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.combo_de = self.criar_combobox_pesquisavel(frame_principal, row=1, column=1)

        ttk.Label(frame_principal, text="Para:", font=("Helvetica", 12)).grid(row=2, column=0, padx=5, pady=5, sticky="w")
        self.combo_para = self.criar_combobox_pesquisavel(frame_principal, row=2, column=1)

        self.botao_converter = ttk.Button(frame_principal, text="Converter", command=self.converter)
        self.botao_converter.grid(row=3, column=0, columnspan=2, pady=10)

        self.label_resultado = ttk.Label(frame_principal, text="", font=("Helvetica", 14, "bold"))
        self.label_resultado.grid(row=4, column=0, columnspan=2, pady=10)

    def criar_combobox_pesquisavel(self, parent, row, column):
        frame = ttk.Frame(parent)
        frame.grid(row=row, column=column, padx=5, pady=5)

        entry = ttk.Entry(frame, width=25)
        entry.pack(fill=tk.X)

        listbox = tk.Listbox(frame, width=40, height=8)

        def ao_digitar(event):
            texto_digitado = entry.get().lower()
            listbox.delete(0, tk.END)
            for codigo, nome in self.moedas:
                if texto_digitado in nome.lower() or texto_digitado in codigo.lower():
                    try:
                        codigo_pais = codigo[:2].lower()
                        if codigo_pais not in self.fotos_bandeiras:
                            url_bandeira = f"https://flagcdn.com/16x12/{codigo_pais}.png"
                            response_bandeira = requests.get(url_bandeira)
                            if response_bandeira.status_code == 200:
                                img_data = response_bandeira.content
                                img = Image.open(BytesIO(img_data))
                                self.fotos_bandeiras[codigo_pais] = ImageTk.PhotoImage(img)
                        
                        if codigo_pais in self.fotos_bandeiras:
                            listbox.insert(tk.END, f"{codigo} - {nome}")
                    except Exception:
                        listbox.insert(tk.END, f"{codigo} - {nome}")
            if not listbox.winfo_viewable():
                listbox.pack(fill=tk.X)

        def ao_selecionar(event):
            if listbox.curselection():
                selecionado = listbox.get(listbox.curselection())
                entry.delete(0, tk.END)
                entry.insert(0, selecionado.split(" - ")[0])
                listbox.pack_forget()

        entry.bind("<KeyRelease>", ao_digitar)
        listbox.bind("<<ListboxSelect>>", ao_selecionar)

        return entry

    def converter(self):
        try:
            valor_str = self.entry_valor.get()
            if not valor_str:
                messagebox.showwarning("Campo Vazio", "Por favor, insira um valor para converter.")
                return
            valor = float(valor_str)
            
            moeda_de = self.combo_de.get()
            moeda_para = self.combo_para.get()

            if not moeda_de or not moeda_para:
                messagebox.showwarning("Seleção Incompleta", "Por favor, selecione as duas moedas.")
                return

            url = f"https://v6.exchangerate-api.com/v6/{self.api_key}/pair/{moeda_de}/{moeda_para}/{valor}"
            response = requests.get(url)
            response.raise_for_status()
            dados = response.json()

            resultado_conversao = dados['conversion_result']
            taxa_conversao = dados['conversion_rate']

            self.label_resultado.config(text=f"{valor:.2f} {moeda_de} = {resultado_conversao:.2f} {moeda_para}\nTaxa: 1 {moeda_de} = {taxa_conversao} {moeda_para}")

        except ValueError:
            messagebox.showerror("Erro de Entrada", "Por favor, insira um valor numérico válido.")
        except requests.exceptions.RequestException as e:
            messagebox.showerror("Erro de API", f"Não foi possível obter a taxa de conversão.\n{e}")
        except Exception as e:
            messagebox.showerror("Erro Inesperado", f"Ocorreu um erro inesperado.\n{e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = ConversorMoedas(root)
    root.mainloop()
