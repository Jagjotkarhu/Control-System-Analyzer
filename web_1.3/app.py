import streamlit as st # type: ignore #
import control as ct # type: ignore
import numpy as np # type: ignore
import plotly.graph_objects as go # type: ignore
from plotly.subplots import make_subplots # type: ignore
from scipy.linalg import expm # type: ignore
from scipy.optimize import fminbound # type: ignore

# --- 1. CORE ANALYSIS CLASS (ENHANCED & DEBUGGED) ---
class TFAnalyzer:
    def __init__(self, num, den):
        """
        Initialize Transfer Function and extract parameters
        num: numerator coefficients
        den: denominator coefficients
        """
        self.sys = ct.TransferFunction(num, den)
        den_coeffs = self.sys.den[0][0]
        
        # Extract ωₙ and ζ from standard 2nd order form
        self.wn = np.sqrt(den_coeffs[-1]) if len(den_coeffs) > 2 else 0
        self.zeta = den_coeffs[-2] / (2 * self.wn) if self.wn != 0 and len(den_coeffs) > 1 else 0
        self.wd = self.wn * np.sqrt(abs(1 - self.zeta**2))
        self.poles = ct.poles(self.sys)
        self.zeros = ct.zeros(self.sys)
    
    def time_domain_metrics(self, target_sys=None):
        """
        Calculate all time domain parameters from step response
        Returns: dict with tr, tp, ts, Mp, y_final, peak_value
        """
        sys_to_eval = target_sys if target_sys else self.sys
        t, y = ct.step_response(sys_to_eval, T=np.linspace(0, 10, 2000))
        
        # Steady-state value
        y_final = y[-1] if len(y) > 0 else 1.0
        
        # Peak value and overshoot (Mp)
        y_max = np.max(y) if len(y) > 0 else y_final
        mp = ((y_max - y_final) / y_final * 100) if y_final != 0 else 0
        
        # Rise time (10% to 90%)
        try:
            if y_final > 0:
                idx_10 = np.where(y >= 0.1 * y_final)[0]
                idx_90 = np.where(y >= 0.9 * y_final)[0]
                t_rise = (t[idx_90[0]] - t[idx_10[0]]) if len(idx_10) > 0 and len(idx_90) > 0 else 0
            else:
                t_rise = 0
        except:
            t_rise = 0
        
        # Peak time (via formula: tp = π/ωd)
        t_peak = (np.pi / self.wd) if self.wd > 0 and self.zeta < 1 else 0
        
        # Settling time (2% criterion: ts = 4/(ζ*ωₙ))
        t_settle = (4 / (self.zeta * self.wn)) if self.zeta > 0 and self.wn > 0 else 0
        
        return {
            'step_t': t,
            'step_y': y,
            'rise_time': t_rise,
            'peak_time': t_peak,
            'settling_time': t_settle,
            'overshoot': mp,
            'final_value': y_final,
            'peak_value': y_max,
            'wd': self.wd
        }
    
    def freq_domain_metrics(self, target_sys=None):
        """
        Extract frequency domain parameters from Bode/margins
        Returns: dict with margins, crossover frequencies
        """
        sys_to_eval = target_sys if target_sys else self.sys
        omega = np.logspace(-2, 3, 1000)
        mag, phase, omega = ct.frequency_response(sys_to_eval, omega=omega)
        
        try:
            gm, pm, wgc, wpc = ct.margin(sys_to_eval)
        except:
            gm, pm, wgc, wpc = np.inf, 0, 0, 0
        
        # DC gain
        dc_gain = mag[0] if len(mag) > 0 else 1
        
        # Bandwidth (frequency at -3dB)
        mag_db = 20 * np.log10(np.abs(mag) + 1e-10)
        bw_level = mag_db[0] - 3  # -3dB from DC
        bw_idx = np.where(mag_db <= bw_level)[0]
        bandwidth = omega[bw_idx[0]] if len(bw_idx) > 0 else 0
        
        return {
            'mag': mag,
            'phase': phase,
            'omega': omega,
            'gain_margin': 20 * np.log10(gm) if gm != float('inf') and gm > 0 else np.inf,
            'phase_margin': pm,
            'wgc': wgc,  # Gain crossover frequency
            'wpc': wpc,  # Phase crossover frequency
            'dc_gain': dc_gain,
            'bandwidth': bandwidth
        }
    
    def get_pole_zero_data(self):
        """Return poles and zeros for plotting"""
        return self.poles, self.zeros

