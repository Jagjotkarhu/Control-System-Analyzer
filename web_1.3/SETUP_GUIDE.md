# 🚀 Control Systems Master Solver v2.0 - Setup & Usage Guide

## **Installation**

### Step 1: Install Dependencies
```bash
pip install streamlit control numpy plotly scipy
```

### Step 2: Run the App
```bash
streamlit run control_systems_enhanced.py
```

The app opens at: `http://localhost:8501`

---

## **⚙️ App Architecture**

### **Sidebar Workflow**
```
1. Define Plant G(s)
   ├─ Numerator coefficients (e.g., "25")
   └─ Denominator coefficients (e.g., "1, 6, 25")

2. Select Analysis Domain
   ├─ Time Domain Only
   ├─ Frequency Domain Only
   └─ Both (reveals Combined tab)

3. Enable Modules (Checkboxes)
   ├─ 📊 System Overview (basic plots)
   ├─ 📉 Detailed Metrics (full calculations)
   ├─ 🎯 Pole-Zero Map (pole analysis)
   ├─ 🔧 Controllability & Pole Placement
   ├─ ⏱️ State Transition Matrix
   └─ 🎛️ Compensator Tuning (Lead/Lag)

4. Conditional Inputs
   └─ Appear based on enabled modules
```

---

## **📊 What Each Module Does**

### **Module 1: System Overview** 📊
**Shows:**
- Key metrics (ωₙ, ζ, ωd, System Order)
- Basic step response plot
- Bode magnitude & phase (quick view)

**Use:** First module to enable. Gets overview in 5 seconds.

---

### **Module 2: Detailed Metrics** 📉

#### **Time Domain Tab** ⏱️
**Calculates & displays:**
```
Rise Time (tᵣ)      → 10% to 90% of final value
Peak Time (tₚ)      → Time at maximum output (π/ωd)
Overshoot (Mₚ)      → % above steady-state (ζ-dependent)
Settling Time (tₛ)  → 2% criterion: 4/(ζ·ωₙ)
```

**Step response** with annotations:
- Steady-state line (dashed)
- Peak line (dotted red)
- Perfect for identifying undershoot/overshoot

**Formulas shown** in expander (interview prep!)

#### **Frequency Domain Tab** 📊
**Calculates & displays:**
```
Gain Margin (GM)          → Stability buffer (dB)
Phase Margin (PM)         → Stability margin (degrees)
Bandwidth                 → -3dB frequency
DC Gain                   → Magnitude at ω=0
```

**Detailed Bode plot:**
- Magnitude and phase subplots
- Gain/phase crossover markers
- Annotations for critical frequencies

#### **Combined Tab** 🔗 (only if "Both" selected)
**Shows:**
- Time-frequency relationships
- Design trade-offs
- Equivalence table (tᵣ ↔ BW, Mₚ ↔ PM, tₛ ↔ GM)

---

### **Module 3: Pole-Zero Map** 🎯

**Shows:**
- 📍 Red X marks = Poles
- 📍 Blue circles = Zeros
- Gray dashed line = Stability boundary (jω axis)
- Green shaded region = Stable area (σ < 0)

**Hover over poles/zeros** to see:
- Real part (σ)
- Imaginary part (ω)
- Magnitude & angle

**Pole Analysis Table** shows:
| Pole # | Real (σ) | Imag (ω) | Magnitude | Angle (°) |
|--------|----------|----------|-----------|-----------|
| 1      | -3.00    | 4.00     | 5.00      | 126.87    |
| 2      | -3.00    | -4.00    | 5.00      | -126.87   |

**Interview Value:** Demonstrates understanding of pole locations → system behavior

---

### **Module 4: Controllability & Pole Placement** 🔧

**Step 1: Check Controllability**
```python
Controllability Matrix Cₘ = [B  AB  A²B  ...]
If rank(Cₘ) == system_order → Fully Controllable ✅
```

**Step 2: Design State Feedback**
```
Desired Poles (you input) → Calculated Gain Matrix K
K·u = -K·x feedback law
```

**Outputs:**
- ✅/❌ Controllability status
- A, B, C, D matrices
- Controllability matrix rank
- K gain matrix (if controllable)
- Verification: Closed-loop poles match desired

**Practical:** Design custom pole placement for desired speed/damping

---

### **Module 5: State Transition Matrix** ⏱️

**What is Φ(t)?**
```
Φ(t) = e^(At) = State evolution matrix
x(t) = Φ(t)·x(0) + ∫Φ(t-τ)B·u(τ)dτ
```

**Shows:**
- System matrix A
- Transition matrix Φ(t) at user-selected time
- How state moves over time (no input needed)

**Use case:** Predict future state without solving differential equations

---

### **Module 6: Compensator Tuning** 🎛️

**Lead Compensator:**
```
Gc(s) = K·(s+z)/(s+p)   where p > z
Purpose: Increase phase margin (PM) & bandwidth
Effect: Faster response, more oscillation
```

