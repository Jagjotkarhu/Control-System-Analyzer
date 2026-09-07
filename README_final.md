# 🎛️ Control Systems Master Workspace

> 🚀 **An interactive web dashboard for Control Systems engineering. Analyze N-th order transfer functions, tune live compensators, and design state-space controllers in real-time.**

The **Control Systems Master Workspace** is a reactive, no-code engineering solver. Drop in any continuous-time transfer function (1st to N-th order) and instantly generate Bode plots, extract precise time/frequency metrics, verify controllability, and calculate state-feedback gain matrices. Whether you are placing dominant poles or tuning a live Lead/Lag compensator, the math and visuals update in real-time.

---

## ✨ Key Features
* **Instant Analysis:** Live step responses, Bode plots, and Pole-Zero maps.
* **N-th Order Ready:** Dynamic extraction of dominant poles and physical metrics for any system order.
* **Modern State-Space:** Controllability checks, transition matrices Φ(t), and Ackermann pole placement (K matrix).
* **Live Tuning:** Interactive sliders for Lead/Lag compensator design with instant ghost-plot comparisons.

---

## ⚙️ Essentials & Installation

### Prerequisites
Make sure you have Python 3.8 or newer installed on your machine. You will also need `pip` to install the required packages.

### Quick Start
1. **Clone the repository:**
   ```bash
   git clone https://github.com/yourusername/control-systems-workspace.git
   cd control-systems-workspace
   ```

2. **Create a Virtual Environment (Optional but recommended):**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install Dependencies:**
   Install the required libraries via `requirements.txt`:
   ```bash
   pip install -r requirements.txt
   ```
   *(Ensure your requirements file includes: `streamlit`, `control`, `numpy`, `scipy`, `plotly`)*

4. **Run the Application:**
   Launch the Streamlit server:
   ```bash
   streamlit run app.py
   ```
   The dashboard will automatically open in your default browser at `http://localhost:8501`.

---

## 📈 Project Evolution (Changelog)

This tool has been built iteratively to handle increasingly complex control theory mathematics:

* **Version 1: The Basic Analyzer** 
  Established the core architecture. Parsed numerator/denominator inputs and rendered basic time-domain step responses using Plotly.
* **Version 2: Frequency Domain Expansion** 
  Bridged the gap between domains by implementing logarithmic Bode plots (magnitude and phase) alongside the step response.
* **Version 3: State-Space & Advanced Mathematics** 
  Added state-space conversion (A, B, C, D), dynamic controllability rank evaluation, and state transition matrix Φ(t) calculations via `scipy.linalg.expm`.
* **Version 4: The Master Solver (Current Build)** 
  Rebuilt the math engine to handle N-th order systems. Added granular engineering metrics (Rise Time, Overshoot, Gain/Phase Margins), dynamic dominant pole extraction, and live Lead/Lag compensator tuning. *(Note: Active development is ongoing. More features coming soon!)*

---

## 🛠️ Tech Stack
* **Frontend UI:** [Streamlit](https://streamlit.io/)
* **Control Theory Engine:** [python-control](https://python-control.readthedocs.io/)
* **Math & Scientific Computing:** NumPy, SciPy
* **Data Visualization:** Plotly Graph Objects

---

## 🤝 Contributing
Contributions, issues, and feature requests are welcome! 
If you want to add new modules (like Root Locus, Nyquist plots, or PID tuning), feel free to fork the repository and submit a pull request.

## 📝 License
This project is open-source and available under the [MIT License](LICENSE).
