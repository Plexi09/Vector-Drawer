import tkinter as tk
from tkinter import ttk, messagebox, colorchooser
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import numpy as np

class VectorDrawingApp:
	def __init__(self, root):
		self.root = root
		self.root.title("Vecteurs")

		# Liste des vecteurs et leurs noms
		self.vectors = []
		self.vector_names = []
		self.colors = []

		# Conteneur principal
		self.main_frame = ttk.Frame(root, padding="10")
		self.main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

		# Création de la figure matplotlib
		self.fig = Figure(figsize=(6, 6))
		self.ax = self.fig.add_subplot(111)
		self.canvas = FigureCanvasTkAgg(self.fig, master=self.main_frame)
		self.canvas.draw()
		self.canvas.get_tk_widget().grid(row=0, column=0, columnspan=3, padx=5, pady=5)

		# Zone de contrôle
		self.control_frame = ttk.LabelFrame(self.main_frame, text="Contrôles", padding="5")
		self.control_frame.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=5)

		# Entrées pour vecteurs
		ttk.Label(self.control_frame, text="Composante X :").grid(row=0, column=0, padx=5)
		self.x_entry = ttk.Entry(self.control_frame, width=10)
		self.x_entry.grid(row=0, column=1, padx=5)

		ttk.Label(self.control_frame, text="Composante Y :").grid(row=0, column=2, padx=5)
		self.y_entry = ttk.Entry(self.control_frame, width=10)
		self.y_entry.grid(row=0, column=3, padx=5)

		ttk.Label(self.control_frame, text="Nom du vecteur :").grid(row=0, column=4, padx=5)
		self.name_entry = ttk.Entry(self.control_frame, width=10)
		self.name_entry.grid(row=0, column=5, padx=5)

		# Palette de couleurs pour choisir la couleur
		self.color_btn = ttk.Button(self.control_frame, text="Choisir couleur", command=self.choose_color)
		self.color_btn.grid(row=0, column=6, padx=5)

		self.selected_color = 'blue'  # Couleur par défaut

		# Boutons
		self.add_btn = ttk.Button(self.control_frame, text="Ajouter le vecteur", command=self.add_vector)
		self.add_btn.grid(row=0, column=7, padx=5)

		self.clear_btn = ttk.Button(self.control_frame, text="Effacer tout", command=self.clear_vectors)
		self.clear_btn.grid(row=0, column=8, padx=5)

		# Opérations sur les vecteurs
		self.op_frame = ttk.LabelFrame(self.main_frame, text="Opérations sur les vecteurs", padding="5")
		self.op_frame.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=5)

		ttk.Label(self.op_frame, text="Facteur d'échelle :").grid(row=0, column=0, padx=5)
		self.scale_entry = ttk.Entry(self.op_frame, width=10)
		self.scale_entry.grid(row=0, column=1, padx=5)

		ttk.Label(self.op_frame, text="Sélectionner un vecteur :").grid(row=1, column=0, padx=5)
		self.vector_listbox = tk.Listbox(self.op_frame, height=5, selectmode=tk.MULTIPLE)
		self.vector_listbox.grid(row=1, column=1, padx=5)

		self.scale_btn = ttk.Button(self.op_frame, text="Mettre à l'échelle", command=self.scale_vector)
		self.scale_btn.grid(row=0, column=2, padx=5)

		self.addition_btn = ttk.Button(self.op_frame, text="Additionner les vecteurs", command=self.add_vectors)
		self.addition_btn.grid(row=1, column=2, padx=5)

		# Zone de contrôle du déplacement et zoom
		self.zoom_frame = ttk.LabelFrame(self.main_frame, text="Contrôles caméra", padding="5")
		self.zoom_frame.grid(row=3, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=5)

		self.zoom_in_btn = ttk.Button(self.zoom_frame, text="Zoom +", command=self.zoom_in)
		self.zoom_in_btn.grid(row=0, column=0, padx=5)

		self.zoom_out_btn = ttk.Button(self.zoom_frame, text="Zoom -", command=self.zoom_out)
		self.zoom_out_btn.grid(row=0, column=1, padx=5)

		self.move_up_btn = ttk.Button(self.zoom_frame, text="Déplacer Haut", command=self.move_up)
		self.move_up_btn.grid(row=1, column=0, padx=5)

		self.move_down_btn = ttk.Button(self.zoom_frame, text="Déplacer Bas", command=self.move_down)
		self.move_down_btn.grid(row=1, column=1, padx=5)

		self.move_left_btn = ttk.Button(self.zoom_frame, text="Déplacer Gauche", command=self.move_left)
		self.move_left_btn.grid(row=1, column=2, padx=5)

		self.move_right_btn = ttk.Button(self.zoom_frame, text="Déplacer Droite", command=self.move_right)
		self.move_right_btn.grid(row=1, column=3, padx=5)

		# Initialisation du graphique
		self.setup_plot()

	def setup_plot(self):
		"""Initialiser le graphique avec des contrôles de caméra"""
		self.ax.clear()
		self.ax.grid(True)
		self.ax.axhline(y=0, color='k', linestyle='-', linewidth=0.5)
		self.ax.axvline(x=0, color='k', linestyle='-', linewidth=0.5)
		self.ax.set_xlim(-5, 5)
		self.ax.set_ylim(-5, 5)
		self.ax.set_aspect('equal')
		self.canvas.draw()

	def add_vector(self):
		"""Ajouter un vecteur avec un nom et une couleur"""
		try:
			x = float(self.x_entry.get())
			y = float(self.y_entry.get())
			name = self.name_entry.get()
			self.vectors.append([x, y])
			self.vector_names.append(name if name else f"Vecteur {len(self.vectors)}")
			self.colors.append(self.selected_color)
			self.update_vector_listbox()
			self.draw_vectors()
		except ValueError:
			messagebox.showerror("Erreur", "Veuillez entrer des valeurs valides pour les composants du vecteur.")

	def update_vector_listbox(self):
		"""Mettre à jour la liste des vecteurs"""
		self.vector_listbox.delete(0, tk.END)
		for name in self.vector_names:
			self.vector_listbox.insert(tk.END, name)

	def choose_color(self):
		"""Ouvrir la palette de couleurs"""
		color_code = colorchooser.askcolor()[1]
		if color_code:
			self.selected_color = color_code

	def scale_vector(self):
		"""Mettre à l'échelle un vecteur spécifique"""
		try:
			scale = float(self.scale_entry.get())
			selected_idx = self.vector_listbox.curselection()
			if selected_idx:
				idx = selected_idx[0]
				self.vectors[idx] = [scale * x for x in self.vectors[idx]]
				self.draw_vectors()
			else:
				messagebox.showerror("Erreur", "Veuillez sélectionner un vecteur à mettre à l'échelle.")
		except ValueError:
			messagebox.showerror("Erreur", "Veuillez entrer un facteur d'échelle valide.")

	def add_vectors(self):
		"""Additionner plusieurs vecteurs"""
		selected_idx = self.vector_listbox.curselection()
		if len(selected_idx) < 2:
			messagebox.showerror("Erreur", "Veuillez sélectionner au moins deux vecteurs à additionner.")
			return

		# Additionner les vecteurs sélectionnés
		sum_vector = np.zeros(2)
		for idx in selected_idx:
			sum_vector += self.vectors[idx]
		self.vectors.append(sum_vector)
		self.vector_names.append("Somme des vecteurs")
		self.colors.append('black')
		self.update_vector_listbox()
		self.draw_vectors()

	def clear_vectors(self):
		"""Effacer tous les vecteurs"""
		self.vectors = []
		self.vector_names = []
		self.colors = []
		self.setup_plot()

	def draw_vectors(self):
		"""Dessiner tous les vecteurs"""
		self.setup_plot()
		origin = np.zeros(2)
		for vector, color in zip(self.vectors, self.colors):
			self.ax.quiver(*origin, *vector, angles='xy', scale_units='xy', scale=1, color=color)
		self.canvas.draw()

	# Fonctions de contrôle de caméra
	def zoom_in(self):
		self.ax.set_xlim(self.ax.get_xlim()[0] * 0.8, self.ax.get_xlim()[1] * 0.8)
		self.ax.set_ylim(self.ax.get_ylim()[0] * 0.8, self.ax.get_ylim()[1] * 0.8)
		self.canvas.draw()

	def zoom_out(self):
		self.ax.set_xlim(self.ax.get_xlim()[0] * 1.2, self.ax.get_xlim()[1] * 1.2)
		self.ax.set_ylim(self.ax.get_ylim()[0] * 1.2, self.ax.get_ylim()[1] * 1.2)
		self.canvas.draw()

	def move_up(self):
		self.ax.set_ylim(self.ax.get_ylim()[0] + 1, self.ax.get_ylim()[1] + 1)
		self.canvas.draw()

	def move_down(self):
		self.ax.set_ylim(self.ax.get_ylim()[0] - 1, self.ax.get_ylim()[1] - 1)
		self.canvas.draw()

	def move_left(self):
		self.ax.set_xlim(self.ax.get_xlim()[0] - 1, self.ax.get_xlim()[1] - 1)
		self.canvas.draw()

	def move_right(self):
		self.ax.set_xlim(self.ax.get_xlim()[0] + 1, self.ax.get_xlim()[1] + 1)
		self.canvas.draw()

# Lancer l'application
root = tk.Tk()
app = VectorDrawingApp(root)
root.mainloop()
