# 🧪 Test Cases & Example Transfer Functions

Copy-paste these into the app sidebar to experiment!

---

## **Example 1: 2nd Order Underdamped** (Most Common)

**Use Case:** Motor speed control, mass-spring-damper system

```
Numerator:   25
Denominator: 1, 6, 25
```

**Expected Results:**
```
ωₙ = 5.00 rad/s
ζ = 0.60 (underdamped)
ωd = 4.00 rad/s

Time Domain:
  Rise Time:      0.3-0.4 sec
  Peak Time:      0.7-0.8 sec
  Overshoot:      ~9.5%
  Settling Time:  1.3-1.5 sec

Frequency Domain:
  Phase Margin:   ~45°
  Gain Margin:    ~12 dB
  Status:         Stable ✓
```

**📊 Visualization:**
- Step response: Classic S-curve with slight overshoot
- Bode: Magnitude peak at ωd, PM > 30°
- Poles: Complex conjugate pair at σ=-3, ω=±4

**Interview Q:** "Why does ωd ≠ ωₙ here?"
**Answer:** Because ζ < 1 → underdamped → oscillation at ωd, not ωₙ

---

## **Example 2: 2nd Order Critically Damped**

**Use Case:** Measurement sensors, precision instruments

```
Numerator:   25
Denominator: 1, 10, 25
```

**Expected Results:**
```
ωₙ = 5.00 rad/s
ζ = 1.00 (critically damped)
ωd = 0 (no oscillation)

Time Domain:
  Rise Time:      0.5-0.6 sec (slower)
  Peak Time:      0 (monotonic rise)
  Overshoot:      0% (no overshoot!)
  Settling Time:  0.8-1.0 sec

Frequency Domain:
  Phase Margin:   ~65°
  Gain Margin:    ~20 dB
  Status:         Stable ✓
```

**📊 Visualization:**
- Step response: Smooth exponential rise (no overshoot)
- Bode: No resonance peak
- Poles: Two real poles at σ=-5

**Interview Q:** "When would you choose critically damped?"
**Answer:** When overshooting causes damage (sensitive equipment) or when response speed is less critical than accuracy

---

## **Example 3: 2nd Order Overdamped**

**Use Case:** Hydraulic systems, thermal systems

```
Numerator:   25
Denominator: 1, 15, 25
```

**Expected Results:**
```
ωₙ = 5.00 rad/s
ζ = 1.50 (overdamped)
ωd = 0 (imaginary)

Time Domain:
  Rise Time:      1.0-1.5 sec (very slow)
  Peak Time:      0 (monotonic)
  Overshoot:      0% (no overshoot)
  Settling Time:  2.0-3.0 sec (slow!)

Frequency Domain:
  Phase Margin:   ~80°
  Gain Margin:    ~30 dB
  Status:         Very stable ✓✓
```

**📊 Visualization:**
- Step response: Very slow, sluggish rise
- Bode: Very smooth, conservative
- Poles: Two real poles at different locations

**Trade-off:** Super stable BUT slow response. Not ideal for control.

---

## **Example 4: First Order System**

**Use Case:** RC circuits, temperature control, simple lag

```
Numerator:   1
Denominator: 1, 2
```

**Expected Results:**
```
ωₙ = 2.00 rad/s
ζ = 1.00 (always critical for 1st order)

Time Domain:
  Rise Time:      ~0.7 sec
  Overshoot:      0% (never overshots)
  Settling Time:  ~2.0 sec (4/2)

Frequency Domain:
  Phase Margin:   ~90°
  Gain Margin:    ∞ (always stable)
  Status:         Always stable ✓
```

**📊 Visualization:**
- Step response: Exponential decay shape
- Bode: Simple first-order roll-off (-20 dB/decade)
- Poles: Single real pole at σ=-2

**Interview Q:** "Can a 1st order system oscillate?"
**Answer:** No, ζ is always ≥ 1 for real poles → monotonic response

---

## **Example 5: Integrator (Type-1 System)**

**Use Case:** Velocity from acceleration, position control

```
Numerator:   10
Denominator: 1, 0, 0
```

**Expected Results:**
```
⚠️ Pole at origin! System marginally stable
ωₙ = 0 (undefined, pure integrator)
ζ = 0 (undefined)

Characteristics:
  - Responds to ramp input (velocity commands)
  - Zero steady-state error for ramps
  - Requires feedback for stability
  - GM/PM may show "N/A" (on stability boundary)
```

**📊 Visualization:**
- Pole-Zero: Red X at origin (0,0)
- Step response: Linear increase (unbounded!)
- Bode: -90° phase shift, slope -20 dB/decade

