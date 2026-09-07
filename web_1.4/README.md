# Control Systems Master Workspace 🎯

A professional-grade, interactive web dashboard for control systems engineering. Built with **Streamlit** and the **Python Control Systems Library (`python-control`)**, this tool allows engineers and students to analyze transfer functions of any order, design state-space controllers, and tune live compensators in real-time without writing a single line of code.

## ✨ Features

- **N-th Order System Support:** Dynamically analyzes systems from 1st to N-th order, automatically detecting dominant poles and calculating accurate physical metrics.
- **Interactive Dashboards:** Instant reactivity. Change a slider, and the Bode plots, step responses, and metrics update immediately.
- **Time & Frequency Domain Metrics:** 
  - *Time Domain:* Rise time, peak time, settling time, and % overshoot.
  - *Frequency Domain:* Gain margin, phase margin, bandwidth, and DC gain.
- **State-Space & Pole Placement:** Converts transfer functions to state-space (A, B, C, D), checks controllability matrices, and calculates state-feedback gain (K) for exact pole placement.
- **State Transition Matrix:** Evaluates system state evolution at any user-defined time.
- **Live Compensator Tuning:** Design and visualize Lead/Lag compensators with live ghost-plot comparisons against the uncompensated plant.
- **System Presets:** One-click loading for classic 2nd-order, 3rd-order process plants, and unstable systems for quick experimentation.

## 🛠️ Tech Stack

- **Frontend:** [Streamlit](https://streamlit.io/)
- **Control Theory Engine:** [python-control](https://python-control.readthedocs.io/)
- **Mathematics:** NumPy, SciPy
- **Data Visualization:** Plotly Graph Objects

## 🚀 Installation & Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/yourusername/control-systems-workspace.git
   cd control-systems-workspace
   ```

2. **Create a virtual environment (Recommended):**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scriptsctivate`
   ```

3. **Install the dependencies:**
   Ensure you have the required libraries installed. You can create a `requirements.txt` file with the following contents:
   ```text
   streamlit
   control
   numpy
   scipy
   plotly
   ```
   Then run:
   ```bash
   pip install -r requirements.txt
   ```

## 💻 Usage

Run the Streamlit application from your terminal:

```bash
streamlit run app.py
```

The application will automatically open in your default web browser at `http://localhost:8501/`.

## 🗺️ Roadmap (Future Enhancements)
- Root Locus & Nyquist Stability plots
- Live PID Controller tuning module
- LQR (Linear Quadratic Regulator) optimal control
- Discretization module (z-domain analysis)
- Observability checks and Luenberger Observer design

## 📄 License
This project is open-source and available under the MIT License.
