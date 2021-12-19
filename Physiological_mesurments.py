#!/usr/bin/env python
# coding: utf-8

# In[3]:


# import os
import pandas as pd
import re
from openpyxl import load_workbook
import numpy as np
from  datetime import datetime
import plotly.graph_objects as go
import pingouin as pg
from openpyxl.drawing.image import Image
import seaborn as sns
import re
import plotly.express as px
from sklearn.decomposition import PCA
import dataframe_image as dfi
from datetime import datetime as dt


# In[4]:


#insert the path
path=r'C:\Users\bradf\Dropbox\Yarden\yarden\winter 20-21\drought\part 1' #put the location
#The index file path
ind_file='\index-drought part 1.xlsx'
#The date of sampling as it in the index file
dates='Weight' #date of samples 
os.chdir(path)


# In[5]:


#adding the folders of needed 

if not os.path.isdir('input'):
    os.makedirs('input')
if not os.path.isdir('plots'):
    os.makedirs('plots')
if not os.path.isdir('output'):
    os.makedirs('output')
if not os.path.isdir('image'):
    os.makedirs('image')
if not os.path.isdir('image//line'):
    os.makedirs('image//line')
if not os.path.isdir('image//box'):
    os.makedirs('image//box')
if not os.path.isdir('tables'):
    os.makedirs('tables')


#reading the index file
index_day=pd.read_excel(path+ind_file,sheet_name=dates, index_col='Plant number')
index_day.dropna(axis=1,how='all',inplace=True)
index_day.index=index_day.index.astype(str)
index_day['Plant_Name']=index_day.index
index_day.insert(2, 'Plant_Name', index_day.index, True) 


clear_index=pd.read_excel(path+ind_file,sheet_name='Clear', index_col='Plant number')
clear_index.index=clear_index.index.astype(str)
#clear_index['Plant_Name']=clear_index.index
clear_index.insert(2, 'Plant_Name', clear_index.index, True) 


# In[6]:


def outliers_modified_z_score(ys,threshold=2.5):
    median_y = ys.median()
    median_absolute_deviation_y = np.median([np.abs(y - median_y) for y in ys])
    modified_z_scores = [0.6745 * (y - median_y) / median_absolute_deviation_y
                         for y in ys]
        
    return (np.abs(modified_z_scores) > threshold)

def outliers_remover(df,col):
    gro=df.groupby(['Treatment','Line'])[col]
    for name, group in gro:
        group=group.dropna()
        if len(group)<4 & len(group)>0 :
            print (f'{name} group is very small ({len(group)})!!!')
        else:
            n=outliers_modified_z_score(group)
            if any(n)== True:
                #print (f'Delete Plants in group:{name}')
                for p in range (len(n)):
                    if n[p]==True:
                        #print (gro.get_group((i[0],i[1])).index[p])
                        #print (group.index[p])
                        df.drop(axis=0, index=group.index[p], inplace=True)
            if len(group)<4:
                print (f'in {col} {name} , is small the 4')
    return (df)

#creating the box plots
def box_plots (df2, col='sheet_name',satistics='',dates='00/00/00'):
    fig = px.box(df2, x='Line', y=col, color="Treatment",points="all",hover_name=df2.index,
                title=(f'{satistics} {dates}'))
   # fig.update_traces(quartilemethod="exclusive") # or "inclusive", or "linear"  exclusive by default
    if not os.path.isdir(path+'//image//box//'+dates):
        os.makedirs(path+'//image//box//'+dates)
    fig.write_image(path+f'//image//box//{dates}//{col}_{satistics}.jpeg')
    #fig.show()
    

def check_groups(first, second,df):
#יבדוק בין קבוצות האם הם דומים בקבוצות השונות שלהם
    if first in df.index:
        A=list(df[df.index==first]['B'])
        B=list(df[df.index==second]['B'])
    else:
        A=list(df[df['B']==first].index)
        B=list(df[df['B']==second].index)
    return A==B