**Interview Q:** "Why does an integrator need feedback?"
**Answer:** Open-loop pole at origin → marginally stable. Feedback moves pole into left half-plane.

**Tip:** This system is unstable in open loop! Use with compensator.

---

## **Example 6: Unstable System** ⚠️

**Use Case:** Inverted pendulum, missile guidance (needs control!)

```
Numerator:   10
Denominator: 1, -2, 5
```

**Expected Results:**
```
⚠️ Real pole at σ=+1 → UNSTABLE!

Pole-Zero Map:
  - Red X in right half-plane (RHP)
  - System diverges without control

Frequency Domain:
  - GM/PM: May show "N/A" or negative
  - Bode: Diverges at low frequencies
  
Step Response:
  - Exponential blow-up!
```

**📊 Visualization:**
- Pole-Zero: Red X right of jω axis (unstable region)
- Step response: Unbounded growth
- Bode: Unstable regions visible

**Interview Q:** "How would you stabilize this?"
**Answer:** State feedback (pole placement) to move RHP pole to LHP. Use Module 4 (Controllability).

---

## **Example 7: Non-Minimum Phase System**

**Use Case:** Certain aircraft, chemical processes

```
Numerator:   10, -5
Denominator: 1, 6, 25
```

**Expected Results:**
```
ωₙ = 5.00 rad/s
ζ = 0.60

Special Feature: Zero in RHP (σ=0.5)
  - Creates initial negative response
  - Bode shows phase lag > stable minimum-phase

Pole-Zero Map:
  - Blue circle (zero) in right half-plane!
  - Poles still in LHP (stable)
  
Step Response:
  - Initially goes DOWN before going UP!
  - Called "undershoot" or "non-minimum phase behavior"
```

**Interview Q:** "What does a RHP zero mean?"
**Answer:** Initial response opposes desired direction. Harder to control. Common in systems with transport delays or certain dynamics.

---

## **Example 8: Lead Compensator Test**

**Setup:**
```
1. Set Plant: Num=[25], Den=[1,6,25]
2. Enable "Compensator Tuning"
3. Select "Lead"
4. Set K=5, z=2, p=10
```

**Expected Changes:**
```
Before Compensator:
  PM = ~45°, BW = ~4 rad/s

After Lead:
  PM = ~55-65° (improved!)
  BW = ~6-8 rad/s (faster!)
  Step response: Faster, still stable
```

**Why it works:**
- Lead adds phase boost (s+z)/(s+p) has peak phase when z < p
- Improves PM → more stable
- Increases BW → faster response

---

## **Example 9: Lag Compensator Test**

**Setup:**
```
1. Set Plant: Num=[10], Den=[1,10,1]
2. Enable "Compensator Tuning"
3. Select "Lag"
4. Set K=2, p=0.5, z=2
```

**Expected Changes:**
```
Before Compensator:
  Steady-state error = high

After Lag:
  K gain boost → error reduction
  PM ~same (lag doesn't hurt stability much)
  BW slightly lower
```

**Why it works:**
- Lag adds gain at low frequency (DC)
- Improves steady-state accuracy
- Doesn't boost bandwidth (conservative)

---

## **Testing Checklist** ✅

For each example, verify:

- [ ] Numerator & Denominator parse correctly
- [ ] Metrics match expected values (±5% tolerance)
- [ ] Pole-Zero map shows poles in LHP (for stable systems)
- [ ] Step response shape matches theory
- [ ] Bode plot consistent with pole locations
- [ ] PM > 0° → system is stable

---

## **📋 Quick Comparison Table**

| System Type | ζ | Overshoot | Rise Time | Settling Time | Stability |
|------------|---|-----------|-----------|---------------|-----------|
| Underdamped | <1 | 5-30% | Fast | Medium | ✓ |
| Critical | 1 | 0% | Medium | Medium | ✓ |
| Overdamped | >1 | 0% | Slow | Slow | ✓ |
| Integrator | 0 | — | Ramp | Infinite | ⚠️ |
| Unstable | Any | ∞ | — | — | ✗ |

---

## **🎯 Learning Progression**

1. **Start:** Example 1 (underdamped) — most common, intuitive
2. **Explore:** Examples 2-4 (different ζ values) — understand trade-offs
3. **Challenge:** Example 5 (integrator) — edge case, requires feedback
4. **Master:** Example 6 (unstable) + Module 4 (pole placement) — full control
5. **Advanced:** Examples 7-9 (non-min phase, compensators) — interview-level

---

**💡 Tip:** Once you understand Example 1, you understand 80% of real control systems!