# --- 2. STREAMLIT UI SETUP ---
st.set_page_config(page_title="Control Systems Master Solver v2", layout="wide")
st.title("🎯 Control Systems Master Solver v2.0")
st.markdown("*Time Domain + Frequency Domain Analysis with Pole Placement & Compensator Design*")

# ==========================================
# SIDEBAR: CONFIGURATION
# ==========================================
st.sidebar.header("⚙️ System Configuration")

col_num, col_den = st.sidebar.columns(2)
with col_num:
    num_input = st.sidebar.text_input("Numerator (e.g., '10')", "25")
with col_den:
    den_input = st.sidebar.text_input("Denominator (e.g., '1, 6, 25')", "1, 6, 25")

st.sidebar.divider()

st.sidebar.subheader("📈 Analysis Domain")
analysis_domain = st.sidebar.radio(
    "Select Analysis Focus:",
    ["Time Domain", "Frequency Domain", "Both"],
    horizontal=False
)

st.sidebar.divider()

st.sidebar.subheader("📦 Enable Modules")
show_simple = st.sidebar.checkbox("📊 System Overview", value=True)
show_metrics = st.sidebar.checkbox("📉 Detailed Metrics (Time/Freq)", value=True)
show_poles = st.sidebar.checkbox("🎯 Pole-Zero Map", value=True)
show_ctrl = st.sidebar.checkbox("🔧 Controllability & Pole Placement")
show_stm = st.sidebar.checkbox("⏱️ State Transition Matrix")
show_comp = st.sidebar.checkbox("🎛️ Compensator Tuning")

st.sidebar.divider()

if show_ctrl:
    st.sidebar.subheader("Target Pole Specs")
    req_zeta = st.sidebar.slider("Target Damping (ζ)", 0.1, 1.0, 0.707)
    req_wn = st.sidebar.slider("Target Freq (ωₙ)", 1.0, 50.0, 10.0)
    
    rp = -req_zeta * req_wn
    ip = req_wn * np.sqrt(abs(1 - req_zeta**2))
    poles_input = st.sidebar.text_input(
        "Poles to place:", 
        f"{rp:.2f}+{ip:.2f}j, {rp:.2f}{'-' if -ip < 0 else '+'}{abs(-ip):.2f}j"
    )

if show_stm:
    st.sidebar.subheader("⏱️ Transition Matrix")
    t_val = st.sidebar.slider("Time (t) seconds", 0.0, 10.0, 1.0, 0.1)

if show_comp:
    st.sidebar.subheader("🎛️ Compensator Design")
    comp_type = st.sidebar.radio("Type", ["Lead", "Lag"], horizontal=True)
    K_val = st.sidebar.slider("Gain (K)", 0.1, 50.0, 10.0)
    
    if comp_type == "Lead":
        z_val = st.sidebar.slider("Zero (z)", 0.1, 20.0, 2.0)
        p_val = st.sidebar.slider("Pole (p)", z_val + 0.1, 50.0, 10.0)
    else:
        p_val = st.sidebar.slider("Pole (p)", 0.1, 20.0, 1.0)
        z_val = st.sidebar.slider("Zero (z)", p_val + 0.1, 50.0, 5.0)

