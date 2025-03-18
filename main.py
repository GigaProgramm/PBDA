import tkinter as tk
from tkinter import filedialog, colorchooser, messagebox
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
from scipy.stats import gmean, hmean

class DataAnalyzerApp:
    def __init__(self, master):
        self.master = master
        master.title("Анализ Данных")

        self.df = None
        self.selected_column = None
        self.scatter_visible = tk.BooleanVar(value=True)
        self.boxplot_visible = tk.BooleanVar(value=True)
        self.scatter_color = "blue"
        self.boxplot_color = "green"

        # Кнопка для загрузки данных
        self.load_data_button = tk.Button(master, text="Загрузить CSV", command=self.load_data)
        self.load_data_button.pack()

        # Выпадающий список для выбора столбца
        self.column_label = tk.Label(master, text="Выберите столбец:")
        self.column_label.pack()
        self.column_var = tk.StringVar(master)
        self.column_dropdown = tk.OptionMenu(master, self.column_var, "")
        self.column_dropdown.pack()
        self.column_var.trace("w", self.update_plots_and_stats)

        # Чекбоксы для включения/выключения графиков
        self.scatter_check = tk.Checkbutton(master, text="График расхождений", variable=self.scatter_visible, command=self.update_plots_and_stats)
        self.scatter_check.pack()
        self.boxplot_check = tk.Checkbutton(master, text="Ящик с усами", variable=self.boxplot_visible, command=self.update_plots_and_stats)
        self.boxplot_check.pack()

        # Кнопки для выбора цвета
        self.scatter_color_button = tk.Button(master, text="Цвет графика", command=self.choose_scatter_color)
        self.scatter_color_button.pack()
        self.boxplot_color_button = tk.Button(master, text="Цвет ящика с усами", command=self.choose_boxplot_color)
        self.boxplot_color_button.pack()

        # Область для графиков (уменьшенные размеры)
        self.fig, (self.ax_scatter, self.ax_boxplot) = plt.subplots(2, 1, figsize=(6, 6))
        self.canvas = FigureCanvasTkAgg(self.fig, master=master)
        self.canvas.get_tk_widget().pack()

        # Текстовое поле для отображения статистики
        self.stats_text = tk.Text(master, height=10, width=50)
        self.stats_text.pack()

    def load_data(self):
        file_path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
        if file_path:
            try:
                self.df = pd.read_csv(file_path)
                columns = list(self.df.columns)
                self.column_var.set(columns[0])  # set the default value
                self.column_dropdown['menu'].delete(0, 'end')
                for column in columns:
                    self.column_dropdown['menu'].add_command(label=column, command=tk._setit(self.column_var, column))
                self.update_plots_and_stats()
            except Exception as e:
                messagebox.showerror("Ошибка", str(e))

    def choose_scatter_color(self):
        color_code = colorchooser.askcolor(title="Выберите цвет графика")
        if color_code:
            self.scatter_color = color_code[1]
            self.update_plots_and_stats()

    def choose_boxplot_color(self):
        color_code = colorchooser.askcolor(title="Выберите цвет ящика с усами")
        if color_code:
            self.boxplot_color = color_code[1]
            self.update_plots_and_stats()

    def update_plots_and_stats(self, *args):
        if self.df is None:
            return

        self.selected_column = self.column_var.get()
        if self.selected_column not in self.df.columns:
            return

        data = self.df[self.selected_column].dropna()

        # График расхождений
        self.ax_scatter.clear()
        if self.scatter_visible.get():
            self.ax_scatter.scatter(data.index, data.values, color=self.scatter_color)
            self.ax_scatter.set_title(f"График расхождений для {self.selected_column}")
            self.ax_scatter.set_xlabel("Индекс")
            self.ax_scatter.set_ylabel("Значение")
        self.ax_scatter.set_visible(self.scatter_visible.get())

        # Ящик с усами
        self.ax_boxplot.clear()
        if self.boxplot_visible.get():
            self.ax_boxplot.boxplot(data.values, vert=False, patch_artist=True, boxprops=dict(facecolor=self.boxplot_color))
            self.ax_boxplot.set_title(f"Ящик с усами для {self.selected_column}")
            self.ax_boxplot.set_xlabel("Значение")
        self.ax_boxplot.set_visible(self.boxplot_visible.get())

        self.fig.tight_layout()
        self.canvas.draw()

        # Расчет статистики
        mean = data.mean()
        variance = data.var()
        range_val = data.max() - data.min()
        max_val = data.max()
        min_val = data.min()
        try:
            geometric_mean = gmean(data.values)
            harmonic_mean = hmean(data.values)
        except:
            geometric_mean = "N/A (values must be positive)"
            harmonic_mean = "N/A (values must be positive)"
            
        median = data.median()
        std_dev = data.std()
        try:
            mode = data.mode().iloc[0]  # Handle multiple modes
        except:
            mode = "N/A"

        # Вывод статистики
        self.stats_text.delete("1.0", tk.END)
        self.stats_text.insert(tk.END, f"Среднее арифметическое: {mean:.2f}\n")
        self.stats_text.insert(tk.END, f"Дисперсия: {variance:.2f}\n")
        self.stats_text.insert(tk.END, f"Размах: {range_val:.2f}\n")
        self.stats_text.insert(tk.END, f"Макс. значение: {max_val:.2f}\n")
        self.stats_text.insert(tk.END, f"Мин. значение: {min_val:.2f}\n")
        self.stats_text.insert(tk.END, f"Среднее геометрическое: {geometric_mean}\n")
        self.stats_text.insert(tk.END, f"Среднее гармоническое: {harmonic_mean}\n")
        self.stats_text.insert(tk.END, f"Медиана: {median:.2f}\n")
        self.stats_text.insert(tk.END, f"Стандартное отклонение: {std_dev:.2f}\n")
        self.stats_text.insert(tk.END, f"Мода: {mode}\n")

root = tk.Tk()
app = DataAnalyzerApp(root)
root.mainloop()
