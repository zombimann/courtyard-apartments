"""
issb_cost_model.py -- ISSB block production cost model, Kenyan context.

Inputs marked [GIVEN] come from the operator. Everything else is a market input
that MUST be confirmed locally before the figures are quoted to anyone.

  python issb_cost_model.py
"""
import sys

# ─────────────────────────────────────────────────────────────────────────────
#  INPUTS
# ─────────────────────────────────────────────────────────────────────────────
# [GIVEN] production
BLOCKS_PER_BAG_MURRAM = 100        # 1 bag cement + 5 wheelbarrows murram
BLOCKS_PER_BAG_REDSOIL = 100       # 1 bag cement + 4 wheelbarrows red soil
WB_MURRAM = 5                      # wheelbarrows of murram per bag
WB_REDSOIL = 4                     # wheelbarrows of red soil per bag
CREW = 4                           # people producing blocks
OUTPUT_LOW, OUTPUT_MID, OUTPUT_HIGH = 350, 425, 500   # blocks per day
LABOUR_PER_BLOCK = 12.0            # KES, [GIVEN] recommended allocation

# [MARKET] confirm locally
CEMENT_BAG = (700.0, 750.0, 850.0)        # KES per 50 kg bag
CEMENT_TRANSPORT_BAG = (40.0, 60.0, 120.0)  # KES per bag delivered to site
MACHINE_DAY = (2000.0, 3000.0, 5000.0)    # KES per day, hired
CONSUMABLES_100 = 100.0                   # water, sheeting, PPE, tools per 100

WB_LITRES = 75.0                   # wheelbarrow capacity, litres
SAND_PER_M3 = 3000.0               # KES per m3 delivered, for clay stabilisation
CLAY_SAND_FRACTION = 0.30          # coarse sand added to clay soil, by volume

# wall build-up comparison (per m2 of finished wall face)
BLOCK_FACE_M2 = 0.29 * 0.14        # 290 x 140 mm face
WASTE = 1.05
BLOCKS_PER_M2 = 1.0 / BLOCK_FACE_M2 * WASTE
# Joints are DRY. The interlock carries alignment and shear; there is no mortar
# in the running joints. Cement appears only at special junctions -- to RC
# columns, to frames and lintels, to the plinth, to the ring beam, and where
# ISSB meets a different material.
LAID_PER_DAY = 350                 # dry-stacked, so faster than mortared masonry
MASON_DAY = 1200.0                 # KES
ISSB_SPECIAL_JOINTS_M2 = 25.0      # KES per m2, cement at junctions only

# Foundation is ordinary machine-cut quarry stone, not reinforced concrete.
# The same foundation serves either wall type, so it does not change the
# comparison below.
STONE_PER_M2 = 10.4                # 450 x 225 mm machine-cut quarry stone
STONE_EACH = 35.0                  # KES
STONE_MORTAR_M2 = 180.0
STONE_MASON_M2 = 500.0
RENDER_M2 = 900.0                  # two-coat render, two faces


def money(x):
    return f"{x:,.0f}"


def per_100(cement, ctrans, machine_day, output, labour=LABOUR_PER_BLOCK,
            consumables=CONSUMABLES_100, extra=0.0):
    """Cost of a 100-block batch, and the per-block figure."""
    machine = 100.0 * machine_day / output
    row = {
        "cement": cement,
        "cement transport": ctrans,
        "labour (100 x %g)" % labour: labour * 100.0,
        "machine hire": machine,
        "consumables": consumables,
    }
    if extra:
        row["soil preparation"] = extra
    return row, sum(row.values())


def table(headers, rows, widths=None):
    widths = widths or [max(len(str(r[i])) for r in [headers] + rows)
                        for i in range(len(headers))]
    line = "  ".join(str(h).ljust(w) for h, w in zip(headers, widths))
    print(line)
    print("  ".join("-" * w for w in widths))
    for r in rows:
        print("  ".join(str(c).ljust(w) for c, w in zip(r, widths)))


