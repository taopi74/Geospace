import tkinter as tk
from tkinter import ttk, messagebox

class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Soil Specific Gravity Calculator")
        self.root.geometry("1000x800")

        # Create DataGridViews (Treeviews)
        self.dgv_data = ttk.Treeview(self.root, columns=("Parameter", "Unit", "Value"), show="headings")
        self.dgv_data.heading("Parameter", text="Parameter")
        self.dgv_data.heading("Unit", text="Unit")
        self.dgv_data.heading("Value", text="Value")
        self.dgv_data.pack(fill="both", expand=True, padx=5, pady=5)

        # Create input fields
        self.input_frame = ttk.Frame(self.root)
        self.input_frame.pack(fill="x", padx=5, pady=5)

        ttk.Label(self.input_frame, text="Boring No:").grid(row=0, column=0, padx=2, pady=2)
        self.txt_boring_no = ttk.Entry(self.input_frame)
        self.txt_boring_no.grid(row=0, column=1, padx=2, pady=2)

        ttk.Label(self.input_frame, text="Sample No:").grid(row=1, column=0, padx=2, pady=2)
        self.txt_sample_no = ttk.Entry(self.input_frame)
        self.txt_sample_no.grid(row=1, column=1, padx=2, pady=2)

        ttk.Label(self.input_frame, text="Sample Depth (m):").grid(row=2, column=0, padx=2, pady=2)
        self.txt_sample_depth = ttk.Entry(self.input_frame)
        self.txt_sample_depth.grid(row=2, column=1, padx=2, pady=2)

        ttk.Label(self.input_frame, text="Soil Description:").grid(row=3, column=0, padx=2, pady=2)
        self.cmb_soil_description = ttk.Combobox(self.input_frame, values=["Clayey Silt", "Silty Sand", "Other"])
        self.cmb_soil_description.grid(row=3, column=1, padx=2, pady=2)

        ttk.Label(self.input_frame, text="Observed Temperature (T₁ °C):").grid(row=4, column=0, padx=2, pady=2)
        self.txt_observed_temperature = ttk.Entry(self.input_frame)
        self.txt_observed_temperature.grid(row=4, column=1, padx=2, pady=2)

        ttk.Label(self.input_frame, text="Weight of pycnometer (gm):").grid(row=5, column=0, padx=2, pady=2)
        self.txt_m1 = ttk.Entry(self.input_frame)
        self.txt_m1.grid(row=5, column=1, padx=2, pady=2)

        ttk.Label(self.input_frame, text="Weight of pycnometer + Soil + Water (gm):").grid(row=6, column=0, padx=2, pady=2)
        self.txt_m4 = ttk.Entry(self.input_frame)
        self.txt_m4.grid(row=6, column=1, padx=2, pady=2)

        ttk.Label(self.input_frame, text="Pycnometer Capacity (ml):").grid(row=7, column=0, padx=2, pady=2)
        self.txt_pycnometer_capacity = ttk.Entry(self.input_frame)
        self.txt_pycnometer_capacity.grid(row=7, column=1, padx=2, pady=2)

        # Buttons
        self.btn_add = ttk.Button(self.input_frame, text="Add to DataGrid", command=self.add_initial_rows)
        self.btn_add.grid(row=8, column=0, padx=2, pady=2)

        self.btn_calculate = ttk.Button(self.input_frame, text="Calculate", command=self.perform_calculation)
        self.btn_calculate.grid(row=8, column=1, padx=2, pady=2)

        # Store multiple samples
        self.samples = []

    def add_initial_rows(self):
        # Collect data from input fields
        boring_no = self.txt_boring_no.get()
        sample_no = self.txt_sample_no.get()
        sample_depth = self.txt_sample_depth.get()
        soil_description = self.cmb_soil_description.get()
        observed_temp = self.txt_observed_temperature.get()
        m1 = self.txt_m1.get()
        m4 = self.txt_m4.get()
        pycnometer_capacity = self.txt_pycnometer_capacity.get()

        # Add sample data to list
        self.samples.append({
            "Boring No": boring_no,
            "Sample No": sample_no,
            "Sample Depth": sample_depth,
            "Soil Description": soil_description,
            "Observed Temperature": observed_temp,
            "M1": m1,
            "M4": m4,
            "Pycnometer Capacity": pycnometer_capacity
        })

        # Clear and add rows to DataGridView
        self.dgv_data.delete(*self.dgv_data.get_children())
        for sample in self.samples:
            self.dgv_data.insert("", "end", values=("Boring No.", "", sample["Boring No"]))
            self.dgv_data.insert("", "end", values=("Sample No.", "", sample["Sample No"]))
            self.dgv_data.insert("", "end", values=("Sample Depth (m)", "", sample["Sample Depth"]))
            self.dgv_data.insert("", "end", values=("Soil Description", "", sample["Soil Description"]))
            self.dgv_data.insert("", "end", values=("Observed Temperature (T₁ °C)", "", sample["Observed Temperature"]))
            self.dgv_data.insert("", "end", values=("Weight of pycnometer (gm)", "M1", sample["M1"]))
            self.dgv_data.insert("", "end", values=("Weight of pycnometer + Soil + Water (gm)", "M4", sample["M4"]))
            self.dgv_data.insert("", "end", values=("Pycnometer Capacity (ml)", "", sample["Pycnometer Capacity"]))
            self.dgv_data.insert("", "end", values=("Weight of pycnometer + Soil (gm)", "M2", 0))
            self.dgv_data.insert("", "end", values=("Specific Gravity of Soil", "GTX", 0))
            self.dgv_data.insert("", "end", values=("Specific Gravity (20°C)", "G20", 0))

    def get_density_at_temperature(self, temp):
        # Density data for temperatures from 15°C to 30.9°C
        density_data = [
            0.9991, 0.99909, 0.99907, 0.99906, 0.99904, 0.99902, 0.99901, 0.99899, 0.99898, 0.99896,
            0.99895, 0.99893, 0.99891, 0.9989, 0.99888, 0.99886, 0.99885, 0.99883, 0.99881, 0.99879,
            0.99878, 0.99876, 0.99874, 0.99872, 0.99871, 0.99869, 0.99867, 0.99865, 0.99863, 0.99862,
            0.9986, 0.99858, 0.99856, 0.99854, 0.99852, 0.9985, 0.99848, 0.99847, 0.99845, 0.99843,
            0.99841, 0.99839, 0.99837, 0.99835, 0.99833, 0.99831, 0.99829, 0.99827, 0.99825, 0.99823,
            0.99821, 0.99819, 0.99816, 0.99814, 0.99812, 0.9981, 0.99808, 0.99806, 0.99802, 0.99799,
            0.99797, 0.99795, 0.99793, 0.99791, 0.99789, 0.99786, 0.99784, 0.99782, 0.9978, 0.99777,
            0.99775, 0.99773, 0.9977, 0.99768, 0.99766, 0.99764, 0.99761, 0.99759, 0.99756, 0.99754,
            0.99752, 0.99749, 0.99747, 0.99745, 0.99742, 0.9974, 0.99737, 0.99735, 0.99732, 0.9973,
            0.99727, 0.99725, 0.99723, 0.9972, 0.99717, 0.99715, 0.99712, 0.9971, 0.99707, 0.99705,
            0.99702, 0.997, 0.99697, 0.99694, 0.99692, 0.99689, 0.99687, 0.99684, 0.99681, 0.99679,
            0.99676, 0.99673, 0.99671, 0.99668, 0.99665, 0.99663, 0.9966, 0.99657, 0.99654, 0.99652,
            0.99649, 0.99646, 0.99643, 0.99641, 0.99638, 0.99635, 0.99632, 0.99629, 0.99627, 0.99624,
            0.99621, 0.99618, 0.99615, 0.99612, 0.99609, 0.99607, 0.99604, 0.99601, 0.99598, 0.99595,
            0.99592, 0.99589, 0.99586, 0.99583, 0.9958, 0.99577, 0.99574, 0.99571, 0.99568, 0.99565,
            0.99562, 0.99559, 0.99556, 0.99553, 0.9955, 0.99547, 0.99544, 0.99541, 0.99538
        ]

        if temp < 15 or temp > 30.9:
            return -1  # Out of range
        index = int((temp - 15) * 10)
        return density_data[index]

    def perform_calculation(self):
        try:
            m1 = float(self.txt_m1.get())
            m4 = float(self.txt_m4.get())
            temperature = float(self.txt_observed_temperature.get())
            pycnometer_capacity = float(self.txt_pycnometer_capacity.get())
        except ValueError:
            messagebox.showerror("Input Error", "Please enter valid numbers for weights, temperature, and capacity.")
            return

        # Determine M2 based on soil description
        soil_description = self.cmb_soil_description.get().strip()
        if soil_description == "Clayey Silt":
            m2 = 40 + m1
        elif soil_description == "Silty Sand":
            m2 = 50 + m1
        else:
            m2 = 35 + m1  # Default soil type value

        # Calculate M3 based on temperature and pycnometer capacity
        density = self.get_density_at_temperature(temperature)
        if density == -1:
            messagebox.showerror("Temperature Error", "Temperature is out of range (15°C to 30.9°C).")
            return
        m3 = m1 + pycnometer_capacity * density

        # Calculate GTX and G20
        denominator = (m2 - m1) + (m3 - m4)
        gtx = (m2 - m1) / denominator 
        correction_factor = self.get_density_at_temperature(20)  # Correction factor at 20°C
        g20 = gtx * correction_factor

        # Update DataGridView
        self.update_data_grid(m1, m2, m3, m4, gtx, g20)

    def update_data_grid(self, m1, m2, m3, m4, gtx, g20):
        # Ensure there are enough rows
        while len(self.dgv_data.get_children()) < 12:
            self.dgv_data.insert("", "end", values=("", "", ""))

        # Update specific rows
        self.dgv_data.item(self.dgv_data.get_children()[5], values=("Weight of pycnometer (gm)", "M1", f"{m1:.2f}"))
        self.dgv_data.item(self.dgv_data.get_children()[6], values=("Weight of pycnometer + Water (gm)", "M3", f"{m3:.2f}"))
        self.dgv_data.item(self.dgv_data.get_children()[7], values=("Weight of pycnometer + Soil + Water (gm)", "M4", f"{m4:.2f}"))
        self.dgv_data.item(self.dgv_data.get_children()[9], values=("Weight of pycnometer + Soil (gm)", "M2", f"{m2:.2f}"))
        self.dgv_data.item(self.dgv_data.get_children()[10], values=("Specific Gravity of Soil", "GTX", f"{gtx:.3f}"))
        self.dgv_data.item(self.dgv_data.get_children()[11], values=("Specific Gravity (20°C)", "G20", f"{g20:.3f}"))

# Run the application
if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()