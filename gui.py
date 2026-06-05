import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import pandas as pd
from data_cleaning import clean_dataset
from PIL import Image, ImageTk

class LagoonAnalyticsApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Lagoon Sales Analytics System")
        icon = tk.PhotoImage(file="assets/PUPLogo.png")
        self.root.iconphoto(False, icon)
        self.root.icon_image = icon
        self.root.geometry("1300x700")
        self.root.configure(bg="#F5F5F5")

        self.file_path = None
        self.df = None
        self.cleaned_df = None

        self.MAROON = "#800000"
        self.DARK_MAROON = "#5A0000"
        self.GOLD = "#FFD700"
        self.LIGHT_BG = "#F5F5F5"
        self.WHITE = "#FFFFFF"
        self.DARK_TEXT = "#222222"

        style = ttk.Style()
        style.theme_use("default")

        style.configure(
            "Treeview",
            background=self.WHITE,
            foreground=self.DARK_TEXT,
            rowheight=26,
            fieldbackground=self.WHITE,
            font=("Arial", 10)
        )

        style.configure(
            "Treeview.Heading",
            background=self.MAROON,
            foreground=self.WHITE,
            font=("Arial", 10, "bold")
        )

        style.map(
            "Treeview",
            background=[("selected", self.GOLD)],
            foreground=[("selected", self.DARK_TEXT)]
        )

        main_frame = tk.Frame(self.root, bg=self.LIGHT_BG)
        main_frame.pack(fill="both", expand=True)

        sidebar = tk.Frame(main_frame, width=240, bg=self.MAROON)
        sidebar.pack(side="left", fill="y")
        sidebar.pack_propagate(False)

        try:
            logo_image = Image.open("assets/PUPLogo.png")
            logo_image = logo_image.resize((90, 90))
            self.logo_photo = ImageTk.PhotoImage(logo_image)

            logo_label = tk.Label(
                sidebar,
                image=self.logo_photo,
                bg=self.MAROON
            )
            logo_label.pack(pady=(25, 10))

        except Exception as e:
            print("Logo not found or cannot be loaded:", e)

        title = tk.Label(
            sidebar,
            text="LAGOON\nANALYTICS",
            font=("Arial", 18, "bold"),
            bg=self.MAROON,
            fg=self.GOLD,
            justify="center"
        )
        title.pack(pady=(30, 5))

        subtitle = tk.Label(
            sidebar,
            text="PUP Lagoon Stalls",
            font=("Arial", 10),
            bg=self.MAROON,
            fg=self.WHITE
        )
        subtitle.pack(pady=(0, 25))

        self.create_sidebar_button(sidebar, "Load Dataset", self.load_dataset)
        self.create_sidebar_button(sidebar, "Clean Dataset", self.clean_data)
        self.create_sidebar_button(sidebar, "Show Dataset Info", self.show_info)
        self.create_sidebar_button(sidebar, "Show Raw Data", self.show_raw_data)
        self.create_sidebar_button(sidebar, "Show Cleaned Data", self.show_cleaned_data)

        exit_button = tk.Button(
            sidebar,
            text="Exit",
            width=22,
            bg=self.DARK_MAROON,
            fg=self.WHITE,
            activebackground=self.GOLD,
            activeforeground=self.DARK_TEXT,
            font=("Arial", 10, "bold"),
            relief="flat",
            command=self.root.destroy
        )
        exit_button.pack(pady=30, ipady=6)

        content = tk.Frame(main_frame, bg=self.LIGHT_BG)
        content.pack(side="right", fill="both", expand=True)

        heading = tk.Label(
            content,
            text="Lagoon Sales and Food Preference Analytics System",
            font=("Arial", 18, "bold"),
            bg=self.LIGHT_BG,
            fg=self.MAROON
        )
        heading.pack(pady=(20, 5))

        table_frame = tk.Frame(content, bg=self.WHITE, bd=2, relief="groove")
        table_frame.pack(fill="both", expand=True, padx=15, pady=10)

        self.tree = ttk.Treeview(table_frame, show="headings")

        self.scroll_y = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        self.scroll_x = ttk.Scrollbar(table_frame, orient="horizontal", command=self.tree.xview)

        self.tree.configure(
            yscrollcommand=self.scroll_y.set,
            xscrollcommand=self.scroll_x.set
        )

        self.tree.grid(row=0, column=0, sticky="nsew")
        self.scroll_y.grid(row=0, column=1, sticky="ns")
        self.scroll_x.grid(row=1, column=0, sticky="ew")

        table_frame.rowconfigure(0, weight=1)
        table_frame.columnconfigure(0, weight=1)

        self.status_label = tk.Label(
            content,
            text="No dataset loaded.",
            anchor="w",
            font=("Arial", 10),
            bg=self.MAROON,
            fg=self.WHITE,
            padx=10
        )
        self.status_label.pack(fill="x", padx=15, pady=(0, 10), ipady=6)

    def create_sidebar_button(self, parent, text, command):
        button = tk.Button(
            parent,
            text=text,
            width=22,
            bg=self.GOLD,
            fg=self.DARK_TEXT,
            activebackground=self.WHITE,
            activeforeground=self.MAROON,
            font=("Arial", 10, "bold"),
            relief="flat",
            command=command
        )
        button.pack(pady=7, ipady=6)
        return button

    def load_dataset(self):
        self.file_path = filedialog.askopenfilename(
            title="Select CSV File",
            filetypes=[("CSV Files", "*.csv")]
        )

        if self.file_path:
            self.df = pd.read_csv(self.file_path)
            self.cleaned_df = None
            self.display_table(self.df)

            self.status_label.config(
                text=f"Loaded dataset: {self.file_path} | Rows: {self.df.shape[0]} | Columns: {self.df.shape[1]}"
            )

            messagebox.showinfo("Success", "Dataset loaded successfully!")

    def clean_data(self):
        if not self.file_path:
            messagebox.showwarning("Warning", "Please load a dataset first.")
            return

        self.cleaned_df = clean_dataset(self.file_path)
        self.display_table(self.cleaned_df)

        self.status_label.config(
            text=f"Dataset cleaned successfully! Rows: {self.cleaned_df.shape[0]} | Columns: {self.cleaned_df.shape[1]} | Saved as data/lagoon_sales_cleaned.csv"
        )

        messagebox.showinfo("Success", "Dataset cleaned successfully!")

    def show_info(self):
        df = self.get_current_dataframe()

        if df is None:
            messagebox.showwarning("Warning", "Please load a dataset first.")
            return

        info_window = tk.Toplevel(self.root)
        info_window.title("Dataset Information")
        info_window.geometry("650x500")
        info_window.configure(bg=self.LIGHT_BG)

        header = tk.Label(
            info_window,
            text="Dataset Information",
            font=("Arial", 15, "bold"),
            bg=self.MAROON,
            fg=self.GOLD,
            pady=10
        )
        header.pack(fill="x")

        text_box = tk.Text(
            info_window,
            wrap="word",
            bg=self.WHITE,
            fg=self.DARK_TEXT,
            font=("Consolas", 10)
        )
        text_box.pack(fill="both", expand=True, padx=10, pady=10)

        info = ""
        info += "DATASET INFORMATION\n\n"
        info += f"Rows: {df.shape[0]}\n"
        info += f"Columns: {df.shape[1]}\n\n"

        info += "COLUMN NAMES\n"
        for col in df.columns:
            info += f"- {col}\n"

        info += "\nMISSING VALUES\n"
        info += str(df.isnull().sum())

        info += "\n\nDUPLICATE ROWS\n"
        info += str(df.duplicated().sum())

        info += "\n\nNUMERICAL SUMMARY\n"
        info += str(df.describe())

        text_box.insert("1.0", info)
        text_box.config(state="disabled")

    def show_raw_data(self):
        if self.df is None:
            messagebox.showwarning("Warning", "Please load a dataset first.")
            return

        self.display_table(self.df)
        self.status_label.config(
            text=f"Showing raw dataset | Rows: {self.df.shape[0]} | Columns: {self.df.shape[1]}"
        )

    def show_cleaned_data(self):
        if self.cleaned_df is None:
            messagebox.showwarning("Warning", "Please clean the dataset first.")
            return

        self.display_table(self.cleaned_df)
        self.status_label.config(
            text=f"Showing cleaned dataset | Rows: {self.cleaned_df.shape[0]} | Columns: {self.cleaned_df.shape[1]}"
        )

    def display_table(self, df):
        self.tree.delete(*self.tree.get_children())
        self.tree["columns"] = list(df.columns)

        for col in df.columns:
            self.tree.heading(col, text=col)

            max_data_length = df[col].astype(str).map(len).max()
            header_length = len(col)
            max_length = max(max_data_length, header_length)

            column_width = max_length * 10

            if column_width < 100:
                column_width = 100
            elif column_width > 240:
                column_width = 240

            self.tree.column(
                col,
                width=column_width,
                minwidth=column_width,
                anchor="center",
                stretch=False
            )

        for _, row in df.iterrows():
            self.tree.insert("", "end", values=list(row))

    def get_current_dataframe(self):
        if self.cleaned_df is not None:
            return self.cleaned_df
        return self.df

    def run(self):
        self.root.mainloop()