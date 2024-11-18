import tkinter as tk
from tkinter import ttk, messagebox, colorchooser
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import numpy as np
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from ttkbootstrap.dialogs import Messagebox
from ttkbootstrap.toast import ToastNotification
import json
from datetime import datetime
import os

class VectorDrawingApp:
	def __init__(self, root):
		self.root = root
		self.root.title("Calcul Vectoriel")

		# Variables d'état
		self.vectors = []
		self.vector_names = []
		self.colors = []
		self.selected_color = '#3498db'  # Bleu par défaut
		self.history = []  # Pour undo/redo
		self.current_step = -1

		# Configuration de la grille principale
		self.root.grid_columnconfigure(0, weight=1)
		self.root.grid_columnconfigure(1, weight=3)
		self.root.grid_rowconfigure(1, weight=1)

		self.create_gui()

	def create_gui(self):
		"""Interface utilisateur moderne"""
		self.create_header()
		self.create_sidebar()
		self.create_main_content()
		self.create_status_bar()

	def create_header(self):
		"""En-tête avec titre et outils rapides"""
		header = ttk.Frame(self.root, style='primary.TFrame', padding=10)
		header.grid(row=0, column=0, columnspan=2, sticky="ew")

		# Logo et titre
		title = ttk.Label(
			header,
			text="📐 Calcul Vectoriel",
			font=("Helvetica", 20, "bold"),
			style='primary.Inverse.TLabel'
		)
		title.pack(side="left", padx=10)

		# Barre d'outils rapide
		toolbar = ttk.Frame(header, style='primary.TFrame')
		toolbar.pack(side="right")

		# Boutons undo/redo
		self.undo_btn = ttk.Button(
			toolbar,
			text="↩️",
			style='primary.Outline.TButton',
			command=self.undo,
			state="disabled"
		)
		self.undo_btn.pack(side="left", padx=2)

		self.redo_btn = ttk.Button(
			toolbar,
			text="↪️",
			style='primary.Outline.TButton',
			command=self.redo,
			state="disabled"
		)
		self.redo_btn.pack(side="left", padx=2)

	def create_sidebar(self):
		"""Panneau de contrôle latéral amélioré"""
		sidebar = ttk.Frame(self.root, style='secondary.TFrame', padding=10)
		sidebar.grid(row=1, column=0, sticky="nsew")

		# Section Création de vecteur
		vector_frame = ttk.LabelFrame(sidebar, text="Création de Vecteur", padding=10)
		vector_frame.pack(fill="x", pady=5)

		# Entrées X et Y avec validation
		ttk.Label(vector_frame, text="Composante X:").pack(anchor="w")
		self.x_entry = ttk.Entry(vector_frame, width=15)
		self.x_entry.pack(fill="x", pady=2)

		ttk.Label(vector_frame, text="Composante Y:").pack(anchor="w")
		self.y_entry = ttk.Entry(vector_frame, width=15)
		self.y_entry.pack(fill="x", pady=2)

		ttk.Label(vector_frame, text="Nom du vecteur:").pack(anchor="w")
		self.name_entry = ttk.Entry(vector_frame, width=15)
		self.name_entry.pack(fill="x", pady=2)

		# Sélecteur de couleur amélioré
		color_frame = ttk.Frame(vector_frame)
		color_frame.pack(fill="x", pady=5)

		self.color_preview = ttk.Label(
			color_frame,
			text="  ",
			background=self.selected_color,
			width=2
		)
		self.color_preview.pack(side="left", padx=5)

		color_btn = ttk.Button(
			color_frame,
			text="🎨 Couleur",
			style='info.Outline.TButton',
			command=self.choose_color
		)
		color_btn.pack(side="left", fill="x", expand=True)

		# Bouton d'ajout
		add_btn = ttk.Button(
			vector_frame,
			text="➕ Ajouter le vecteur",
			style='success.TButton',
			command=self.add_vector
		)
		add_btn.pack(fill="x", pady=5)

		# Section Opérations
		op_frame = ttk.LabelFrame(sidebar, text="Opérations", padding=10)
		op_frame.pack(fill="x", pady=5)

		# Liste des vecteurs avec scrollbar
		self.vector_listbox = ttk.Treeview(
			op_frame,
			height=6,
			selectmode="extended",
			columns=("x", "y"),
			show="headings"
		)
		self.vector_listbox.heading("x", text="X")
		self.vector_listbox.heading("y", text="Y")
		self.vector_listbox.pack(fill="x", pady=5)

		# Facteur d'échelle
		scale_frame = ttk.Frame(op_frame)
		scale_frame.pack(fill="x", pady=5)

		ttk.Label(scale_frame, text="Échelle:").pack(side="left")
		self.scale_entry = ttk.Entry(scale_frame, width=8)
		self.scale_entry.pack(side="left", padx=5)

		scale_btn = ttk.Button(
			scale_frame,
			text="↔️ Mettre à l'échelle",
			style='info.TButton',
			command=self.scale_vector
		)
		scale_btn.pack(fill="x", pady=2)

		# Bouton d'addition
		add_vectors_btn = ttk.Button(
			op_frame,
			text="✚ Additionner les vecteurs",
			style='info.TButton',
			command=self.add_vectors
		)
		add_vectors_btn.pack(fill="x", pady=2)

		# Bouton de suppression
		delete_btn = ttk.Button(
			op_frame,
			text="🗑️ Supprimer sélection",
			style='danger.Outline.TButton',
			command=self.delete_selected
		)
		delete_btn.pack(fill="x", pady=2)

	def create_main_content(self):
		"""Zone principale avec graphique et contrôles de vue"""
		main_frame = ttk.Frame(self.root, padding=10)
		main_frame.grid(row=1, column=1, sticky="nsew")

		# Création du graphique
		self.fig = Figure(figsize=(6, 6), facecolor='#2b3e50')
		self.ax = self.fig.add_subplot(111, facecolor='#2b3e50')
		self.canvas = FigureCanvasTkAgg(self.fig, master=main_frame)
		self.canvas.draw()
		self.canvas.get_tk_widget().pack(fill="both", expand=True, padx=5, pady=5)

		# Contrôles de vue
		view_frame = ttk.LabelFrame(main_frame, text="Contrôles de Vue", padding=5)
		view_frame.pack(fill="x", pady=5)

		# Grille de boutons de contrôle
		controls_grid = ttk.Frame(view_frame)
		controls_grid.pack()

		ttk.Button(controls_grid, text="🔍+", command=self.zoom_in).grid(row=0, column=1)
		ttk.Button(controls_grid, text="🔍-", command=self.zoom_out).grid(row=2, column=1)
		ttk.Button(controls_grid, text="⬅️", command=self.move_left).grid(row=1, column=0)
		ttk.Button(controls_grid, text="➡️", command=self.move_right).grid(row=1, column=2)
		ttk.Button(controls_grid, text="⬆️", command=self.move_up).grid(row=0, column=1)
		ttk.Button(controls_grid, text="⬇️", command=self.move_down).grid(row=2, column=1)
		ttk.Button(controls_grid, text="🔄", command=self.reset_view).grid(row=1, column=1)

	def create_status_bar(self):
		"""Barre d'état avec informations"""
		status_bar = ttk.Frame(self.root, style='primary.TFrame', padding=5)
		status_bar.grid(row=2, column=0, columnspan=2, sticky="ew")

		self.status_label = ttk.Label(
			status_bar,
			text="Prêt",
			style='primary.Inverse.TLabel'
		)
		self.status_label.pack(side="left", padx=5)

		self.coords_label = ttk.Label(
			status_bar,
			text="",
			style='primary.Inverse.TLabel'
		)
		self.coords_label.pack(side="right", padx=5)

	def setup_plot(self):
		"""Configuration initiale du graphique"""
		self.ax.clear()
		self.ax.grid(True, color='#4a6b8c', linestyle='--', alpha=0.5)
		self.ax.axhline(y=0, color='#4a6b8c', linestyle='-', linewidth=0.5)
		self.ax.axvline(x=0, color='#4a6b8c', linestyle='-', linewidth=0.5)
		self.ax.set_facecolor('#2b3e50')
		self.ax.tick_params(colors='white')
		self.ax.set_xlim(-5, 5)
		self.ax.set_ylim(-5, 5)
		self.ax.set_aspect('equal')

	def choose_color(self):
		"""Sélecteur de couleur amélioré"""
		color = colorchooser.askcolor(color=self.selected_color)
		if color[1]:
			self.selected_color = color[1]
			self.color_preview.configure(background=self.selected_color)

	def add_vector(self):
		"""Ajout d'un vecteur avec validation"""
		try:
			x = float(self.x_entry.get())
			y = float(self.y_entry.get())
			name = self.name_entry.get() or f"V{len(self.vectors)+1}"

			self.vectors.append([x, y])
			self.vector_names.append(name)
			self.colors.append(self.selected_color)

			# Mise à jour de l'historique
			self.add_to_history()

			# Mise à jour interface
			self.update_vector_listbox()
			self.draw_vectors()

			# Notification
			ToastNotification(
				title="Vecteur ajouté",
				message=f"Vecteur {name} ({x}, {y}) ajouté avec succès",
				duration=2000
			).show_toast()

			# Reset des entrées
			self.x_entry.delete(0, tk.END)
			self.y_entry.delete(0, tk.END)
			self.name_entry.delete(0, tk.END)

		except ValueError:
			Messagebox.show_error(
				"Erreur de saisie",
				"Veuillez entrer des valeurs numériques valides pour X et Y"
			)

	def draw_vectors(self):
		"""Dessin des vecteurs avec style"""
		self.setup_plot()
		origin = np.zeros(2)

		for i, (vector, name, color) in enumerate(zip(self.vectors, self.vector_names, self.colors)):
			# Dessin du vecteur
			self.ax.quiver(*origin, *vector,
						   angles='xy',
						   scale_units='xy',
						   scale=1,
						   color=color,
						   width=0.008,
						   headwidth=8,
						   headlength=10)

			# Étiquette du vecteur
			midpoint = np.array(vector) / 2
			self.ax.annotate(name,
							 xy=(midpoint[0], midpoint[1]),
							 xytext=(5, 5),
							 textcoords='offset points',
							 color='white',
							 fontsize=8)

		self.canvas.draw()
		self.update_status(f"{len(self.vectors)} vecteur(s) affichés")

	def add_to_history(self):
		"""Gestion de l'historique pour undo/redo"""
		# Supprime les étapes futures si on fait une nouvelle action après un undo
		self.history = self.history[:self.current_step + 1]

		# Sauvegarde l'état actuel
		current_state = {
			'vectors': self.vectors.copy(),
			'names': self.vector_names.copy(),
			'colors': self.colors.copy()
		}
		self.history.append(current_state)
		self.current_step += 1

		# Met à jour les boutons
		self.undo_btn.configure(state="normal")
		self.redo_btn.configure(state="disabled")

	def undo(self):
		"""Annuler la dernière action"""
		if self.current_step > 0:
			self.current_step -= 1
			state = self.history[self.current_step]

			self.vectors = state['vectors'].copy()
			self.vector_names = state['names'].copy()
			self.colors = state['colors'].copy()

			self.update_vector_listbox()
			self.draw_vectors()

			self.redo_btn.configure(state="normal")
			if self.current_step == 0:
				self.undo_btn.configure(state="disabled")

	def redo(self):
		"""Rétablir la dernière action annulée"""
		if self.current_step < len(self.history) - 1:
			self.current_step += 1
			state = self.history[self.current_step]

			self.vectors = state['vectors'].copy()
			self.vector_names = state['names'].copy()
			self.colors = state['colors'].copy()

			self.update_vector_listbox()
			self.draw_vectors()

			self.undo_btn.configure(state="normal")
			if self.current_step == len(self.history) - 1:
				self.redo_btn.configure(state="disabled")

			ToastNotification(
				title="Action rétablie",
				message="La dernière action a été rétablie",
				duration=1000
			).show_toast()

	def update_vector_listbox(self):
		"""Mise à jour de la liste des vecteurs"""
		# Effacer la liste actuelle
		for item in self.vector_listbox.get_children():
			self.vector_listbox.delete(item)

		# Ajouter les vecteurs avec leurs composantes
		for i, (vector, name) in enumerate(zip(self.vectors, self.vector_names)):
			self.vector_listbox.insert(
				"",
				"end",
				values=(f"{vector[0]:.2f}", f"{vector[1]:.2f}"),
				text=name,
				tags=(name,)
			)

			# Appliquer la couleur à la ligne
			self.vector_listbox.tag_configure(name, foreground=self.colors[i])

	def scale_vector(self):
		"""Mettre à l'échelle les vecteurs sélectionnés"""
		selection = self.vector_listbox.selection()
		if not selection:
			Messagebox.show_warning(
				"Aucune sélection",
				"Veuillez sélectionner au moins un vecteur"
			)
			return

		try:
			scale_factor = float(self.scale_entry.get())
			indices = [self.vector_listbox.index(item) for item in selection]

			for idx in indices:
				self.vectors[idx] = [v * scale_factor for v in self.vectors[idx]]

			# Ajouter à l'historique
			self.add_to_history()

			# Mettre à jour l'affichage
			self.update_vector_listbox()
			self.draw_vectors()

			ToastNotification(
				title="Mise à l'échelle effectuée",
				message=f"Facteur d'échelle {scale_factor} appliqué",
				duration=2000
			).show_toast()

		except ValueError:
			Messagebox.show_error(
				"Erreur de saisie",
				"Veuillez entrer un facteur d'échelle valide"
			)

	def add_vectors(self):
		"""Additionner les vecteurs sélectionnés"""
		selection = self.vector_listbox.selection()
		if len(selection) < 2:
			Messagebox.show_warning(
				"Sélection insuffisante",
				"Veuillez sélectionner au moins deux vecteurs"
			)
			return

		# Calculer la somme des vecteurs sélectionnés
		indices = [self.vector_listbox.index(item) for item in selection]
		sum_vector = np.array([0.0, 0.0])
		for idx in indices:
			sum_vector += np.array(self.vectors[idx])

		# Ajouter le vecteur résultant
		self.vectors.append(sum_vector.tolist())
		self.vector_names.append(f"Somme_{len(self.vectors)}")
		self.colors.append('#ff9800')  # Orange pour le vecteur somme

		# Ajouter à l'historique
		self.add_to_history()

		# Mettre à jour l'affichage
		self.update_vector_listbox()
		self.draw_vectors()

		ToastNotification(
			title="Addition effectuée",
			message="Les vecteurs ont été additionnés avec succès",
			duration=2000
		).show_toast()

	def delete_selected(self):
		"""Supprimer les vecteurs sélectionnés"""
		selection = self.vector_listbox.selection()
		if not selection:
			return

		if Messagebox.show_question(
				"Confirmer la suppression",
				"Voulez-vous vraiment supprimer les vecteurs sélectionnés ?"
		):
			indices = [self.vector_listbox.index(item) for item in selection]
			indices.sort(reverse=True)  # Supprimer de la fin vers le début

			for idx in indices:
				del self.vectors[idx]
				del self.vector_names[idx]
				del self.colors[idx]

			# Ajouter à l'historique
			self.add_to_history()

			# Mettre à jour l'affichage
			self.update_vector_listbox()
			self.draw_vectors()

			ToastNotification(
				title="Suppression effectuée",
				message="Les vecteurs sélectionnés ont été supprimés",
				duration=2000
			).show_toast()

	def zoom_in(self):
		"""Zoom avant sur le graphique"""
		xlim = self.ax.get_xlim()
		ylim = self.ax.get_ylim()
		self.ax.set_xlim([x * 0.8 for x in xlim])
		self.ax.set_ylim([y * 0.8 for y in ylim])
		self.canvas.draw()

	def zoom_out(self):
		"""Zoom arrière sur le graphique"""
		xlim = self.ax.get_xlim()
		ylim = self.ax.get_ylim()
		self.ax.set_xlim([x * 1.2 for x in xlim])
		self.ax.set_ylim([y * 1.2 for y in ylim])
		self.canvas.draw()

	def move_left(self):
		"""Déplacer la vue vers la gauche"""
		xlim = self.ax.get_xlim()
		shift = (xlim[1] - xlim[0]) * 0.1
		self.ax.set_xlim([x - shift for x in xlim])
		self.canvas.draw()

	def move_right(self):
		"""Déplacer la vue vers la droite"""
		xlim = self.ax.get_xlim()
		shift = (xlim[1] - xlim[0]) * 0.1
		self.ax.set_xlim([x + shift for x in xlim])
		self.canvas.draw()

	def move_up(self):
		"""Déplacer la vue vers le haut"""
		ylim = self.ax.get_ylim()
		shift = (ylim[1] - ylim[0]) * 0.1
		self.ax.set_ylim([y + shift for y in ylim])
		self.canvas.draw()

	def move_down(self):
		"""Déplacer la vue vers le bas"""
		ylim = self.ax.get_ylim()
		shift = (ylim[1] - ylim[0]) * 0.1
		self.ax.set_ylim([y - shift for y in ylim])
		self.canvas.draw()

	def reset_view(self):
		"""Réinitialiser la vue"""
		self.ax.set_xlim(-5, 5)
		self.ax.set_ylim(-5, 5)
		self.canvas.draw()

		ToastNotification(
			title="Vue réinitialisée",
			message="La vue a été réinitialisée",
			duration=1000
		).show_toast()

	def update_status(self, message):
		"""Mettre à jour la barre d'état"""
		self.status_label.configure(text=message)

	def save_project(self):
		"""Sauvegarder le projet"""
		try:
			data = {
				'vectors': self.vectors,
				'names': self.vector_names,
				'colors': self.colors,
				'timestamp': datetime.now().isoformat()
			}

			filename = f"vector_project_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
			with open(filename, 'w') as f:
				json.dump(data, f)

			ToastNotification(
				title="Projet sauvegardé",
				message=f"Projet sauvegardé dans {filename}",
				duration=2000
			).show_toast()

		except Exception as e:
			Messagebox.show_error(
				"Erreur de sauvegarde",
				f"Impossible de sauvegarder le projet: {str(e)}"
			)

	def load_project(self):
		"""Charger un projet"""
		try:
			filename = tk.filedialog.askopenfilename(
				filetypes=[("Fichiers JSON", "*.json")]
			)
			if filename:
				with open(filename, 'r') as f:
					data = json.load(f)

				self.vectors = data['vectors']
				self.vector_names = data['names']
				self.colors = data['colors']

				self.update_vector_listbox()
				self.draw_vectors()

				# Réinitialiser l'historique
				self.history = []
				self.current_step = -1
				self.add_to_history()

				ToastNotification(
					title="Projet chargé",
					message="Le projet a été chargé avec succès",
					duration=2000
				).show_toast()

		except Exception as e:
			Messagebox.show_error(
				"Erreur de chargement",
				f"Impossible de charger le projet: {str(e)}"
			)

def main():
	root = ttk.Window(themename="superhero")
	app = VectorDrawingApp(root)
	root.mainloop()

if __name__ == "__main__":
	main()