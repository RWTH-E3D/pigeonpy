from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.image as mpimg
from matplotlib.lines import Line2D
import matplotlib.cm as cm


def plot_ap_overview(study, partition_keys, save_path=None):
    """Visualize AP results from a Study as a pie-chart grid.

    Parameters
    ----------
    study : Study
        A Study instance after run_calculation() has been called.
    partition_keys : list of tuple
        Three-element tuples (Dataholz ID, Dataholz insulation option, <attribute>)
        as passed to run_calculation().
    save_path : Path or str, optional
        Output path for the PNG. Defaults to ap_overview.png in cwd.
    """
    script_dir = Path(__file__).parent
    if save_path is None:
        save_path = Path.cwd() / "ap_overview.png"

    # ---- Insulation label lookup ----
    calc_in = study.calculation_input
    insulation_label = (
        calc_in.subset_df
        .merge(calc_in.partition_df, on="partition_id")
        .pivot(index="calculation_id", columns="partition_name", values="subset_name")
        .reset_index()
        .drop_duplicates(subset=["Dataholz ID", "Dataholz insulation option"])
        .set_index(["Dataholz ID", "Dataholz insulation option"])["Insulation Type and Thickness"]
        .to_dict()
    )

    # ---- Rows and constructions ----
    results = study.result["indicator_values"]
    unique_rows = list(dict.fromkeys(
        (str(idx[0]), str(idx[1])) for idx in results[partition_keys[0]].index
    ))
    unique_constructions = list(dict.fromkeys(r[0] for r in unique_rows))
    unique_rows.sort(key=lambda r: (unique_constructions.index(r[0]), insulation_label.get(r, "")))

    # ---- Per-partition info ----
    color_families = [cm.Blues, cm.Greens, cm.Oranges, cm.Reds, cm.Purples]
    partition_infos = []
    for i, key in enumerate(partition_keys):
        series  = results[key]
        p_name  = key[2]
        subsets = sorted({str(idx[2]) for idx in series.index})
        cmap_fn = color_families[i % len(color_families)]
        cmap    = {s: cmap_fn(0.35 + 0.45 * j / max(len(subsets) - 1, 1)) for j, s in enumerate(subsets)}
        ap_data = {(str(idx[0]), str(idx[1]), str(idx[2])): dataset.get_sum("ap")
                   for idx, dataset in series.items()}
        partition_infos.append((p_name, subsets, cmap, ap_data))

    # ---- Merge Load-bearing + Insulation → Function ----
    lb_idx  = next((i for i, p in enumerate(partition_infos) if p[0] == "Load-bearing"), None)
    ins_idx = next((i for i, p in enumerate(partition_infos) if p[0] == "Insulation"),   None)
    if lb_idx is not None and ins_idx is not None:
        lb_ap_data  = partition_infos[lb_idx][3]
        ins_ap_data = partition_infos[ins_idx][3]
        combined_ap_data = {}
        for dh_id, ins_opt, _ in lb_ap_data:
            if (dh_id, ins_opt, "Load-bearing") in combined_ap_data:
                continue
            ins_val = ins_ap_data.get((dh_id, ins_opt, "True"), 0)
            combined_ap_data[(dh_id, ins_opt, "Load-bearing")] = lb_ap_data.get((dh_id, ins_opt, "True"),  0)
            combined_ap_data[(dh_id, ins_opt, "Insulation")]   = ins_val
            combined_ap_data[(dh_id, ins_opt, "Other")]        = lb_ap_data.get((dh_id, ins_opt, "False"), 0) - ins_val
        first = min(lb_idx, ins_idx)
        partition_infos = (
            partition_infos[:first]
            + [("Function",
                ["Load-bearing", "Insulation", "Other"],
                {"Load-bearing": cm.Greens(0.85), "Insulation": cm.Greens(0.5), "Other": cm.Greens(0.2)},
                combined_ap_data)]
            + [p for i, p in enumerate(partition_infos) if i not in (lb_idx, ins_idx) and i > first]
        )

    # ---- Total AP per row ----
    row_total_ap = {
        (dh_id, ins_opt): sum(
            partition_infos[0][3].get((dh_id, ins_opt, s), 0) for s in partition_infos[0][1]
        )
        for dh_id, ins_opt in unique_rows
    }
    max_ap = max(abs(v) for v in row_total_ap.values()) if row_total_ap else 1.0

    n_rows = len(unique_rows)
    n_cols = len(partition_infos)

    # ---- Layout ----
    LINE_H        = 0.17
    cell_size     = 0.55
    img_width     = 2.0
    name_height   = 0.22
    label_width   = 1.0
    ap_col_width  = 0.8
    header_height = 0.35
    margin        = 0.15

    legend_section_heights = [(len(p[1]) + 1.5) * LINE_H for p in partition_infos]
    legend_height = max(legend_section_heights) + 0.1
    grid_offset   = margin + legend_height

    fig_w = margin + img_width + label_width + n_cols * cell_size + ap_col_width + margin
    fig_h = margin + legend_height + n_rows * cell_size + header_height + margin

    def fx(x): return x / fig_w
    def fy(y): return y / fig_h

    fig = plt.figure(figsize=(fig_w, fig_h))

    # ---- Legend ----
    section_w = (fig_w - 2 * margin) / n_cols
    for i, (p_name, subsets, cmap, _) in enumerate(partition_infos):
        leg_ax = fig.add_axes([fx(margin + i * section_w), fy(margin),
                               fx(section_w), fy(legend_section_heights[i])])
        leg_ax.set_axis_off()
        leg_ax.legend(
            handles=[mpatches.Patch(color="none", label=f"$\\bf{{{p_name}}}$")]
                    + [mpatches.Patch(color=cmap[s], label=s) for s in subsets],
            fontsize=5.5, loc="upper left", frameon=False,
            handlelength=1.0, handleheight=0.9, borderpad=0, labelspacing=0.3,
        )

    # ---- Column headers ----
    header_y = fy(grid_offset + n_rows * cell_size + header_height / 2)
    for x_in, label in (
        [(margin + (img_width - 0.1) / 2,                                              "Construction"),
         (margin + img_width + label_width / 2,                                        "Insulation\ntype")]
        + [(margin + img_width + label_width + (i + 0.5) * cell_size, p_name)
           for i, (p_name, _, _, _) in enumerate(partition_infos)]
        + [(margin + img_width + label_width + n_cols * cell_size + ap_col_width / 2, "Overall AP\n(d mol H⁺ eq.)")]
    ):
        fig.text(fx(x_in), header_y, label,
                 ha="center", va="center", fontsize=5.5, fontweight="bold", linespacing=1.3)

    # ---- Row labels + pie charts + AP column ----
    for row_idx, (dh_id, ins_opt) in enumerate(unique_rows):
        row_bottom = grid_offset + (n_rows - row_idx - 1) * cell_size
        row_mid_y  = fy(row_bottom + cell_size / 2)
        total_ap   = row_total_ap[(dh_id, ins_opt)]
        radius     = 0.4 + 0.6 * abs(total_ap) / max_ap if max_ap > 0 else 1.0

        fig.text(fx(margin + img_width + label_width - 0.08), row_mid_y,
                 insulation_label.get((dh_id, ins_opt), f"{dh_id}-{ins_opt}"),
                 ha="right", va="center", fontsize=5.5)

        for col_idx, (_, subsets, cmap, ap_data) in enumerate(partition_infos):
            values = {s: ap_data[(dh_id, ins_opt, s)] for s in subsets
                      if (dh_id, ins_opt, s) in ap_data and ap_data[(dh_id, ins_opt, s)] > 0}
            ax = fig.add_axes([fx(margin + img_width + label_width + col_idx * cell_size),
                               fy(row_bottom), fx(cell_size), fy(cell_size)])
            if values:
                ax.pie(list(values.values()), colors=[cmap[k] for k in values],
                       startangle=90, radius=radius)
            else:
                ax.text(0.5, 0.5, "—", ha="center", va="center",
                        transform=ax.transAxes, fontsize=9, color="#888888")
                ax.set_axis_off()

        fig.text(fx(margin + img_width + label_width + n_cols * cell_size + ap_col_width / 2),
                 row_mid_y, f"{total_ap * 10:.2f}", ha="center", va="center", fontsize=5.5)

    # ---- Construction images and names ----
    for construction_id in unique_constructions:
        row_indices  = [i for i, r in enumerate(unique_rows) if r[0] == construction_id]
        group_bottom = grid_offset + (n_rows - row_indices[-1] - 1) * cell_size
        group_top    = grid_offset + (n_rows - row_indices[0]) * cell_size
        img_height   = (group_top - group_bottom) * 0.75
        img_bottom   = (group_bottom + group_top) / 2 - img_height / 2

        img_ax = fig.add_axes([fx(margin), fy(img_bottom), fx(img_width - 0.1), fy(img_height)])
        img_ax.set_axis_off()
        png_path = script_dir / f"{construction_id}.png"
        if png_path.exists():
            img_ax.imshow(mpimg.imread(str(png_path)), aspect="equal")
        else:
            img_ax.text(0.5, 0.5, f"[{construction_id}]", ha="center", va="center",
                        fontsize=6, color="#aaaaaa", transform=img_ax.transAxes)

        fig.text(fx(margin + (img_width - 0.1) / 2), fy(img_bottom - name_height / 2),
                 construction_id, ha="center", va="center", fontsize=6)

    # ---- Separator ----
    sep_idx = sum(1 for r in unique_rows if r[0] == unique_constructions[0])
    sep_y   = fy(grid_offset + (n_rows - sep_idx) * cell_size)
    fig.add_artist(Line2D(
        [fx(margin), fx(margin + img_width + label_width + n_cols * cell_size + ap_col_width)],
        [sep_y, sep_y],
        transform=fig.transFigure, color="#666666", lw=0.8, linestyle="--",
    ))

    fig.savefig(save_path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"Saved to: {save_path}")


