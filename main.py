import os
import json
import webbrowser
from tkinter import messagebox
from tkinter import ttk
import customtkinter as ctk  # pip install customtkinter
from PIL import Image, ImageTk  # pip install pillow
import tkinter as tk
from tkinter.font import Font

class AccountManagerApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("League Account Manager")
        self.geometry("1280x720")
        self.resizable(width=False, height=False)
        self.configure(fg_color="#010a13")
        self.icon_path = os.path.join("assets", "logo.ico")  # Caminho do ícone
        self.iconbitmap(self.icon_path)  # Define o ícone principal

        #Spiegel Font
        self.Spiegel_path = "assets/fonts/Spiegel.ttf"
        self.Spiegel = ctk.CTkFont(family="Spiegel", size=14)
        #Spiegel Bold Font
        self.SpiegelBold = ctk.CTkFont(family="Spiegel", size=14, weight="bold")

        #Salvar as contas em arquivo
        self.accounts = []
        self.data_file = "accounts.json"
        self.load_accounts()
        self.create_widgets()


    def create_widgets(self):
        # Configurar o logo
        try:
            logo_path = os.path.join("assets", "interfacelogo.png")
            logo_image = ctk.CTkImage(light_image=Image.open(logo_path), dark_image=Image.open(logo_path), size=(243, 131))
            self.logo_label = ctk.CTkLabel(self, image=logo_image, text="")
            self.logo_label.pack(pady=10)
        except FileNotFoundError:
            self.logo_label = ctk.CTkLabel(self, text="Logo não encontrada", font=self.Spiegel, text_color="white")
            self.logo_label.pack(pady=10)

        # Botão de adicionar conta
        self.add_account_button = ctk.CTkButton(
            self, text="Adicionar Conta", command=self.open_add_account_window, fg_color="#1e2328",
            hover_color="#20252a", border_width=1, border_color="#c6a86c", font=self.Spiegel, text_color="#cdbe91", corner_radius=0
        )
        self.add_account_button.pack(pady=10)

        # Frame para filtros
        self.filter_frame = ctk.CTkFrame(self, fg_color="#010a13")
        self.filter_frame.pack(pady=10, fill="x")

        self.filter_type_listbox = ctk.CTkComboBox(
            self.filter_frame, values=["Elo", "Honra", "Level"], command=self.update_filter_options, state="readonly",
            font=self.Spiegel
        )
        self.filter_type_listbox.set("Selecione um filtro")
        self.filter_type_listbox.pack(side="left", padx=5)

        self.filter_option_listbox = ctk.CTkComboBox(self.filter_frame, values=[], state="readonly", font=self.Spiegel)
        self.filter_option_listbox.set("")
        self.filter_option_listbox.pack(side="left", padx=5)

        self.filter_button = ctk.CTkButton(
            self.filter_frame, text="Aplicar Filtro", command=self.filter_accounts, fg_color="#1e2328",
            hover_color="#20252a", border_width=1, border_color="#c6a86c", font=self.Spiegel, text_color="#cdbe91", corner_radius=0
        )
        self.filter_button.pack(side="left", padx=5)

        self.clear_filter_button = ctk.CTkButton(
            self.filter_frame, text="Remover Filtros", command=self.clear_filters, fg_color="#1e2328",
            hover_color="#20252a", border_width=1, border_color="#c6a86c", font=self.Spiegel, text_color="#cdbe91", corner_radius=0
        )
        self.clear_filter_button.pack(side="left", padx=5)

        # Lista de contas com barra de rolagem
        self.account_frame = ctk.CTkFrame(self, fg_color="#010a13")
        self.account_frame.pack(pady=10, fill="both", expand=True)

        # Headers
        headers_frame = ctk.CTkFrame(self.account_frame, fg_color="#010a13")
        headers_frame.pack(fill="x", padx=10)

        labels = ["Login", "Riot ID", "Nível", "Elo", "Honra", "Ações"]
        self.column_weights = [2, 2, 1, 1, 1, 1]  # Define relative widths for each column
        total_width = 1200  # Largura total fixa
        self.column_widths = [int(total_width * (w / sum(self.column_weights))) for w in self.column_weights]

        # Criação dos cabeçalhos estilizados
        for i, label in enumerate(labels):
            header_div = ctk.CTkFrame(
                headers_frame,
                fg_color="#1e2328",
                border_width=1,
                border_color="#c6a86c",
                corner_radius=0,
                width=self.column_widths[i],
                height=35  # Altura fixa para o cabeçalho
            )
            header_div.pack(side="left", padx=5, pady=5)
            header_div.pack_propagate(False)  # Impede que o conteúdo afete o tamanho

            header_label = ctk.CTkLabel(
                header_div,
                text=label,
                font=self.SpiegelBold,
                text_color="#cdbe91"
            )
            header_label.pack(padx=5, pady=5, expand=True)

        # Canvas para contas
        canvas_frame = ctk.CTkFrame(self.account_frame, fg_color="#010a13")
        canvas_frame.pack(fill="both", expand=True, padx=10)

        self.account_canvas = ctk.CTkCanvas(canvas_frame, bg="#222b3d", highlightthickness=0)
        self.account_list = ctk.CTkFrame(self.account_canvas, fg_color="#222b3d")
        
        # Adicionando a Scrollbar personalizada
        self.scrollbar = ctk.CTkScrollbar(
            canvas_frame,
            orientation="vertical",
            command=self.account_canvas.yview,
            fg_color="#2E2E2E",
            button_color="#5A5A5A",
            button_hover_color="#A1A1A1"
        )
        self.scrollbar.pack(side="right", fill="y")

        # Configurar o canvas
        self.account_canvas.pack(side="left", fill="both", expand=True)
        self.account_list.pack(fill="both", expand=True)

        self.account_canvas.bind(
            "<Configure>",
            lambda e: self.on_canvas_configure(e)
        )
        
        self.account_list.bind(
            "<Configure>",
            lambda e: self.account_canvas.configure(scrollregion=self.account_canvas.bbox("all"))
        )
        
        self.account_canvas.create_window((0, 0), window=self.account_list, anchor="nw")
        self.account_canvas.configure(yscrollcommand=self.scrollbar.set)

        # Atualizar a lista de contas
        self.update_account_list()

    def on_canvas_configure(self, event):
        # Atualiza a largura da janela do canvas para corresponder à largura do canvas
        try:
            self.account_canvas.itemconfig(
                self.account_canvas.find_withtag("all")[0],
                width=event.width
            )
        except:
            pass

    def open_add_account_window(self):
        Spiegel = ctk.CTkFont(family="Segoe UI", size=14, weight="bold")
        add_window = ctk.CTkToplevel(self)
        add_window.title("Adicionar Conta")
        add_window.geometry("400x500")
        add_window.resizable(width=False, height=False)
        add_window.configure(fg_color="#010a13")
        add_window.iconbitmap(self.icon_path)

        # Configurar a janela para permanecer no topo e bloquear interações com a janela principal
        add_window.grab_set()  # Bloqueia interações na janela principal
        add_window.focus_set()  # Foca automaticamente na nova janela

        # Formulário de adicionar conta
        ctk.CTkLabel(add_window, text="Nome de Login:", text_color="white", font=Spiegel).pack(pady=5)
        login_entry = ctk.CTkEntry(add_window)
        login_entry.pack(pady=5)

        ctk.CTkLabel(add_window, text="Riot ID (ex: riot#id):", text_color="white", font=Spiegel).pack(pady=5)
        riot_id_entry = ctk.CTkEntry(add_window)
        riot_id_entry.pack(pady=5)

        ctk.CTkLabel(add_window, text="Nível da Conta:", text_color="white", font=Spiegel).pack(pady=5)
        level_entry = ctk.CTkEntry(add_window)
        level_entry.pack(pady=5)

        ctk.CTkLabel(add_window, text="Elo:", text_color="white", font=Spiegel).pack(pady=5)
        elo_listbox = ctk.CTkComboBox(
            add_window,
            values=["Unranked", "Ferro", "Bronze", "Prata", "Ouro", "Platina", "Esmeralda", "Diamante", "Mestre",
                    "Grão Mestre", "Desafiante"], state="readonly"
        )
        elo_listbox.pack(pady=5)

        ctk.CTkLabel(add_window, text="Nível de Honra:", text_color="white", font=Spiegel).pack(pady=5)
        honor_listbox = ctk.CTkComboBox(add_window, values=["1", "2", "3", "4", "5"], state="readonly")
        honor_listbox.pack(pady=5)

        def save_account():
            login = login_entry.get()
            riot_id = riot_id_entry.get()
            level = level_entry.get()
            elo = elo_listbox.get()
            honor = honor_listbox.get()

            if not (login and riot_id and level and elo and honor):
                messagebox.showerror("Erro", "Todos os campos devem ser preenchidos!")
                return

            if "#" not in riot_id:
                messagebox.showerror("Erro", "Riot ID deve conter # (ex: deoxu#dede)")
                return

            try:
                level = int(level)
                if level < 30 and elo != "Unranked":
                    messagebox.showerror("Erro", "Contas abaixo do nível 30 não podem ter elo.")
                    return
            except ValueError:
                messagebox.showerror("Erro", "Nível da conta deve ser um número válido.")
                return

            opgg_link = self.generate_opgg_link(riot_id)
            account = {
                "login": login,
                "riot_id": riot_id,
                "level": level,
                "elo": elo,
                "honor": honor,
                "opgg": opgg_link
            }

            self.accounts.append(account)
            self.save_accounts()
            self.update_account_list()
            add_window.destroy()  # Fecha a janela após salvar

        save_button = ctk.CTkButton(
            add_window, text="Salvar", command=save_account, fg_color="#1e2328",
            hover_color="#20252a", border_width=1, border_color="#c6a86c", font=self.Spiegel, text_color="#cdbe91", corner_radius=0
        )
        save_button.pack(pady=20)

        # Botão para fechar a janela
        def close_window():
            add_window.destroy()

        close_button = ctk.CTkButton(
            add_window, text="Cancelar", command=close_window, fg_color="#1e2328",
            hover_color="#20252a", border_width=1, border_color="#c6a86c", font=self.Spiegel, text_color="#cdbe91", corner_radius=0
        )
        close_button.pack(pady=10)

    def generate_opgg_link(self, riot_id):
        name, tag = riot_id.split("#")
        name = name.replace(" ", "-")
        return f"https://www.op.gg/summoners/br/{name}-{tag}"

    def update_account_list(self, filtered_accounts=None):
        Spiegel_path = "assets/fonts/Spiegel.ttf"
        Spiegel = ctk.CTkFont(family="Spiegel", size=14)
        for widget in self.account_list.winfo_children():
            widget.destroy()

        accounts_to_show = filtered_accounts if filtered_accounts else self.accounts

        if not accounts_to_show:
            no_accounts_label = ctk.CTkLabel(self.account_list, text="Nenhuma conta adicionada ainda.", font=Spiegel)
            no_accounts_label.pack(pady=10, fill="x")
        else:
            for account in accounts_to_show:
                account_frame = ctk.CTkFrame(self.account_list, fg_color="#1e2328")
                account_frame.pack(fill="x", pady=2, padx=5)

                # Frame que conterá os campos estilizados
                fields_frame = ctk.CTkFrame(account_frame, fg_color="#222b3d")
                fields_frame.pack(fill="x", expand=True)

                # Campos para os dados das contas
                fields = [
                    {"key": "login", "text": account['login'], "color": "white", "width": self.column_widths[0]},
                    {"key": "riot_id", "text": account['riot_id'], "color": "#c89c38", "link": account['opgg'], "width": self.column_widths[1]},
                    {"key": "level", "text": account['level'], "color": "white", "width": self.column_widths[2]},
                    {"key": "elo", "text": account['elo'], "color": "white", "width": self.column_widths[3]},
                    {"key": "honor", "text": account['honor'], "color": "white", "width": self.column_widths[4]}
                ]

                for field in fields:
                    # Criação do frame estilizado para cada campo
                    field_div = ctk.CTkFrame(
                        fields_frame,
                        fg_color="#1e2328",
                        border_width=1,
                        border_color="#c6a86c",
                        corner_radius=0,
                        width=field["width"],
                        height=35  # Altura fixa para cada campo
                    )
                    field_div.pack(side="left", padx=5, pady=5)
                    field_div.pack_propagate(False)  # Impede que o conteúdo afete o tamanho

                    # Criação do texto dentro do frame
                    if "link" in field:
                        field_label = ctk.CTkLabel(
                            field_div,
                            text=field["text"],
                            font=("Segoe UI", 12, "underline"),
                            text_color=field["color"],
                            cursor="hand2"
                        )
                        field_label.bind("<Button-1>", lambda e, link=field["link"]: webbrowser.open(link))
                    else:
                        field_label = ctk.CTkLabel(
                            field_div,
                            text=field["text"],
                            font=("Segoe UI", 12),
                            text_color=field["color"]
                        )

                    field_label.pack(padx=5, pady=5, expand=True)

                # Ações (botões de editar e deletar)
                actions_frame = ctk.CTkFrame(
                    fields_frame,
                    fg_color="#1e2328",
                    border_width=1,
                    border_color="#c6a86c",
                    corner_radius=0,
                    width=self.column_widths[5],
                    height=35  # Altura fixa para o frame de ações
                )
                actions_frame.pack(side="left", padx=5, pady=5)
                actions_frame.pack_propagate(False)  # Impede que o conteúdo afete o tamanho

                # Frame interno para os botões
                button_container = ctk.CTkFrame(actions_frame, fg_color="#1e2328")
                button_container.pack(expand=True, fill="both", padx=1, pady=1)

                # Frame para centralizar os botões
                button_frame = ctk.CTkFrame(button_container, fg_color="#1e2328")
                button_frame.pack(expand=True)

                delete_img = ctk.CTkImage(Image.open(os.path.join("assets", "deleteimg.png")), size=(16, 16))
                edit_img = ctk.CTkImage(Image.open(os.path.join("assets", "editimg.png")), size=(16, 16))

                edit_button = ctk.CTkButton(
                    button_frame,
                    image=edit_img,
                    text="",
                    fg_color="#1e2328",
                    hover_color="#20252a",
                    width=25,
                    height=25,
                    corner_radius=0,
                    command=lambda acc=account: self.edit_account(acc)
                )
                edit_button.pack(side="left", padx=2)

                delete_button = ctk.CTkButton(
                    button_frame,
                    image=delete_img,
                    text="",
                    fg_color="#1e2328",
                    hover_color="#20252a",
                    width=25,
                    height=25,
                    corner_radius=0,
                    command=lambda acc=account: self.delete_account(acc)
                )
                delete_button.pack(side="left", padx=2)

    def update_filter_options(self, selection):
        if selection == "Elo":
            self.filter_option_listbox.configure(values=["Unranked", "Ferro", "Bronze", "Prata", "Ouro", "Platina", "Esmeralda", "Diamante", "Mestre", "Grão Mestre", "Desafiante"])
            self.filter_option_listbox.set("")
        elif selection == "Honra":
            self.filter_option_listbox.configure(values=["1", "2", "3", "4", "5"])
            self.filter_option_listbox.set("")
        elif selection == "Level":
            self.filter_option_listbox.configure(values=["Nível 30+", "Nível 30-"])
            self.filter_option_listbox.set("")

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

    def clear_filters(self):
        self.update_account_list()

    def edit_account(self, account):
        messagebox.showinfo("Editar Conta", f"Editar função ainda não implementada para {account['login']}.")

    def delete_account(self, account):
        self.accounts.remove(account)
        self.save_accounts()
        self.update_account_list()

    def save_accounts(self):
        with open(self.data_file, "w") as file:
            json.dump(self.accounts, file, indent=4)

    def load_accounts(self):
        if os.path.exists(self.data_file):
            with open(self.data_file, "r") as file:
                self.accounts = json.load(file)

if __name__ == "__main__":
    app = AccountManagerApp()
    app.mainloop()