def main():
    print("=" * 78)
    print("ISSB BLOCK PRODUCTION — COST MODEL")
    print("=" * 78)

    # ---------------------------------------------------------------- base case
    print("\n1.  BASE CASE — 100-block batch, murram on site\n")
    cement, ctrans, mach = 750.0, 60.0, 3000.0
    out = OUTPUT_MID
    row, total = per_100(cement, ctrans, mach, out)
    rows = [[k, money(v), f"{100*v/total:5.1f}%"] for k, v in row.items()]
    rows.append(["TOTAL per 100 blocks", money(total), "100.0%"])
    rows.append(["PER BLOCK", f"{total/100:.2f}", ""])
    table(["line item", "KES", "share"], rows, [26, 10, 8])

    print(f"\n  Crew of {CREW}, output {out} blocks/day.")
    print(f"  Daily production cost : KES {money(total*out/100)}")
    print(f"  Daily labour bill     : KES {money(LABOUR_PER_BLOCK*out)}"
          f"   -> KES {money(LABOUR_PER_BLOCK*out/CREW)} per person per day")

    # ------------------------------------------------------- sensitivity: output
    print("\n2.  SENSITIVITY — daily output (machine is hired per day)\n")
    rows = []
    for o in (OUTPUT_LOW, OUTPUT_MID, OUTPUT_HIGH):
        _, t = per_100(cement, ctrans, mach, o)
        rows.append([f"{o}", f"{100*mach/o:.2f}", f"{t/100:.2f}",
                     f"{money(t*o/100)}", f"{money(LABOUR_PER_BLOCK*o/CREW)}"])
    table(["blocks/day", "machine/block", "cost/block", "day cost", "KES/person/day"],
          rows, [12, 15, 12, 12, 16])

    # ------------------------------------------------------ sensitivity: cement
    print("\n3.  SENSITIVITY — cement price and its transport\n")
    rows = []
    for c in CEMENT_BAG:
        for t in CEMENT_TRANSPORT_BAG:
            _, tot = per_100(c, t, mach, out)
            rows.append([money(c), money(t), f"{tot/100:.2f}",
                         f"{100*(c+t)/tot:.1f}%"])
    table(["cement/bag", "transport/bag", "cost/block", "cement share"],
          rows, [13, 15, 12, 14])
    print("\n  Cement transport is a rounding error against labour and the machine.")

    # ------------------------------------------------------ sensitivity: machine
    print("\n4.  SENSITIVITY — machine day rate\n")
    rows = []
    for m in MACHINE_DAY:
        _, t = per_100(cement, ctrans, m, out)
        rows.append([money(m), f"{100*m/out:.2f}", f"{t/100:.2f}",
                     f"{money(t*out/100)}"])
    table(["KES/day", "per block", "cost/block", "day cost"], rows, [12, 12, 12, 12])

    # ------------------------------------------------------------ the soil trap
    print("\n5.  THE SOIL TRAP — what happens if soil must be imported\n")
    wb_m3 = WB_LITRES / 1000.0
    soil_per_100 = WB_MURRAM * wb_m3
    soil_per_block = soil_per_100 / 100.0
    print(f"  {WB_MURRAM} wheelbarrows x {WB_LITRES:.0f} L = {soil_per_100:.3f} m3"
          f" loose soil per 100 blocks")
    print(f"  = {soil_per_block*1000:.2f} litres per block")
    print(f"  = {soil_per_block*BLOCKS_PER_M2:.4f} m3 per m2 of wall\n")
    rows = []
    for label, per_m3 in (("won on site", 0.0), ("trucked 5 km", 1200.0),
                          ("trucked 20 km", 2500.0), ("trucked 50 km", 4000.0)):
        add = soil_per_block * per_m3
        _, t = per_100(cement, ctrans, mach, out, extra=add * 100)
        rows.append([label, money(per_m3), f"{add:.2f}", f"{t/100:.2f}",
                     f"{t/100/ (total/100) * 100:.0f}%"])
    table(["soil source", "KES/m3", "add/block", "cost/block", "vs base"],
          rows, [14, 10, 12, 12, 9])
    print("\n  Importing soil can add 50% or more to the block cost. Winning it")
    print("  site is not a saving — it is the whole business model.")
    # --------------------------------------------------------- clay site penalty
    print("\n6.  CLAY SITE — coarse sand stabilisation\n")
    rows = []
    for frac in (0.25, 0.30, 0.40):
        sand_m3 = soil_per_block * frac
        add = sand_m3 * SAND_PER_M3
        _, t = per_100(cement, ctrans, mach, out, extra=add * 100)
        rows.append([f"{frac*100:.0f}%", f"{sand_m3*1000:.2f}",
                     f"{add:.2f}", f"{t/100:.2f}"])
    table(["sand added", "litres/block", "KES/block", "cost/block"],
          rows, [12, 14, 12, 12])
    print("\n  Clay must be blended or it will crack as it dries. Budget for it,")
    print("  or test the soil before committing to the site.")

    # ------------------------------------------------------- wall cost comparison
    print("\n7.  WALL COST PER M2 OF FINISHED FACE\n")
    blocks_m2 = BLOCKS_PER_M2
    isssb_units = blocks_m2 * total / 100.0
    isssb_lay = blocks_m2 * (MASON_DAY / LAID_PER_DAY)
    isssb_total = isssb_units + isssb_lay + ISSB_SPECIAL_JOINTS_M2

    stone_units = STONE_PER_M2 * STONE_EACH
    stone_fair = stone_units + STONE_MORTAR_M2 + STONE_MASON_M2
    stone_rend = stone_fair + RENDER_M2

    print(f"  blocks per m2 of face : {blocks_m2:.1f}"
          f"  ({BLOCK_FACE_M2*1e4:.0f} cm2 face, {WASTE:.2f} waste)")
    print(f"  laying rate           : {LAID_PER_DAY} blocks/day dry-stacked")
    rows = [
        ["ISSB 140 mm, dry-jointed, fair-faced", money(isssb_units),
         money(isssb_lay), money(ISSB_SPECIAL_JOINTS_M2), money(isssb_total)],
        ["Quarry stone 200 mm, fair-faced", money(stone_units), money(STONE_MASON_M2),
         money(STONE_MORTAR_M2), money(stone_fair)],
        ["Quarry stone 200 mm, rendered", money(stone_units), money(STONE_MASON_M2),
         money(STONE_MORTAR_M2 + RENDER_M2), money(stone_rend)],
    ]
    table(["wall type", "units", "laying", "mortar/finish", "TOTAL/m2"],
          rows, [36, 10, 10, 14, 11])
    print(f"\n  ISSB dry-jointed fair-faced vs quarry stone rendered: "
          f"{100*(1-isssb_total/stone_rend):.0f}% cheaper per m2 of wall.")
    print("  Fair, because ISSB is designed to be left fair-faced while quarry")
    print("  stone is normally rendered. Render the ISSB and the advantage goes.")
    print("\n  Note: the ISSB wall carries NO jointing cement beyond the block mix")
    print("  itself. Quarry stone masonry carries a full 1:4 mortar bed.")

    print("\n" + "=" * 78)
    print("INPUTS TO CONFIRM: cement price, cement transport, machine day rate,")
    print("mason day rate, stone price, sand price, render rate. The [GIVEN]")
    print("production figures are the operator's; the derived costs move with")
    print("the market inputs, so re-run this before quoting anyone.")
    print("=" * 78)


if __name__ == "__main__":
    main()
