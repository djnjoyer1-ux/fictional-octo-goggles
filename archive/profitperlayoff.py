import matplotlib.pyplot as plt

# Data
companies = ["Alphabet", "Microsoft", "Meta", "Tesla", "Amazon"]
net_income = [100e9, 88.1e9, 39.6e9, 12.6e9, 59e9]
layoffs = [12000, 6000, 3600, 14000, 1000]  # Amazon estimate

# Calculate profit per layoff
profit_per_layoff = [ni / lo for ni, lo in zip(net_income, layoffs)]

# Plotting
fig, ax = plt.subplots(figsize=(10, 6))
bars = ax.bar(companies, profit_per_layoff, color='steelblue')

# Labels and titles
ax.set_title("Profit per Layoff (2024)")
ax.set_ylabel("USD")
ax.set_ylim(0, max(profit_per_layoff) * 1.1)
ax.grid(axis='y', linestyle='--', alpha=0.7)

# Annotate bars
for bar in bars:
    height = bar.get_height()
    ax.annotate(f'${height/1e6:.1f}M',
                xy=(bar.get_x() + bar.get_width() / 2, height),
                xytext=(0, 3),
                textcoords="offset points",
                ha='center', va='bottom', fontsize=8)

plt.tight_layout()
plt.show()
