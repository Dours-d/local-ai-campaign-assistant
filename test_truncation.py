def simulate_truncation(english, arabic, limit=75):
    combined = f"{english} | {arabic}"
    if len(combined) > limit:
        combined = combined[:limit-3] + "..."
    return combined

t1 = simulate_truncation("Help Mohammed complete his studies and help his family live", "ساعدو محمد على اكمال دراسته ومساعدة عائلته على العيش")
print(f"Truncated Title: {t1}")
print(f"Length: {len(t1)}")
