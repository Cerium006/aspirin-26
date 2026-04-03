import tkinter as tk
from tkinter import ttk, messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.image as mpimg
import random
import time
import json
import threading
import os
import pygame
from PIL import Image, ImageTk, ImageDraw

class Virus:
    def __init__(self, name="ASPIRIN-26"):
        self.name = name
        self.contagion = 0.05
        self.lethality = 0.01 
        self.mutation_level = 1
        
    def mutate(self):
        self.mutation_level += 1
        change = random.choice(['contagion', 'lethality', 'resistance'])
        if change == 'contagion':
            self.contagion *= 1.25
            return "Вирус стал более заразным!"
        elif change == 'lethality':
            self.lethality *= 1.2
            return "Смертность вируса возросла!"
        else:
            self.contagion *= 1.1
            return "Вирус выработал устойчивость к антисептикам!"

class Laboratory:
    def __init__(self):
        self.budget = 1200
        self.research_progress = 0
        self.scientists = 1
        self.equipment_level = 1
        self.efficiency = 1.0
        
    def get_hire_cost(self):
        return 300 * self.scientists

    def get_upgrade_cost(self):
        return 500 * self.equipment_level

    def invest(self, amount):
        if self.budget >= amount:
            self.budget -= amount
            self.research_progress += (amount / 600) * self.efficiency
            return True
        return False

    def upgrade_equipment(self):
        cost = self.get_upgrade_cost()
        if self.budget >= cost:
            self.budget -= cost
            self.equipment_level += 1
            self.efficiency += 0.4
            return True
        return False

    def hire_scientist(self):
        cost = self.get_hire_cost()
        if self.budget >= cost:
            self.budget -= cost
            self.scientists += 1
            self.efficiency += 0.2
            return True
        return False

