import pandas as pd

# happiness score
score_df = pd.read_excel("data/DataForFigure2.1WHR2023.xls")
score_df.rename(columns={'Country name': "country", 'Ladder score': "score"}, inplace=True)
score_df = score_df[["country", "score"]]
score_df["score"] = score_df["score"].round(3)

# income level
income_df = pd.read_excel("data/API_NY.GDP.PCAP.CD_DS2_en_excel_v2_55.xls",
                          sheet_name="Metadata - Countries")
income_df.rename(columns={'TableName': "country", 'IncomeGroup': "income"}, inplace=True)
income_df = income_df[["country", "income"]]

df = pd.merge(score_df, income_df, how="left", on="country")
df = df.fillna(value="Unknown")
print(df.info())
print(df.tail())
df.to_excel("data/merged_data.xlsx", index=False)

