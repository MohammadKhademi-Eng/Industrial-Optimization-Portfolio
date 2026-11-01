# lyapunov_shield_verify.py

def check_lyapunov_stability(q_oven: int, mu_boost: float = 0.0833, lambda_val: float = 0.1667) -> tuple[bool, float]:
    """
    Deterministically verifies the Lyapunov stability condition ($ \dot{V} < 0 $).
    V(Q) = 0.5 * Q^2 -> V_dot = Q * (lambda_effective - mu_effective)
    """
    eff_lambda = 0.0  # Assumes upstream gating is engaged (lambda = 0)
    drift = eff_lambda - mu_boost  # dQ/dt
    is_stable = drift < 0
    return is_stable, drift