def reading_CSV(p):
#readinbg CSV file and adjust them the the formant
    df=pd.read_csv(p,index_col='Timestamp')
    col=df.columns.to_list()
    for n in range(len(col)):
        parameter=(re.search('\-(.*?)\(', col[n]).group(1).lstrip(' '))#
        col[n]= re.search('\(([^)]+)', col[n]).group(1) #reading only the numbers in the breckets
    df.columns=col
    df.index=pd.to_datetime(df.index)
    df.dropna(axis=1, how='all', inplace=True)
    df=df.T
    if parameter in ['Weather station PARLight ', 'Weather Station VPD ']:
        df.rename(index={df.index[0]:parameter},inplace=True)
        #df.index[0]=
    return (df)

def number_check(n):
#jump from Z to a and pass the simbles between.
    if n== 91:
        n= 97
    return (n)

def lable_to_groups(limited):
#מקבל טבלה לי רמת פי ווליו ומחזיר את אות כל קבוצה לפי סקניפקטיות
    significants={}#label dictnery 
    letter_order=65 #the number of the letter A
    Li=list(np.unique(limited.index)) #get list of the uniqe groups in columns A
    LB=list(np.unique(limited['B'])) #get list of the uniqe groups in columns B 
    for index, row in limited.iterrows(): #loop to run over the row
        if letter_order== 65: #checking if it in the first character If yes it will give character to the groups in line one
            significants[index]=(chr(letter_order))
            letter_order+= 1
            letter_order=number_check(letter_order)
            significants[row['B']]=(chr(letter_order))
        elif index not in significants.keys():
        #if it not the first row it will check it 
            for n in Li[:Li.index(index)]: #& index not in significants.keys():
                if index not in significants.keys():
                    if check_groups(index,n,limited):
                        significants[index]=(significants[n])
                    else:
                        letter_order+= 1
                        letter_order=number_check(letter_order)
                        significants[index]=(chr(letter_order))
        if row['B'] not in significants.keys():
            for n in LB[:LB.index(row['B'])]: #& index not in significants.keys():
                if n not in significants.keys():
                    if check_groups(row['B'],n,limited):
                        significants[row['B']]=(significants[n])
                    else:
                        letter_order+= 1
                        letter_order=number_check(letter_order)
                        significants[row['B']]=(chr(letter_order))
    return (significants)
    
    

def lable_adding (lite, s,lable):
#recived df will all the unsignificant p-value between groups  
    for n in range (len(lite)): #loop on the df
        #add the lable to columns B from the columns A
        if lite.index[n] in s.keys(): #cheking it got singficent lable
            if lite.iloc[n,0] not in lable.keys(): #if B have key in in the dictionery 
                lable[lite.iloc[n,0]]=s[lite.index[n]] #add to dictionery if not and give him the lable of columns A
            if s[lite.index[n]][0] not in lable[lite.iloc[n,0]]: 
                lable[lite.iloc[n,0]]=lable[lite.iloc[n,0]]+s[lite.index[n]] #add the lable from column A to B 


        #add the lable to columns A from the columns B
        if lite.iloc[n,0] in s.keys():
            if lite.index[n] not in lable.keys():
                lable[lite.index[n]]=s[lite.iloc[n,0]]
            if s[lite.iloc[n,0]][0] not in lable[lite.index[n]]:
                lable[lite.index[n]]=lable[lite.index[n]]+s[lite.iloc[n,0]]

    for r in lable.keys():
    #sorting the lable by alpah-betic 
        lable[r]=''.join((sorted(lable[r])))
    return lable


def group_signification_lable (df, col):
    #it wll resive DF with Treatment and line columns and the columns name
    #retuen df with columns that have compact letter display (cld)
    #df['Group']=df['Treatment']+' '+df['Line']
    lable={}
    o=pg.pairwise_tukey(data=df, dv=col, between='Group')
    o.set_index('A',inplace=True) #set the index
    if not o[o['p-tukey']<0.05].empty:
        l= o[o['p-tukey']<0.05] #gathering all the signficatnt calls
        s=lable_to_groups(l)
        for k in s.keys():
            lable[k]=s[k]
        lable=lable_adding(o[o['p-tukey']>=0.05],s,lable)
    else:
        for G in df.Group.unique():
            lable[G]='A'
    return (lable)

