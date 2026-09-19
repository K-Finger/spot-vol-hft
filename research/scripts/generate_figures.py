"""Regenerate the example figures embedded in the README.

Run with: python scripts/generate_figures.py
"""
import matplotlib
matplotlib.use("Agg")

from pathlib import Path

from spotvol.align import align_ticks
from spotvol.beta import estimate_beta
from spotvol.features import build_features
from spotvol.plot import make_report_figure, plot_beta_recovery
from spotvol.synthetic import generate

FIGURES_DIR = Path(__file__).resolve().parent.parent / "figures"
TRUE_BETA = -3.0


def main() -> None:
    FIGURES_DIR.mkdir(exist_ok=True)

    spot_df, option_df = generate(beta=TRUE_BETA, seed=42)
    aligned = align_ticks(spot_df, option_df)
    features = build_features(aligned)
    result = estimate_beta(features)

    fig = make_report_figure(features, result)
    fig.savefig(FIGURES_DIR / "summary.png", dpi=150, bbox_inches="tight")

    # Beta recovery vs. sample size: scale n_spot and n_option together (more,
    # finer ticks over the same horizon) and hold total realized spot
    # variance roughly constant across n by scaling per-tick spot_vol down,
    # so larger n means "observed more finely," not "wandered further from
    # the strike." Multiple seeds per n give the sampling spread.
    base_n, base_vol = 500, 0.01
    n_spots = [100, 250, 500, 1000, 2000]
    betas_by_n = {}
    for n_spot in n_spots:
        n_option = int(n_spot * 0.6)
        spot_vol = base_vol * (base_n / n_spot) ** 0.5
        betas_by_n[n_option] = [
            estimate_beta(
                build_features(
                    align_ticks(
                        *generate(
                            n_spot=n_spot, n_option=n_option,
                            beta=TRUE_BETA, spot_vol=spot_vol, seed=seed,
                        )
                    )
                )
            ).beta
            for seed in range(30)
        ]

    ax = plot_beta_recovery(betas_by_n, true_beta=TRUE_BETA)
    ax.figure.savefig(FIGURES_DIR / "beta_recovery.png", dpi=150, bbox_inches="tight")

    print(f"wrote {FIGURES_DIR / 'summary.png'}")
    print(f"wrote {FIGURES_DIR / 'beta_recovery.png'}")


if __name__ == "__main__":
    main()
