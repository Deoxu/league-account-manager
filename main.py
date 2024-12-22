from tkinter import messagebox

import customtkinter as ctk #pip install customtkinter
import webbrowser
from PIL import Image, ImageTk #pip install pillow
import os

class AccountManagerApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Configurações de estilo
        ctk.set_appearance_mode("dark")  # Modo escuro
        ctk.set_default_color_theme("dark-blue")  # Tema base
        self.configure(bg="#0a1428")
        self.title("League Account Manager")
        self.geometry("700x500")
        self.font = my_font = ctk.CTkFont(family="Segoe UI", size=14, weight="bold")

        self.accounts = []  # Lista para armazenar as contas

        self.create_widgets()

    def create_widgets(self):
        my_font = ctk.CTkFont(family="Segoe UI", size=14, weight="bold")
        # Caminho relativo para a imagem
        logo_path = os.path.join("assets", "interfacelogo.png")

        try:
            # Carregar a imagem do logo usando CTkImage
            logo_image = ctk.CTkImage(
                light_image=Image.open(logo_path),
                dark_image=Image.open(logo_path),
                size=(243, 131),  # Substitua por tamanhos adequados
            )

            # Substituir o título pelo logo
            self.logo_label = ctk.CTkLabel(self, image=logo_image, text="")
            self.logo_label.pack(pady=10)
        except FileNotFoundError:
            # Caso a imagem não seja encontrada, exibir mensagem padrão
            self.logo_label = ctk.CTkLabel(self, text="Logo não encontrada", font=self.font, bg_color="#0a1428",
                                           text_color="white")
            self.logo_label.pack(pady=10)

        # Botões principais
        self.add_account_button = ctk.CTkButton(
            self,
            text="Adicionar Conta",
            command=self.open_add_account_window,
            fg_color="#c89c38",
            hover_color="#b29a5e",
            border_width=1,
            border_color="black",
            corner_radius=0,
            font=self.font
        )
        self.add_account_button.pack(pady=10)

        self.filter_frame = ctk.CTkFrame(self, bg_color="#0a1428")
        self.filter_frame.pack(pady=10, fill="x")

        self.filter_type_listbox = ctk.CTkComboBox(
            self.filter_frame, values=["Elo", "Honra", "Level"], command=self.update_filter_options, state="readonly",
            font=self.font
        )
        self.filter_type_listbox.set("")  # Valor padrão
        self.filter_type_listbox.pack(side="left", padx=5)

        self.filter_option_listbox = ctk.CTkComboBox(self.filter_frame, values=[], state="readonly", font=self.font)
        self.filter_option_listbox.set("")  # Valor inicial vazio
        self.filter_option_listbox.pack(side="left", padx=5)

        self.filter_button = ctk.CTkButton(
            self.filter_frame,
            text="Aplicar Filtro",
            command=self.filter_accounts,
            fg_color="#c89c38",
            hover_color="#b29a5e",
            border_width=1,
            border_color="black",
            corner_radius=0,
            font=self.font
        )
        self.filter_button.pack(side="left", padx=5)

        # Lista de contas
        self.account_frame = ctk.CTkFrame(self, bg_color="#0a1428")
        self.account_frame.pack(pady=10, fill="both", expand=True)

        self.account_list_header = ctk.CTkLabel(
            self.account_frame, text="Login | Riot ID | Nível | Elo | Honra", font=my_font, text_color="white"
        )
        self.account_list_header.pack(pady=5)

        self.account_list = ctk.CTkFrame(self.account_frame, bg_color="#0a1428")
        self.account_list.pack(fill="both", expand=True)

        self.update_account_list()

    def open_add_account_window(self):
        add_window = ctk.CTkToplevel(self)
        add_window.title("Adicionar Conta")
        add_window.geometry("400x500")

        add_window.transient(self)  # Define como janela dependente da principal
        add_window.grab_set()  # Impede interação com a janela principal
        add_window.focus_set()  # Define o foco para a nova janela

        # Formulário para adicionar conta
        ctk.CTkLabel(add_window, text="Nome de Login:").pack(pady=5)
        login_entry = ctk.CTkEntry(add_window)
        login_entry.pack(pady=5)

        ctk.CTkLabel(add_window, text="Riot ID (ex: riot#id):").pack(pady=5)
        riot_id_entry = ctk.CTkEntry(add_window)
        riot_id_entry.pack(pady=5)

        ctk.CTkLabel(add_window, text="Nível da Conta:").pack(pady=5)
        level_entry = ctk.CTkEntry(add_window)
        level_entry.pack(pady=5)

        ctk.CTkLabel(add_window, text="Elo:").pack(pady=5)
        elo_listbox = ctk.CTkComboBox(add_window, values=["Unranked", "Ferro", "Bronze", "Prata", "Ouro", "Platina", "Esmeralda", "Diamante", "Mestre", "Grão Mestre", "Desafiante"], state="readonly")
        elo_listbox.pack(pady=5)

        ctk.CTkLabel(add_window, text="Nível de Honra:").pack(pady=5)
        honor_listbox = ctk.CTkComboBox(add_window, values=["1", "2", "3", "4", "5"], state="readonly")
        honor_listbox.pack(pady=5)

        def save_account():
            login = login_entry.get()
            riot_id = riot_id_entry.get()
            level = level_entry.get()
            elo = elo_listbox.get()
            honor = honor_listbox.get()

            # Verificar se todos os campos estão preenchidos
            if not (login and riot_id and level and elo and honor):
                messagebox.showerror("Erro", "Todos os campos devem ser preenchidos!")
                return

            # Validar Riot ID
            if "#" not in riot_id:
                messagebox.showerror("Erro", "Riot ID deve conter # (ex: deoxu#dede)")
                return

            # Validar nível e elo
            try:
                level = int(level)  # Converter nível para inteiro
                if level < 30 and elo != "Unranked":
                    messagebox.showerror("Erro", "Contas abaixo do nível 30 não podem ter elo.")
                    return
            except ValueError:
                messagebox.showerror("Erro", "Nível da conta deve ser um número válido.")
                return

            # Gerar link do op.gg
            opgg_link = self.generate_opgg_link(riot_id)

            # Criar conta
            account = {
                "login": login,
                "riot_id": riot_id,
                "level": level,
                "elo": elo,
                "honor": honor,
                "opgg": opgg_link
            }

            # Adicionar conta à lista e atualizar interface
            self.accounts.append(account)
            self.update_account_list()
            add_window.destroy()

        save_button = ctk.CTkButton(add_window, text="Salvar", command=save_account)
        save_button.pack(pady=20)

    def generate_opgg_link(self, riot_id):
        name, tag = riot_id.split("#")
        name = name.replace(" ", "-")
        return f"https://www.op.gg/summoners/br/{name}-{tag}"

    def update_account_list(self, filtered_accounts=None):
        for widget in self.account_list.winfo_children():
            widget.destroy()

        accounts_to_show = filtered_accounts if filtered_accounts else self.accounts

        if not accounts_to_show:
            no_accounts_label = ctk.CTkLabel(self.account_list, text="Nenhuma conta adicionada ainda.", font=("Arial", 12))
            no_accounts_label.pack(pady=10)
        else:
            for account in accounts_to_show:
                account_frame = ctk.CTkFrame(self.account_list)
                account_frame.pack(fill="x", pady=2)

                clickable_label = ctk.CTkLabel(account_frame, text=account['login'], font=("Arial", 12, "underline"), text_color="blue", cursor="hand2")
                clickable_label.pack(side="left", padx=5)

                clickable_label.bind("<Button-1>", lambda e, link=account['opgg']: webbrowser.open(link))

                details_label = ctk.CTkLabel(account_frame, text=f"| {account['riot_id']} | {account['level']} | {account['elo']} | {account['honor']}", font=("Arial", 12))
                details_label.pack(side="left")

    def update_filter_options(self, selection):
        if selection == "Elo":
            self.filter_option_listbox.configure(values=["Unranked", "Ferro", "Bronze", "Prata", "Ouro", "Platina", "Esmeralda", "Diamante", "Mestre", "Grão Mestre", "Desafiante"])
            self.filter_option_listbox.set("")  # Resetar valor
        elif selection == "Honra":
            self.filter_option_listbox.configure(values=["1", "2", "3", "4", "5"])
            self.filter_option_listbox.set("")  # Resetar valor
        elif selection == "Level":
            self.filter_option_listbox.configure(values=["Nível 30+", "Nível 30-"])
            self.filter_option_listbox.set("")  # Resetar valor

    def filter_accounts(self):
        filter_type = self.filter_type_listbox.get()
        filter_value = self.filter_option_listbox.get()

        if not filter_type or not filter_value:
            messagebox.showerror("Erro", "Selecione um tipo e um valor de filtro.")
            return

        if filter_type == "Elo":
            filtered = [account for account in self.accounts if account['elo'] == filter_value]
        elif filter_type == "Honra":
            filtered = [account for account in self.accounts if account['honor'] == filter_value]
        elif filter_type == "Level":
            if filter_value == "Nível 30+":
                filtered = [account for account in self.accounts if int(account['level']) >= 30]
            else:
                filtered = [account for account in self.accounts if int(account['level']) < 30]

        if not filtered:
            messagebox.showinfo("Filtro", "Nenhuma conta encontrada com os critérios selecionados.")

        self.update_account_list(filtered)

if __name__ == "__main__":
    app = AccountManagerApp()
    app.mainloop()
