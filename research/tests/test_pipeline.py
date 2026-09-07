from spotvol.align import align_ticks
from spotvol.beta import estimate_beta
from spotvol.features import build_features
from spotvol.synthetic import generate

INJECTED_BETA = -3.0


def test_beta_recovery():
    spot_df, option_df = generate(beta=INJECTED_BETA, seed=42)
    aligned = align_ticks(spot_df, option_df)
    features = build_features(aligned)
    recovered = estimate_beta(features)
    assert abs(recovered - INJECTED_BETA) < 0.5
