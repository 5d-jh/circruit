def display_rank(point):
    rank_names = [
        "브론즈 I", "브론즈 II", "브론즈 III", "브론즈 IV", "브론즈 V",
        "실버 I", "실버 II", "실버 III", "실버 IV", "실버 V",
        "플레티넘 I", "플레티넘 II", "플레티넘 III", "플레티넘 IV", "플레티넘 V",
        "다이아몬드 I", "다이아몬드 II", "다이아몬드 III", "다이아몬드 IV", "다이아몬드 V",
    ]
    return rank_names[int(point//250)], point%250