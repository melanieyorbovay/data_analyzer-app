import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
import pyperclip

class DataAnalyzer:
    def __init__(self, root):
        self.root = root
        self.root.title("Analyseur de Données CSV")
        self.root.geometry("900x600")
        self.df = None
        self.setup_ui()

    def setup_ui(self):
        """Configuration de l'interface utilisateur."""
        title = tk.Label(self.root, text="Analyseur de Données CSV", font=("Arial", 18, "bold"))
        title.pack(pady=10)

        # Premiere Frame
        main_frame = tk.Frame(self.root)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Colonne de Gauche
        left_frame = tk.Frame(main_frame, width=300)
        left_frame.pack(side="left", fill="y", padx=(0, 10))
        left_frame.pack_propagate(False)

        #Bouton de chargement de fichier
        load_btn = tk.Button(left_frame, text="Charger un fichier CSV",
                              command=self.load_csv,
                              font=("Arial", 12, "bold"),
                              padx=20, pady=10)
        load_btn.pack(pady=20, fill="x")

        #Statistques
        tk.Label(left_frame, text="Statistiques",
                  font=("Arial", 12, "bold")).pack(pady=(20, 10))
        
        self.stats_text = tk.Text(left_frame, height=15, width=35)
        self.stats_text.pack(pady=5, fill="both", expand=True)

        #Boutons graphiques
        tk.Label(left_frame, text="Graphiques",
                  font=("Arial", 12, "bold")).pack(pady=(10,5))
        
        hist_btn = tk.Button(left_frame, text="Histogramme",
                              command=lambda: self.plot_graph('hist'),
                              padx=10, pady=5)
        hist_btn.pack(fill="x", pady=2)

        box_btn = tk.Button(left_frame, text="Boxplot",
                              command=lambda: self.plot_graph('box'),
                              padx=10, pady=5)
        box_btn.pack(fill="x", pady=2)

        # Colonne de droite: Données et graphique
        right_frame = tk.Frame(main_frame)
        right_frame.pack(side="right", fill="both", expand=True)

        #Apercu des données
        tk.Label(right_frame, text="Aperçu des données",
                  font=("Arial", 12, "bold")).pack(pady=(0,10))

        #Treeview pour les données
        tree_frame = ttk.Frame(right_frame)
        tree_frame.pack(fill="both", expand=True, pady=(0, 10)) 

        self.tree = ttk.Treeview(tree_frame, columns=("C1","C2","C3","C4"), show="headings", height=8)
        for col in ("C1","C2","C3","C4"):
            self.tree.heading(col, text=col)
            self.tree.column(col, width=120)

        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        scrollbar.pack(side="right", fill="y")
        self.tree.configure(yscroll=scrollbar.set)
        
        #Frame pour graphiques
        tk.Label(right_frame, text="Graphiques",
                  font=("Arial", 12, "bold")).pack(pady=(10,5))
        self.plot_frame = tk.Frame(right_frame, bg="white", height=300)
        self.plot_frame.pack(fill="both", expand=True)
        self.plot_frame.pack_propagate(False)
        
        #Barre de statut
        self.status_var = tk.StringVar(value="Prêt à charger un fichier CSV")
        status_bar = tk.Label(self.root, textvariable=self.status_var,
                               relief="sunken", anchor="w")
        status_bar.pack(side="bottom", fill="x")
    
    def load_csv(self):
        filename = filedialog.askopenfilename(
            title="Choisir fichier CSV",
            filetypes=[("CSV", "*.csv")]
        )
        if not filename:
            return

        try:
            self.df = pd.read_csv(filename)
            self.status_var.set(f"{len(self.df)} lignes chargées")
            self.refresh_preview()
            self.show_stats()
            messagebox.showinfo("OK", f"{len(self.df)} lignes × {len(self.df.columns)} colonnes")
        except Exception as e:
            messagebox.showerror("Erreur", str(e))

    def refresh_preview(self):
        #Efface Treeview
        for item in self.tree.get_children():
            self.tree.delete(item)

        if self.df is None:
            return
        
        #Ajoute les 10 premières lignes
        for i in range(min(10, len(self.df))):
            row = [str(x)[:10]for x in self.df.iloc[i].head(4).values] + self.df.iloc[i].head(4).astype(str).tolist()
            self.tree.insert("", "end", values=row)

    def show_stats(self):
        if self.df is None:
            self.stats_text.delete(1.0, tk.END)
            self.stats_text.insert(1.0, "Chargez un fichier CSV d'abord!")
            return

        self.stats_text.delete(1.0, tk.END)

        stats = f""" Analyse Rapide
{'='*30}
DIMENSIONS

LIGNES: {len(self.df):,}
COLONNES: {len(self.df.columns)}

PREMIERES COLONNES:
"""
        # Liste TOUTES les colonnes
        for i, col in enumerate(self.df.columns):
            stats += f" {i+1:2d}. {col}\n"

        #statistiques numériques simples
        numeric_cols = self.df.select_dtypes(include=['number']).columns
        if len(numeric_cols) > 0:
            stats += f"\n  ({len(numeric_cols)} colonnes numériques)\n{'='*30}\n"

            for col in numeric_cols:
                serie = self.df[col].dropna()
                if len(serie) > 0:
                    stats += f"\n {col}:\n"
                    stats += f" Valeurs: {len(serie):,}\n"
                    stats += f" Moyenne: {serie.mean():.1f}\n"
                    stats += f" Min: {serie.min():.1f}\n"
                    stats += f" Max: {serie.max():.1f}\n"
        else:
            stats += f"\n Aucune colonne numérique\n"
        
        # Affiche les statistiques
        self.stats_text.insert(1.0, stats)

    def plot_graph(self, type_graph):
        if self.df is None:
            messagebox.showwarning("Attention", "Chargez d'abord un fichier CSV !")
            return

        numeric = self.df.select_dtypes(include=[np.number])
        
        if numeric.empty:
            messagebox.showwarning("Attention", "Aucune colonne numérique trouvée !")
            return

        #Efface le graphique précédent
        for widget in self.plot_frame.winfo_children():
            widget.destroy()

        #Nouveau graphique
        fig, ax = plt.subplots(figsize=(8,4))

        if type_graph == 'hist' and len(numeric.columns) > 0:
            numeric.iloc [:, 0].hist(ax=ax, bins=10, color='skyblue')
            ax.set_title("Histogramme")
        else: #Boxplot
            numeric.boxplot(ax=ax)
            ax.set_title("Boxplot")

        ax.grid(True, alpha=0.3)

        #Affiche dans TKinter
        canvas = FigureCanvasTkAgg(fig, master=self.plot_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)

        self.status_var.set(f"Graphique '{type_graph}' généré")
    
def main():
    root = tk.Tk()
    app = DataAnalyzer(root)
    root.mainloop()

if __name__ == "__main__":
    main()