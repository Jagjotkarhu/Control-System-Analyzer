try:
    import control as ct  # type: ignore[import-not-found]
    import streamlit as st  # type: ignore[import-not-found]
    import plotly.graph_objects as go  # type: ignore[import-not-found]
    from plotly.subplots import make_subplots  # type: ignore[import-not-found]
    import numpy as np  # type: ignore[import-not-found]
except ImportError:
    ct = None
    st = None
    go = None
    make_subplots = None

st.title("Control Systems Dashboard")


# --- 1. YOUR ANALYSIS CLASS (Unchanged) ---
class TFAnalyzer:
    def __init__(self, num, den):
        self.sys = ct.TransferFunction(num, den)
        self.extract_params()
    
    def extract_params(self):
        den = self.sys.den[0][0]
        self.wn = np.sqrt(den[-1])
        self.zeta = den[-2] / (2 * self.wn) if self.wn != 0 else 0
        self.wd = self.wn * np.sqrt(abs(1 - self.zeta**2))
        self.poles = ct.poles(self.sys)
    
    def time_domain(self):
        # Prevent division by zero if zeta is 0 or negative
        zeta_safe = self.zeta if self.zeta > 0 else 0.01
        t = np.linspace(0, 5 / (zeta_safe * self.wn), 1000)
        t, y = ct.step_response(self.sys, T=t)
        
        y_final = y[-1]
        y_max = np.max(y)
        mp = ((y_max - y_final) / y_final) * 100 if y_final != 0 else 0
        
        idx_10 = np.where(y >= 0.1*y_final)[0][0] if y_final > 0 else 0
        idx_90 = np.where(y >= 0.9*y_final)[0][0] if y_final > 0 else len(y)-1
        tr = t[idx_90] - t[idx_10]
        
        tp = np.pi / self.wd if self.wd > 0 else 0
        ts = 4 / (self.zeta * self.wn) if (self.zeta * self.wn) > 0 else float('inf')
        
        return {
            'step_t': t, 'step_y': y,
            'rise_time': tr, 'peak_time': tp, 'settling_time': ts,
            'overshoot': mp, 'final_value': y_final
        }
    
    def freq_domain(self):
        omega = np.logspace(-2, 3, 1000)
        mag, phase, omega = ct.frequency_response(self.sys, omega=omega)
        gm, pm, wgc, wpc = ct.margin(self.sys)
        
        gm_db = 20 * np.log10(gm) if gm != float('inf') else float('inf')
        
        return {
            'mag': mag, 'phase': np.degrees(phase), 'omega': omega,
            'gain_margin': gm_db, 'phase_margin': pm,
            'wgc': wgc, 'wpc': wpc
        }

# --- 2. STREAMLIT UI DESIGN ---
st.set_page_config(page_title="Control Systems Analyzer", layout="wide")

st.title("Control Systems Analysis Dashboard")
st.write("Analyze transfer functions, stability margins, time-domain metrics, and frequency responses interactively.")

# Sidebar Inputs
st.sidebar.header("System Configuration")
num_input = st.sidebar.text_input("Numerator Coefficients (comma-separated)", "25")
den_input = st.sidebar.text_input("Denominator Coefficients (comma-separated)", "1, 6, 25")

