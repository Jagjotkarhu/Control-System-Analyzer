import streamlit as st  # type: ignore[import-not-found]
import control as ct # type: ignore[import-not-found]
import numpy as np # type: ignore[import-not-found]
import plotly.graph_objects as go # type: ignore[import-not-found]
from scipy.linalg import expm # type: ignore[import-not-found]
from plotly.subplots import make_subplots # type: ignore[import-not-found]

# --- 1. CORE ANALYSIS CLASS ---
class TFAnalyzer:
    def __init__(self, num, den):
        self.sys = ct.TransferFunction(num, den)
        den_coeffs = self.sys.den[0][0]
        
        self.wn = np.sqrt(den_coeffs[-1]) if len(den_coeffs) > 2 else 0
        self.zeta = den_coeffs[-2] / (2 * self.wn) if self.wn != 0 and len(den_coeffs) > 1 else 0
        self.wd = self.wn * np.sqrt(abs(1 - self.zeta**2))
        self.poles = ct.poles(self.sys)
    
    def time_domain(self, system=None):
        target_sys = system if system else self.sys
        t, y = ct.step_response(target_sys)
        return t, y
    
    def freq_domain(self, system=None):
        target_sys = system if system else self.sys
        omega = np.logspace(-2, 3, 1000)
        mag, phase, omega = ct.frequency_response(target_sys, omega=omega)
        gm, pm, wgc, wpc = ct.margin(target_sys)
        return mag, phase, omega, gm, pm

# --- 2. STREAMLIT UI SETUP ---
st.set_page_config(page_title="Control Systems Master Solver", layout="wide")
st.title("Control Systems Master Solver")

# ==========================================
# SIDEBAR: LIVE CONFIGURATION
# ==========================================
st.sidebar.header("1. Define Plant G(s)")
num_input = st.sidebar.text_input("Numerator Coefficients", "10")
den_input = st.sidebar.text_input("Denominator Coefficients", "1, 2, 0")

st.sidebar.divider()
st.sidebar.header("2. Enable Modules")

# Use checkboxes so the user can select multiple simultaneously
show_simple = st.sidebar.checkbox("📊 Simple Calculations & Plots", value=True)
show_ctrl = st.sidebar.checkbox("🎯 Controllability & Pole Placement")
show_stm = st.sidebar.checkbox("⏱️ State Transition Matrix")
show_comp = st.sidebar.checkbox("🎛️ Interactive Compensator Tuning")

st.sidebar.divider()

# Conditional Sidebar Inputs based on active checkboxes
if show_ctrl:
    st.sidebar.subheader("Target Pole Specs")
    req_zeta = st.sidebar.slider("Target Damping (ζ)", 0.1, 1.0, 0.707)
    req_wn = st.sidebar.slider("Target Freq (ωₙ)", 1.0, 50.0, 10.0)
    
    rp = -req_zeta * req_wn
    ip = req_wn * np.sqrt(abs(1 - req_zeta**2))
    poles_input = st.sidebar.text_input("Poles to place:", f"{rp:.2f}+{ip:.2f}j, {rp:.2f}{'-' if -ip < 0 else '+'}{abs(-ip):.2f}j")

if show_stm:
    st.sidebar.subheader("Transition Matrix Time")
    t_val = st.sidebar.slider("Time (t) seconds", 0.0, 10.0, 1.0, 0.1)

if show_comp:
    st.sidebar.subheader("Compensator Parameters")
    comp_type = st.sidebar.radio("Type", ["Lead", "Lag"])
    K_val = st.sidebar.slider("Gain (K)", 0.1, 50.0, 10.0)
    
    if comp_type == "Lead":
        z_val = st.sidebar.slider("Zero (z)", 0.1, 20.0, 2.0)
        p_val = st.sidebar.slider("Pole (p)", z_val + 0.1, 50.0, 10.0) # Pole must be > Zero for Lead
    else:
        p_val = st.sidebar.slider("Pole (p)", 0.1, 20.0, 1.0)
        z_val = st.sidebar.slider("Zero (z)", p_val + 0.1, 50.0, 5.0) # Zero must be > Pole for Lag