# ==========================================
# MAIN EXECUTION
# ==========================================
try:
    num = [float(x.strip()) for x in num_input.split(',')]
    den = [float(x.strip()) for x in den_input.split(',')]
    analyzer = TFAnalyzer(num, den)
    
    # ===== MODULE 1: SYSTEM OVERVIEW =====
    if show_simple:
        st.header("📊 System Overview")
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Natural Freq (ωₙ)", f"{analyzer.wn:.3f} rad/s")
        with col2:
            st.metric("Damping Ratio (ζ)", f"{analyzer.zeta:.3f}")
        with col3:
            st.metric("Damped Freq (ωd)", f"{analyzer.wd:.3f} rad/s")
        with col4:
            st.metric("System Order", f"{len(analyzer.poles)}")
        
        t_td, y_td = ct.step_response(analyzer.sys, T=np.linspace(0, 5, 500))
        fd_base = analyzer.freq_domain_metrics()
        
        plot_col1, plot_col2 = st.columns(2)
        
        with plot_col1:
            fig_step = go.Figure()
            fig_step.add_trace(go.Scatter(x=t_td, y=y_td, mode='lines', 
                                          line=dict(color='#1f77b4', width=2),
                                          name='Step Response'))
            fig_step.update_layout(
                title="Step Response", xaxis_title="Time (s)", yaxis_title="Output",
                template="plotly_white", hovermode='x unified'
            )
            st.plotly_chart(fig_step, use_container_width=True)
        
        with plot_col2:
            fig_bode = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.12,
                                     subplot_titles=("Magnitude", "Phase"))
            fig_bode.add_trace(
                go.Scatter(x=fd_base['omega'], y=20*np.log10(np.abs(fd_base['mag']) + 1e-10), 
                          line=dict(color='#ff7f0e', width=2)),
                row=1, col=1
            )
            fig_bode.add_trace(
                go.Scatter(x=fd_base['omega'], y=np.degrees(fd_base['phase']),
                          line=dict(color='#2ca02c', width=2)),
                row=2, col=1
            )
            fig_bode.update_xaxes(type="log", row=2, col=1)
            fig_bode.update_layout(title="Bode Plot", template="plotly_white", showlegend=False)
            st.plotly_chart(fig_bode, use_container_width=True)
        
        st.divider()
    
    # ===== MODULE 2: DETAILED METRICS =====
    if show_metrics:
        st.header("📉 Detailed System Metrics")
        
        if analysis_domain == "Both":
            tab1, tab2, tab3 = st.tabs(["⏱️ Time Domain", "📊 Frequency Domain", "🔗 Combined"])
        else:
            tab1, tab2 = st.tabs(["⏱️ Time Domain", "📊 Frequency Domain"])
        
        with tab1:
            if analysis_domain in ["Time Domain", "Both"]:
                td_data = analyzer.time_domain_metrics()
                
                st.subheader("Time Domain Parameters")
                col_td1, col_td2, col_td3, col_td4 = st.columns(4)
                
                col_td1.metric("Rise Time (tᵣ)", f"{td_data['rise_time']:.4f} s")
                col_td2.metric("Peak Time (tₚ)", f"{td_data['peak_time']:.4f} s")
                col_td3.metric("Overshoot (Mₚ)", f"{td_data['overshoot']:.2f}%")
                col_td4.metric("Settling Time (tₛ)", f"{td_data['settling_time']:.4f} s")
                
                fig_step_annot = go.Figure()
                fig_step_annot.add_trace(go.Scatter(x=td_data['step_t'], y=td_data['step_y'], mode='lines', line=dict(color='#1f77b4', width=2.5)))
                fig_step_annot.add_hline(y=td_data['final_value'], line_dash="dash", line_color="gray", annotation_text=f"SS: {td_data['final_value']:.3f}")
                fig_step_annot.add_hline(y=td_data['peak_value'], line_dash="dot", line_color="red", annotation_text=f"Peak: {td_data['peak_value']:.3f}")
                
                fig_step_annot.update_layout(title="Step Response with Annotations", template="plotly_white")
                st.plotly_chart(fig_step_annot, use_container_width=True)
                
                with st.expander("📐 Formulas Used"):
                    st.markdown("""
                    **Time Domain Calculations:**
                    - **ωₙ** (Natural Freq): √(constant term of denominator)
                    - **ζ** (Damping Ratio): (s coefficient) / (2·ωₙ)
                    - **ωd** (Damped Freq): ωₙ·√(1 - ζ²)
                    - **tᵣ** (Rise Time): From step response (10% → 90%)
                    - **tₚ** (Peak Time): π / ωd
                    - **Mₚ** (Overshoot): (Peak - Final) / Final × 100%
                    - **tₛ** (Settling Time): 4 / (ζ·ωₙ)
                    """)
        
        with tab2:
            if analysis_domain in ["Frequency Domain", "Both"]:
                fd_data = analyzer.freq_domain_metrics()
                
                st.subheader("Frequency Domain Parameters")
                col_fd1, col_fd2, col_fd3, col_fd4 = st.columns(4)
                
                gm_val = fd_data['gain_margin']
                col_fd1.metric("Gain Margin", f"{gm_val:.2f} dB" if gm_val != np.inf else "∞")
                col_fd2.metric("Phase Margin", f"{fd_data['phase_margin']:.2f}°")
                col_fd3.metric("Bandwidth", f"{fd_data['bandwidth']:.3f} rad/s")
                col_fd4.metric("DC Gain", f"{20*np.log10(fd_data['dc_gain']):.2f} dB")
                
                fig_bode_detail = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.12)
                fig_bode_detail.add_trace(go.Scatter(x=fd_data['omega'], y=20*np.log10(np.abs(fd_data['mag']) + 1e-10), line=dict(color='#ff7f0e', width=2.5)), row=1, col=1)
                fig_bode_detail.add_trace(go.Scatter(x=fd_data['omega'], y=np.degrees(fd_data['phase']), line=dict(color='#2ca02c', width=2.5)), row=2, col=1)
                
                if fd_data['wgc'] > 0: fig_bode_detail.add_vline(x=fd_data['wgc'], line_dash="dash", line_color="red", row=1, col=1)
                if fd_data['wpc'] > 0: fig_bode_detail.add_vline(x=fd_data['wpc'], line_dash="dash", line_color="purple", row=2, col=1)
                
                fig_bode_detail.update_xaxes(type="log", row=2, col=1)
                fig_bode_detail.update_layout(title="Detailed Bode Plot", template="plotly_white", showlegend=False)
                st.plotly_chart(fig_bode_detail, use_container_width=True)
                
        if analysis_domain == "Both":
            with tab3:
                st.subheader("🔗 Time-Frequency Relationship")
                td = analyzer.time_domain_metrics()
                fd = analyzer.freq_domain_metrics()
                
                rel_data = {
                    'Parameter': ['Rise Time', 'Overshoot', 'Settling Time'],
                    'Time Domain': [td['rise_time'], td['overshoot'], td['settling_time']],
                    'Freq Domain Equiv': [f"{fd['bandwidth']:.3f}", f"{analyzer.zeta:.3f}", f"{fd['phase_margin']:.2f}°"]
                }
                st.dataframe(rel_data, use_container_width=True)
        
        st.divider()
    
    # ===== MODULE 3: POLE-ZERO MAP =====
    if show_poles:
        st.header("🎯 Pole-Zero Map")
        poles, zeros = analyzer.get_pole_zero_data()
        
        fig_pz = go.Figure()
        if len(poles) > 0:
            fig_pz.add_trace(go.Scatter(x=np.real(poles), y=np.imag(poles), mode='markers', marker=dict(size=12, color='red', symbol='x'), name='Poles'))
        if len(zeros) > 0:
            fig_pz.add_trace(go.Scatter(x=np.real(zeros), y=np.imag(zeros), mode='markers', marker=dict(size=12, color='blue', symbol='o'), name='Zeros'))
        
        fig_pz.add_vline(x=0, line_dash="dash", line_color="gray")
        fig_pz.add_vrect(x0=-5, x1=0, fillcolor="green", opacity=0.1, layer="below")
        
        fig_pz.update_layout(title="Pole-Zero Map", template="plotly_white", width=700, height=600)
        fig_pz.update_yaxes(scaleanchor="x", scaleratio=1)
        st.plotly_chart(fig_pz, use_container_width=True)
        st.divider()
    
    # ===== MODULE 4: CONTROLLABILITY & POLE PLACEMENT =====
    if show_ctrl:
        st.header("🔧 Controllability & Pole Placement")
        sys_ss = ct.tf2ss(analyzer.sys)
        A, B = sys_ss.A, sys_ss.B
        sys_order = A.shape[0]
        
        Cm = ct.ctrb(A, B)
        is_controllable = np.linalg.matrix_rank(Cm) == sys_order
        
        col_ctrl1, col_ctrl2 = st.columns(2)
        col_ctrl1.metric("System Order", sys_order)
        col_ctrl2.metric("Controllability", "✅ Fully Controllable" if is_controllable else "❌ Uncontrollable")
        
        if is_controllable:
            clean_input = poles_input.replace(' ', '').replace('i', 'j')
            try:
                desired_poles = [complex(p) for p in clean_input.split(',')]
                if len(desired_poles) == sys_order:
                    K = ct.place(A, B, desired_poles)
                    st.success("✅ Pole Placement Successful!")
                    st.write("**Calculated Gain Matrix K:**")
                    st.dataframe(np.round(K, 4), use_container_width=True)
                else:
                    st.warning(f"⚠️ Please provide exactly {sys_order} poles")
            except Exception as e:
                st.error(f"❌ Error parsing poles. Use format: 'a+bj, c+dj'")
        st.divider()
    
    # ===== MODULE 5: STATE TRANSITION MATRIX =====
    if show_stm:
        st.header(f"⏱️ State Transition Matrix Φ(t) @ t={t_val}s")
        A = ct.tf2ss(analyzer.sys).A
        stm = expm(A * t_val)
        
        col_stm1, col_stm2 = st.columns(2)
        with col_stm1:
            st.write("**System Matrix A:**")
            st.dataframe(np.round(A, 4), use_container_width=True)
        with col_stm2:
            st.write(f"**Transition Matrix Φ({t_val}):**")
            st.dataframe(np.round(stm, 4), use_container_width=True)
        st.divider()
    
    # ===== MODULE 6: COMPENSATOR DESIGN =====
    if show_comp:
        st.header(f"🎛️ Live {comp_type} Compensator Design")
        
        Gc = ct.TransferFunction([K_val, K_val * z_val], [1, p_val])
        L = ct.series(Gc, analyzer.sys)  
        T = ct.feedback(L, 1)  
        
        # Now passing the new system into your metric methods!
        fd_comp = analyzer.freq_domain_metrics(L)
        td_comp = analyzer.time_domain_metrics(T)
        
        st.info(f"**Current Compensator:** Gc(s) = {K_val:.2f} · (s + {z_val:.2f}) / (s + {p_val:.2f})")
        
        col_comp1, col_comp2, col_comp3 = st.columns(3)
        col_comp1.metric("New Phase Margin", f"{fd_comp['phase_margin']:.2f}°" if not np.isnan(fd_comp['phase_margin']) else "N/A")
        
        gm_db = fd_comp['gain_margin']
        col_comp2.metric("New Gain Margin", f"{gm_db:.2f} dB" if gm_db != np.inf else "∞")
        col_comp3.metric("Comp Type", comp_type)
        
        plot_col1, plot_col2 = st.columns(2)
        
        with plot_col1:
            fig_comp_step = go.Figure()
            try:
                td_orig = analyzer.time_domain_metrics(ct.feedback(analyzer.sys, 1))
                fig_comp_step.add_trace(go.Scatter(x=td_orig['step_t'], y=td_orig['step_y'], mode='lines', line=dict(dash='dot', color='gray', width=2), name='Original'))
            except:
                pass
            
            fig_comp_step.add_trace(go.Scatter(x=td_comp['step_t'], y=td_comp['step_y'], mode='lines', line=dict(color='purple', width=2.5), name='Compensated'))
            fig_comp_step.update_layout(title="Closed-Loop Step Response", template="plotly_white")
            st.plotly_chart(fig_comp_step, use_container_width=True)
        
        with plot_col2:
            fig_comp_bode = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.12)
            
            try:
                fd_orig = analyzer.freq_domain_metrics()
                fig_comp_bode.add_trace(go.Scatter(x=fd_orig['omega'], y=20*np.log10(np.abs(fd_orig['mag']) + 1e-10), line=dict(dash='dot', color='gray', width=1.5)), row=1, col=1)
                fig_comp_bode.add_trace(go.Scatter(x=fd_orig['omega'], y=np.degrees(fd_orig['phase']), line=dict(dash='dot', color='gray', width=1.5)), row=2, col=1)
            except:
                pass
            
            fig_comp_bode.add_trace(go.Scatter(x=fd_comp['omega'], y=20*np.log10(np.abs(fd_comp['mag']) + 1e-10), line=dict(color='orange', width=2.5)), row=1, col=1)
            fig_comp_bode.add_trace(go.Scatter(x=fd_comp['omega'], y=np.degrees(fd_comp['phase']), line=dict(color='green', width=2.5)), row=2, col=1)
            
            fig_comp_bode.update_xaxes(type="log", row=2, col=1)
            fig_comp_bode.update_layout(title="Open-Loop Bode Comparison", template="plotly_white", showlegend=False)
            st.plotly_chart(fig_comp_bode, use_container_width=True)

except Exception as e:
    st.error(f"❌ Error in calculation: {str(e)}")