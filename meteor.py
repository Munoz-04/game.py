import tkinter as tk
from PIL import Image, ImageTk
import random
import time
import json
import os

# Configuración de la ventana
root = tk.Tk()
root.title("Meteor Game")
root.geometry("600x600")
root.config(bg="#000000")

# Configuración del lienzo
canvas = tk.Canvas(root, width=600, height=600, bg="#000000")
canvas.pack()

# Archivo de puntajes
SCORES_FILE = "scores/scores.scores.json"

# Función para cargar y guardar puntajes
def cargar_puntajes():
    try:
        if os.path.exists(SCORES_FILE):
            with open(SCORES_FILE, "r") as file:
                data = json.load(file)
                if isinstance(data, dict) and "scores" in data and "max_score" in data:
                    return data
                else:
                    return {"scores": [], "max_score": 0}
        else:
            return {"scores": [], "max_score": 0}
    except json.JSONDecodeError:
        return {"scores": [], "max_score": 0}

def guardar_puntajes(score):
    data = cargar_puntajes()
    data["scores"].append(score)
    data["max_score"] = max(data["max_score"], score)
    os.makedirs(os.path.dirname(SCORES_FILE), exist_ok=True)
    with open(SCORES_FILE, "w") as file:
        json.dump(data, file)

puntajes = cargar_puntajes()

# Variables iniciales
player_size = 30
bullet_size = 5
bullet_speed = 10
enemy_size = 62
enemy_speed = 6  
enemies = []
bullets = []
wave = 1
score = 0
enemies_killed = 0
enemies_to_kill = 20
special_ready = True
special_cooldown = 30  # Segundos de recarga
last_special_time = 0

# Variables del jefe
jefe = None
jefe_activo = False
jefe_vida_actual = 0
jefe_tamano = 200
jefe_bullets = []
jefe_bullet_speed = 4

# Cargar imágenes
try:
    fondo_img = Image.open("images/fondo.png").resize((600, 600))
    fondo_tk = ImageTk.PhotoImage(fondo_img)
    canvas.create_image(300, 300, image=fondo_tk)
except FileNotFoundError:
    fondo_tk = None

try:
    nave_img = Image.open("images/nave.png").resize((player_size * 2, player_size * 2))
    nave_tk = ImageTk.PhotoImage(nave_img)
except FileNotFoundError:
    nave_tk = None

try:
    meteorito_img = Image.open("images/meteorito.png").resize((enemy_size, enemy_size))
    meteorito_tk = ImageTk.PhotoImage(meteorito_img)
except FileNotFoundError:
    meteorito_tk = None

player = canvas.create_image(300, 500, image=nave_tk)

# Etiquetas
score_label = tk.Label(root, text=f"Puntaje: {score}", fg="white", bg="#000000", font=("Arial", 14))
score_label.pack(pady=10)
wave_label = tk.Label(root, text=f"Wave: {wave}", fg="white", bg="#000000", font=("Arial", 14))
wave_label.pack(pady=5)
max_score_label = tk.Label(root, text=f"Puntaje Máximo: {puntajes['max_score']}", fg="white", bg="#000000", font=("Arial", 14))
max_score_label.pack(pady=5)
special_label = tk.Label(root, text="Especial: Listo", fg="white", bg="#000000", font=("Arial", 14))
special_label.pack(pady=5)

# Funciones del juego
def mover_jugador(event):
    x, y = event.x, event.y
    canvas.coords(player, x - player_size / 2, y - player_size / 2)

def disparar():
    x, y = canvas.coords(player)
    bullet = canvas.create_oval(x - bullet_size / 2, y - bullet_size, 
                                 x + bullet_size / 2, y, fill="yellow")
    bullets.append(bullet)

def mover_balas():
    for bullet in bullets[:]:
        canvas.move(bullet, 0, -bullet_speed)
        if canvas.coords(bullet)[1] < 0:
            canvas.delete(bullet)
            bullets.remove(bullet)

def crear_enemigos():
    if not jefe_activo and random.random() < 0.05 + (wave * 0.01):
        x = random.randint(0, 550)
        enemy = canvas.create_image(x, 0, image=meteorito_tk)
        enemies.append(enemy)

def mover_enemigos():
    for enemy in enemies[:]:
        canvas.move(enemy, 0, enemy_speed)
        if canvas.coords(enemy)[1] > 600:
            canvas.delete(enemy)
            enemies.remove(enemy)

def verificar_colisiones():
    global score, enemies_killed, jefe_vida_actual, jefe_activo
    for bullet in bullets[:]:
        bullet_coords = canvas.coords(bullet)
        for enemy in enemies[:]:
            enemy_coords = canvas.coords(enemy)
            if (enemy_coords[0] - enemy_size / 2 <= bullet_coords[0] <= enemy_coords[0] + enemy_size / 2 and
                enemy_coords[1] - enemy_size / 2 <= bullet_coords[1] <= enemy_coords[1] + enemy_size / 2):
                canvas.delete(bullet)
                canvas.delete(enemy)
                bullets.remove(bullet)
                enemies.remove(enemy)
                score += 10
                enemies_killed += 1
                score_label.config(text=f"Puntaje: {score}")
                break

def actualizar_wave():
    global wave, enemies_killed, enemy_speed
    if enemies_killed >= enemies_to_kill:
        wave += 1
        enemies_killed = 0
        enemy_speed += 0.5
        wave_label.config(text=f"Wave: {wave}")

def game_over():
    canvas.create_text(300, 300, text="GAME OVER", fill="white", font=("Arial", 24))
    guardar_puntajes(score)
    root.after(2000, root.quit)

def juego():
    crear_enemigos()
    mover_enemigos()
    mover_balas()
    verificar_colisiones()
    actualizar_wave()
    root.after(30, juego)

canvas.bind("<Motion>", mover_jugador)
root.bind("<space>", lambda event: disparar())

juego()
root.mainloop()