# ==========================================
# MAIN EXECUTION (Runs live as inputs change)
# ==========================================
try:
    num = [float(x.strip()) for x in num_input.split(',')]
    den = [float(x.strip()) for x in den_input.split(',')]
    analyzer = TFAnalyzer(num, den)

    # MODULE 1: SIMPLE CALCULATIONS
    if show_simple:
        st.header("📊 System Overview & Calculations")
        mag, phase, omega, gm, pm = analyzer.freq_domain()
        
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Natural Freq (ωₙ)", f"{analyzer.wn:.2f} rad/s")
        c2.metric("Damping Ratio (ζ)", f"{analyzer.zeta:.2f}")
        c3.metric("Phase Margin", f"{pm:.2f}°" if not np.isnan(pm) else "N/A")
        c4.metric("Gain Margin", f"{20*np.log10(gm):.2f} dB" if gm != float('inf') and gm > 0 else "Infinite")

        t, y = analyzer.time_domain()
        
        plot_col1, plot_col2 = st.columns(2)
        with plot_col1:
            fig_step = go.Figure(go.Scatter(x=t, y=y, mode='lines', line=dict(color='blue')))
            fig_step.update_layout(title="Step Response", template="plotly_white", margin=dict(t=40, b=10, l=10, r=10))
            st.plotly_chart(fig_step, use_container_width=True)
            
        with plot_col2:
            fig_bode = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.1)
            fig_bode.add_trace(go.Scatter(x=omega, y=20*np.log10(mag), line=dict(color='orange')), row=1, col=1)
            fig_bode.add_trace(go.Scatter(x=omega, y=np.degrees(phase), line=dict(color='green')), row=2, col=1)
            fig_bode.update_xaxes(type="log", row=2, col=1)
            fig_bode.update_layout(title="Bode Plot", showlegend=False, template="plotly_white", margin=dict(t=40, b=10, l=10, r=10))
            st.plotly_chart(fig_bode, use_container_width=True)
        st.divider()

    # MODULE 2: CONTROLLABILITY & POLE PLACEMENT
    if show_ctrl:
        st.header("🎯 Controllability & Pole Placement")
        sys_ss = ct.tf2ss(analyzer.sys)
        A, B = sys_ss.A, sys_ss.B
        sys_order = A.shape[0]

        Cm = ct.ctrb(A, B)
        is_controllable = np.linalg.matrix_rank(Cm) == sys_order
        st.metric("Controllability", "Fully Controllable" if is_controllable else "Uncontrollable")
        
        clean_input = poles_input.replace(' ', '').replace('i', 'j')
        try:
            desired_poles = [complex(p) for p in clean_input.split(',')]
            if len(desired_poles) == sys_order and is_controllable:
                K = ct.place(A, B, desired_poles)
                st.success("Calculated State Feedback Gain Matrix (K):")
                st.dataframe(np.round(K, 4))
            else:
                st.warning(f"Please provide exactly {sys_order} poles to calculate K matrix.")
        except:
            st.error("Invalid pole format. Use 'a+bj' formatting.")
        st.divider()

    # MODULE 3: STATE TRANSITION
    if show_stm:
        st.header(f"⏱️ State Transition Matrix Φ(t) at t={t_val}s")
        A = ct.tf2ss(analyzer.sys).A
        stm = expm(A * t_val)
        
        c1, c2 = st.columns(2)
        with c1:
            st.write("**System Matrix A:**")
            st.dataframe(np.round(A, 4))
        with c2:
            st.write("**Transition Matrix Φ(t):**")
            st.dataframe(np.round(stm, 4))
        st.divider()

    # MODULE 4: INTERACTIVE COMPENSATOR
    if show_comp:
        st.header(f"🎛️ Live {comp_type} Compensator Design")
        
        # Create Compensator Gc(s) = K(s+z)/(s+p)
        Gc = ct.TransferFunction([K_val, K_val * z_val], [1, p_val])
        L = ct.series(Gc, analyzer.sys) # Open Loop
        T = ct.feedback(L, 1)           # Closed Loop

        mag_L, phase_L, omega_L, gm_L, pm_L = analyzer.freq_domain(L)
        t_T, y_T = analyzer.time_domain(T)

        st.info(f"**Current Compensator Gc(s):** {K_val} * (s + {z_val:.2f}) / (s + {p_val:.2f})")
        st.metric("New Compensated Phase Margin", f"{pm_L:.2f}°" if not np.isnan(pm_L) else "N/A")

        c1, c2 = st.columns(2)
        with c1:
            fig_comp_step = go.Figure()
            # If simple is checked, grab the original step for comparison
            if show_simple: 
                t_orig, y_orig = analyzer.time_domain(ct.feedback(analyzer.sys, 1))
                fig_comp_step.add_trace(go.Scatter(x=t_orig, y=y_orig, mode='lines', name='Original', line=dict(dash='dot', color='gray')))
            fig_comp_step.add_trace(go.Scatter(x=t_T, y=y_T, mode='lines', name='Compensated', line=dict(color='purple')))
            fig_comp_step.update_layout(title="Closed-Loop Step Response Comparison", template="plotly_white")
            st.plotly_chart(fig_comp_step, use_container_width=True)

        with c2:
            fig_comp_bode = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.1)
            if show_simple:
                mag_orig, phase_orig, _, _, _ = analyzer.freq_domain(analyzer.sys)
                fig_comp_bode.add_trace(go.Scatter(x=omega_L, y=20*np.log10(mag_orig), line=dict(dash='dot', color='gray'), name="Orig Mag"), row=1, col=1)
                fig_comp_bode.add_trace(go.Scatter(x=omega_L, y=np.degrees(phase_orig), line=dict(dash='dot', color='gray'), name="Orig Phase"), row=2, col=1)
            
            fig_comp_bode.add_trace(go.Scatter(x=omega_L, y=20*np.log10(mag_L), line=dict(color='orange'), name="Comp Mag"), row=1, col=1)
            fig_comp_bode.add_trace(go.Scatter(x=omega_L, y=np.degrees(phase_L), line=dict(color='green'), name="Comp Phase"), row=2, col=1)
            fig_comp_bode.update_xaxes(type="log", row=2, col=1)
            fig_comp_bode.update_layout(title="Open-Loop Bode Plot Comparison", template="plotly_white", showlegend=False)
            st.plotly_chart(fig_comp_bode, use_container_width=True)

except Exception as e:
    st.error(f"Please check your input values. Error: {e}")