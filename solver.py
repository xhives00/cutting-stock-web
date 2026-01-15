from dataclasses import dataclass
from typing import List, Tuple, Dict, Any


@dataclass
class Piece:
    length: int  # mm
    count: int


def best_cut(bar_length: int, pieces: List[Piece], kerf: int, max_pieces: int = 6) -> Dict[str, Any]:
    """
    Nájde najlepšiu kombináciu kusov pre jednu tyč.

    Vracia dict:
      - cost: hodnotenie riešenia
      - waste: zvyšný odpad na tyči
      - combo: zoznam dĺžok kusov, ktoré sa majú rezať na tejto tyči
    """

    best = {"cost": float("inf"), "waste": bar_length, "combo": []}
    current: List[int] = []  # budeme si ukladať LEN dĺžky (nie referencie na Piece objekty)

    def cost_function(waste: int, cuts: int, combo_lengths: List[int]) -> float:
        # približná "kriticita": preferuj kratšie kusy s nízkym zvyšným count
        # -> pre kriticitu potrebujeme vedieť count pre danú dĺžku
        # spravíme si lookup:
        counts = {p.length: p.count for p in pieces}
        criticality = sum(length / max(counts.get(length, 1), 1) for length in combo_lengths)
        return 1.0 * waste + 0.02 * cuts - 0.1 * criticality

    def backtrack(remaining: int, start_idx: int, cuts: int):
        nonlocal best, current

        waste = remaining
        c = cost_function(waste, cuts, current)
        if c < best["cost"]:
            best = {"cost": c, "waste": waste, "combo": current.copy()}

        if len(current) >= max_pieces:
            return

        for i in range(start_idx, len(pieces)):
            p = pieces[i]
            if p.count <= 0:
                continue

            needed = p.length + (kerf if current else 0)
            if needed > remaining:
                continue

            # jednoduchý pruning: ak už teraz viem, že odpad bude horší než best
            if remaining - needed >= best["waste"]:
                continue

            # choose
            p.count -= 1
            was_empty = (len(current) == 0)
            current.append(p.length)

            # počet rezov: keď pridávam ďalší kus po prvom, pribudne rez
            backtrack(remaining - needed, i, cuts + (0 if was_empty else 1))

            # unchoose
            current.pop()
            p.count += 1

    backtrack(bar_length, 0, 0)
    return best


def solve_cutting_stock(bar_length: int, items: List[Tuple[int, int]], kerf: int) -> Dict[str, Any]:
    """
    Web-friendly wrapper.
    items: [(length_mm, count), ...]

    Vracia dict s:
      - bars: zoznam tyčí s combo + waste
      - stats: real_bars, ideal_bars, efficiency, total_length, total_waste
    """

    pieces = [Piece(length, count) for length, count in items]
    pieces.sort(key=lambda p: p.length, reverse=True)

    if not pieces:
        return {"status": "error", "message": "Žiadne položky."}

    if min(p.length for p in pieces) <= 0:
        return {"status": "error", "message": "Dĺžky musia byť > 0."}

    # max_pieces: koľko najmenších kusov sa teoreticky zmestí do tyče
    max_pieces = int(bar_length / min(p.length for p in pieces))
    max_pieces = max(1, min(max_pieces, 50))  # ochrana proti extrémom

    # kópia pre štatistiky
    original_pieces = [Piece(p.length, p.count) for p in pieces]

    bars: List[Dict[str, Any]] = []

    # hlavná slučka
    while any(p.count > 0 for p in pieces):
        result = best_cut(bar_length, pieces, kerf, max_pieces)

        if not result["combo"]:
            return {
                "status": "error",
                "message": "Nie je možné viac kombinovať s aktuálnym nastavením.",
                "bars": bars
            }

        # odpočítanie kusov podľa combo dĺžok
        for length in result["combo"]:
            for orig in pieces:
                if orig.length == length and orig.count > 0:
                    orig.count -= 1
                    break

        bars.append({
            "combo": result["combo"],
            "waste": result["waste"],
            "cost": result["cost"]
        })

        # bezpečnostná brzda (aby to na free hostingu neviselo večne pri šialených vstupoch)
        if len(bars) > 5000:
            return {"status": "error", "message": "Príliš veľa tyčí (limit).", "bars": bars}

    real_bars = len(bars)
    total_length = sum(p.length * p.count for p in original_pieces)
    ideal_bars = (total_length + bar_length - 1) // bar_length  # ceil
    efficiency = (ideal_bars / real_bars) if real_bars else 0.0
    total_waste = sum(b["waste"] for b in bars)

    return {
        "status": "ok",
        "bars": bars,
        "stats": {
            "real_bars": real_bars,
            "ideal_bars": ideal_bars,
            "efficiency": efficiency,
            "total_length": total_length,
            "total_waste": total_waste,
            "kerf": kerf,
            "bar_length": bar_length
        }
    }
