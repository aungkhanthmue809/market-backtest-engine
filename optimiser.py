import json
import itertools
from pathlib import Path
from tqdm import tqdm

from engine import calculate
import src.loader as loader
import src.processor as processor


START_DATE = "2020-04-06"
END_DATE = "2023-05-07"

STRATEGY = "market_structure"


# Parameters to optimize

_PARAM_GRID = {
    "look_back": [
        5, 8, 10, 12, 15, 18, 20, 25,
        30, 35, 40, 50, 60, 75, 100, 125, 150
    ],

    "swing_window": [
        2, 3, 4, 5, 6, 7, 8, 10, 12, 15
    ],

    "swing_count": [
        2, 3, 4, 5, 6, 7, 8, 10
    ],

    "rr_ratio": [
        1.0, 1.25, 1.5, 1.75,
        2.0, 2.5, 3.0, 3.5,
        4.0, 5.0, 6.0
    ],
}

PARAM_GRID = {
    "look_back": [
        10, 15, 20, 25, 30, 40, 50, 60, 75, 100
    ],

    "swing_window": [
        2, 3, 4, 5, 6, 8, 10
    ],

    "swing_count": [
        2,3, 4, 5, 6, 8
    ],

    "rr_ratio": [
        1.0, 2.0, 3.0, 4.0, 5.0
    ],
}

# Load config
with open("config.json", "r") as f:
    config = json.load(f)

# Load original parameters
with open("parameters.json", "r") as f:
    parameters = json.load(f)


# def rank_index(result):
#     dd = result["maximum_drawdown"]
#     calmar = result["return_percent"] / dd if dd > 0 else result["return_percent"]
#     pf = result["gross_profit"] / result["gross_loss"] if result["gross_loss"] > 0 else (
#         result["gross_profit"] if result["gross_profit"] > 0 else 0.0
#     )
#     return 0.5 * calmar + 0.3 * min(pf, 5.0) + 0.2 * result["win_rate"] / 100.0


# New index: also rewards a bigger number of trades.
# trade_score = trades / (trades + 50) is a saturating curve:
# 0 trades -> 0, 50 -> 0.5, 100 -> 0.67, 200 -> 0.8, so more trades
# help but each extra trade matters less and less.
def rank_index(result):
    dd = result["maximum_drawdown"]
    return_pct = result["return_percent"]
    gross_profit = result["gross_profit"]
    gross_loss = result["gross_loss"]
    trades = result["total_trades"]

    # Return relative to drawdown
    calmar = return_pct / dd if dd > 0 else return_pct

    # Profit factor. No losing trades = the best case, so score it as max.
    if gross_loss > 0:
        pf = gross_profit / gross_loss
    elif gross_profit > 0:
        pf = 5.0
    else:
        pf = 0.0

    # More trades = more confidence, but diminishing returns
    trade_score = trades / (trades + 50)

    # Cap extreme values so one metric doesn't dominate
    calmar_score = min(calmar, 10.0) / 10.0
    pf_score = min(pf, 5.0) / 5.0

    return (
        0.50 * calmar_score
        + 0.30 * pf_score
        + 0.20 * trade_score
    )
    
# Create every combination
combinations = list(
    itertools.product(
        PARAM_GRID["look_back"],
        PARAM_GRID["swing_window"],
        PARAM_GRID["swing_count"],
        PARAM_GRID["rr_ratio"]
    )
)
results = []
results_path = Path("results") / "optimization_results.json"
results_path.parent.mkdir(exist_ok=True)

# =========================
# RESUME: load any previously saved results and skip those combos
# =========================

done = set()
if results_path.exists():
    try:
        with open(results_path, "r") as f:
            old_results = json.load(f)
        if isinstance(old_results, list):
            results = []
            for entry in old_results:
                if all(k in entry for k in ("look_back", "swing_window", "swing_count", "rr_ratio")):
                    results.append(entry)
                    done.add((
                        entry["look_back"],
                        entry["swing_window"],
                        entry["swing_count"],
                        entry["rr_ratio"]
                    ))
            print(f"Resuming: {len(done)} combination(s) already done.",
                  f"({len(old_results) - len(done)} stale entries dropped.)")
    except (json.JSONDecodeError, OSError) as e:
        print(f"Could not load existing results ({e}); starting fresh.")

# =========================
# OPTIMIZATION
# =========================

#load data once and reuse across every combination
df_ltf, df_htf = loader.load_data(START_DATE, END_DATE)
df_data = processor.process(df_ltf, df_htf)

for look_back, swing_window, swing_count, rr_ratio in tqdm(
    combinations,
    desc="Optimizing",
    unit="test"
):

    combo_key = (look_back, swing_window, swing_count, rr_ratio)

    if combo_key in done:
        continue

    # Change the parameters for this test
    parameters["market_structure"]["look_back"] = look_back
    parameters["market_structure"]["swing_window"] = swing_window
    parameters["market_structure"]["swing_count"] = swing_count
    parameters["market_structure"]["rr_ratio"] = rr_ratio 
    try:
        _, _, stats = calculate(
            START_DATE,
            END_DATE,
            config,
            parameters,
            df_data
        )

        res = {
            "look_back": look_back,
            "swing_window": swing_window,
            "swing_count": swing_count,
            "rr_ratio": rr_ratio,
            
            "final_balance": stats["final_balance"],
            "return_percent": stats["return_percent"],

            "total_trades": stats["total_trades"],
            "winning_trades": stats["winning_trades"],
            "losing_trades": stats["losing_trades"],
            "win_rate": stats["win_rate"],

            "gross_profit": stats["gross_profit"],
            "gross_loss": stats["gross_loss"],

            "average_winning_trade":
                stats["average_winning_trade"],

            "average_losing_trade":
                stats["average_losing_trade"],

            "maximum_drawdown":
                stats["maximum_drawdown"]
        }
        res["index"] = rank_index(res)
        results.append(res)

        #checkpoint: persist after every combo so a pause/resume loses nothing
        with open(results_path, "w") as f:
            json.dump(results, f, indent=4)

    except KeyboardInterrupt:
        with open(results_path, "w") as f:
            json.dump(results, f, indent=4)
        print("\nInterrupted. Progress saved. Re-run to resume.")
        raise SystemExit(130)

    except Exception as e:
        print(
            f"\nError with "
            f"look_back={look_back}, "
            f"swing_window={swing_window}, "
            f"swing_count={swing_count}, "
            f"rr_ratio={rr_ratio}: {e}"
        )


# =========================
# RANK RESULTS
# =========================

results.sort(
    key=lambda x: x["index"],
    reverse=True
)


# =========================
# SHOW TOP 10
# =========================

print("\n==============================")
print("TOP 10 RESULTS")
print("==============================")

for rank, result in enumerate(results[:10], 1):

    print(
        f"\n#{rank}"
        f"\nlook_back: {result['look_back']}"
        f"\nswing_window: {result['swing_window']}"
        f"\nswing_count: {result['swing_count']}"
        f"\nRR: {result['rr_ratio']}:1"
        f"\nIndex: {result['index']:.3f}"
        f"\nReturn: {result['return_percent']:.2f}%"
        f"\nFinal Balance: {result['final_balance']:.2f}"
        f"\nTrades: {result['total_trades']}"
        f"\nWin Rate: {result['win_rate']:.2f}%"
        f"\nMax Drawdown: {result['maximum_drawdown']:.2f}%"
    )


# =========================
# SAVE RESULTS
# =========================

results.sort(
    key=lambda x: x["index"],
    reverse=True
)

with open(results_path, "w") as f:
    json.dump(results, f, indent=4)

print(f"\nResults saved to {results_path}")