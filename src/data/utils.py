def email_name_preprocessing(df):
    pattern = r'(?P<Name>.*?)(?:\s+<)?(?P<Email>[\w\.-]+@[\w\.-]+)>?'
    df[['Name', 'Email']] = df['From'].str.extract(pattern)
    df.replace('', pd.NA, inplace=True)
    df[['Name', 'Email']] 
    return df