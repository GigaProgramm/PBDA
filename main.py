import tkinter as tk
from tkinter import filedialog, colorchooser, messagebox, Toplevel, ttk
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
import numpy as np
from scipy.stats import gmean, hmean
import statistics
import seaborn as sns  # Import seaborn

plt.style.use('seaborn-v0_8')  # Set default plot style

class ScrollableFrame(tk.Frame):
    def __init__(self, master, **kwargs):
        tk.Frame.__init__(self, master, **kwargs)

        # Canvas для прокрутки
        self.canvas = tk.Canvas(self, borderwidth=0, highlightthickness=0)
        self.vsb = tk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=self.vsb.set)

        self.vsb.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=True)

        self.inner_frame = tk.Frame(self.canvas, borderwidth=0)
        self.inner_frame_id = self.canvas.create_window((0, 0), window=self.inner_frame, anchor="nw")

        self.inner_frame.bind("<Configure>", self._configure_inner_frame)
        self.canvas.bind("<Configure>", self._configure_canvas)

        self.bind("<Enter>", self._bound_to_mousewheel)
        self.bind("<Leave>", self._unbound_to_mousewheel)

    def _configure_inner_frame(self, event):
        size = (self.inner_frame.winfo_reqwidth(), self.inner_frame.winfo_reqheight())
        self.canvas.config(scrollregion="0 0 %s %s" % size)

    def _configure_canvas(self, event):
        if self.inner_frame.winfo_reqwidth() != self.canvas.winfo_width():
            self.canvas.itemconfigure(self.inner_frame_id, width=self.canvas.winfo_width())

    def _bound_to_mousewheel(self, event):
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)

    def _unbound_to_mousewheel(self, event):
        self.canvas.unbind_all("<MouseWheel>")

    def _on_mousewheel(self, event):
        self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