def box_writer(df,lb,col,satistics='',dates='00/00/00'):
#creating the box plots
    fig = go.Figure()
    for g in df.Group.unique():
        fig.add_trace(go.Box(
            y=df[df['Group']==g][col],
            name=g+', '+ lb[g]+'\n ('+str(df[df['Group']==g][col].count())+")",
            boxpoints='all'))
        fig.update_traces(hovertext=df.index, selector=dict(type='box'))
    fig.update_layout(title_text=(f'{col} {satistics} {dates}'))
    fig.update_layout(width=2000, height=1200)
    fig.update_layout(font_size=24)
    if not os.path.isdir(path+'//image//box//'+dates):
        os.makedirs(path+'//image//box//'+dates)
    fig.write_image(path+f'//image//box//{dates}//{col}_{satistics}.jpeg')
    #fig.show()

def add_treatment_and_line(licor,day):
###add plant name, treatment, line and avrage rows###
    index=pd.read_excel(path+ind_file, index_col='Plant number',sheet_name=day)
    index.dropna(subset=['obs'],inplace=True)
    index.index=index.index.astype(str)
    for i in index.index:
        obs= index.loc[i,'obs']
        if isinstance(obs, str): #if is list to chack if there are more then one chack
            obs=list(map(int,list(obs.split(','))))#get the list of the obserbes on the plant
            licor.loc[obs[0],'Plant number']=i
            if len(obs)>1:            
                for ob in range (len(obs))[1:]:
                    #licor.loc[str(obs),:]=licor.loc[obs,:].mean() #if you want to mean all the observes 
                    licor.loc[obs[ob],'Plant number']=(f'{i} ({ob+1})')
                    licor.loc[obs[ob],'Treatment']=index.loc[i,'Treatment']
                    licor.loc[obs[ob],'Line']=index.loc[i,'Line']
                    #licor.drop(obs, axis=0, index=None, columns=None, level=None, inplace=True, errors='raise')      
        else:
            licor.loc[obs,'Plant number']=i
            licor.loc[obs,'Treatment']=index.loc[i,'Treatment']
            licor.loc[obs,'Line']=index.loc[i,'Line']
    return (licor)


def reading_files(file):
    path_read=r'tables//'+file.split('.')[0]+'//'+file
    row=pd.read_excel(path_read, index_col='Plant number',sheet_name='Row')
    row.dropna(axis=1, how='all', inplace=True)
    out=pd.read_excel(path_read, index_col='Plant number',sheet_name='outliers')
    out.dropna(axis=1, how='all', inplace=True)
    Line_graph (row.drop(['Plant_Name'], axis=1),file.split('.')[0]+' Row')
    Line_graph (out.drop(['Plant_Name'], axis=1),file.split('.')[0]+' Outliers')
    #for col in row.columns[3:]:
     #   box_plots(row, col=col,dates=col)
      #  box_plots(out, col=col,dates=col)
    
def Line_graph (in_df,col=''):
    df=in_df.groupby(['Treatment','Line'])
    #print (df.count().head)
    #df.head()
    fig = go.Figure()
    for name, group in df:
        dash='dashdot'
        #count= (str(group.count()[2:][0]))
        if name[0]== 'Control':
            fig.add_trace(go.Scatter(x=group.mean().index, y=group.mean(),name=name[0]+' '+name[1],
                            mode='lines+markers',
                            line=dict(dash=dash),
                            error_y=dict(type='data', array=group.sem()),
                                    ))
        else:
            fig.add_trace(go.Scatter(x=group.mean().index, y=group.mean(),name=name[0]+' '+name[1],
                            mode='lines+markers',
                            error_y=dict(type='data', array=group.sem()),
                                    ))
        fig.update_traces(connectgaps=True, selector=dict(type='scatter'))
            
    listToStr = ' '.join([str(elem) for elem in col.split(' ')[:-1]])
    if not os.path.isdir('image//line//'+listToStr):
        os.makedirs('image//line//'+listToStr)
    #fig.show()
    fig.update_layout(height=800,width=1500)
    fig.update_layout(legend_font_size=18)
    fig.update_layout(legend_title_font_size=15)
    fig.update_layout(font_size=20)
    fig.update_layout(
    title={
        'text': col,
        'y':0.93,
        'x':0.4,
        'xanchor': 'center',
        'yanchor': 'top'})
    fig.write_image('image//line//'+listToStr+'//'+col+'.jpeg')
    #fig.show()


