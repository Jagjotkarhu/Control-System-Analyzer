import streamlit as st # type: ignore
import control as ct # type: ignore
import numpy as np # type: ignore
import plotly.graph_objects as go # type: ignore
from plotly.subplots import make_subplots # type: ignore
from scipy.linalg import expm # type: ignore

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="Control Systems Master Solver",
    page_icon="⚙️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for polished UI
st.markdown("""
    <style>
        .main { background-color: #f8fafc; }
        .stMetric { background-color: #ffffff; padding: 15px; border-radius: 8px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); }
    </style>
""", unsafe_allow_html=True)

# --- CORE ANALYSIS CLASS (1st to Nth Order Support) ---
class TFAnalyzer:
    def __init__(self, num, den):
        self.sys = ct.TransferFunction(num, den)
        den_coeffs = np.array(self.sys.den[0][0], dtype=float)
        
        self.system_order = len(den_coeffs) - 1
        self.poles = ct.poles(self.sys)
        self.zeros = ct.zeros(self.sys)
        
        if self.system_order == 2:
            self.wn = np.sqrt(den_coeffs[-1]) if den_coeffs[-1] > 0 else 0
            self.zeta = den_coeffs[-2] / (2 * self.wn) if self.wn != 0 else 0
            self.wd = self.wn * np.sqrt(abs(1 - self.zeta**2))
        else:
            self.wn = "N/A (Higher Order)"
            self.zeta = "N/A (Higher Order)"
            self.wd = 0
            self._extract_dominant_poles()
    
    def _extract_dominant_poles(self):
        if len(self.poles) > 0:
            sorted_poles = sorted(self.poles, key=lambda p: np.abs(np.real(p)))
            if len(sorted_poles) >= 2:
                dominant_pair = sorted_poles[:2]
                if np.abs(np.imag(dominant_pair[0])) > 0.01:
                    sigma = np.real(dominant_pair[0])
                    omega = np.abs(np.imag(dominant_pair[0]))
                    self.wd = omega
                    self.wn = np.sqrt(sigma**2 + omega**2)
                    self.zeta = sigma / self.wn if self.wn > 0 else 0
                else:
                    self.wn = np.abs(np.real(sorted_poles[0]))
                    self.zeta = 2.0
                    self.wd = 0
    
    def time_domain_metrics(self, target_sys=None):
        sys_to_eval = target_sys if target_sys else self.sys
        t, y = ct.step_response(sys_to_eval, T=np.linspace(0, 20, 3000))
        
        y_final = y[-1] if len(y) > 0 else 1.0
        y_max = np.max(y) if len(y) > 0 else y_final
        mp = ((y_max - y_final) / y_final * 100) if y_final != 0 else 0
        
        try:
            if y_final > 0:
                idx_10 = np.where(y >= 0.1 * y_final)[0]
                idx_90 = np.where(y >= 0.9 * y_final)[0]
                t_rise = (t[idx_90[0]] - t[idx_10[0]]) if len(idx_10) > 0 and len(idx_90) > 0 else 0
            else:
                t_rise = 0
        except:
            t_rise = 0
        
        peak_idx = np.argmax(y) if len(y) > 0 else 0
        t_peak = t[peak_idx] if peak_idx < len(t) else 0
        
        band_2pct = 0.02 * y_final
        try:
            idx_settle = np.where(np.abs(y - y_final) <= band_2pct)[0]
            t_settle = t[idx_settle[0]] if len(idx_settle) > 0 else t[-1]
        except:
            t_settle = 0
        
        return {
            'step_t': t, 'step_y': y,
            'rise_time': t_rise, 'peak_time': t_peak,
            'settling_time': t_settle, 'overshoot': mp,
            'final_value': y_final, 'peak_value': y_max, 'wd': self.wd
        }
    
    def freq_domain_metrics(self, target_sys=None):
        sys_to_eval = target_sys if target_sys else self.sys
        omega = np.logspace(-2, 3, 1000)
        mag, phase, omega = ct.frequency_response(sys_to_eval, omega=omega)
        
        try:
            gm, pm, wgc, wpc = ct.margin(sys_to_eval)
        except:
            gm, pm, wgc, wpc = np.inf, 0, 0, 0
        
        dc_gain = mag[0] if len(mag) > 0 else 1
        mag_db = 20 * np.log10(np.abs(mag) + 1e-10)
        bw_level = mag_db[0] - 3
        bw_idx = np.where(mag_db <= bw_level)[0]
        bandwidth = omega[bw_idx[0]] if len(bw_idx) > 0 else 0
        
        return {
            'mag': mag, 'phase': phase, 'omega': omega,
            'gain_margin': 20 * np.log10(gm) if gm != float('inf') and gm > 0 else np.inf,
            'phase_margin': pm, 'wgc': wgc, 'wpc': wpc,
            'dc_gain': dc_gain, 'bandwidth': bandwidth
        }