try:
    # Parse string inputs into float lists
    num = [float(x.strip()) for x in num_input.split(',')]
    den = [float(x.strip()) for x in den_input.split(',')]
    
    # Initialize your Analyzer class
    analyzer = TFAnalyzer(num, den)
    td = analyzer.time_domain()
    fd = analyzer.freq_domain()

    # --- TOP METRICS SECTION ---
    st.subheader("System Parameters & Overview")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Natural Freq (ωₙ)", f"{analyzer.wn:.2f} rad/s")
    col2.metric("Damping Ratio (ζ)", f"{analyzer.zeta:.2f}")
    col3.metric("Phase Margin", f"{fd['phase_margin']:.2f}°" if not np.isnan(fd['phase_margin']) else "N/A")
    
    gm_display = f"{fd['gain_margin']:.2f} dB" if fd['gain_margin'] != float('inf') else "Infinite (Stable)"
    col4.metric("Gain Margin", gm_display)

    # Display Poles safely
    poles_str = ", ".join([f"{p.real:.2f} + {p.imag:.2f}j" if p.imag != 0 else f"{p.real:.2f}" for p in analyzer.poles])
    st.info(f"**System Poles:** [{poles_str}]")

    # --- TABS FOR PLOTS ---
    tab1, tab2, tab3 = st.tabs(["Time Domain (Step Response)", "Frequency Domain (Bode Plot)", "Pole-Zero Map"])

    with tab1:
        st.subheader("Step Response Performance")
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Overshoot", f"{td['overshoot']:.2f}%")
        m2.metric("Rise Time", f"{td['rise_time']:.3f} s")
        m3.metric("Peak Time", f"{td['peak_time']:.3f} s")
        m4.metric("Settling Time (2%)", f"{td['settling_time']:.3f} s")

        # Plotly Step Response
        fig_step = go.Figure()
        fig_step.add_trace(go.Scatter(x=td['step_t'], y=td['step_y'], mode='lines', name='Step Response', line=dict(color='blue', width=2)))
        fig_step.update_layout(title="Closed-Loop Step Response", xaxis_title="Time (seconds)", yaxis_title="Amplitude", template="plotly_white")
        st.plotly_chart(fig_step, use_container_width=True)

    with tab2:
        st.subheader("Bode Frequency Response")
        
        # Plotly Bode Plot (Magnitude & Phase stacked)
        fig_bode = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.1,
                                 subplot_names=("Magnitude (dB)", "Phase (Degrees)"))

        fig_bode.add_trace(go.Scatter(x=fd['omega'], y=20*np.log10(fd['mag']), mode='lines', name='Magnitude', line=dict(color='orange')), row=1, col=1)
        fig_bode.add_trace(go.Scatter(x=fd['omega'], y=fd['phase'], mode='lines', name='Phase', line=dict(color='green')), row=2, col=1)

        fig_bode.update_xaxes(type="log", title_text="Frequency (rad/s)", row=2, col=1)
        fig_bode.update_yaxes(title_text="Magnitude (dB)", row=1, col=1)
        fig_bode.update_yaxes(title_text="Phase (deg)", row=2, col=1)
        fig_bode.update_layout(height=600, template="plotly_white", showlegend=False)

        st.plotly_chart(fig_bode, use_container_width=True)

    with tab3:
        st.subheader("Pole-Zero Map (s-plane)")
        
        p_real = [p.real for p in analyzer.poles]
        p_imag = [p.imag for p in analyzer.poles]
        
        zeros = ct.zeros(analyzer.sys)
        z_real = [z.real for z in zeros] if len(zeros) > 0 else []
        z_imag = [z.imag for z in zeros] if len(zeros) > 0 else []

        fig_pz = go.Figure()
        # Plot Poles (X markers)
        fig_pz.add_trace(go.Scatter(x=p_real, y=p_imag, mode='markers', marker=dict(symbol='x', size=12, color='red'), name='Poles'))
        # Plot Zeros (O markers) if any exist
        if len(zeros) > 0:
            fig_pz.add_trace(go.Scatter(x=z_real, y=z_imag, mode='markers', marker=dict(symbol='circle-open', size=12, color='blue'), name='Zeros'))

        fig_pz.update_layout(title="Pole-Zero Map", xaxis_title="Real Axis", yaxis_title="Imaginary Axis", template="plotly_white")
        fig_pz.add_hline(y=0, line_dash="dash", line_color="gray")
        fig_pz.add_vline(x=0, line_dash="dash", line_color="gray")
        st.plotly_chart(fig_pz, use_container_width=True)

except Exception as e:
    st.error(f"Error parsing coefficients or running analysis: {e}")

