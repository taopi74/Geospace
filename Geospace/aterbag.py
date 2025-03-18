import tkinter as tk 
from tkinter import ttk, messagebox
import numpy as np
from scipy.interpolate import interp1d
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

class aterbag(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.boring_data = {}
        self.entry_widgets = {}
        self.liquid_limit = 0
        self.plastic_limit = 0
        self.PI = 0
        
        # প্রধান ফ্রেম: পুরো উইন্ডো দখল করবে
        aterbag_frame = ttk.Frame(self)
        aterbag_frame.pack(fill="both", expand=True)
        
        # ---------------------------------------
        # 1) First Column: Project Details, Inputs & Calculations
        # ---------------------------------------
        first_column = ttk.Frame(aterbag_frame, width=200, relief="solid", borderwidth=2)
        first_column.pack(side="left", fill="y", expand=False, padx=5, pady=5)

        # -- Project Details --
        ttk.Label(first_column, text="Project Details", font=("Arial", 10)).pack(pady=10)
        for field in controller.shared_data.keys():
            frame = ttk.Frame(first_column, relief="solid", borderwidth=2)
            frame.pack(pady=5, padx=20, fill="x")
            ttk.Label(frame, text=f"{field}:", width=10).pack(side="left", padx=5)
            ttk.Label(frame, textvariable=controller.shared_data[field]).pack(side="right", expand=True, fill="x", padx=5)
        
        # -- Liquid Limit Analysis Section --
        ttk.Label(first_column, text="Liquid Limit Analysis", font=("Arial", 10, "bold")).pack(pady=5)
        liquid_frame = ttk.Frame(first_column)
        liquid_frame.pack(fill="x", padx=5, pady=5)

        headers = ["Can No.", "Wt. clean\nCan (gm)", "Wt. Can+\nMoist soil", 
                   "Wt. Can+\nDry soil", "Blow\nCount"]
        for col, header in enumerate(headers):
            ttk.Label(liquid_frame, text=header).grid(row=0, column=col, padx=2, pady=2)
        
        self.liquid_entries = []
        for row in range(1, 4):  # 3 samples
            row_entries = []
            for col in range(len(headers)):
                entry = ttk.Entry(liquid_frame, width=10)
                entry.grid(row=row, column=col, padx=2, pady=2)
                row_entries.append(entry)
            self.liquid_entries.append(row_entries)
        
        # -- Plastic Limit Analysis Section --
        ttk.Label(first_column, text="Plastic Limit Analysis", font=("Arial", 10, "bold")).pack(pady=5)
        plastic_frame = ttk.Frame(first_column)
        plastic_frame.pack(fill="x", padx=5, pady=5)
        
        pheaders = ["Can No.", "Wt. clean\nCan (gm)", "Wt. Can+\nMoist soil", "Wt. Can+\nDry soil"]
        for col, header in enumerate(pheaders):
            ttk.Label(plastic_frame, text=header).grid(row=0, column=col, padx=2, pady=2)
        
        self.plastic_entries = []
        for row in range(1, 3):  # 2 samples
            row_entries = []
            for col in range(len(pheaders)):
                entry = ttk.Entry(plastic_frame, width=10)
                entry.grid(row=row, column=col, padx=2, pady=2)
                row_entries.append(entry)
            self.plastic_entries.append(row_entries)
        
        # -- Results Display Label --
        self.results_label = ttk.Label(first_column, text="", justify="center")
        self.results_label.pack(pady=10)

        # -- Single Button for All Calculations --
        self.calculate_btn = ttk.Button(first_column, text="Calculate All", command=self.calculate_all)
        self.calculate_btn.pack(pady=5)

        # ---------------------------------------
        # 2) Second Column: Graph Display
        # ---------------------------------------
        second_column = ttk.Frame(aterbag_frame, relief="solid", borderwidth=2)
        second_column.pack(side="left", fill="both", expand=True, padx=5, pady=5)

        # একটি ফ্রেম, তার ভেতরে দুটি সাব-ফ্রেমে গ্রাফ
        self.graph_frame = ttk.Frame(second_column)
        self.graph_frame.pack(fill="both", expand=True)

        # দুই সাব-ফ্রেম: একটিতে LL Graph, অন্যটিতে Casagrande Chart
        self.ll_graph_frame = ttk.Frame(self.graph_frame)
        self.ll_graph_frame.pack(fill="both", expand=True)

        self.casagrande_graph_frame = ttk.Frame(self.graph_frame)
        self.casagrande_graph_frame.pack(fill="both", expand=True)

    # -----------------------------------------------------------------
    # মেইন ফাংশনসমূহ
    # -----------------------------------------------------------------
    def calculate_all(self):
        """
        Calculate liquid limit, plastic limit, and show graphs.
        """
        self.calculate_liquid_limit()
        self.classify_soil()

    def calculate_liquid_limit(self):
        """
        Calculate liquid limit using blow counts & moisture contents.
        """
        try:
            moisture_contents = []
            blow_counts = []
            liquid_results = []
            
            for row_entries in self.liquid_entries:
                can_no = row_entries[0].get().strip()
                if not can_no:
                    continue
                wt_clean = float(row_entries[1].get())
                wt_moist = float(row_entries[2].get())
                wt_dry = float(row_entries[3].get())
                blow_count = int(row_entries[4].get())
                
                dry_soil = wt_dry - wt_clean
                pore_water = wt_moist - wt_dry
                mc = (pore_water / dry_soil) * 100 if dry_soil != 0 else 0
                
                moisture_contents.append(mc)
                blow_counts.append(blow_count)
                
                liquid_results.append({
                    "Can No.": can_no,
                    "Wt. of Can+Moist soil (gm)": wt_moist,
                    "Wt. of Can+Dry soil (gm)": wt_dry,
                    "Wt. of Dry soil (gm)": dry_soil,
                    "Wt. of pore Water (gm)": pore_water,
                    "Moisture Content (%)": mc,
                    "Blow Count": blow_count
                })
            
            if not blow_counts:
                raise ValueError("No sample data entered for Liquid Limit Analysis.")
            
            blow_counts = np.array(blow_counts)
            moisture_contents = np.array(moisture_contents)
            
            sorted_idx = np.argsort(blow_counts)
            sorted_blows = blow_counts[sorted_idx]
            sorted_mc = moisture_contents[sorted_idx]
            
            if len(sorted_blows) < 2:
                raise ValueError("Insufficient data for interpolation.")
            
            # Interpolate to find moisture content at 25 blows
            f = interp1d(sorted_blows, sorted_mc, kind='linear', fill_value='extrapolate')
            ll_value = float(f(25))
            
            # Simple rounding
            decimal_part = ll_value - int(ll_value)
            if decimal_part >= 0.5:
                ll_value = int(ll_value) + 1
            else:
                ll_value = int(ll_value)
            
            # Build result text
            result_text = "Liquid Limit Analysis Results:\n"
            result_text += ("Can No.\tWt. of Can+Moist\tWt. of Can+Dry\tWt. Dry soil\t"
                            "Wt. pore Water\tMoisture (%)\tBlow Count\n")
            for r in liquid_results:
                result_text += (f"{r['Can No.']}\t{r['Wt. of Can+Moist soil (gm)']:.2f}\t"
                                f"{r['Wt. of Can+Dry soil (gm)']:.2f}\t{r['Wt. of Dry soil (gm)']:.2f}\t"
                                f"{r['Wt. of pore Water (gm)']:.2f}\t{r['Moisture Content (%)']:.2f}\t"
                                f"{r['Blow Count']}\n")
            
            # Plastic Limit
            plastic_text, plastic_limit = self.calculate_plastic_limit(display_only=True)
            result_text += plastic_text
            
            # Update class variables
            self.liquid_limit = ll_value
            self.plastic_limit = plastic_limit
            self.PI = ll_value - plastic_limit
            
            # Append final results
            result_text += f"\nLiquid Limit (LL): {self.liquid_limit}%"
            result_text += f"\nPlastic Limit (PL): {self.plastic_limit}%"
            result_text += f"\nPlasticity Index (PI): {self.PI}%\n"
            
            # Show in label
            self.results_label.config(text=result_text)
            
            # Plot Liquid Limit Graph
            self.plot_liquid_limit_graph(sorted_blows, sorted_mc, ll_value)
            
        except ValueError as e:
            messagebox.showerror("Error", str(e))

    def calculate_plastic_limit(self, display_only=False):
        """
        Calculate plastic limit using minimum moisture content from plastic_entries.
        """
        try:
            moisture_contents = []
            results = []
            
            for row_entries in self.plastic_entries:
                can_no = row_entries[0].get().strip()
                if not can_no:
                    continue
                wt_clean = float(row_entries[1].get())
                wt_moist = float(row_entries[2].get())
                wt_dry = float(row_entries[3].get())
                
                dry_soil = wt_dry - wt_clean
                pore_water = wt_moist - wt_dry
                mc = (pore_water / dry_soil) * 100 if dry_soil != 0 else 0
                
                moisture_contents.append(mc)
                results.append({
                    "Can No.": can_no,
                    "Wt. of Can+Moist soil (gm)": wt_moist,
                    "Wt. of Can+Dry soil (gm)": wt_dry,
                    "Wt. of Dry soil (gm)": dry_soil,
                    "Wt. of pore Water (gm)": pore_water,
                    "Moisture Content (%)": mc
                })
            
            if not moisture_contents:
                raise ValueError("No sample data entered for Plastic Limit Analysis.")
            
            # Use the minimum moisture content as Plastic Limit
            pl_unrounded = min(moisture_contents)
            decimal_part = pl_unrounded - int(pl_unrounded)
            if decimal_part >= 0.5:
                plastic_limit = int(pl_unrounded) + 1
            else:
                plastic_limit = int(pl_unrounded)
            
            # Build result text
            result_text = "\nPlastic Limit Analysis Results:\n"
            result_text += ("Can No.\tWt. of Can+Moist\tWt. of Can+Dry\tWt. Dry soil\t"
                            "Wt. pore Water\tMoisture (%)\n")
            for r in results:
                result_text += (f"{r['Can No.']}\t{r['Wt. of Can+Moist soil (gm)']:.2f}\t"
                                f"{r['Wt. of Can+Dry soil (gm)']:.2f}\t{r['Wt. of Dry soil (gm)']:.2f}\t"
                                f"{r['Wt. of pore Water (gm)']:.2f}\t{r['Moisture Content (%)']:.2f}\n")
            
            return result_text, plastic_limit
        
        except ValueError as e:
            messagebox.showerror("Error", str(e))
            return "", 0

    # -----------------------------------------------------------------
    # গ্রাফ আঁকার ফাংশন
    # -----------------------------------------------------------------
    def plot_liquid_limit_graph(self, blow_counts, moisture_contents, ll_value):
        """
        Draw the Liquid Limit Analysis graph in ll_graph_frame
        with a fixed size (width x height).
        """
        # ll_graph_frame এর পূর্ববর্তী সব উইজেট মুছে দিন
        for widget in self.ll_graph_frame.winfo_children():
            widget.destroy()
        
        # figsize=(width_in_inches, height_in_inches), dpi=100 => পিক্সেলে পরিণত হবে
        fig, ax = plt.subplots(figsize=(5, 4), dpi=100)  
        ax.plot(blow_counts, moisture_contents, 'bo-', label="Moisture Content")
        ax.axvline(x=25, color='g', linestyle='--', label="25 Blows")
        
        ax.set_xlabel("Blow Count")
        ax.set_ylabel("Moisture Content (%)")
        ax.set_title("Liquid Limit Analysis")
        ax.grid(True)
        ax.legend()
        
        canvas = FigureCanvasTkAgg(fig, master=self.ll_graph_frame)
        canvas.draw()
        # গ্রাফের ক্যানভাসের আকারও নির্দিষ্ট করতে চাইলে:
        # canvas.get_tk_widget().config(width=500, height=400)
        canvas.get_tk_widget().pack(fill="both", expand=True)

    def classify_soil(self):
        """
        Classify the soil based on Liquid Limit (LL) and Plasticity Index (PI).
        """
        try:
            LL = self.liquid_limit
            PI = self.PI
            soil_type = self.classify_soil_type(LL, PI)
            self.plot_casagrande_chart(LL, PI, soil_type)
            
            # Append soil type info to results label
            current_text = self.results_label.cget("text")
            self.results_label.config(text=f"{current_text}\nSoil Type: {soil_type}")
        except AttributeError:
            messagebox.showerror("Error", "Please calculate Liquid & Plastic Limits first.")

    def classify_soil_type(self, LL, PI):
        """
        Determine the soil type using A-line & standard classification rules.
        """
        A_line_PI = 0.73 * (LL - 20)

        # CL-ML zone
        if 4 <= PI <= 7 and 12 <= LL <= 29.59:
            return "CL-ML (Intermediate Clay-Silt Soil)"

        if LL < 50:
            if PI > A_line_PI:
                return "CL or OL (Clay or Organic Clay)"
            else:
                return "ML or OL (Silt or Organic Silt)"
        else:
            if PI > A_line_PI:
                return "CH or OH (High Plastic Clay or Organic Clay)"
            else:
                return "MH or OH (High Plastic Silt or Organic Silt)"

    def plot_casagrande_chart(self, LL, PI, soil_type):
        """
        Draw the Casagrande’s Plasticity Chart in casagrande_graph_frame
        with a fixed size (width x height).
        """
        # casagrande_graph_frame এর পূর্ববর্তী সব উইজেট মুছে দিন
        for widget in self.casagrande_graph_frame.winfo_children():
            widget.destroy()

        fig, ax = plt.subplots(figsize=(5, 4), dpi=100)  # 5x4 inches, 100 dpi
        # "A" Line
        LL_A = np.linspace(10, 100, 20)
        A_Line = 0.73 * (LL_A - 20)
        
        # "U" Line
        LL_U = np.linspace(8, 100, 20)
        U_Line = 0.9 * (LL_U - 8)
        
        ax.plot(LL_A, A_Line, label='"A" Line', color='blue', linewidth=2)
        ax.plot(LL_U, U_Line, label='"U" Line', color='purple', linewidth=2)

        # Horizontal lines for typical boundaries
        ax.hlines(y=7, xmin=16, xmax=29.59, color='red', linewidth=2)
        ax.hlines(y=4, xmin=12, xmax=25.47, color='green', linewidth=2)
        ax.axvline(x=50, color='black', linewidth=2, label='50% LL Line')

        # Text labels
        ax.text(16, 5,  "CL-ML", color='green', fontsize=12, fontweight='bold')
        ax.text(35, 5,  "ML or OL", color='red', fontsize=12, fontweight='bold')
        ax.text(38, 23, "CL or OL", color='blue', fontsize=12, fontweight='bold')
        ax.text(60, 40, "CH or OH", color='blue', fontsize=12, fontweight='bold')
        ax.text(65, 10, "MH or OH", color='red', fontsize=12, fontweight='bold')

        # Plot the test point
        ax.scatter(LL, PI, color='red', marker='x', s=100, label=f'Soil Sample ({soil_type})')

        ax.set_xlabel("Liquid Limit, LL (%)", fontsize=12, fontweight='bold')
        ax.set_ylabel("Plasticity Index, PI (%)", fontsize=12, fontweight='bold')
        ax.set_title("Casagrande’s Plasticity Chart", fontsize=14, fontweight='bold')

        ax.set_xticks(np.arange(0, 110, 10))
        ax.set_yticks(np.arange(0, 60, 10))
        ax.set_xlim(0, 100)
        ax.set_ylim(0, 50)
        ax.legend()
        ax.grid(True, linestyle='--', linewidth=0.5)

        canvas = FigureCanvasTkAgg(fig, master=self.casagrande_graph_frame)
        canvas.draw()
        # চাইলে এখানেও ক্যানভাসের আকার নির্দিষ্ট করা যেতে পারে
        # canvas.get_tk_widget().config(width=500, height=400)
        canvas.get_tk_widget().pack(fill="both", expand=True)