class Simulation:
    def __init__(self):
        self.population = 7000000000
        self.infected = 100
        self.dead = 0
        self.recovered = 0
        self.day = 0
        self.virus = Virus()
        self.lab = Laboratory()
        self.lockdown_active = False
        self.news_feed = "Глобальные новости: Зафиксированы первые случаи заражения."
        
        self.regions = [
            {"name": "Евразия", "pos": (0.65, 0.7), "infected": 50},
            {"name": "Северная Америка", "pos": (0.2, 0.7), "infected": 20},
            {"name": "Южная Америка", "pos": (0.3, 0.35), "infected": 10},
            {"name": "Африка", "pos": (0.5, 0.45), "infected": 10},
            {"name": "Австралия", "pos": (0.85, 0.25), "infected": 10}
        ]
        
        self.history = {
            'days': [0],
            'infected': [100],
            'dead': [0],
            'recovered': [0]
        }
        self.running = False
        self.game_over = False

    def load_from_dict(self, data):
        self.day = data.get("day", 0)
        self.infected = data.get("infected", 100)
        self.dead = data.get("dead", 0)
        self.recovered = data.get("recovered", 0)
        
        virus_data = data.get("virus", {})
        self.virus.contagion = virus_data.get("contagion", 0.05)
        self.virus.lethality = virus_data.get("lethality", 0.01)
        self.virus.mutation_level = virus_data.get("mutation_level", 1)
        
        lab_data = data.get("lab", {})
        self.lab.budget = lab_data.get("budget", 1200)
        self.lab.research_progress = lab_data.get("research", 0)
        self.lab.scientists = lab_data.get("scientists", 1)
        self.lab.equipment_level = lab_data.get("equipment_level", 1)
        self.lab.efficiency = lab_data.get("efficiency", 1.0)
        
        self.history = data.get("history", {
            'days': list(range(self.day + 1)),
            'infected': [self.infected] * (self.day + 1),
            'dead': [self.dead] * (self.day + 1),
            'recovered': [self.recovered] * (self.day + 1)
        })

    def toggle_lockdown(self):
        self.lockdown_active = not self.lockdown_active
        if self.lockdown_active:
            return "Введен глобальный карантин. Распространение замедлено, но бюджет не пополняется."
        else:
            return "Карантин отменен. Экономика восстанавливается."

    def tick(self):
        if self.game_over:
            return

        self.day += 1

        spread_factor = self.virus.contagion * 1.5
        if self.lockdown_active:
            spread_factor *= 0.4
            
        new_infected = int(self.infected * spread_factor * (1 - self.infected/self.population))
        if new_infected < 1 and self.infected > 0:
            new_infected = random.randint(1, 5)
            
        self.infected += new_infected
        
        for region in self.regions:
            region["infected"] = int(self.infected * (1 / len(self.regions)))

        new_deaths = int(self.infected * self.virus.lethality)
        self.infected -= new_deaths
        self.dead += new_deaths
        
        self.lab.research_progress += (self.lab.scientists * 0.04 * self.lab.efficiency)
        
        if not self.lockdown_active:
            self.lab.budget += 40 + (self.lab.scientists * 5)
        else:
            self.lab.budget += 5

        if self.lab.research_progress > 30:
            recovery_rate = (self.lab.research_progress - 30) / 1200
            new_recovered = int(self.infected * recovery_rate)
            self.infected -= new_recovered
            self.recovered += new_recovered

        if self.infected + self.dead + self.recovered > self.population:
            self.infected = max(0, self.population - self.dead - self.recovered)

        self.history['days'].append(self.day)
        self.history['infected'].append(self.infected)
        self.history['dead'].append(self.dead)
        self.history['recovered'].append(self.recovered)

        if self.lab.research_progress >= 100:
            self.game_over = True
            return "WIN"
        if self.infected <= 0 and self.day > 20:
            self.game_over = True
            return "WIN"
        if self.dead >= self.population * 0.7:
            self.game_over = True
            return "LOSE"
            
        if random.random() < 0.08:
            msg = self.virus.mutate()
            self.news_feed = f"СРОЧНО: {msg}"
            return f"MUTATION:{msg}"
            
        return None

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("ASPIRIN-26: Глобальная Угроза")
        self.geometry("1200x850")
        self.configure(bg="#1a1a1a")
        
        self.sim = Simulation()
        self.map_img = None
        self.menu_bg_img = None
        
        try:
            pygame.mixer.init()
            self.play_music()
        except:
            print("Звуковая карта не обнаружена или pygame не установлен")

        self.load_map_image()
        self.load_menu_bg()
        
        self.main_frame = None
        self.show_main_menu()

    def play_music(self):
        music_path = "Absconditus - ZhayTee.mp3"
        if os.path.exists(music_path):
            pygame.mixer.music.load(music_path)
            pygame.mixer.music.play(-1)
        else:
            print("Файл soundtrack.mp3 не найден")

    def load_menu_bg(self):
        bg_path = "menu.jpg"
        if not os.path.exists(bg_path):
            self.generate_menu_bg(bg_path)
        
        try:
            img = Image.open(bg_path)
            img = img.resize((1200, 850), Image.Resampling.LANCZOS)
            self.menu_bg_img = ImageTk.PhotoImage(img)
        except Exception as e:
            print(f"Ошибка загрузки фона меню: {e}")

    def generate_menu_bg(self, path):
        img = Image.new('RGB', (1200, 850), color='#050505')
        draw = ImageDraw.Draw(img)
        
        for i in range(0, 1200, 50):
            draw.line([(i, 0), (i, 850)], fill='#0f1f1f', width=1)
        for i in range(0, 850, 50):
            draw.line([(0, i), (1200, i)], fill='#0f1f1f', width=1)
            
        for _ in range(200):
            x = random.randint(0, 1200)
            y = random.randint(0, 850)
            size = random.randint(1, 3)
            draw.ellipse([x, y, x+size, y+size], fill='#1a3a3a')
            
        for _ in range(10):
            x = random.randint(0, 1200)
            y = random.randint(0, 850)
            radius = random.randint(20, 100)
            draw.ellipse([x-radius, y-radius, x+radius, y+radius], outline='#401010', width=2)

        img.save(path)

    def show_main_menu(self):
        if self.main_frame:
            self.main_frame.destroy()
        
        self.menu_frame = tk.Frame(self, bg="#1a1a1a")
        self.menu_frame.pack(fill=tk.BOTH, expand=True)
        
        if self.menu_bg_img:
            bg_label = tk.Label(self.menu_frame, image=self.menu_bg_img)
            bg_label.place(x=0, y=0, relwidth=1, relheight=1)
        
        content_frame = tk.Frame(self.menu_frame, bg="#1a1a1a", padx=50, pady=50)
        content_frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
        
        tk.Label(content_frame, text="ASPIRIN-26", font=("Segoe UI", 48, "bold"), fg="#e74c3c", bg="#1a1a1a").pack(pady=20)
        tk.Label(content_frame, text="ГЛОБАЛЬНЫЙ СИМУЛЯТОР ПАНДЕМИИ", font=("Segoe UI", 14), fg="#ecf0f1", bg="#1a1a1a").pack(pady=(0, 40))
        
        style = ttk.Style()
        style.configure("Menu.TButton", font=("Segoe UI", 14, "bold"), padding=10, width=25)
        
        ttk.Button(content_frame, text="НОВАЯ ИГРА", style="Menu.TButton", command=self.start_new_game).pack(pady=10)
        ttk.Button(content_frame, text="ЗАГРУЗИТЬ ИГРУ", style="Menu.TButton", command=self.load_saved_game_from_menu).pack(pady=10)
        ttk.Button(content_frame, text="ВЫХОД", style="Menu.TButton", command=self.quit).pack(pady=10)

    def start_new_game(self):
        self.sim = Simulation()
        self.menu_frame.destroy()
        self.setup_ui()
        self.update_display()

    def load_saved_game_from_menu(self):
        if os.path.exists("save_game.json"):
            with open("save_game.json", "r") as f:
                data = json.load(f)
            self.sim = Simulation()
            self.sim.load_from_dict(data)
            self.menu_frame.destroy()
            self.setup_ui()
            self.update_display()
            self.log_event("Игра успешно загружена!")
        else:
            messagebox.showwarning("ОШИБКА", "Файл сохранения не найден!")

    def load_map_image(self):
        map_path = "World.png"
        
        if not os.path.exists(map_path):
            self.generate_placeholder_map(map_path)
            
        try:
            self.map_img = plt.imread(map_path)
        except Exception as e:
            print(f"Не удалось загрузить карту: {e}")

    def generate_placeholder_map(self, path):

        img = Image.new('RGB', (1000, 600), color='#1a1a1a')
        draw = ImageDraw.Draw(img)

        draw.polygon([(450, 100), (850, 100), (900, 300), (700, 500), (500, 400)], fill='#2c3e50', outline='#34495e')
        draw.polygon([(50, 100), (350, 100), (300, 350), (100, 300)], fill='#2c3e50', outline='#34495e')
        draw.polygon([(200, 350), (350, 350), (300, 550), (250, 550)], fill='#2c3e50', outline='#34495e')
        draw.polygon([(450, 300), (600, 300), (650, 500), (500, 550), (450, 450)], fill='#2c3e50', outline='#34495e')
        draw.polygon([(750, 450), (900, 450), (850, 550), (800, 550)], fill='#2c3e50', outline='#34495e')
        
        img.save(path)

    def setup_ui(self):
        style = ttk.Style()
        style.theme_use('clam')
        style.configure("TFrame", background="#1a1a1a")
        style.configure("TLabel", background="#1a1a1a", foreground="#ecf0f1", font=("Segoe UI", 10))
        style.configure("Header.TLabel", font=("Segoe UI", 16, "bold"), foreground="#e74c3c")
        style.configure("TButton", font=("Segoe UI", 10, "bold"), padding=5)
        style.configure("Lockdown.TButton", background="#c0392b", foreground="white")

        self.news_frame = tk.Frame(self, bg="#c0392b", height=40)
        self.news_frame.pack(fill=tk.X)
        self.news_label = tk.Label(self.news_frame, text=self.sim.news_feed, bg="#c0392b", fg="white", font=("Segoe UI", 11, "bold"))
        self.news_label.pack(pady=5)

        self.main_frame = ttk.Frame(self)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        stats_frame = ttk.Frame(self.main_frame)
        stats_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 20))

        ttk.Label(stats_frame, text="ЦЕНТР УПРАВЛЕНИЯ", style="Header.TLabel").pack(pady=(0, 20))
        
        self.lbl_day = ttk.Label(stats_frame, text="ДЕНЬ: 0", font=("Segoe UI", 12, "bold"))
        self.lbl_day.pack(anchor=tk.W, pady=2)
        
        self.lbl_infected = ttk.Label(stats_frame, text="ЗАРАЖЕНО: 0", foreground="#e74c3c", font=("Segoe UI", 11))
        self.lbl_infected.pack(anchor=tk.W)
        
        self.lbl_dead = ttk.Label(stats_frame, text="СМЕРТЕЙ: 0", foreground="#95a5a6", font=("Segoe UI", 11))
        self.lbl_dead.pack(anchor=tk.W)
        
        self.lbl_recovered = ttk.Label(stats_frame, text="ВЫЛЕЧЕНО: 0", foreground="#2ecc71", font=("Segoe UI", 11))
        self.lbl_recovered.pack(anchor=tk.W)
        
        ttk.Separator(stats_frame, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=15)
        
        ttk.Label(stats_frame, text="ЛАБОРАТОРИЯ", font=("Segoe UI", 12, "bold")).pack(pady=(0, 10))
        
        self.lbl_budget = ttk.Label(stats_frame, text="БЮДЖЕТ: $0", foreground="#f1c40f")
        self.lbl_budget.pack(anchor=tk.W)
        
        self.lbl_research = ttk.Label(stats_frame, text="ПРОГРЕСС ЛЕКАРСТВА: 0%")
        self.lbl_research.pack(anchor=tk.W, pady=(10, 0))
        
        self.research_bar = ttk.Progressbar(stats_frame, length=220, mode='determinate')
        self.research_bar.pack(pady=5)
        
        self.lbl_scientists = ttk.Label(stats_frame, text="ПЕРСОНАЛ: 1")
        self.lbl_scientists.pack(anchor=tk.W)

        btn_frame = ttk.Frame(stats_frame)
        btn_frame.pack(pady=20, fill=tk.X)

        self.btn_invest = ttk.Button(btn_frame, text="ИНВЕСТИРОВАТЬ ($100)", command=self.on_invest)
        self.btn_invest.pack(fill=tk.X, pady=3)
        
        self.btn_hire = ttk.Button(btn_frame, text="НАНЯТЬ УЧЕНОГО", command=self.on_hire)
        self.btn_hire.pack(fill=tk.X, pady=3)
        
        self.btn_upgrade = ttk.Button(btn_frame, text="УЛУЧШИТЬ ОБОРУД.", command=self.on_upgrade)
        self.btn_upgrade.pack(fill=tk.X, pady=3)

        self.btn_lockdown = ttk.Button(btn_frame, text="ВВЕСТИ КАРАНТИН", command=self.on_lockdown)
        self.btn_lockdown.pack(fill=tk.X, pady=10)
        
        self.btn_start = ttk.Button(btn_frame, text="ЗАПУСТИТЬ СИСТЕМУ", command=self.toggle_sim)
        self.btn_start.pack(fill=tk.X, pady=(20, 3))
        
        ttk.Button(btn_frame, text="СОХРАНИТЬ ДАННЫЕ", command=self.save_game).pack(fill=tk.X, pady=3)
        ttk.Button(btn_frame, text="В ГЛАВНОЕ МЕНЮ", command=self.back_to_menu).pack(fill=tk.X, pady=3)

        right_frame = ttk.Frame(self.main_frame)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        self.fig = plt.figure(figsize=(9, 9), dpi=100)
        self.fig.patch.set_facecolor('#1a1a1a')
        
        self.ax_stats = self.fig.add_subplot(211)
        self.ax_stats.set_facecolor('#2c3e50')
        self.ax_stats.tick_params(colors='white')
        for spine in self.ax_stats.spines.values():
            spine.set_color('white')

        self.ax_map = self.fig.add_subplot(212)
        self.ax_map.set_facecolor('#1a1a1a')
        
        self.canvas = FigureCanvasTkAgg(self.fig, master=right_frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        self.log_text = tk.Text(stats_frame, height=10, width=32, bg="#000", fg="#2ecc71", font=("Consolas", 9))
        self.log_text.pack(pady=10)
        self.log_event("Система инициализирована...")

    def back_to_menu(self):
        if messagebox.askyesno("ВЫХОД", "Вы уверены, что хотите выйти в главное меню? Несохраненный прогресс будет потерян."):
            self.sim.running = False
            self.main_frame.destroy()
            self.news_frame.destroy()
            self.show_main_menu()

    def log_event(self, msg):
        self.log_text.insert(tk.END, f"> {msg}\n")
        self.log_text.see(tk.END)

    def on_invest(self):
        if self.sim.lab.invest(100):
            self.log_event("Инвестиции приняты. Прогресс ускорен.")
            self.update_display()
        else:
            messagebox.showwarning("БЮДЖЕТ", "Недостаточно средств для транзакции!")

    def on_hire(self):
        cost = self.sim.lab.get_hire_cost()
        if self.sim.lab.hire_scientist():
            self.log_event(f"Новый специалист в штате. Расход: ${cost}.")
            self.update_display()
        else:
            messagebox.showwarning("БЮДЖЕТ", f"Требуется ${cost}!")

    def on_upgrade(self):
        cost = self.sim.lab.get_upgrade_cost()
        if self.sim.lab.upgrade_equipment():
            self.log_event(f"Оборудование модернизировано. Расход: ${cost}.")
            self.update_display()
        else:
            messagebox.showwarning("БЮДЖЕТ", f"Требуется ${cost}!")

    def on_lockdown(self):
        msg = self.sim.toggle_lockdown()
        self.log_event(msg)
        self.news_label.config(text=msg)
        self.update_display()

    def toggle_sim(self):
        if not self.sim.running:
            self.sim.running = True
            self.btn_start.config(text="ПАУЗА СИСТЕМЫ")
            self.run_sim_loop()
        else:
            self.sim.running = False
            self.btn_start.config(text="ПРОДОЛЖИТЬ")

    def run_sim_loop(self):
        if self.sim.running and not self.sim.game_over:
            event = self.sim.tick()
            if event:
                if event == "WIN":
                    messagebox.showinfo("ПОБЕДА", f"УГРОЗА НЕЙТРАЛИЗОВАНА ЗА {self.sim.day} ДНЕЙ!")
                    self.sim.running = False
                elif event == "LOSE":
                    messagebox.showerror("КРИТИЧЕСКАЯ ОШИБКА", "БИОСФЕРА УНИЧТОЖЕНА.")
                    self.sim.running = False
                elif event.startswith("MUTATION"):
                    m_msg = event.split(":")[1]
                    self.log_event(f"ВНИМАНИЕ: {m_msg}")
            
            self.update_display()
            self.after(500, self.run_sim_loop)

    def update_display(self):
        self.lbl_day.config(text=f"ДЕНЬ: {self.sim.day}")
        self.lbl_infected.config(text=f"ЗАРАЖЕНО: {self.sim.infected:,}")
        self.lbl_dead.config(text=f"СМЕРТЕЙ: {self.sim.dead:,}")
        self.lbl_recovered.config(text=f"ВЫЛЕЧЕНО: {self.sim.recovered:,}")
        self.lbl_budget.config(text=f"БЮДЖЕТ: ${int(self.sim.lab.budget)}")
        self.lbl_research.config(text=f"ПРОГРЕСС ЛЕКАРСТВА: {int(self.sim.lab.research_progress)}%")
        self.lbl_scientists.config(text=f"ПЕРСОНАЛ: {self.sim.lab.scientists}")
        self.research_bar['value'] = self.sim.lab.research_progress
        self.news_label.config(text=self.sim.news_feed)
        
        self.btn_hire.config(text=f"НАНЯТЬ УЧЕНОГО (${self.sim.lab.get_hire_cost()})")
        self.btn_upgrade.config(text=f"УЛУЧШИТЬ ОБОРУД. (${self.sim.lab.get_upgrade_cost()})")
        self.btn_lockdown.config(text="ОТМЕНИТЬ КАРАНТИН" if self.sim.lockdown_active else "ВВЕСТИ КАРАНТИН")
        
        self.ax_stats.clear()
        self.ax_stats.plot(self.sim.history['days'], self.sim.history['infected'], label='Зараженные', color='#e74c3c', linewidth=2)
        self.ax_stats.plot(self.sim.history['days'], self.sim.history['dead'], label='Умершие', color='#ecf0f1', linewidth=2)
        self.ax_stats.plot(self.sim.history['days'], self.sim.history['recovered'], label='Выздоровевшие', color='#2ecc71', linewidth=2)
        self.ax_stats.legend(loc='upper left', fontsize='x-small', facecolor='#2c3e50', labelcolor='white')
        self.ax_stats.set_title("АНАЛИЗ ДИНАМИКИ", color='white', fontsize=10)
        self.ax_stats.grid(True, alpha=0.2)
        
        self.ax_map.clear()
        if self.map_img is not None:
            self.ax_map.imshow(self.map_img, extent=[0, 1, 0, 1], aspect='auto', alpha=0.4)
        
        self.ax_map.set_facecolor('#1a1a1a')
        self.ax_map.set_title("ГЛОБАЛЬНАЯ КАРТА РАСПРОСТРАНЕНИЯ", color='white', fontsize=10)
        self.ax_map.set_xlim(0, 1)
        self.ax_map.set_ylim(0, 1)
        self.ax_map.axis('off')
        
        for region in self.sim.regions:
            size = 150 + (region["infected"] / self.sim.population) * 10000
            color = '#e74c3c' if region["infected"] > 1000 else '#f1c40f'
            self.ax_map.scatter(region["pos"][0], region["pos"][1], s=size, c=color, alpha=0.7, edgecolors='white', linewidth=1)
            self.ax_map.text(region["pos"][0], region["pos"][1]-0.06, region["name"], color='white', ha='center', fontsize=9, fontweight='bold')

        self.canvas.draw()

    def save_game(self):
        data = {
            "day": self.sim.day,
            "infected": self.sim.infected,
            "dead": self.sim.dead,
            "recovered": self.sim.recovered,
            "virus": {
                "contagion": self.sim.virus.contagion,
                "lethality": self.sim.virus.lethality,
                "mutation_level": self.sim.virus.mutation_level
            },
            "lab": {
                "budget": self.sim.lab.budget,
                "research": self.sim.lab.research_progress,
                "scientists": self.sim.lab.scientists,
                "equipment_level": self.sim.lab.equipment_level,
                "efficiency": self.sim.lab.efficiency
            },
            "history": self.sim.history,
            "rating": (self.sim.population - self.sim.dead) / self.sim.day if self.sim.day > 0 else 0
        }
        with open("save_game.json", "w") as f:
            json.dump(data, f)
        self.log_event("Игра сохранена в save_game.json")
        messagebox.showinfo("Сохранение", "Результаты сохранены!")

if __name__ == "__main__":
    app = App()
    app.mainloop()