# --- SIDEBAR CONFIGURATION ---
st.sidebar.header("⚙️ System Control Panel")

# System Presets for Quick Interactivity
preset = st.sidebar.selectbox(
    "📂 Load System Preset:",
    ["Custom Input", "Standard 2nd Order (Underdamped)", "3rd Order Process Plant", "Unstable System"]
)

if preset == "Standard 2nd Order (Underdamped)":
    default_num, default_den = "25", "1, 6, 25"
elif preset == "3rd Order Process Plant":
    default_num, default_den = "10", "1, 5, 8, 10"
elif preset == "Unstable System":
    default_num, default_den = "1", "1, -2, 5"
else:
    default_num, default_den = "25", "1, 6, 25"

num_input = st.sidebar.text_input("Numerator Coefficients", default_num)
den_input = st.sidebar.text_input("Denominator Coefficients", default_den)

st.sidebar.divider()

# Analysis Domain & Modules
st.sidebar.subheader("📦 Active Modules")
show_overview = st.sidebar.checkbox("📊 System Overview", value=True)
show_metrics = st.sidebar.checkbox("📉 Detailed Metrics", value=True)
show_poles = st.sidebar.checkbox("🎯 Pole-Zero Map", value=True)
show_ctrl = st.sidebar.checkbox("🔧 Controllability & Pole Placement")
show_stm = st.sidebar.checkbox("⏱️ State Transition Matrix")
show_comp = st.sidebar.checkbox("🎛️ Compensator Tuning")