# In[61]:


###################orentated the data to df and save it#################
###################will use for the whole expitiemtn analysis################

#for dates in os.listdir(r'input'):
#daily_traspiration=reading_CSV(path+'\\client\Daily Transpiration__GraphViewer.csv')
licor=pd.DataFrame()
if os.path.isdir(r'input\\'+ dates):
    for files_input in os.listdir(r'input\\'+ dates):
        if 'licor' or 'Licor' in files_input:
            r=list(pd.read_excel(r'input\\'+ dates+'\\'+files_input, index_col=0).index).index('[Data]')
            try:
                licor=pd.read_excel(r'input\\'+ dates+'\\'+files_input,header=0,skiprows=r+3, index_col='obs')
            except:
                print ('ckeck the licor file!!!!')
            if licor.empty:
                pass
            else:
                licor=licor[licor.index!='Const:S'] 
                ad_licor=add_treatment_and_line(licor,str(dates))
                ad_licor.reset_index(inplace=True)
                ad_licor.set_index('Plant number',inplace=True)
                ad_licor[ad_licor.index.notnull()]
                patameters=ad_licor.iloc[0,:]
                ad_licor=ad_licor.iloc[1:,:]


                for i in index_day.index:
                    if not pd.isna (index_day.loc[i,'obs']):
                        if ',' in str(index_day.loc[i,'obs']):
                            lis=list(index_day.loc[i,'obs'].split(','))
                            if len(lis)>1:            
                                for l in range (len(lis))[1:]:

                                    index_day.loc[f'{i} ({l+1})','Treatment']=ad_licor.loc[f'{i} ({l+1})','Treatment']
                                    index_day.loc[f'{i} ({l+1})','Line']=ad_licor.loc[f'{i} ({l+1})','Line']
                                    index_day.loc[f'{i} ({l+1})','Plant_Name']=i


                for col in clear_index.columns[4:]:
                    if col in ad_licor.columns: #and col!='obs' and col!='Treatment' and col!='Line':
                       # for i in index:
                        #index_day.loc[i,col]=ad_licor.loc[i,col]
                        for i in index_day.index:
                            if i in ad_licor.index:
                                index_day.loc[i,col]=ad_licor.loc[i,col]
                        index_day[col] =index_day[col].apply(pd.to_numeric, downcast='unsigned', errors='coerce')
                        #index_day[col]=pd.to_numeric(index_day[col], downcast='float')

if 'E' in index_day.columns and 'A' in index_day.columns:
    index_day['WUE']=index_day['A']/index_day['E']
if 'Osmotic potantional' in index_day.columns:
    index_day['Osmotic potantional (MPa)']=index_day['Osmotic potantional']*2.5/1000*(-1)
    index_day.drop('Osmotic potantional', axis=1, index=None, columns=None, level=None, inplace=True, errors='raise')
if 'Soil WP' in index_day.columns:
    index_day['Soil WP (MPa)']=index_day['Soil WP']*2.5/1000*(-1)
    index_day.drop('Soil WP', axis=1, index=None, columns=None, level=None, inplace=True, errors='raise') 
if 'Leaf WP (kPs)' in index_day.columns:
    index_day['Leaf WP (MPa)']=index_day['Leaf WP (kPs)']/1000*(-1)
    index_day.drop('Leaf WP (kPs)', axis=1, index=None, columns=None, level=None, inplace=True, errors='raise')    