class DataAnalyzerApp:
    def __init__(self, master):
        self.master = master
        master.title("Data Analysis")  # Default title in English

        self.df = None
        self.filtered_df = None
        self.selected_column = None
        self.scatter_visible = tk.BooleanVar(value=True)
        self.boxplot_visible = tk.BooleanVar(value=True)
        self.scatter_color = "blue"
        self.boxplot_color = "green"
        self.current_language = "en"  # Default language is English

        # Translations dictionary
        self.translations = {
            "en": {
                "title": "Data Analysis",
                "load_data": "Load CSV",
                "select_column": "Select Column:",
                "scatter_plot": "Scatter Plot",
                "box_plot": "Box Plot",
                "scatter_color": "Scatter Color",
                "box_color": "Box Color",
                "save_scatter": "Save Scatter Plot",
                "save_box": "Save Box Plot",
                "open_scatter": "Open Scatter Plot in New Window",
                "open_box": "Open Box Plot in New Window",
                "mean": "Mean:",
                "variance": "Variance:",
                "range": "Range:",
                "max": "Max:",
                "min": "Min:",
                "geometric_mean": "Geometric Mean:",
                "harmonic_mean": "Harmonic Mean:",
                "quadratic_mean": "Quadratic Mean:",
                "median": "Median:",
                "std_dev": "Standard Deviation:",
                "mode": "Mode:",
                "info": "Information",
                "load_data_first": "Load data and select a column first.",
                "language": "Language",
                "english": "English",
                "russian": "Russian",
                "tab1": "Data Analysis",
                "tab2": "Outlier Analysis",
                "min_value": "Min Value:",
                "max_value": "Max Value:",
                "apply_filter": "Apply Filter",
                "histogram": "Histogram"
            },
            "ru": {
                "title": "Анализ Данных",
                "load_data": "Загрузить CSV",
                "select_column": "Выберите столбец:",
                "scatter_plot": "График расхождений",
                "box_plot": "Ящик с усами",
                "scatter_color": "Цвет графика",
                "box_color": "Цвет ящика с усами",
                "save_scatter": "Сохранить график расхождений",
                "save_box": "Сохранить ящик с усами",
                "open_scatter": "Открыть график расхождений в новом окне",
                "open_box": "Открыть ящик с усами в новом окне",
                "mean": "Среднее арифметическое:",
                "variance": "Дисперсия:",
                "range": "Размах:",
                "max": "Макс. значение:",
                "min": "Мин. значение:",
                "geometric_mean": "Среднее геометрическое:",
                "harmonic_mean": "Среднее гармоническое:",
                "quadratic_mean": "Среднее квадратическое:",
                "median": "Медиана:",
                "std_dev": "Стандартное отклонение:",
                "mode": "Мода:",
                "info": "Информация",
                "load_data_first": "Сначала загрузите данные и выберите столбец.",
                "language": "Язык",
                "english": "Английский",
                "russian": "Русский",
                "tab1": "Анализ Данных",
                "tab2": "Анализ Выбросов",
                "min_value": "Мин. значение:",
                "max_value": "Макс. значение:",
                "apply_filter": "Применить фильтр",
                "histogram": "Гистограмма"
            }
        }

        # Notebook для вкладок
        self.notebook = ttk.Notebook(master)
        self.notebook.pack(fill="both", expand=True)

        # Вкладка 1: Анализ данных
        self.tab1 = tk.Frame(self.notebook)
        self.notebook.add(self.tab1, text=self.translations[self.current_language]["tab1"])
        self.create_tab1_content(self.tab1)

        # Вкладка 2: Анализ выбросов
        self.tab2 = tk.Frame(self.notebook)
        self.notebook.add(self.tab2, text=self.translations[self.current_language]["tab2"])
        self.create_tab2_content(self.tab2)

        self.notebook.bind("<<NotebookTabChanged>>", self.update_tab_text)

    def create_tab1_content(self, tab):
        # Frame для элементов управления и статистики
        self.control_frame = ScrollableFrame(tab)  # Use ScrollableFrame
        self.control_frame.pack(side=tk.RIGHT, padx=10, fill="both", expand=True)

        self.inner_control_frame = self.control_frame.inner_frame  # Access inner frame

        # Frame для графиков
        self.plot_frame = tk.Frame(tab)
        self.plot_frame.pack(side=tk.LEFT, padx=10)

        # Language selection menu
        self.language_label = tk.Label(self.inner_control_frame, text=self.translations[self.current_language]["language"])
        self.language_label.pack()
        self.language_var = tk.StringVar(self.master)
        self.language_var.set(self.translations[self.current_language]["english"])  # Default language
        self.language_dropdown = tk.OptionMenu(self.inner_control_frame, self.language_var, 
                                                self.translations[self.current_language]["english"], 
                                                self.translations[self.current_language]["russian"], 
                                                command=self.change_language)
        self.language_dropdown.pack()

        # Кнопка для загрузки данных
        self.load_data_button = tk.Button(self.inner_control_frame, text=self.translations[self.current_language]["load_data"], command=self.load_data)
        self.load_data_button.pack()

        # Выпадающий список для выбора столбца
        self.column_label = tk.Label(self.inner_control_frame, text=self.translations[self.current_language]["select_column"])
        self.column_label.pack()
        self.column_var = tk.StringVar(self.master)
        self.column_dropdown = tk.OptionMenu(self.inner_control_frame, self.column_var, "")
        self.column_dropdown.pack()
        self.column_var.trace("w", self.update_plots_and_stats)

        # Чекбоксы для включения/выключения графиков
        self.scatter_check = tk.Checkbutton(self.inner_control_frame, text=self.translations[self.current_language]["scatter_plot"], variable=self.scatter_visible, command=self.update_plots_and_stats)
        self.scatter_check.pack()
        self.boxplot_check = tk.Checkbutton(self.inner_control_frame, text=self.translations[self.current_language]["box_plot"], variable=self.boxplot_visible, command=self.update_plots_and_stats)
        self.boxplot_check.pack()

        # Кнопки для выбора цвета
        self.scatter_color_button = tk.Button(self.inner_control_frame, text=self.translations[self.current_language]["scatter_color"], command=self.choose_scatter_color)
        self.scatter_color_button.pack()
        self.boxplot_color_button = tk.Button(self.inner_control_frame, text=self.translations[self.current_language]["box_color"], command=self.choose_boxplot_color)
        self.boxplot_color_button.pack()

        # Кнопки для сохранения графиков
        self.save_scatter_button = tk.Button(self.inner_control_frame, text=self.translations[self.current_language]["save_scatter"], command=self.save_scatter_plot)
        self.save_scatter_button.pack()
        self.save_boxplot_button = tk.Button(self.inner_control_frame, text=self.translations[self.current_language]["save_box"], command=self.save_boxplot)
        self.save_boxplot_button.pack()

        # Кнопки для открытия графиков в новом окне
        self.open_scatter_button = tk.Button(self.inner_control_frame, text=self.translations[self.current_language]["open_scatter"], command=self.open_scatter_plot)
        self.open_scatter_button.pack()
        self.open_boxplot_button = tk.Button(self.inner_control_frame, text=self.translations[self.current_language]["open_box"], command=self.open_boxplot)
        self.open_boxplot_button.pack()

        # Button to plot histogram
        self.histogram_button = tk.Button(self.inner_control_frame, text=self.translations[self.current_language]["histogram"], command=self.plot_histogram)
        self.histogram_button.pack()

        # Область для графиков (уменьшенные размеры)
        self.fig, (self.ax_scatter, self.ax_boxplot) = plt.subplots(2, 1, figsize=(4, 4))
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.plot_frame)
        self.canvas.get_tk_widget().pack()

        # Текстовые поля для отображения статистики
        self.mean_label = tk.Label(self.inner_control_frame, text=self.translations[self.current_language]["mean"])
        self.mean_label.pack()
        self.mean_text = tk.Text(self.inner_control_frame, height=1, width=30)
        self.mean_text.pack()

        self.variance_label = tk.Label(self.inner_control_frame, text=self.translations[self.current_language]["variance"])
        self.variance_label.pack()
        self.variance_text = tk.Text(self.inner_control_frame, height=1, width=30)
        self.variance_text.pack()

        self.range_label = tk.Label(self.inner_control_frame, text=self.translations[self.current_language]["range"])
        self.range_label.pack()
        self.range_text = tk.Text(self.inner_control_frame, height=1, width=30)
        self.range_text.pack()

        self.max_label = tk.Label(self.inner_control_frame, text=self.translations[self.current_language]["max"])
        self.max_label.pack()
        self.max_text = tk.Text(self.inner_control_frame, height=1, width=30)
        self.max_text.pack()

        self.min_label = tk.Label(self.inner_control_frame, text=self.translations[self.current_language]["min"])
        self.min_label.pack()
        self.min_text = tk.Text(self.inner_control_frame, height=1, width=30)
        self.min_text.pack()

        self.geometric_mean_label = tk.Label(self.inner_control_frame, text=self.translations[self.current_language]["geometric_mean"])
        self.geometric_mean_label.pack()
        self.geometric_mean_text = tk.Text(self.inner_control_frame, height=1, width=30)
        self.geometric_mean_text.pack()

        self.harmonic_mean_label = tk.Label(self.inner_control_frame, text=self.translations[self.current_language]["harmonic_mean"])
        self.harmonic_mean_label.pack()
        self.harmonic_mean_text = tk.Text(self.inner_control_frame, height=1, width=30)
        self.harmonic_mean_text.pack()
        
        self.quadratic_mean_label = tk.Label(self.inner_control_frame, text=self.translations[self.current_language]["quadratic_mean"])
        self.quadratic_mean_label.pack()
        self.quadratic_mean_text = tk.Text(self.inner_control_frame, height=1, width=30)
        self.quadratic_mean_text.pack()

        self.median_label = tk.Label(self.inner_control_frame, text=self.translations[self.current_language]["median"])
        self.median_label.pack()
        self.median_text = tk.Text(self.inner_control_frame, height=1, width=30)
        self.median_text.pack()

        self.std_dev_label = tk.Label(self.inner_control_frame, text=self.translations[self.current_language]["std_dev"])
        self.std_dev_label.pack()
        self.std_dev_text = tk.Text(self.inner_control_frame, height=1, width=30)
        self.std_dev_text.pack()

        self.mode_label = tk.Label(self.inner_control_frame, text=self.translations[self.current_language]["mode"])
        self.mode_label.pack()
        self.mode_text = tk.Text(self.inner_control_frame, height=1, width=30)
        self.mode_text.pack()

    def create_tab2_content(self, tab):
        # Frame для элементов управления и статистики
        self.control_frame_tab2 = ScrollableFrame(tab)  # Use ScrollableFrame
        self.control_frame_tab2.pack(side=tk.RIGHT, padx=10, fill="both", expand=True)

        self.inner_control_frame_tab2 = self.control_frame_tab2.inner_frame  # Access inner frame

        # Frame для графиков
        self.plot_frame_tab2 = tk.Frame(tab)
        self.plot_frame_tab2.pack(side=tk.LEFT, padx=10)

        # Кнопка для загрузки данных
        self.load_data_button_tab2 = tk.Button(self.inner_control_frame_tab2, text=self.translations[self.current_language]["load_data"], command=self.load_data)
        self.load_data_button_tab2.pack()

        # Выпадающий список для выбора столбца
        self.column_label_tab2 = tk.Label(self.inner_control_frame_tab2, text=self.translations[self.current_language]["select_column"])
        self.column_label_tab2.pack()
        self.column_var_tab2 = tk.StringVar(self.master)
        self.column_dropdown_tab2 = tk.OptionMenu(self.inner_control_frame_tab2, self.column_var_tab2, "")
        self.column_dropdown_tab2.pack()
        self.column_var_tab2.trace("w", self.update_plots_and_stats_tab2)

        # Чекбоксы для включения/выключения графиков
        self.scatter_check_tab2 = tk.Checkbutton(self.inner_control_frame_tab2, text=self.translations[self.current_language]["scatter_plot"], variable=self.scatter_visible, command=self.update_plots_and_stats_tab2)
        self.scatter_check_tab2.pack()
        self.boxplot_check_tab2 = tk.Checkbutton(self.inner_control_frame_tab2, text=self.translations[self.current_language]["box_plot"], variable=self.boxplot_visible, command=self.update_plots_and_stats_tab2)
        self.boxplot_check_tab2.pack()

        # Кнопки для выбора цвета
        self.scatter_color_button_tab2 = tk.Button(self.inner_control_frame_tab2, text=self.translations[self.current_language]["scatter_color"], command=self.choose_scatter_color)
        self.scatter_color_button_tab2.pack()
        self.boxplot_color_button_tab2 = tk.Button(self.inner_control_frame_tab2, text=self.translations[self.current_language]["box_color"], command=self.choose_boxplot_color)
        self.boxplot_color_button_tab2.pack()

        # Кнопки для сохранения графиков
        self.save_scatter_button_tab2 = tk.Button(self.inner_control_frame_tab2, text=self.translations[self.current_language]["save_scatter"], command=self.save_scatter_plot)
        self.save_scatter_button_tab2.pack()
        self.save_boxplot_button_tab2 = tk.Button(self.inner_control_frame_tab2, text=self.translations[self.current_language]["save_box"], command=self.save_boxplot)
        self.save_boxplot_button_tab2.pack()

        # Кнопки для открытия графиков в новом окне
        self.open_scatter_button_tab2 = tk.Button(self.inner_control_frame_tab2, text=self.translations[self.current_language]["open_scatter"], command=self.open_scatter_plot)
        self.open_scatter_button_tab2.pack()
        self.open_boxplot_button_tab2 = tk.Button(self.inner_control_frame_tab2, text=self.translations[self.current_language]["open_box"], command=self.open_boxplot)
        self.open_boxplot_button_tab2.pack()

        # Button to plot histogram in Tab 2
        self.histogram_button_tab2 = tk.Button(self.inner_control_frame_tab2, text=self.translations[self.current_language]["histogram"], command=self.plot_histogram_tab2)
        self.histogram_button_tab2.pack()

        # Labels and entry fields for min and max values
        self.min_value_label = tk.Label(self.inner_control_frame_tab2, text=self.translations[self.current_language]["min_value"])
        self.min_value_label.pack()
        self.min_value_entry = tk.Entry(self.inner_control_frame_tab2)
        self.min_value_entry.pack()

        self.max_value_label = tk.Label(self.inner_control_frame_tab2, text=self.translations[self.current_language]["max_value"])
        self.max_value_label.pack()
        self.max_value_entry = tk.Entry(self.inner_control_frame_tab2)
        self.max_value_entry.pack()

        # Button to apply the filter
        self.apply_filter_button = tk.Button(self.inner_control_frame_tab2, text=self.translations[self.current_language]["apply_filter"], command=self.apply_outlier_filter)
        self.apply_filter_button.pack()

        # Область для графиков (уменьшенные размеры)
        self.fig_tab2, (self.ax_scatter_tab2, self.ax_boxplot_tab2) = plt.subplots(2, 1, figsize=(4, 4))
        self.canvas_tab2 = FigureCanvasTkAgg(self.fig_tab2, master=self.plot_frame_tab2)
        self.canvas_tab2.get_tk_widget().pack()

        # Текстовые поля для отображения статистики
        self.mean_label_tab2 = tk.Label(self.inner_control_frame_tab2, text=self.translations[self.current_language]["mean"])
        self.mean_label_tab2.pack()
        self.mean_text_tab2 = tk.Text(self.inner_control_frame_tab2, height=1, width=30)
        self.mean_text_tab2.pack()

        self.variance_label_tab2 = tk.Label(self.inner_control_frame_tab2, text=self.translations[self.current_language]["variance"])
        self.variance_label_tab2.pack()
        self.variance_text_tab2 = tk.Text(self.inner_control_frame_tab2, height=1, width=30)
        self.variance_text_tab2.pack()

        self.range_label_tab2 = tk.Label(self.inner_control_frame_tab2, text=self.translations[self.current_language]["range"])
        self.range_label_tab2.pack()
        self.range_text_tab2 = tk.Text(self.inner_control_frame_tab2, height=1, width=30)
        self.range_text_tab2.pack()

        self.max_label_tab2 = tk.Label(self.inner_control_frame_tab2, text=self.translations[self.current_language]["max"])
        self.max_label_tab2.pack()
        self.max_text_tab2 = tk.Text(self.inner_control_frame_tab2, height=1, width=30)
        self.max_text_tab2.pack()

        self.min_label_tab2 = tk.Label(self.inner_control_frame_tab2, text=self.translations[self.current_language]["min"])
        self.min_label_tab2.pack()
        self.min_text_tab2 = tk.Text(self.inner_control_frame_tab2, height=1, width=30)
        self.min_text_tab2.pack()

        self.geometric_mean_label_tab2 = tk.Label(self.inner_control_frame_tab2, text=self.translations[self.current_language]["geometric_mean"])
        self.geometric_mean_label_tab2.pack()
        self.geometric_mean_text_tab2 = tk.Text(self.inner_control_frame_tab2, height=1, width=30)
        self.geometric_mean_text_tab2.pack()

        self.harmonic_mean_label_tab2 = tk.Label(self.inner_control_frame_tab2, text=self.translations[self.current_language]["harmonic_mean"])
        self.harmonic_mean_label_tab2.pack()
        self.harmonic_mean_text_tab2 = tk.Text(self.inner_control_frame_tab2, height=1, width=30)
        self.harmonic_mean_text_tab2.pack()
        
        self.quadratic_mean_label_tab2 = tk.Label(self.inner_control_frame_tab2, text=self.translations[self.current_language]["quadratic_mean"])
        self.quadratic_mean_label_tab2.pack()
        self.quadratic_mean_text_tab2 = tk.Text(self.inner_control_frame_tab2, height=1, width=30)
        self.quadratic_mean_text_tab2.pack()

        self.median_label_tab2 = tk.Label(self.inner_control_frame_tab2, text=self.translations[self.current_language]["median"])
        self.median_label_tab2.pack()
        self.median_text_tab2 = tk.Text(self.inner_control_frame_tab2, height=1, width=30)
        self.median_text_tab2.pack()

        self.std_dev_label_tab2 = tk.Label(self.inner_control_frame_tab2, text=self.translations[self.current_language]["std_dev"])
        self.std_dev_label_tab2.pack()
        self.std_dev_text_tab2 = tk.Text(self.inner_control_frame_tab2, height=1, width=30)
        self.std_dev_text_tab2.pack()

        self.mode_label_tab2 = tk.Label(self.inner_control_frame_tab2, text=self.translations[self.current_language]["mode"])
        self.mode_label_tab2.pack()
        self.mode_text_tab2 = tk.Text(self.inner_control_frame_tab2, height=1, width=30)
        self.mode_text_tab2.pack()

    def load_data(self):
        file_path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
        if file_path:
            try:
                self.df = pd.read_csv(file_path)
                self.filtered_df = self.df.copy()  # Initialize filtered_df with a copy of the original DataFrame
                columns = list(self.df.columns)
                # Update dropdowns in both tabs
                self.update_column_dropdown(columns)
                self.update_column_dropdown_tab2(columns)
                self.update_plots_and_stats()
                self.update_plots_and_stats_tab2()
            except Exception as e:
                messagebox.showerror("Error", str(e))

    def update_column_dropdown(self, columns):
        self.column_var.set(columns[0])  # set the default value
        self.column_dropdown['menu'].delete(0, 'end')
        for column in columns:
            self.column_dropdown['menu'].add_command(label=column, command=tk._setit(self.column_var, column))

    def update_column_dropdown_tab2(self, columns):
        self.column_var_tab2.set(columns[0])  # set the default value
        self.column_dropdown_tab2['menu'].delete(0, 'end')
        for column in columns:
            self.column_dropdown_tab2['menu'].add_command(label=column, command=tk._setit(self.column_var_tab2, column))

    def choose_scatter_color(self):
        color_code = colorchooser.askcolor(title=self.translations[self.current_language]["scatter_color"])
        if color_code:
            self.scatter_color = color_code[1]
            self.update_plots_and_stats()
            self.update_plots_and_stats_tab2()

    def choose_boxplot_color(self):
        color_code = colorchooser.askcolor(title=self.translations[self.current_language]["box_color"])
        if color_code:
            self.boxplot_color = color_code[1]
            self.update_plots_and_stats()
            self.update_plots_and_stats_tab2()

    def save_scatter_plot(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".png", filetypes=[("PNG files", "*.png")])
        if file_path:
            self.fig.savefig(file_path)
            self.fig_tab2.savefig(file_path)

    def save_boxplot(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".png", filetypes=[("PNG files", "*.png")])
        if file_path:
            self.fig.savefig(file_path)
            self.fig_tab2.savefig(file_path)

    def open_scatter_plot(self):
        if self.df is None or self.selected_column is None:
            messagebox.showinfo(self.translations[self.current_language]["info"], self.translations[self.current_language]["load_data_first"])
            return

        data = self.df[self.selected_column].dropna()

        # Создаем новое окно
        new_window = Toplevel(self.master)
        new_window.title(self.translations[self.current_language]["scatter_plot"])

        # Создаем новую фигуру и оси
        fig, ax = plt.subplots(figsize=(6, 4))
        sns.scatterplot(x=data.index, y=data.values, color=self.scatter_color, ax=ax)  # Use seaborn
        ax.set_title(f"{self.translations[self.current_language]['scatter_plot']} ({self.selected_column})")
        ax.set_xlabel("Index")
        ax.set_ylabel("Value")

        # Создаем canvas для отображения графика в окне
        canvas = FigureCanvasTkAgg(fig, master=new_window)
        canvas.get_tk_widget().pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        # Добавляем панель инструментов навигации
        toolbar = NavigationToolbar2Tk(canvas, new_window)
        toolbar.update()
        toolbar.pack(side=tk.LEFT, fill=tk.Y)

        canvas.draw()

        # Добавляем возможность перетаскивания графика
        self.add_pan_and_zoom(canvas, ax)

    def open_boxplot(self):
        if self.df is None or self.selected_column is None:
            messagebox.showinfo(self.translations[self.current_language]["info"], self.translations[self.current_language]["load_data_first"])
            return

        data = self.df[self.selected_column].dropna()

        # Создаем новое окно
        new_window = Toplevel(self.master)
        new_window.title(self.translations[self.current_language]["box_plot"])

        # Создаем новую фигуру и оси
        fig, ax = plt.subplots(figsize=(6, 4))
        sns.boxplot(y=data.values, color=self.boxplot_color, ax=ax)  # Use seaborn
        ax.set_title(f"{self.translations[self.current_language]['box_plot']} ({self.selected_column})")
        ax.set_ylabel("Value")

        # Создаем canvas для отображения графика в окне
        canvas = FigureCanvasTkAgg(fig, master=new_window)
        canvas.get_tk_widget().pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        # Добавляем панель инструментов навигации
        toolbar = NavigationToolbar2Tk(canvas, new_window)
        toolbar.update()
        toolbar.pack(side=tk.LEFT, fill=tk.Y)

        canvas.draw()

        # Добавляем возможность перетаскивания графика
        self.add_pan_and_zoom(canvas, ax)

    def add_pan_and_zoom(self, canvas, ax):
        def on_press(event):
            if event.inaxes == ax:
                self.x0, self.y0 = event.xdata, event.ydata

        def on_motion(event):
            if event.inaxes == ax:
                dx = event.xdata - self.x0
                dy = event.ydata - self.y0
                ax.set_xlim([ax.get_xlim()[0] - dx, ax.get_xlim()[1] - dx])
                ax.set_ylim([ax.get_ylim()[0] - dy, ax.get_ylim()[1] - dy])
                canvas.draw_idle()
                self.x0, self.y0 = event.xdata, event.ydata

        canvas.mpl_connect('button_press_event', on_press)
        canvas.mpl_connect('motion_notify_event', on_motion)

    def apply_outlier_filter(self):
        try:
            min_value = float(self.min_value_entry.get())
            max_value = float(self.max_value_entry.get())
        except ValueError:
            messagebox.showerror("Error", "Invalid min or max value.")
            return

        selected_column = self.column_var_tab2.get()
        if selected_column not in self.df.columns:
            messagebox.showerror("Error", "Select a column first.")
            return

        # Apply the filter
        self.filtered_df = self.df[(self.df[selected_column] >= min_value) & (self.df[selected_column] <= max_value)]
        self.update_plots_and_stats_tab2()

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
            self.ax_scatter.set_title(f"{self.translations[self.current_language]['scatter_plot']} ({self.selected_column})")
            self.ax_scatter.set_xlabel("Index")
            self.ax_scatter.set_ylabel("Value")
        self.ax_scatter.set_visible(self.scatter_visible.get())

        # Ящик с усами
        self.ax_boxplot.clear()
        if self.boxplot_visible.get():
            sns.boxplot(y=data.values, color=self.boxplot_color, ax=self.ax_boxplot)  # Use seaborn
            self.ax_boxplot.set_title(f"{self.translations[self.current_language]['box_plot']} ({self.selected_column})")
            self.ax_boxplot.set_ylabel("Value")
        self.ax_boxplot.set_visible(self.boxplot_visible.get())

        self.fig.tight_layout()
        self.canvas.draw()

    def update_plots_and_stats_tab2(self, *args):
        if self.df is None:
            return

        selected_column = self.column_var_tab2.get()
        if selected_column not in self.df.columns:
            return

        if self.filtered_df is None:
            data = self.df[selected_column].dropna()
        else:
            data = self.filtered_df[selected_column].dropna()

        # Calculate statistics
        mean_val = data.mean()
        variance_val = data.var()
        range_val = data.max() - data.min()
        max_val = data.max()
        min_val = data.min()

        try:
            geometric_mean_val = gmean(data)
        except ValueError:
            geometric_mean_val = "N/A (negative values)"
        try:
            harmonic_mean_val = hmean(data)
        except ValueError:
            harmonic_mean_val = "N/A (zero values)"
            
        try:
            quadratic_mean_val = np.sqrt(np.mean(data**2))
        except ValueError:
            quadratic_mean_val = "N/A"

        median_val = data.median()
        std_dev_val = data.std()
        try:
            mode_val = statistics.mode(data)
        except statistics.StatisticsError:
            mode_val = "N/A (no unique mode)"

        # Update text fields with statistics
        self.mean_text_tab2.delete("1.0", tk.END)
        self.mean_text_tab2.insert(tk.END, str(mean_val))

        self.variance_text_tab2.delete("1.0", tk.END)
        self.variance_text_tab2.insert(tk.END, str(variance_val))

        self.range_text_tab2.delete("1.0", tk.END)
        self.range_text_tab2.insert(tk.END, str(range_val))

        self.max_text_tab2.delete("1.0", tk.END)
        self.max_text_tab2.insert(tk.END, str(max_val))

        self.min_text_tab2.delete("1.0", tk.END)
        self.min_text_tab2.insert(tk.END, str(min_val))

        self.geometric_mean_text_tab2.delete("1.0", tk.END)
        self.geometric_mean_text_tab2.insert(tk.END, str(geometric_mean_val))

        self.harmonic_mean_text_tab2.delete("1.0", tk.END)
        self.harmonic_mean_text_tab2.insert(tk.END, str(harmonic_mean_val))
        
        self.quadratic_mean_text_tab2.delete("1.0", tk.END)
        self.quadratic_mean_text_tab2.insert(tk.END, str(quadratic_mean_val))

        self.median_text_tab2.delete("1.0", tk.END)
        self.median_text_tab2.insert(tk.END, str(median_val))

        self.std_dev_text_tab2.delete("1.0", tk.END)
        self.std_dev_text_tab2.insert(tk.END, str(std_dev_val))

        self.mode_text_tab2.delete("1.0", tk.END)
        self.mode_text_tab2.insert(tk.END, str(mode_val))

        # График расхождений
        self.ax_scatter_tab2.clear()
        if self.scatter_visible.get():
            sns.scatterplot(x=data.index, y=data.values, color=self.scatter_color, ax=self.ax_scatter_tab2)  # Use seaborn
            self.ax_scatter_tab2.set_title(f"{self.translations[self.current_language]['scatter_plot']} ({selected_column})")
            self.ax_scatter_tab2.set_xlabel("Index")
            self.ax_scatter_tab2.set_ylabel("Value")
        self.ax_scatter_tab2.set_visible(self.scatter_visible.get())

        # Ящик с усами
        self.ax_boxplot_tab2.clear()
        if self.boxplot_visible.get():
            sns.boxplot(y=data.values, color=self.boxplot_color, ax=self.ax_boxplot_tab2)  # Use seaborn
            self.ax_boxplot_tab2.set_title(f"{self.translations[self.current_language]['box_plot']} ({selected_column})")
            self.ax_boxplot_tab2.set_ylabel("Value")
        self.ax_boxplot_tab2.set_visible(self.boxplot_visible.get())

        self.fig_tab2.tight_layout()
        self.canvas_tab2.draw()

    def change_language(self, language):
        if language == self.translations[self.current_language]["russian"]:
            self.current_language = "ru"
        else:
            self.current_language = "en"
        self.update_text()

    def update_text(self):
        # Update all the text elements in the UI
        self.master.title(self.translations[self.current_language]["title"])
        self.language_label.config(text=self.translations[self.current_language]["language"])
        current_language_english = self.translations[self.current_language]["english"]
        language_var_value = self.language_var.get()
        self.language_var.set(self.translations[self.current_language][language_var_value == current_language_english and "russian" or "english"])
        menu = self.language_dropdown["menu"]
        menu.delete(0, "end")
        for lang in [self.translations[self.current_language]["english"], self.translations[self.current_language]["russian"]]:
            menu.add_command(label=lang, command=tk._setit(self.language_var, lang))
        self.load_data_button.config(text=self.translations[self.current_language]["load_data"])
        self.load_data_button_tab2.config(text=self.translations[self.current_language]["load_data"])
        self.column_label.config(text=self.translations[self.current_language]["select_column"])
        self.column_label_tab2.config(text=self.translations[self.current_language]["select_column"])
        self.scatter_check.config(text=self.translations[self.current_language]["scatter_plot"])
        self.scatter_check_tab2.config(text=self.translations[self.current_language]["scatter_plot"])
        self.boxplot_check.config(text=self.translations[self.current_language]["box_plot"])
        self.boxplot_check_tab2.config(text=self.translations[self.current_language]["box_plot"])
        self.scatter_color_button.config(text=self.translations[self.current_language]["scatter_color"])
        self.scatter_color_button_tab2.config(text=self.translations[self.current_language]["scatter_color"])
        self.boxplot_color_button.config(text=self.translations[self.current_language]["box_color"])
        self.boxplot_color_button_tab2.config(text=self.translations[self.current_language]["box_color"])
        self.save_scatter_button.config(text=self.translations[self.current_language]["save_scatter"])
        self.save_scatter_button_tab2.config(text=self.translations[self.current_language]["save_scatter"])
        self.save_boxplot_button.config(text=self.translations[self.current_language]["save_box"])
        self.save_boxplot_button_tab2.config(text=self.translations[self.current_language]["save_box"])
        self.open_scatter_button.config(text=self.translations[self.current_language]["open_scatter"])
        self.open_scatter_button_tab2.config(text=self.translations[self.current_language]["open_box"])
        self.open_boxplot_button.config(text=self.translations[self.current_language]["open_box"])
        self.open_boxplot_button_tab2.config(text=self.translations[self.current_language]["open_box"])
        self.mean_label.config(text=self.translations[self.current_language]["mean"])
        self.mean_label_tab2.config(text=self.translations[self.current_language]["mean"])
        self.variance_label.config(text=self.translations[self.current_language]["variance"])
        self.variance_label_tab2.config(text=self.translations[self.current_language]["variance"])
        self.range_label.config(text=self.translations[self.current_language]["range"])
        self.range_label_tab2.config(text=self.translations[self.current_language]["range"])
        self.max_label.config(text=self.translations[self.current_language]["max"])
        self.max_label_tab2.config(text=self.translations[self.current_language]["max"])
        self.min_label.config(text=self.translations[self.current_language]["min"])
        self.min_label_tab2.config(text=self.translations[self.current_language]["min"])
        self.geometric_mean_label.config(text=self.translations[self.current_language]["geometric_mean"])
        self.geometric_mean_label_tab2.config(text=self.translations[self.current_language]["geometric_mean"])
        self.harmonic_mean_label.config(text=self.translations[self.current_language]["harmonic_mean"])
        self.harmonic_mean_label_tab2.config(text=self.translations[self.current_language]["harmonic_mean"])
        self.quadratic_mean_label.config(text=self.translations[self.current_language]["quadratic_mean"])
        self.quadratic_mean_label_tab2.config(text=self.translations[self.current_language]["quadratic_mean"])
        self.median_label.config(text=self.translations[self.current_language]["median"])
        self.median_label_tab2.config(text=self.translations[self.current_language]["median"])
        self.std_dev_label.config(text=self.translations[self.current_language]["std_dev"])
        self.std_dev_label_tab2.config(text=self.translations[self.current_language]["std_dev"])
        self.mode_label.config(text=self.translations[self.current_language]["mode"])
        self.mode_label_tab2.config(text=self.translations[self.current_language]["mode"])
        self.histogram_button.config(text=self.translations[self.current_language]["histogram"])
        self.histogram_button_tab2.config(text=self.translations[self.current_language]["histogram"])
        self.notebook.tab(0, text=self.translations[self.current_language]["tab1"])
        self.notebook.tab(1, text=self.translations[self.current_language]["tab2"])
        self.update_plots_and_stats()
        self.update_plots_and_stats_tab2()

    def update_tab_text(self, event):
        self.update_text()

    def plot_histogram(self):
        if self.df is None or self.selected_column is None:
            messagebox.showinfo(self.translations[self.current_language]["info"], self.translations[self.current_language]["load_data_first"])
            return

        data = self.df[self.selected_column].dropna()

        # Create a new window
        new_window = Toplevel(self.master)
        new_window.title(self.translations[self.current_language]["histogram"])

        # Create a new figure and axes
        fig, ax = plt.subplots(figsize=(6, 4))
        sns.histplot(data.values, kde=False, ax=ax)  # Use seaborn for histogram
        ax.set_title(f"{self.translations[self.current_language]['histogram']} ({self.selected_column})")
        ax.set_xlabel("Value")
        ax.set_ylabel("Frequency")

        # Create a canvas to display the plot in the window
        canvas = FigureCanvasTkAgg(fig, master=new_window)
        canvas.get_tk_widget().pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        # Add navigation toolbar
        toolbar = NavigationToolbar2Tk(canvas, new_window)
        toolbar.update()
        toolbar.pack(side=tk.LEFT, fill=tk.Y)

        canvas.draw()

        # Add pan and zoom functionality
        self.add_pan_and_zoom(canvas, ax)

    def plot_histogram_tab2(self):
        if self.df is None or self.column_var_tab2.get() is None:
            messagebox.showinfo(self.translations[self.current_language]["info"], self.translations[self.current_language]["load_data_first"])
            return

        selected_column = self.column_var_tab2.get()

        if self.filtered_df is None:
            data = self.df[selected_column].dropna()
        else:
            data = self.filtered_df[selected_column].dropna()

        # Create a new window
        new_window = Toplevel(self.master)
        new_window.title(self.translations[self.current_language]["histogram"])

        # Create a new figure and axes
        fig, ax = plt.subplots(figsize=(6, 4))
        sns.histplot(data.values, kde=False, ax=ax)  # Use seaborn for histogram
        ax.set_title(f"{self.translations[self.current_language]['histogram']} ({selected_column})")
        ax.set_xlabel("Value")
        ax.set_ylabel("Frequency")

        # Create a canvas to display the plot in the window
        canvas = FigureCanvasTkAgg(fig, master=new_window)
        canvas.get_tk_widget().pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        # Add navigation toolbar
        toolbar = NavigationToolbar2Tk(canvas, new_window)
        toolbar.update()
        toolbar.pack(side=tk.LEFT, fill=tk.Y)

        canvas.draw()

        # Add pan and zoom functionality
        self.add_pan_and_zoom(canvas, ax)

root = tk.Tk()
app = DataAnalyzerApp(root)
root.mainloop()