# --- MAIN APP EXECUTION ---
try:
    num = [float(x.strip()) for x in num_input.split(',')]
    den = [float(x.strip()) for x in den_input.split(',')]
    analyzer = TFAnalyzer(num, den)
    sys_order = analyzer.system_order

    st.title("🎯 Control Systems Master Workspace")
    st.markdown(f"**Active Transfer Function:** Order `{sys_order}` System | **Poles:** `{len(analyzer.poles)}`")

    # CONDITIONAL SIDEBAR CONFIGS FOR MODULES
    if show_ctrl:
        st.sidebar.divider()
        st.sidebar.subheader("🎯 Pole Placement Config")
        req_zeta = st.sidebar.slider("Target Damping (ζ)", 0.1, 1.0, 0.707)
        req_wn = st.sidebar.slider("Target Freq (ωₙ)", 1.0, 50.0, 10.0)
        rp = -req_zeta * req_wn
        ip = req_wn * np.sqrt(abs(1 - req_zeta**2))
        
        default_poles = []
        if sys_order == 1:
            default_poles = [f"{rp:.2f}"]
        elif sys_order == 2:
            default_poles = [f"{rp:.2f}+{ip:.2f}j", f"{rp:.2f}-{ip:.2f}j"]
        else:
            default_poles.append(f"{rp:.2f}+{ip:.2f}j")
            default_poles.append(f"{rp:.2f}-{ip:.2f}j")
            for i in range(sys_order - 2):
                default_poles.append(f"{rp - (i+1):.2f}")
        poles_input = st.sidebar.text_input(f"Enter {sys_order} poles:", ", ".join(default_poles))

    if show_stm:
        st.sidebar.divider()
        st.sidebar.subheader("⏱️ State Transition Config")
        t_val = st.sidebar.slider("Evaluation Time (t)", 0.0, 10.0, 1.0, 0.1)

    if show_comp:
        st.sidebar.divider()
        st.sidebar.subheader("🎛️ Compensator Design")
        comp_type = st.sidebar.radio("Compensator Type", ["Lead", "Lag"], horizontal=True)
        K_val = st.sidebar.slider("Gain (K)", 0.1, 50.0, 10.0)
        if comp_type == "Lead":
            z_val = st.sidebar.slider("Zero (z)", 0.1, 20.0, 2.0)
            p_val = st.sidebar.slider("Pole (p)", z_val + 0.1, 50.0, 10.0)
        else:
            p_val = st.sidebar.slider("Pole (p)", 0.1, 20.0, 1.0)
            z_val = st.sidebar.slider("Zero (z)", p_val + 0.1, 50.0, 5.0)

    # ===== 1. SYSTEM OVERVIEW =====
    if show_overview:
        st.header("📊 System Overview")
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("System Order", f"{sys_order}")
        wn_str = f"{analyzer.wn:.3f} rad/s" if isinstance(analyzer.wn, (int, float)) else analyzer.wn
        c2.metric("Natural Freq (ωₙ)", wn_str)
        zeta_str = f"{analyzer.zeta:.3f}" if isinstance(analyzer.zeta, (int, float)) else analyzer.zeta
        c3.metric("Damping Ratio (ζ)", zeta_str)
        c4.metric("Total Poles", len(analyzer.poles))

        t_td, y_td = ct.step_response(analyzer.sys, T=np.linspace(0, 10, 500))
        fd_data = analyzer.freq_domain_metrics()

        col_p1, col_p2 = st.columns(2)
        with col_p1:
            fig_step = go.Figure(go.Scatter(x=t_td, y=y_td, mode='lines', line=dict(color='#2563eb', width=2.5)))
            fig_step.update_layout(title="Step Response", xaxis_title="Time (s)", yaxis_title="Output", template="plotly_white")
            st.plotly_chart(fig_step, use_container_width=True)
        with col_p2:
            fig_bode = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.1)
            fig_bode.add_trace(go.Scatter(x=fd_data['omega'], y=20*np.log10(np.abs(fd_data['mag']) + 1e-10), line=dict(color='#d97706', width=2)), row=1, col=1)
            fig_bode.add_trace(go.Scatter(x=fd_data['omega'], y=np.degrees(fd_data['phase']), line=dict(color='#16a34a', width=2)), row=2, col=1)
            fig_bode.update_xaxes(type="log", row=2, col=1)
            fig_bode.update_layout(title="Frequency Response (Bode)", template="plotly_white", showlegend=False)
            st.plotly_chart(fig_bode, use_container_width=True)
        st.divider()

    # ===== 2. DETAILED METRICS =====
    if show_metrics:
        st.header("📉 Detailed Engineering Metrics")
        tab1, tab2 = st.tabs(["⏱️ Time Domain", "📊 Frequency Domain"])
        
        with tab1:
            td_data = analyzer.time_domain_metrics()
            m1, m2, m3, m4 = st.columns(4)
            m1.metric("Rise Time (tᵣ)", f"{td_data['rise_time']:.4f} s")
            m2.metric("Peak Time (tₚ)", f"{td_data['peak_time']:.4f} s")
            m3.metric("Overshoot (Mₚ)", f"{td_data['overshoot']:.2f}%")
            m4.metric("Settling Time (tₛ)", f"{td_data['settling_time']:.4f} s")
            
        with tab2:
            fd_data = analyzer.freq_domain_metrics()
            m1, m2, m3, m4 = st.columns(4)
            gm_val = fd_data['gain_margin']
            m1.metric("Gain Margin", f"{gm_val:.2f} dB" if gm_val != np.inf else "∞")
            m2.metric("Phase Margin", f"{fd_data['phase_margin']:.2f}°")
            m3.metric("Bandwidth", f"{fd_data['bandwidth']:.3f} rad/s")
            m4.metric("DC Gain", f"{20*np.log10(fd_data['dc_gain']):.2f} dB")
        st.divider()

    # ===== 3. POLE-ZERO MAP =====
    if show_poles:
        st.header("🎯 Pole-Zero Map (s-plane)")
        fig_pz = go.Figure()
        if len(analyzer.poles) > 0:
            fig_pz.add_trace(go.Scatter(x=np.real(analyzer.poles), y=np.imag(analyzer.poles), mode='markers', marker=dict(size=14, color='red', symbol='x'), name='Poles'))
        if len(analyzer.zeros) > 0:
            fig_pz.add_trace(go.Scatter(x=np.real(analyzer.zeros), y=np.imag(analyzer.zeros), mode='markers', marker=dict(size=14, color='blue', symbol='circle-open'), name='Zeros'))
        fig_pz.add_vline(x=0, line_dash="dash", line_color="gray")
        fig_pz.update_layout(title="Pole-Zero Configuration", xaxis_title="Real (σ)", yaxis_title="Imaginary (ω)", template="plotly_white", width=700, height=500)
        fig_pz.update_yaxes(scaleanchor="x", scaleratio=1)
        st.plotly_chart(fig_pz, use_container_width=True)
        st.divider()

    # ===== 4. CONTROLLABILITY & POLE PLACEMENT =====
    if show_ctrl:
        st.header("🔧 Controllability & State Feedback Assignment")
        sys_ss = ct.tf2ss(analyzer.sys)
        A, B = sys_ss.A, sys_ss.B
        Cm = ct.ctrb(A, B)
        is_controllable = np.linalg.matrix_rank(Cm) == sys_order
        
        c1, c2 = st.columns(2)
        c1.metric("System Order", sys_order)
        c2.metric("Controllability", "✅ Fully Controllable" if is_controllable else "❌ Uncontrollable")
        
        if is_controllable:
            try:
                desired_poles = [complex(p) for p in poles_input.replace(' ', '').replace('i', 'j').split(',')]
                if len(desired_poles) == sys_order:
                    K = ct.place(A, B, desired_poles)
                    st.success("✅ State Feedback Gain Matrix (K) Calculated:")
                    st.dataframe(np.round(K, 4), use_container_width=True)
                else:
                    st.warning(f"⚠️ Provide exactly {sys_order} poles.")
            except Exception as e:
                st.error(f"❌ Parse error in poles format: {e}")
        st.divider()

    # ===== 5. STATE TRANSITION MATRIX =====
    if show_stm:
        st.header(f"⏱️ State Transition Matrix Φ(t) @ t = {t_val}s")
        A = ct.tf2ss(analyzer.sys).A
        stm = expm(A * t_val)
        c1, c2 = st.columns(2)
        with c1:
            st.write("**System Matrix A:**")
            st.dataframe(np.round(A, 4), use_container_width=True)
        with c2:
            st.write(f"**Transition Matrix Φ({t_val}):**")
            st.dataframe(np.round(stm, 4), use_container_width=True)
        st.divider()

    # ===== 6. COMPENSATOR DESIGN =====
    if show_comp:
        st.header(f"🎛️ Live {comp_type} Compensator Tuning")
        Gc = ct.TransferFunction([K_val, K_val * z_val], [1, p_val])
        L = ct.series(Gc, analyzer.sys)
        T = ct.feedback(L, 1)
        
        fd_comp = analyzer.freq_domain_metrics(L)
        td_comp = analyzer.time_domain_metrics(T)
        
        c1, c2, c3 = st.columns(3)
        c1.metric("Compensated Phase Margin", f"{fd_comp['phase_margin']:.2f}°")
        c2.metric("Compensated Gain Margin", f"{fd_comp['gain_margin']:.2f} dB" if fd_comp['gain_margin'] != np.inf else "∞")
        c3.metric("Type", comp_type)
        
        fig_comp = go.Figure()
        fig_comp.add_trace(go.Scatter(x=td_comp['step_t'], y=td_comp['step_y'], mode='lines', line=dict(color='#7c3aed', width=2.5), name='Compensated System'))
        fig_comp.update_layout(title="Compensated Closed-Loop Step Response", xaxis_title="Time (s)", yaxis_title="Output", template="plotly_white")
        st.plotly_chart(fig_comp, use_container_width=True)

except Exception as e:
    st.error(f"❌ Error in system configuration: {str(e)}")
    st.info("💡 Ensure coefficients are comma-separated numbers (e.g., Numerator: '10', Denominator: '1, 2, 10').")