import tkinter as tk
from tkinter import filedialog, colorchooser, messagebox, Toplevel
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
from scipy.stats import gmean, hmean
import statistics
import seaborn as sns  # Import seaborn

plt.style.use('seaborn-v0_8')  # Set default plot style

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

        # Frame для элементов управления и статистики
        self.control_frame = tk.Frame(master)
        self.control_frame.pack(side=tk.RIGHT, padx=10)

        # Frame для графиков
        self.plot_frame = tk.Frame(master)
        self.plot_frame.pack(side=tk.LEFT, padx=10)

        # Кнопка для загрузки данных
        self.load_data_button = tk.Button(self.control_frame, text="Загрузить CSV", command=self.load_data)
        self.load_data_button.pack()

        # Выпадающий список для выбора столбца
        self.column_label = tk.Label(self.control_frame, text="Выберите столбец:")
        self.column_label.pack()
        self.column_var = tk.StringVar(master)
        self.column_dropdown = tk.OptionMenu(self.control_frame, self.column_var, "")
        self.column_dropdown.pack()
        self.column_var.trace("w", self.update_plots_and_stats)

        # Чекбоксы для включения/выключения графиков
        self.scatter_check = tk.Checkbutton(self.control_frame, text="График расхождений", variable=self.scatter_visible, command=self.update_plots_and_stats)
        self.scatter_check.pack()
        self.boxplot_check = tk.Checkbutton(self.control_frame, text="Ящик с усами", variable=self.boxplot_visible, command=self.update_plots_and_stats)
        self.boxplot_check.pack()

        # Кнопки для выбора цвета
        self.scatter_color_button = tk.Button(self.control_frame, text="Цвет графика", command=self.choose_scatter_color)
        self.scatter_color_button.pack()
        self.boxplot_color_button = tk.Button(self.control_frame, text="Цвет ящика с усами", command=self.choose_boxplot_color)
        self.boxplot_color_button.pack()

        # Кнопки для сохранения графиков
        self.save_scatter_button = tk.Button(self.control_frame, text="Сохранить график расхождений", command=self.save_scatter_plot)
        self.save_scatter_button.pack()
        self.save_boxplot_button = tk.Button(self.control_frame, text="Сохранить ящик с усами", command=self.save_boxplot)
        self.save_boxplot_button.pack()

        # Кнопки для открытия графиков в новом окне
        self.open_scatter_button = tk.Button(self.control_frame, text="Открыть график расхождений в новом окне", command=self.open_scatter_plot)
        self.open_scatter_button.pack()
        self.open_boxplot_button = tk.Button(self.control_frame, text="Открыть ящик с усами в новом окне", command=self.open_boxplot)
        self.open_boxplot_button.pack()

        # Область для графиков (уменьшенные размеры)
        self.fig, (self.ax_scatter, self.ax_boxplot) = plt.subplots(2, 1, figsize=(4, 4))
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.plot_frame)
        self.canvas.get_tk_widget().pack()

        # Текстовые поля для отображения статистики
        self.mean_label = tk.Label(self.control_frame, text="Среднее арифметическое:")
        self.mean_label.pack()
        self.mean_text = tk.Text(self.control_frame, height=1, width=30)
        self.mean_text.pack()

        self.variance_label = tk.Label(self.control_frame, text="Дисперсия:")
        self.variance_label.pack()
        self.variance_text = tk.Text(self.control_frame, height=1, width=30)
        self.variance_text.pack()

        self.range_label = tk.Label(self.control_frame, text="Размах:")
        self.range_label.pack()
        self.range_text = tk.Text(self.control_frame, height=1, width=30)
        self.range_text.pack()

        self.max_label = tk.Label(self.control_frame, text="Макс. значение:")
        self.max_label.pack()
        self.max_text = tk.Text(self.control_frame, height=1, width=30)
        self.max_text.pack()

        self.min_label = tk.Label(self.control_frame, text="Мин. значение:")
        self.min_label.pack()
        self.min_text = tk.Text(self.control_frame, height=1, width=30)
        self.min_text.pack()

        self.geometric_mean_label = tk.Label(self.control_frame, text="Среднее геометрическое:")
        self.geometric_mean_label.pack()
        self.geometric_mean_text = tk.Text(self.control_frame, height=1, width=30)
        self.geometric_mean_text.pack()

        self.harmonic_mean_label = tk.Label(self.control_frame, text="Среднее гармоническое:")
        self.harmonic_mean_label.pack()
        self.harmonic_mean_text = tk.Text(self.control_frame, height=1, width=30)
        self.harmonic_mean_text.pack()
        
        self.quadratic_mean_label = tk.Label(self.control_frame, text="Среднее квадратическое:")
        self.quadratic_mean_label.pack()
        self.quadratic_mean_text = tk.Text(self.control_frame, height=1, width=30)
        self.quadratic_mean_text.pack()

        self.median_label = tk.Label(self.control_frame, text="Медиана:")
        self.median_label.pack()
        self.median_text = tk.Text(self.control_frame, height=1, width=30)
        self.median_text.pack()

        self.std_dev_label = tk.Label(self.control_frame, text="Стандартное отклонение:")
        self.std_dev_label.pack()
        self.std_dev_text = tk.Text(self.control_frame, height=1, width=30)
        self.std_dev_text.pack()

        self.mode_label = tk.Label(self.control_frame, text="Мода:")
        self.mode_label.pack()
        self.mode_text = tk.Text(self.control_frame, height=1, width=30)
        self.mode_text.pack()

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

    def save_scatter_plot(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".png", filetypes=[("PNG files", "*.png")])
        if file_path:
            self.fig.savefig(file_path)

    def save_boxplot(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".png", filetypes=[("PNG files", "*.png")])
        if file_path:
            self.fig.savefig(file_path)

    def open_scatter_plot(self):
        if self.df is None or self.selected_column is None:
            messagebox.showinfo("Информация", "Сначала загрузите данные и выберите столбец.")
            return

        data = self.df[self.selected_column].dropna()

        # Создаем новое окно
        new_window = Toplevel(self.master)
        new_window.title("График расхождений")

        # Создаем новую фигуру и оси
        fig, ax = plt.subplots(figsize=(6, 4))
        sns.scatterplot(x=data.index, y=data.values, color=self.scatter_color, ax=ax)  # Use seaborn
        ax.set_title(f"График расхождений для {self.selected_column}")
        ax.set_xlabel("Индекс")
        ax.set_ylabel("Значение")

        # Создаем canvas для отображения графика в окне
        canvas = FigureCanvasTkAgg(fig, master=new_window)
        canvas.get_tk_widget().pack()
        canvas.draw()

    def open_boxplot(self):
        if self.df is None or self.selected_column is None:
            messagebox.showinfo("Информация", "Сначала загрузите данные и выберите столбец.")
            return

        data = self.df[self.selected_column].dropna()

        # Создаем новое окно
        new_window = Toplevel(self.master)
        new_window.title("Ящик с усами")

        # Создаем новую фигуру и оси
        fig, ax = plt.subplots(figsize=(6, 4))
        sns.boxplot(y=data.values, color=self.boxplot_color, ax=ax)  # Use seaborn
        ax.set_title(f"Ящик с усами для {self.selected_column}")
        ax.set_ylabel("Значение")

        # Создаем canvas для отображения графика в окне
        canvas = FigureCanvasTkAgg(fig, master=new_window)
        canvas.get_tk_widget().pack()
        canvas.draw()

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
            sns.scatterplot(x=data.index, y=data.values, color=self.scatter_color, ax=self.ax_scatter)  # Use seaborn
            self.ax_scatter.set_title(f"График расхождений для {self.selected_column}")
            self.ax_scatter.set_xlabel("Индекс")
            self.ax_scatter.set_ylabel("Значение")
        self.ax_scatter.set_visible(self.scatter_visible.get())

        # Ящик с усами
        self.ax_boxplot.clear()
        if self.boxplot_visible.get():
            sns.boxplot(y=data.values, color=self.boxplot_color, ax=self.ax_boxplot)  # Use seaborn
            self.ax_boxplot.set_title(f"Ящик с усами для {self.selected_column}")
            self.ax_boxplot.set_ylabel("Значение")
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
        
        try:
            quadratic_mean = statistics.mean(x**2 for x in data.values)**0.5
        except:
            quadratic_mean = "N/A"

        median = data.median()
        std_dev = data.std()
        try:
            mode = data.mode().iloc[0]  # Handle multiple modes
        except:
            mode = "N/A"

        # Вывод статистики в отдельные текстовые поля
        self.mean_text.delete("1.0", tk.END)
        self.mean_text.insert(tk.END, f"{mean:.2f}")

        self.variance_text.delete("1.0", tk.END)
        self.variance_text.insert(tk.END, f"{variance:.2f}")

        self.range_text.delete("1.0", tk.END)
        self.range_text.insert(tk.END, f"{range_val:.2f}")

        self.max_text.delete("1.0", tk.END)
        self.max_text.insert(tk.END, f"{max_val:.2f}")

        self.min_text.delete("1.0", tk.END)
        self.min_text.insert(tk.END, f"{min_val:.2f}")

        self.geometric_mean_text.delete("1.0", tk.END)
        self.geometric_mean_text.insert(tk.END, f"{geometric_mean}")

        self.harmonic_mean_text.delete("1.0", tk.END)
        self.harmonic_mean_text.insert(tk.END, f"{harmonic_mean}")
        
        self.quadratic_mean_text.delete("1.0", tk.END)
        self.quadratic_mean_text.insert(tk.END, f"{quadratic_mean}")

        self.median_text.delete("1.0", tk.END)
        self.median_text.insert(tk.END, f"{median:.2f}")

        self.std_dev_text.delete("1.0", tk.END)
        self.std_dev_text.insert(tk.END, f"{std_dev:.2f}")

        self.mode_text.delete("1.0", tk.END)
        self.mode_text.insert(tk.END, f"{mode}")

root = tk.Tk()
app = DataAnalyzerApp(root)
root.mainloop()