**Lag Compensator:**
```
Gc(s) = K·(s+z)/(s+p)   where z > p
Purpose: Improve steady-state error
Effect: Slower response, better accuracy
```

**Adjustable Parameters:**
- Gain K (0.1 to 50)
- Zero z (frequency of zero)
- Pole p (frequency of pole)

**Outputs:**
- Original vs Compensated comparison
- Step response improvement
- Bode plot (open-loop) with overlay
- New PM/GM metrics

**Interview Gold:** Shows understanding of compensation theory + practical tuning

---

## **💡 Example Workflows**

### **Workflow 1: Quick System Check** (2 min)
```
1. Input TF: Num=[25], Den=[1,6,25]
2. Enable: ✅ System Overview
3. Read: ωₙ=5 rad/s, ζ=0.6, 2nd order underdamped
4. Decision: "This system oscillates at 6.4 rad/s"
```

### **Workflow 2: Interview Preparation** (10 min)
```
1. Enable all modules
2. Select "Both" domains
3. Walk through each calculation
4. Screenshot metrics table
5. Add to portfolio as "Full Control System Analysis"
```

### **Workflow 3: Tuning a Controller** (15 min)
```
1. Enable: Detailed Metrics + Pole-Zero + Compensator
2. Start with Lead compensator
3. Adjust K, z, p sliders
4. Watch PM/step response improve
5. Find optimal trade-off point
6. Document the compensator TF
```

### **Workflow 4: Hardware Deployment Planning** (20 min)
```
1. Analyze original plant (all modules)
2. Note: tᵣ, tₛ, required PM
3. Design compensator to meet specs
4. Extract K gain values
5. Convert to Arduino code structure
```

---

## **📐 Key Formulas (Interview Checklist)**

### **Time Domain**
- ✓ ωₙ = √(constant term of den)
- ✓ ζ = (s coefficient) / (2·ωₙ)
- ✓ ωd = ωₙ·√(1 - ζ²)
- ✓ tᵣ = from step response (10→90%)
- ✓ tₚ = π / ωd
- ✓ Mₚ = e^(-π·ζ/√(1-ζ²)) × 100%
- ✓ tₛ = 4 / (ζ·ωₙ)

### **Frequency Domain**
- ✓ GM = 1 / |G(jω)| at phase = -180°
- ✓ PM = -180° + ∠G(jω) at |G(jω)| = 1
- ✓ Stability: GM > 0 dB AND PM > 0°
- ✓ Bandwidth = frequency at -3dB

### **State Space**
- ✓ Controllability: rank([B  AB  A²B  ...]) = n
- ✓ Pole placement: K = place(A, B, poles)
- ✓ Φ(t) = e^(At) = State transition matrix

---

## **🎯 Resume Portfolio Tips**

### **What to Screenshot:**
1. ✅ Detailed Metrics comparison table
2. ✅ Pole-Zero map (shows stability understanding)
3. ✅ Bode plot with margins
4. ✅ Compensator design before/after
5. ✅ Pole placement verification

### **Write-up Example:**
```
"Developed comprehensive control system analysis tool using Python-control library.
Implemented manual calculation of time-domain metrics (rise time, overshoot, settling time),
frequency-domain stability margins (GM, PM), pole placement controller design, and
state transition matrix analysis. Demonstrated through 6 interconnected modules
with interactive Plotly visualizations."
```

### **GitHub Link:**
- Upload `control_systems_enhanced.py` to GitHub
- Add sample analyses as `.html` exports
- Tag: #control-systems #python-control #engineering

---

## **🐛 Troubleshooting**

### **Error: "Please check your input values"**
```
Check format:
✓ Numerator:   "25" or "1, 5, 6"
✓ Denominator: "1, 6, 25"
✗ Don't use: "25.0" with spaces, scientific notation
```

### **Poles Not Calculating**
```
Ensure denominator has at least 2 terms:
✗ Den = [1]        → 0th order (no poles)
✓ Den = [1, 5]     → 1st order (1 pole)
✓ Den = [1, 6, 25] → 2nd order (2 poles)
```

### **Compensator PM = "N/A"**
```
System may be unstable. Add integrator in loop or lower gain K.
```

---

## **⚡ Performance Tips**

1. **Start with System Overview only** → then enable others
2. **Use Time Domain for step response analysis**
3. **Use Frequency Domain for stability margins**
4. **Use Both for design trade-off understanding**
5. **Refresh page (F5) to clear all inputs**

---

## **📚 Next: Deployment to Hardware**

Once you understand this app, convert to:
- **Arduino C++:** Use Φ(t) for state update in code
- **PLC:** Implement K gain matrix in ladder logic
- **Raspberry Pi:** Real-time compensator as Python daemon

---

**🚀 Ready to deploy? Start with Workflow 1, progress to Workflow 4!**