def _bar_axes(ax, x, values, bar_width, colors, ylabel, tick_labels, title):
    """Draw a single bar chart on ax with shared styling. Returns the bar container."""
    bars = ax.bar(x, values, bar_width, color=colors)
    ax.set_ylabel(ylabel)
    ax.set_xticks(x)
    ax.set_xticklabels(tick_labels, rotation=45, ha="right", fontsize=8)
    ax.set_title(title)
    return bars


def _bar_chart_setup(study, result_reference_flow):
    """Shared setup for the bar-chart functions: insulation labels, keys, tick
    labels, construction id list and the common x/figure-width values."""
    calc_in = study.calculation_input
    insulation_label = (
        calc_in.subset_df
        .merge(calc_in.partition_df, on="partition_id")
        .pivot(index="calculation_id", columns="partition_name", values="subset_name")
        .reset_index()
        .drop_duplicates(subset=["Dataholz ID", "Dataholz insulation option"])
        .set_index(["Dataholz ID", "Dataholz insulation option"])["Insulation Type and Thickness"]
        .to_dict()
    )

    keys = list(result_reference_flow.keys())
    tick_labels = [insulation_label.get(k, f"{k[0]}-{k[1]}") for k in keys]
    construction_ids = list(dict.fromkeys(k[0] for k in keys))

    n = len(keys)
    x = np.arange(n) * 0.5
    fig_w = max(7, n * 0.55)

    return keys, tick_labels, construction_ids, x, fig_w