if 'xylem WP (kPs)' in index_day.columns or 'Xylem WP (kPs)' in index_day.columns:
    try: 
        index_day['Xylem WP (MPa)']=index_day['xylem WP (kPs)']/1000*(-1)
        index_day.drop('xylem WP (kPs)', axis=1, index=None, columns=None, level=None, inplace=True, errors='raise') 
    except:
        index_day['Xylem WP (MPa)']=index_day['Xylem WP (kPs)']/1000*(-1)
        index_day.drop('Xylem WP (kPs)', axis=1, index=None, columns=None, level=None, inplace=True, errors='raise')
if 'Leaf WP (MPa)' in index_day.columns and 'Osmotic potantional (MPa)' in index_day.columns:
    index_day['Turgor pressure']=index_day['Leaf WP (MPa)']-index_day['Osmotic potantional (MPa)']
    
#plant Hydrolic: Normelized Transpiration/(leaf WP-Soil WP)
if 'Leaf WP (MPa)' in index_day.columns and 'Soil WP (MPa)' in index_day.columns and 'E' in index_day.columns:
    index_day['Plant Hydraulic_Lic']= index_day['E']/(index_day['Soil WP (MPa)']-index_day['Leaf WP (MPa)'])
#Leaf Hydrolic: Normelized Transpiration/(leaf WP-Xylem WP)
if 'Leaf WP (MPa)' in index_day.columns and 'Xylem WP (MPa)' in index_day.columns and 'E' in index_day.columns: 
    index_day['Leaf Hydraulic_Lic']= index_day['E']/(index_day['Xylem WP (MPa)']-index_day['Leaf WP (MPa)'])
#Root Hydrolic: Normelized Transpiration/(leaf WP-Soil WP)
if 'Soil WP (MPa)' in index_day.columns and 'Xylem WP (MPa)' in index_day.columns and 'E' in index_day.columns: 
    index_day['Root Hydraulic_Lic']= index_day['E']/(index_day['Soil WP (MPa)']-index_day['Xylem WP (MPa)'])
#index_day=index_day[index_day.Treatment != 'Pre-Flooding ']
#index_day['Leaf WP (MPa) per size']=index_day['Leaf WP (MPa)']/index_day['S']
#index_day.drop('S',axis=1)
if "Fv'/Fm'" in index_day.columns:
    index_day.rename(columns={"Fv'/Fm'": 'FvFm'}, errors="raise",inplace=True)
index_day.dropna(inplace=True, axis=1, thresh=5)
#index_day.dropna(inplace=True, axis=0 )
if dates=='Weight':
    index_day['Shoot-Root ratio']=index_day['Shoot Dry weight (g)']/index_day['Root Dry weight (g)']
    index_day['Biomass Allocation']=index_day['Root Dry weight (g)']/index_day['Shoot Dry weight (g)']+index_day['Root Dry weight (g)']
    if 'Crown Dry weight (g)' in index_day.columns:
        index_day['Shoot Root ratio-with Crown']=index_day['Shoot Dry weight (g)']/(index_day['Root Dry weight (g)']+index_day['Crown Dry weight (g)'])
        index_day['Shoot-Rhizome ratio']=index_day['Shoot Dry weight (g)']/index_day['Crown Dry weight (g)']
        index_day['Root-Rhizome ration']=index_day['Root Dry weight (g)']/index_day['Crown Dry weight (g)']
        index_day['Biomass Allocation- Crown part of the root']=(index_day['Root Dry weight (g)']+index_day['Crown Dry weight (g)'])/(index_day['Shoot Dry weight (g)']+index_day['Root Dry weight (g)']+index_day['Crown Dry weight (g)'])
        index_day['Biomass Allocation- Crown not part of the root']=index_day['Root Dry weight (g)']/(index_day['Shoot Dry weight (g)']+index_day['Root Dry weight (g)']+index_day['Crown Dry weight (g)'])
