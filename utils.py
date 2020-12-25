def clean_df(df):
    import re
    import pandas as pd
    initial_rows = df.shape[0]
    ## Flags for errors in Time column
    def time_flag(text):
        pattern = '\d+/\d+\d+, \d+:\d+'
        if bool(re.findall(pattern, text)):
            return 1
        else:
            return 0

    ## Flags for errors in Text column
    def text_flag(text):
        if text == None:
            return 0
        else:
            return 1

    ## Returns msg sender name, or 0 for a notif
    def name_extractor(text):
        pattern = '\S:'
        pattern_2 = ' IPBA'
        match = re.search(pattern, text) ## will return span of indices if pattern found else None
        if match:
            end_index = match.span()[1]-1
            name = text[:end_index]
            match_2 = re.search(pattern_2, name)
            if match_2:
                name = name.replace(pattern_2, '')
            return name
        else:
            return 'Notification'

    def name_remover(text):
        pattern = '\S:'
        match = re.search(pattern, text)
        if match:
            end_index = match.span()[1]+1
            text = text[end_index:]
        return text


    df[['datetime_str','Text']] = df["text"].str.split(" - ", 1, expand=True)
    df = df.drop(columns = ['text'])
    df = df.dropna(how='all')
    df = df.reset_index(drop=True)




    df['TimeFlag'] = df.datetime_str.apply(time_flag) 
    # print('TimeFlags')
    # print(df.TimeFlag.value_counts())
    # print('882 rows with problems')



    df['TextFlag'] = df.Text.apply(text_flag)
    # print('TextFlags')
    # print(df.TextFlag.value_counts())
    # print('867 rows with problems')


    ## Replaced `None` values with empty string '' to facilitate addition
    df = df.fillna('')


    ## Move Text from datetime_str col to Text col
    for ind, row in df.iterrows():
        if df.loc[ind, 'TimeFlag'] == 0:
            df.loc[ind, 'Text'] = df.loc[ind, 'datetime_str'] + ' ' + df.loc[ind, 'Text']
            df.loc[ind, 'datetime_str'] = 0
            df.loc[ind, 'datetime_str'] = 0
            df.loc[ind, 'TextFlag'] = 1

    ## Drop 882rows with problems in date
    drop_index = df[df.datetime_str==0].index
    df = df.drop(drop_index, axis=0)
    
    # df[df.TextFlag==0] ## Fixed all TextFlag Errors so drop col now
    df.drop(columns=['TextFlag'], inplace = True)
    df.drop(columns='TimeFlag', inplace = True)

    df['Sender'] = df.Text.apply(name_extractor)
    df['Text'] = df.Text.apply(name_remover)
    
    df['datetime'] = pd.to_datetime(df['datetime_str'], format='%m/%d/%y, %H:%M')
    df.drop(columns=['datetime_str'], inplace=True)

    final_rows = df.shape[0]
    
    print('Succesfully cleaned dataframe')
    print(f'Rows before cleaning: {initial_rows}')
    print(f'Rows after cleaning: {final_rows}')
    return df