def plot_weighted_score_bar(study, result_reference_flow, u_values, save_path=None):
    """Bar chart of the weighted score per construction.

    Parameters
    ----------
    study : Study
        A Study instance after run_calculation() has been called (used for insulation labels).
    result_reference_flow : dict
        Dict with (Dataholz ID, insulation option) tuples as keys and scalar values.
    u_values : dict
        Dict with the same keys mapping to U-values [W/(m²·K)].
    save_path : Path or str, optional
        Output path for the chart. Defaults to weighted_score_bar.png in cwd.
    """
    if save_path is None:
        save_path = Path.cwd() / "weighted_score_bar.png"

    keys, tick_labels, construction_ids, x, fig_w = _bar_chart_setup(study, result_reference_flow)
    weighted_values = [float(result_reference_flow[k] / u_values[k]) for k in keys]

    bar_width = 0.3
    palette = ["#6baed6", "#2171b5"]   # light blue, dark blue
    id_color = {cid: palette[i % len(palette)] for i, cid in enumerate(construction_ids)}
    bar_colors = [id_color[k[0]] for k in keys]
    legend_handles = [mpatches.Patch(color=id_color[cid], label=cid) for cid in construction_ids]

    fig, ax = plt.subplots(figsize=(fig_w, 6))
    _bar_axes(ax, x, weighted_values, bar_width, bar_colors, "Weighted score", tick_labels, "Weighted score")
    ax.legend(handles=legend_handles, fontsize=8, loc="upper left")
    fig.tight_layout()
    fig.savefig(save_path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"Saved to: {save_path}")