index_day= index_day.loc[:,~index_day.columns.duplicated()]
if not os.path.isdir('output\\'+dates):
    os.makedirs('output\\'+dates)
index_day.to_excel(path+'\\output\\'+dates+'\\full_excel_'+dates+'.xlsx', sheet_name=dates)


# In[62]:


##################creating plots by group and treatments#####################


index_day['Group']=index_day['Treatment']+' '+index_day['Line']
if 'Avrage Spad' in index_day.columns:
    lb= group_signification_lable (index_day, 'Avrage Spad')
    box_writer(index_day,lb,'Avrage Spad','Row',dates=dates)
    outliers=index_day.copy()
    outliers=outliers_remover(outliers,'Avrage Spad')
    lb= group_signification_lable (outliers, 'Avrage Spad')
    box_writer(outliers,lb,col,'Outliers',dates=dates)
else:   
    for col in index_day.columns[4:-1]:
        if 'Spad' in str(index_day.columns):
            pass
        else:
            try:
                try:
                    lb= group_signification_lable (index_day, col)
                except:
                    pass
                box_writer(index_day,lb,col,'Row',dates=dates)
                outliers=index_day.copy()
                outliers=outliers_remover(outliers,col)
                try:
                    lb= group_signification_lable (outliers, col)
                except:
                    pass
                box_writer(outliers,lb,col,'Outliers',dates=dates)
            except:
                print (col)
            
index_day.drop(columns='Group', inplace=True)

table_R=index_day.copy()
table_O=outliers.copy()
for col in table_R.columns[4:]:
    if col!='salt constration (Ec/m)':
        if not os.path.isdir(r'tables//'+col):
            os.makedirs(r'tables//'+col)
            with pd.ExcelWriter(path+'//tables//'+col+'//'+col+'.xlsx') as writer:
                row_t=table_R[['Treatment','Line','Plant_Name',col]]
                row_t.columns=['Treatment','Line','Plant_Name',dates]
                out_t=table_O[['Treatment','Line','Plant_Name',col]]
                out_t.columns=['Treatment','Line','Plant_Name',dates]
                row_t.to_excel(writer, sheet_name='Row')
                out_t.to_excel(writer, sheet_name='outliers')
        else:
            path_read=path+'//tables//'+col+'//'+col+'.xlsx'
            row_t=pd.read_excel(path_read, index_col='Plant number',sheet_name='Row')
            out_t=pd.read_excel(path_read, index_col='Plant number',sheet_name='outliers')
            row_t.index=row_t.index.astype(str)
            out_t.index=out_t.index.astype(str)
            for ind in table_R.index:
                row_t.loc[ind,dates]=table_R.loc[ind,col]
                if str(row_t.loc[ind,'Treatment'])=='nan':
                    row_t.loc[ind,'Treatment':'Line']=table_R.loc[ind,'Treatment':'Line']
            for ind in table_O.index:
                out_t.loc[ind,dates]=table_O.loc[ind,col]
                if str(out_t.loc[ind,'Treatment'])=='nan':
                    out_t.loc[ind,'Treatment':'Line']=table_O.loc[ind,'Treatment':'Line']
            with pd.ExcelWriter(r'tables//'+col+'//'+col+'.xlsx') as writer:  
                row_t.to_excel(writer, sheet_name='Row')
                out_t.to_excel(writer, sheet_name='outliers')
                
############creating the line box               
print ('files in table:')
#for root, directories, files in os.walk(r'tables'):
 #   for filename in files:
        # Join the two strings in order to form the full filepath.
        #filepath = os.path.join(root, filename)
        #print (filename)
choose='' #input('copy the graph name: ')

if choose:
    reading_files(choose)
else:
    for root, directories, files in os.walk(r'tables'):
        for filename in files:
            #if not filename.split(' ')[0] in no_print :
            # Join the two strings in order to form the full filepath.
            #filepath = os.path.join(root, filename)
            reading_files(filename)


# In[ ]:




