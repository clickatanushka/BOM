"""Video 10.2 - Build it: SQL -> pandas -> charts -> model
Run: python module_10_capstone/lesson_10_2_build_it.py"""

from module_10_capstone import capstone

print("Brief: \"Returns are eating our profit. What's going on, and can we predict them?\"\n")

raw = capstone.step_1_load_with_sql()               # Module 4: SQL inside Python
print(raw.head(3).to_string())

capstone.step_2_check(raw)                           # Module 6: same data as our pandas cleaning?
df, overall_rate = capstone.step_3_prepare(raw)
tables = capstone.step_4_where(df, overall_rate)     # Module 8: four return-rate charts
money = capstone.step_5_money(df)
model = capstone.step_6_predict(df)                  # Module 9: baseline, two models, flagging

results = {"overall_rate": overall_rate, "tables": tables, "money": money, "model": model}
print("\nStep 7 - insights and recommendations")
for number, (insight, action) in enumerate(capstone.step_7_insights(results), start=1):
    print(f"\n{number}. {insight}\n   -> {action}")
print(f"\nMoney: about {capstone.lakh(money['revenue_lost'])} of revenue "
      f"({money['share_of_revenue']:.1%}) came from returned orders "
      "(assumption: full refund, no resale, return shipping ignored).")
