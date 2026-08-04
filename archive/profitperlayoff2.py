import matplotlib.pyplot as plt

# Data
companies = ["Alphabet", "Microsoft", "Meta", "Tesla", "Amazon", "Avg US Salary"]
net_income = [100e9, 88.1e9, 39.6e9, 12.6e9, 59e9, None]
layoffs = [12000, 6000, 3600, 14000, 1000, None]
profit_per_layoff = [ni / lo for ni, lo in zip(net_income[:-1], layoffs[:-1])]
profit_per_layoff.append(59000)  # Approx. average US salary in 2024

# Plotting
fig, ax = plt.subplots(figsize=(10, 6))
bars = ax.bar(companies, profit_per_layoff, color=['steelblue'] * 5 + ['darkorange'])

# Labels and titles
ax.set_title("Profit per Layoff vs. Average U.S. Salary (2024)")
ax.set_ylabel("USD")
ax.set_ylim(0, max(profit_per_layoff) * 1.1)
ax.grid(axis='y', linestyle='--', alpha=0.7)

# Annotate bars
for bar in bars:
    height = bar.get_height()
    label = f'${height/1e6:.1f}M' if height > 1e6 else f'${int(height):,}'
    ax.annotate(label,
                xy=(bar.get_x() + bar.get_width() / 2, height),
                xytext=(0, 3),
                textcoords="offset points",
                ha='center', va='bottom', fontsize=8)

plt.tight_layout()
plt.show()