def plot_reference_flow_bar(study, result_reference_flow, u_values, save_path=None):
    """Bar chart of the result per reference flow, annotated with U-values.

    Parameters
    ----------
    study : Study
        A Study instance after run_calculation() has been called (used for insulation labels).
    result_reference_flow : dict
        Dict with (Dataholz ID, insulation option) tuples as keys and scalar values.
    u_values : dict
        Dict with the same keys mapping to U-values [W/(m²·K)].
    save_path : Path or str, optional
        Output path for the chart. Defaults to reference_flow_bar.png in cwd.
    """
    if save_path is None:
        save_path = Path.cwd() / "reference_flow_bar.png"

    keys, tick_labels, construction_ids, x, fig_w = _bar_chart_setup(study, result_reference_flow)
    ref_flow_values = [float(result_reference_flow[k]) for k in keys]

    bar_width = 0.3
    palette = ["#fdae6b", "#d94801"]   # light orange, dark orange
    id_color = {cid: palette[i % len(palette)] for i, cid in enumerate(construction_ids)}
    bar_colors = [id_color[k[0]] for k in keys]
    legend_handles = [mpatches.Patch(color=id_color[cid], label=cid) for cid in construction_ids]

    fig, ax = plt.subplots(figsize=(fig_w, 6))
    bars = _bar_axes(ax, x, ref_flow_values, bar_width, bar_colors,
                      "Weighted score / (1/U-value)", tick_labels, "Result per reference flow")
    for bar, key in zip(bars, keys):
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height() / 2,
            f"U = {u_values[key]} W/m²K",
            ha="center", va="center", fontsize=7, color="white",
            fontweight="bold", rotation=90,
        )
    ax.legend(handles=legend_handles, fontsize=8, loc="upper left")
    fig.tight_layout()
    fig.savefig(save_path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"Saved to: {save_path}")


def plot_indicators_bar(study, result_reference_flow,
                         partition_key=("Dataholz ID", "Dataholz insulation option"),
                         save_path=None):
    """Bar chart of raw AP and GWP values (before normalization/weighting).

    Parameters
    ----------
    study : Study
        A Study instance after run_calculation() has been called (used for insulation labels
        and raw indicator values).
    result_reference_flow : dict
        Dict with (Dataholz ID, insulation option) tuples as keys, used to determine the
        set of constructions to plot.
    partition_key : tuple, optional
        Partition key used to look up raw indicator values from study.lcia.result["indicator_values"].
        Defaults to ("Dataholz ID", "Dataholz insulation option").
    save_path : Path or str, optional
        Output path for the chart. Defaults to indicators_bar.png in cwd.
    """
    if save_path is None:
        save_path = Path.cwd() / "indicators_bar.png"

    keys, tick_labels, construction_ids, x, fig_w = _bar_chart_setup(study, result_reference_flow)

    raw_series = study.result["indicator_values"].get(partition_key)
    if raw_series is None:
        return

    gwp_values = [raw_series[k].get_sum("gwp-total") for k in keys]
    ap_values  = [raw_series[k].get_sum("ap")        for k in keys]

    gwp_palette = ["#74c476", "#238b45"]   # light green, dark green
    ap_palette  = ["#fc8d59", "#b30000"]   # light red, dark red
    gwp_id_color = {cid: gwp_palette[i % len(gwp_palette)] for i, cid in enumerate(construction_ids)}
    ap_id_color  = {cid: ap_palette[i  % len(ap_palette)]  for i, cid in enumerate(construction_ids)}
    gwp_bar_colors = [gwp_id_color[k[0]] for k in keys]
    ap_bar_colors  = [ap_id_color[k[0]]  for k in keys]

    bar_width_ind = 0.2

    fig, ax1 = plt.subplots(figsize=(fig_w, 6))
    ax1.bar(x - bar_width_ind / 2, gwp_values, bar_width_ind, color=gwp_bar_colors)
    ax1.set_ylabel("GWP (kg CO₂ eq.)", color="#238b45")
    ax1.tick_params(axis="y", labelcolor="#238b45")
    ax1.set_xticks(x)
    ax1.set_xticklabels(tick_labels, rotation=45, ha="right", fontsize=8)
    ax1.set_title("GWP and AP per construction (before normalization)")

    ax2 = ax1.twinx()
    ax2.bar(x + bar_width_ind / 2, ap_values, bar_width_ind, color=ap_bar_colors)
    ax2.set_ylabel("AP (mol H⁺ eq.)", color="#b30000")
    ax2.tick_params(axis="y", labelcolor="#b30000")

    legend_handles = (
        [mpatches.Patch(color=gwp_id_color[cid], label=f"{cid} – GWP") for cid in construction_ids]
        + [mpatches.Patch(color=ap_id_color[cid],  label=f"{cid} – AP")  for cid in construction_ids]
    )
    ax1.legend(handles=legend_handles, fontsize=8, loc="upper left")
    fig.tight_layout()
    fig.savefig(save_path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"Saved to: {save_path}")


