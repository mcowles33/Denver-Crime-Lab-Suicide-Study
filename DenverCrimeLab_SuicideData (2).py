#!/usr/bin/env python
# coding: utf-8

# ## Import Python Packages 

# In[237]:


import pandas as pd
import scipy as sp
import numpy as np
from scipy import stats
from scipy.stats import sem
import seaborn as sns
import matplotlib.pyplot as plt
get_ipython().run_line_magic('matplotlib', 'inline')


# ## Create Dictionaries to Replace Drug Codes $\rightarrow$ Drug Names $\rightarrow$ Drug Groups

# In[238]:


#Read in Drug Code to Drug Name file
drugcodedata=pd.read_csv('Drug_Codes_to_Drug_Names.txt',sep='|', names=['drug', 'code'], header=None)
drugcodedata.code = drugcodedata.code.str.replace(' ', '')

#Create a dictionary
drug_dict = pd.Series(drugcodedata.drug.values,index=drugcodedata.code).to_dict()

#Read in Drug Name to Drug Group file
druggroupsdata=pd.read_csv('Drug_Names_to_Drug_Groups.txt',sep='|', names=['name', 'group'], header=None)
druggroupsdata.name = druggroupsdata.name.str.upper()
druggroupsdata.group = druggroupsdata.group.str.strip()

#Create a dictionary
drug_groups = pd.Series(druggroupsdata.group.values,index=druggroupsdata.name).to_dict()


# ## Clean the Data 

# In[239]:


#Read in the data from Excel
suicidedata=pd.read_excel('Denver_LasVegas_Milwaukee_SuicideDate.xlsx',sheet_name=[0,1,2],
                          converters={'Drug1':str,'Drug2':str,'Drug3':str,'Drug4':str,'Drug5':str, 'Tox Substance':str})

#Concatenate the 3 sheets in Excel
suicidedata=pd.concat([suicidedata[0],suicidedata[1],suicidedata[2]],ignore_index=True)


# In[240]:


#----------------------------------------------Clean Column 'Age'-----------------------------------------------------------

#Convert Age column entries into strings
suicidedata.Age=suicidedata.Age.astype(str)

#Replace all non ages into blank spaces
suicidedata.loc[(suicidedata['Age'] == 'No Birthdate Defined'),'Age']=''
suicidedata.loc[(suicidedata['Age'] == '07:52:41'),'Age']=''
suicidedata.loc[(suicidedata['Age'] == 'nan'),'Age']=''
suicidedata.loc[(suicidedata['Age'] == 'THIS IS CONFIDENTIAL INFORMATION IT IS NOT TO BE DUPLICATED OR RELEASED TO ANOTHER PERSON OR AGENCY'),'Age']=''

#Remove Yrs 
suicidedata['Age'] = suicidedata['Age'].str.replace(' Yrs','')

#Replace empty entries with NaN 
suicidedata.Age=suicidedata.Age.replace('',np.NaN)

#Convert strings to float
suicidedata.Age=suicidedata.Age.astype(float)

#------------------------------------------Clean Column 'Race'-----------------------------------------------------------------
#Replacing 
suicidedata.loc[(suicidedata['Race'] == 'I'),'Race']='Eastern Indian'
suicidedata.loc[(suicidedata['Race'] == 'Asian'),'Race']='Asian/Pacific Islander'
suicidedata.loc[(suicidedata['Race']== 'A'),'Race']='Asian/Pacific Islander'
suicidedata.loc[(suicidedata['Race'] == 'Black American'),'Race']='African American'
suicidedata.loc[(suicidedata['Race'] == 'Indian'),'Race']='Eastern Indian'
suicidedata.loc[(suicidedata['Race'] == 'Multi-Cultured'),'Race']='Multi-Racial'

#----------------------------------------------Clean Column 'Marital Status'----------------------------------------------------
#Replacing 
suicidedata.loc[(suicidedata['MaritalStatus'] == 'O'),'MaritalStatus']='Other'
suicidedata.loc[(suicidedata['MaritalStatus'] == 'D'),'MaritalStatus']='Divorced'
suicidedata.loc[(suicidedata['MaritalStatus'] == 'U'),'MaritalStatus']='Unknown'

#----------------------------------------------Combine Columns of the Same Type -------------------------------------------------
#Combine Place of Death with Location Of Death 
suicidedata['Location of Death'].update(suicidedata['PlaceOfDeath'])
#Combine Final Cause Of Death with Cause Of Death
suicidedata['Cause of Death'].update(suicidedata['FinalCODonDC'])
#Combine both Injury Type columns
suicidedata['Injury Type'].update(suicidedata['InjuryType'])

#----------------------------------------------Clean/Combine all Drug Columns----------------------------------------------------
# Get rid of extra whitespaces
suicidedata.Drug1 = (suicidedata.Drug1.str.replace(' ', '')).str.upper()
suicidedata.Drug2 = (suicidedata.Drug2.str.replace(' ', '')).str.upper()
suicidedata.Drug3 = (suicidedata.Drug3.str.replace(' ', '')).str.upper()
suicidedata.Drug4 = (suicidedata.Drug4.str.replace(' ', '')).str.upper()
suicidedata.Drug5 = (suicidedata.Drug5.str.replace(' ', '')).str.upper()

# Drug Codes not in the Dictionary
drugs_not_in_dict = []
for i in range(0, len(suicidedata.Drug1)):
    if suicidedata.Drug1[i] not in drug_dict and suicidedata.Drug1[i] == suicidedata.Drug1[i]:
        drugs_not_in_dict.append(suicidedata.Drug1[i])
for i in range(0, len(suicidedata.Drug2)):
    if suicidedata.Drug2[i] not in drug_dict and suicidedata.Drug2[i] == suicidedata.Drug2[i]:
        drugs_not_in_dict.append(suicidedata.Drug2[i])
for i in range(0, len(suicidedata.Drug3)):
    if suicidedata.Drug3[i] not in drug_dict and suicidedata.Drug3[i] == suicidedata.Drug3[i]:
        drugs_not_in_dict.append(suicidedata.Drug3[i])
for i in range(0, len(suicidedata.Drug4)):
    if suicidedata.Drug4[i] not in drug_dict and suicidedata.Drug4[i] == suicidedata.Drug4[i]:
        drugs_not_in_dict.append(suicidedata.Drug4[i])
for i in range(0, len(suicidedata.Drug5)):
    if suicidedata.Drug5[i] not in drug_dict and suicidedata.Drug5[i] == suicidedata.Drug5[i]:
        drugs_not_in_dict.append(suicidedata.Drug5[i])
print('Drug Codes not in dictionary:', np.unique(drugs_not_in_dict))

# Fix for one instance of 'CARBONMONOXIDE'
suicidedata=suicidedata.replace(to_replace='CARBONMONOXIDE',value=drug_dict['10520'])

#Replace drug codes with drug names 
suicidedata=suicidedata.replace(to_replace=drug_dict,value=None)

# Combine Drug 1,2,3,4,5 into one column
suicidedata['Drug'] = suicidedata[['Drug5', 'Drug4', 'Drug3', 'Drug2', 'Drug1']].apply(lambda x: '; '.join(x[x.notnull()]), axis = 1)

#Combine Drug column with Toxic Substance column
suicidedata['Tox Substance']=suicidedata['Tox Substance'].astype(str)+suicidedata['Drug'].astype(str)                               

#Find Drug-Related in Injury Type Column, Combine Cause A with Toxic Substance
suicidedata.loc[(suicidedata['Injury Type'] == 'Drug - related'),'Tox Substance']=suicidedata['Cause_A']

#Replace nan with blank space
suicidedata['Tox Substance']=suicidedata['Tox Substance'].str.lstrip('nan')

#------------------------------------------------Drop Extra Columns--------------------------------------------------------------
#Drop Manner of Death
todrop=['MannerOfDeath']
suicidedata=suicidedata.drop(todrop,axis=1)
#Drop empty columns
todrop=['Unnamed: 16']
suicidedata=suicidedata.drop(todrop,axis=1)
todrop=['Unnamed: 9']
suicidedata=suicidedata.drop(todrop,axis=1)
#Drop Place of Death Column
todrop=['PlaceOfDeath']
suicidedata=suicidedata.drop(todrop,axis=1)
#Drop Final Cause of Death Column
todrop=['FinalCODonDC']
suicidedata=suicidedata.drop(todrop,axis=1)
#Drop Extra Injury Type Column
todrop=['InjuryType']
suicidedata=suicidedata.drop(todrop,axis=1)
#Drop Drug 1,2,3,4,5 Columns
todrop=['Drug1','Drug2','Drug3','Drug4','Drug5']
suicidedata=suicidedata.drop(todrop,axis=1)
#Drop new Drug Column
todrop=['Drug']
suicidedata=suicidedata.drop(todrop,axis=1)

#------------------------------------------------------Clean Column 'Tox'---------------------------------------------------------
#Create a new column 'Tox' that will be a copy of column 'Tox Substance'
suicidedata['Tox'] = suicidedata['Tox Substance']

# Fix misspelling
suicidedata.Tox = suicidedata.Tox.str.replace('Citalpram \(celexa\)', 'Citalopram (Celexa)', regex=True)

# Temporarily remove problematic commas and paranthesis 
suicidedata.Tox = suicidedata.Tox.str.replace('1,1,1-trichloroethane', '111trichloroethane', regex=True)
suicidedata.Tox = suicidedata.Tox.str.replace('Nitrate, amyl', 'Nitrateamyl', regex=True)
suicidedata.Tox = suicidedata.Tox.str.replace('Alcohol , benzyl', 'Alcoholbenzyl', regex=True)
suicidedata.Tox = suicidedata.Tox.str.replace('Alcohol, isopropyl', 'Alcoholisopropyl', regex=True)
suicidedata.Tox = suicidedata.Tox.str.replace('Alcohol, methyl', 'Alcoholmethyl', regex=True)
suicidedata.Tox = suicidedata.Tox.str.replace('Alcohol, ethyl', 'Alcoholethyl', regex=True)
suicidedata.Tox = suicidedata.Tox.str.replace('Antidepressant, NOS', 'AntidepressantNOS', regex=True)
suicidedata.Tox = suicidedata.Tox.str.replace('Benzodiazepine, NOS', 'BenzodiazepineNOS', regex=True)
suicidedata.Tox = suicidedata.Tox.str.replace('EDDP (2-ethylidine-1,5-dimethyl-3,3-diphenylpyrrolidine)', 'EDDP 2-ethylidine-15-dimethyl-33-diphenylpyrrolidine', regex=True)
suicidedata.Tox = suicidedata.Tox.str.replace('Glycol, ethylene', 'Glycolethylene', regex=True)
suicidedata.Tox = suicidedata.Tox.str.replace('Hydrate, chloral', 'Hydratechloral', regex=True)
suicidedata.Tox = suicidedata.Tox.str.replace('Hypnotic or sedative, NOS', 'Hypnotic or sedativeNOS', regex=True)
suicidedata.Tox = suicidedata.Tox.str.replace('\(NOS\)', 'NOS!', regex=True)
suicidedata.Tox = suicidedata.Tox.str.replace('Citalopram \(Celexa\)', 'Citalopram!Celexa!', regex=True)
suicidedata.Tox = suicidedata.Tox.str.replace('Methylenedioxymethamphetamine\(MDMA\)', 'Methylenedioxymethamphetamine!MDMA!', regex=True)
suicidedata.Tox = suicidedata.Tox.str.replace('Lametrigine \(Lamictal\)', 'Lametrigine !Lamictal!', regex=True)
suicidedata.Tox = suicidedata.Tox.str.replace('Levetiracetam \(Keppra\)', 'Levetiracetam !Keppra!', regex=True)
suicidedata.Tox = suicidedata.Tox.str.replace('Hydrogen Sulfide \(H2S gas\)', 'Hydrogen Sulfide !H2S gas!', regex=True)
suicidedata.Tox = suicidedata.Tox.str.replace('Hydrogen Sulfide \(H2S gas\)', 'Hydrogen Sulfide !H2S gas!', regex=True)
suicidedata.Tox = suicidedata.Tox.str.replace('Gabapentin \(blood\)', 'Gabapentin !blood!', regex=True)

# Remove all words that are not drug names 
suicidedata.Tox = suicidedata.Tox.str.replace(' \(Vitreous Fluid\)', '', regex=True)
suicidedata.Tox = suicidedata.Tox.str.replace(' MIXED DRUG OVERDOSE ', '', regex=True)
suicidedata.Tox = suicidedata.Tox.str.replace(' MIXED DRUG TOXICITY ', '', regex=True)
suicidedata.Tox = suicidedata.Tox.str.replace('MIXED DRUG TOXICITY ', '', regex=True)
suicidedata.Tox = suicidedata.Tox.str.replace('MIXED DRUG TOXCITY ', '', regex=True)
suicidedata.Tox = suicidedata.Tox.str.replace('MIXED DRUG OVERDOSE ', '', regex=True)
suicidedata.Tox = suicidedata.Tox.str.replace('MIXED DRUG INTOXICATION ', '', regex=True)
suicidedata.Tox = suicidedata.Tox.str.replace('Mixed Drug ', '', regex=True)
suicidedata.Tox = suicidedata.Tox.str.replace('MIXED DRUG ', '', regex=True)
suicidedata.Tox = suicidedata.Tox.str.replace('ACUTE DRUG ', '', regex=True)
suicidedata.Tox = suicidedata.Tox.str.replace('ACUTE ', '', regex=True)
suicidedata.Tox = suicidedata.Tox.str.replace('Acute mixed drug ', '', regex=True)
suicidedata.Tox = suicidedata.Tox.str.replace('Acute ', '', regex=True)
suicidedata.Tox = suicidedata.Tox.str.replace(' TOXICITY', '', regex=True)
suicidedata.Tox = suicidedata.Tox.str.replace(' Toxicity', '', regex=True)
suicidedata.Tox = suicidedata.Tox.str.replace(' toxicity', '', regex=True)
suicidedata.Tox = suicidedata.Tox.str.replace(' INTOXICATION', '', regex=True)
suicidedata.Tox = suicidedata.Tox.str.replace(' Intoxication', '', regex=True)
suicidedata.Tox = suicidedata.Tox.str.replace(' intoxication', '', regex=True)
suicidedata.Tox = suicidedata.Tox.str.replace(' Overdose', '', regex=True)
suicidedata.Tox = suicidedata.Tox.str.replace(' OVERDOSE', '', regex=True)
suicidedata.Tox = suicidedata.Tox.str.replace('intoxication with', '', regex=True)
suicidedata.Tox = suicidedata.Tox.str.replace('Drug ', '', regex=True)
suicidedata.Tox = suicidedata.Tox.str.replace('drug ', '', regex=True)
suicidedata.Tox = suicidedata.Tox.str.replace('DRUG ', '', regex=True)
suicidedata.Tox = suicidedata.Tox.str.replace('Delta-9-', '', regex=True)
suicidedata.Tox = suicidedata.Tox.str.replace('Delta-9 ', '', regex=True)
suicidedata.Tox = suicidedata.Tox.str.replace('- Total', '', regex=True)
suicidedata.Tox = suicidedata.Tox.str.replace('POISONING', '', regex=True)
suicidedata.Tox = suicidedata.Tox.str.replace('TOXICITY', '', regex=True)
suicidedata.Tox = suicidedata.Tox.str.replace('INTOXICATION', '', regex=True)

# Fix instance with paranthesis in wrong place
suicidedata.Tox = suicidedata.Tox.str.replace('\) AND ALCOHOL', ' AND ALCOHOL)', regex=True)

# Remove extra spaces and characters 
suicidedata.Tox = suicidedata.Tox.str.strip()
suicidedata.Tox = suicidedata.Tox.str.replace('^\(', '', regex=True)
suicidedata.Tox = suicidedata.Tox.str.replace('\)$', '', regex=True)
suicidedata.Tox = suicidedata.Tox.str.replace(':', '', regex=True)

# Separate drug names by semicolons 
suicidedata.Tox = suicidedata.Tox.str.replace(',', ';', regex=True)
suicidedata.Tox = suicidedata.Tox.str.replace(' AND ', '; ', regex=True)
suicidedata.Tox = suicidedata.Tox.str.replace(' and ', '; ', regex=True)
suicidedata.Tox = suicidedata.Tox.str.replace(';', '; ', regex=True)
suicidedata.Tox = suicidedata.Tox.str.replace(';  ', '; ', regex=True)
suicidedata.Tox = suicidedata.Tox.str.replace(';$', '', regex=True)

# Clear items that don't actually have a drug
suicidedata.loc[suicidedata['Tox'].str.upper().str.contains(" ID "), 'Tox'] = ''
suicidedata.loc[suicidedata['Tox'].str.upper().str.contains(" ID'"), 'Tox'] = ''
suicidedata.loc[suicidedata['Tox'].str.upper().str.endswith(" ID"), 'Tox'] = ''

suicidedata.loc[suicidedata['Tox'].str.upper().str.contains("FREE"), 'Tox'] = ''
suicidedata.loc[suicidedata['Tox'].str.upper().str.contains("NEG"), 'Tox'] = ''
suicidedata.loc[suicidedata['Tox'].str.upper().str.contains("NO POS"), 'Tox'] = ''
suicidedata.loc[suicidedata['Tox'].str.upper().str.contains("NO DRUG"), 'Tox'] = ''

suicidedata.loc[suicidedata['Tox'].str.upper().str.contains("SPECIAL"), 'Tox'] = ''
suicidedata.loc[suicidedata['Tox'].str.upper().str.contains("INJURY"), 'Tox'] = ''
suicidedata.loc[suicidedata['Tox'].str.upper().str.contains("CORONER"), 'Tox'] = ''
suicidedata.loc[suicidedata['Tox'].str.upper().str.contains("ASPHYXIA"), 'Tox'] = ''
suicidedata.loc[suicidedata['Tox'].str.upper().str.contains("INSUFFICIENT"), 'Tox'] = ''
suicidedata.loc[suicidedata['Tox'].str.upper().str.contains("FAILURE"), 'Tox'] = ''
suicidedata.loc[suicidedata['Tox'].str.upper().str.contains("BRONCHOPNEUMONIA"), 'Tox'] = ''
suicidedata.loc[suicidedata['Tox'].str.upper().str.contains("ENCEPHALOPATHY"), 'Tox'] = ''
suicidedata.loc[suicidedata['Tox'].str.upper().str.contains("MULTIPLE PRESCRIPTION"), 'Tox'] = 'MIXED'

# Remove extra spaces 
suicidedata.Tox = suicidedata.Tox.str.strip()

# Replace commas and paranthesis that were removed from above
suicidedata.Tox = suicidedata.Tox.str.replace('Hydrogen Sulfide !H2S gas!', 'Hydrogen Sulfide (H2S gas)', regex=True)
suicidedata.Tox = suicidedata.Tox.str.replace('Methylenedioxymethamphetamine!MDMA!', 'Methylenedioxymethamphetamine(MDMA)', regex=True)
suicidedata.Tox = suicidedata.Tox.str.replace('Lametrigine !Lamictal!', 'Lametrigine (Lamictal)', regex=True)
suicidedata.Tox = suicidedata.Tox.str.replace('Levetiracetam !Keppra!', 'Levetiracetam (Keppra)', regex=True)
suicidedata.Tox = suicidedata.Tox.str.replace('Citalopram!Celexa!', 'Citalopram (Celexa)', regex=True)
suicidedata.Tox = suicidedata.Tox.str.replace('NOS!', '(NOS)', regex=True)
suicidedata.Tox = suicidedata.Tox.str.replace('111trichloroethane', '1,1,1-trichloroethane', regex=True)
suicidedata.Tox = suicidedata.Tox.str.replace('Nitrateamyl', 'Nitrate, amyl', regex=True)
suicidedata.Tox = suicidedata.Tox.str.replace('Alcoholbenzyl', 'Alcohol , benzyl', regex=True)
suicidedata.Tox = suicidedata.Tox.str.replace('Alcoholisopropyl', 'Alcohol, isopropyl', regex=True)
suicidedata.Tox = suicidedata.Tox.str.replace('Alcoholmethyl', 'Alcohol, methyl', regex=True)
suicidedata.Tox = suicidedata.Tox.str.replace('Alcoholethyl', 'Alcohol, ethyl', regex=True)
suicidedata.Tox = suicidedata.Tox.str.replace('AntidepressantNOS', 'Antidepressant, NOS', regex=True)
suicidedata.Tox = suicidedata.Tox.str.replace('BenzodiazepineNOS', 'Benzodiazepine, NOS', regex=True)
suicidedata.Tox = suicidedata.Tox.str.replace('EDDP 2-ethylidine-15-dimethyl-33-diphenylpyrrolidine', 'EDDP (2-ethylidine-1,5-dimethyl-3,3-diphenylpyrrolidine)', regex=True)
suicidedata.Tox = suicidedata.Tox.str.replace('Glycolethylene', 'Glycol, ethylene', regex=True)
suicidedata.Tox = suicidedata.Tox.str.replace('Hydratechloral', 'Hydrate, chloral', regex=True)
suicidedata.Tox = suicidedata.Tox.str.replace('Hypnotic or sedativeNOS', 'Hypnotic or sedative, NOS', regex=True)
suicidedata.Tox = suicidedata.Tox.str.replace('Gabapentin !blood!', 'Gabapentin (blood)', regex=True)

# Replace double parenthesis with one parenthesis
suicidedata.Tox = suicidedata.Tox.str.replace('\)\)', ')', regex=True)

#Create new column for clean drug names 
suicidedata['Tox Substance Clean']=suicidedata['Tox']

#Replace drug names with drug groups
count = 0
for i in suicidedata.Tox:
    toxs = i.split('; ')
    for j in toxs:
        if j.upper() in drug_groups:
            suicidedata.Tox[count] = suicidedata.Tox[count].replace(j, str(drug_groups[j.upper()]))
    count += 1
    
#Replace an instance that occured when replacing drug names with drug groups
suicidedata['Tox']= suicidedata.Tox.str.replace('NOROther','Other')

#------------------------------------------Create New Columns for the Drug Groups------------------------------------------------
#Creating new columns for the drug groups using boolean variables
drug_group_list = ['CNS Depressant',
                   'CNS Stimulant',
                   'Cannabis',
                   'Dissociative Anesthetic',
                   'Hallucinogen',
                   'Inhalant',
                   'Narcotic Analgesic',
                   'Other']

for i in drug_group_list:
    suicidedata[i] = suicidedata.Tox.str.contains(i)  
    
#----------------------------------------Rename Column 'Tox' as 'Drug Class'-----------------------------------------------------
suicidedata=suicidedata.rename({'Tox':'Drug Class'},axis=1)

#----------------------------------------Create New Column just for Drug or no Drug---------------------------------------------
suicidedata['Drug'] = suicidedata['Drug Class']!=''

#----------------------------------------Rearrange Columns----------------------------------------------------------------------
suicidedata=suicidedata[['City','CaseNumber','Age','Sex','Race','Tox Substance','Tox Substance Clean','Drug Class','CNS Depressant',
                         'CNS Stimulant','Cannabis','Dissociative Anesthetic','Hallucinogen','Inhalant','Narcotic Analgesic',
                         'Other','Drug','DateOfDeath','Death_DayOfWeek','MaritalStatus','HIVPositive','Location of Death',
                         'Cause of Death','Cause_A','Cause_B','Cause_C','Cause_D','Cause_Other','Injury Type']]

#------------------------------------------Output an Excel file-----------------------------------------------------------------
suicidedata.to_excel('SuicideData.xlsx')


# ## Data Analysis

# In[241]:


# List of each Age seen in data with counts 
values, counts = np.unique(suicidedata.Age, return_counts=True)
print(values,'\n',counts)


# In[242]:


#Total drug entries
suicidedata['Tox Substance Clean'].value_counts()


# In[243]:


#Total of victims who had said drug group in system at TOD
total=suicidedata[drug_group_list].sum()
print('Total of victims who had said drug group in system at TOD',total)


# In[244]:


#Total of victims who had more than one drug in different drug groups in system at TOD
count=0
for i in suicidedata['Drug Class']:
    split=i.split('; ')
    #print(split)
    #print(len(split))
    if split!=['']:
        if len(split)>1:
            count=count+1
print(count) 


# In[245]:


#Number of victms who did and did not have said drug group in their system at TOD
print(suicidedata['CNS Depressant'].value_counts())

print(suicidedata['CNS Stimulant'].value_counts())

print(suicidedata['Dissociative Anesthetic'].value_counts())

print(suicidedata['Hallucinogen'].value_counts())
      
print(suicidedata['Inhalant'].value_counts())

print(suicidedata['Narcotic Analgesic'].value_counts())

print(suicidedata['Cannabis'].value_counts())

print(suicidedata['Other'].value_counts())


# In[246]:


#Plot drug groups frequency/count with total # of victims 
x = drug_group_list
y=suicidedata[drug_group_list].sum()
y1 =y/6827*100
plt.barh(x, y1)
plt.xlabel('Frequency')
plt.grid()
for xpos, ypos, yval in zip(x,y1,suicidedata[drug_group_list].sum()):
   plt.text(ypos, xpos,"N=%d"%yval, ha="left", va="center")
plt.xticks(np.arange(0, 60, 10))
plt.title('Drug Group Counts/Frequency Against Total # of Victims')


# In[247]:


#Plot drug groups frequency/count with total # of victims who had drugs in their system 
x = drug_group_list
y=suicidedata[drug_group_list].sum()
y1 =y/4382*100
plt.barh(x, y1)
plt.xlabel('Frequency')
plt.grid()
for xpos, ypos, yval in zip(x,y1,suicidedata[drug_group_list].sum()):
   plt.text(ypos, xpos,"N=%d"%yval, ha="left", va="center")
plt.xticks(np.arange(0, 60, 10))
plt.title('Drug Group Counts/Frequency Against Total # of Victims with Drugs in their System at TOD')


# In[248]:


#Finding the sum of individuals with drugs and without drugs at TOD
drug = np.array(suicidedata['Drug'].value_counts())
sex = suicidedata['Sex'].value_counts()

#Finding the sum of each drug group for sex,city,race, and age group
male_drug_groups = []
female_drug_groups = []
for i in drug_group_list:
    male = (suicidedata[i]) & (suicidedata.Sex == 'Male')
    female = (suicidedata[i]) & (suicidedata.Sex == 'Female')
    male_drug_groups.append(male.sum())
    female_drug_groups.append(female.sum())
    
lv_drug_groups=[]
den_drug_groups=[]
ml_drug_groups=[]
for i in drug_group_list:
    lv=(suicidedata[i]) & (suicidedata.City=='Las Vegas')
    den=(suicidedata[i]) & (suicidedata.City=='Denver')
    ml=(suicidedata[i]) & (suicidedata.City=='Milwaukee')
    lv_drug_groups.append(lv.sum())
    den_drug_groups.append(den.sum())
    ml_drug_groups.append(ml.sum())
    
cauc_drug_groups=[]
east_drug_groups=[]
hisp_drug_groups=[]
afr_drug_groups=[]
asian_drug_groups=[]
nat_drug_groups=[]
mul_drug_groups=[]
for i in drug_group_list:
    cauc=(suicidedata[i]) & (suicidedata.Race=='Caucasian')
    east=(suicidedata[i]) & (suicidedata.Race=='Eastern Indian')
    hisp=(suicidedata[i]) & (suicidedata.Race=='Hispanic')
    afr=(suicidedata[i]) & (suicidedata.Race=='African American')
    asian=(suicidedata[i]) & (suicidedata.Race=='Asian') & (suicidedata.Race=='Pacific Islander')
    nat=(suicidedata[i]) & (suicidedata.Race=='Native American')
    mul=(suicidedata[i]) & (suicidedata.Race=='Multi-Racial')
    cauc_drug_groups.append(cauc.sum())
    east_drug_groups.append(east.sum())
    hisp_drug_groups.append(hisp.sum())
    afr_drug_groups.append(afr.sum())
    asian_drug_groups.append(asian.sum())  
    nat_drug_groups.append(nat.sum())
    mul_drug_groups.append(mul.sum())

drug_groups_1=[]
drug_groups_2=[]
drug_groups_3=[] 
drug_groups_4=[]
drug_groups_5=[]
drug_groups_6=[]
drug_groups_7=[]
drug_groups_8=[]
drug_groups_9=[]
drug_groups_10=[]
for i in drug_group_list:
    if (suicidedata.Age).empty:
        pass
    else:
        on=(suicidedata[i]) & (suicidedata.Age<20)
        tw=(suicidedata[i]) & (suicidedata.Age>=20) & (suicidedata.Age<30)
        th=(suicidedata[i]) & (suicidedata.Age>=30) & (suicidedata.Age<40)
        fo=(suicidedata[i]) & (suicidedata.Age>=40) & (suicidedata.Age<50)
        fi=(suicidedata[i]) & (suicidedata.Age>=50) & (suicidedata.Age<60)
        si=(suicidedata[i]) & (suicidedata.Age>=60) & (suicidedata.Age<70)
        se=(suicidedata[i]) & (suicidedata.Age>=70) & (suicidedata.Age<80)
        ei=(suicidedata[i]) & (suicidedata.Age>=80) & (suicidedata.Age<90)
        ni=(suicidedata[i]) & (suicidedata.Age>=90) 
        drug_groups_1.append(on.sum())
        drug_groups_2.append(tw.sum())                                              
        drug_groups_3.append(th.sum())                                            
        drug_groups_4.append(fo.sum())                                              
        drug_groups_5.append(fi.sum())                                              
        drug_groups_6.append(si.sum())                                              
        drug_groups_7.append(se.sum())
        drug_groups_8.append(ei.sum())
        drug_groups_9.append(ni.sum())  

cauc_den_drug_groups=[]
hisp_den_drug_groups=[]
afr_den_drug_groups=[]
for i in drug_group_list:
    cauc_den=(suicidedata[i]) & (suicidedata.Race=='Caucasian') & (suicidedata.City=='Denver')
    hisp_den=(suicidedata[i]) & (suicidedata.Race=='Hispanic') & (suicidedata.City=='Denver')
    afr_den=(suicidedata[i]) & (suicidedata.Race=='African American') & (suicidedata.City=='Denver')
    cauc_den_drug_groups.append(cauc_den.sum())
    hisp_den_drug_groups.append(hisp_den.sum())
    afr_den_drug_groups.append(afr_den.sum())
 
cauc_lv_drug_groups=[] 
hisp_lv_drug_groups=[] 
afr_lv_drug_groups=[]
for i in drug_group_list:
    cauc_lv=(suicidedata[i]) & (suicidedata.Race=='Caucasian') & (suicidedata.City=='Las Vegas')
    hisp_lv=(suicidedata[i]) & (suicidedata.Race=='Hispanic') & (suicidedata.City=='Las Vegas')
    afr_lv=(suicidedata[i]) & (suicidedata.Race=='African American') & (suicidedata.City=='Las Vegas')
    cauc_lv_drug_groups.append(cauc_lv.sum())
    hisp_lv_drug_groups.append(hisp_lv.sum())
    afr_lv_drug_groups.append(afr_lv.sum())
    
cauc_ml_drug_groups=[] 
hisp_ml_drug_groups=[] 
afr_ml_drug_groups=[]
for i in drug_group_list:
    cauc_ml=(suicidedata[i]) & (suicidedata.Race=='Caucasian') & (suicidedata.City=='Milwaukee')
    hisp_ml=(suicidedata[i]) & (suicidedata.Race=='Hispanic') & (suicidedata.City=='Milwaukee')
    afr_ml=(suicidedata[i]) & (suicidedata.Race=='African American') & (suicidedata.City=='Milwaukee')
    cauc_ml_drug_groups.append(cauc_ml.sum())
    hisp_ml_drug_groups.append(hisp_ml.sum())
    afr_ml_drug_groups.append(afr_ml.sum())
    
male_den_drug_groups = []
female_den_drug_groups = []
for i in drug_group_list:
    male_den = (suicidedata[i]) & (suicidedata.Sex == 'Male') & (suicidedata.City=='Denver')
    female_den = (suicidedata[i]) & (suicidedata.Sex == 'Female') & (suicidedata.City=='Denver')
    male_den_drug_groups.append(male_den.sum())
    female_den_drug_groups.append(female_den.sum())
    
male_lv_drug_groups = []
female_lv_drug_groups = []
for i in drug_group_list:
    male_lv = (suicidedata[i]) & (suicidedata.Sex == 'Male') & (suicidedata.City=='Las Vegas')
    female_lv = (suicidedata[i]) & (suicidedata.Sex == 'Female') & (suicidedata.City=='Las Vegas')
    male_lv_drug_groups.append(male_lv.sum())
    female_lv_drug_groups.append(female_lv.sum())
    
male_ml_drug_groups = []
female_ml_drug_groups = []
for i in drug_group_list:
    male_ml = (suicidedata[i]) & (suicidedata.Sex == 'Male') & (suicidedata.City=='Milwaukee')
    female_ml = (suicidedata[i]) & (suicidedata.Sex == 'Female') & (suicidedata.City=='Milwaukee')
    male_ml_drug_groups.append(male_ml.sum())
    female_ml_drug_groups.append(female_ml.sum())
    
print('No Drug vs. Drug',drug) 
print('Total Male and Female', sex)

print('Male',male_drug_groups,'Female',female_drug_groups)

print('Las Vegas',lv_drug_groups,'Denver',den_drug_groups,'Milwaukee',ml_drug_groups)      

print('Caucasian',cauc_drug_groups,'Eastern Indian',east_drug_groups,'Hispanic',hisp_drug_groups,'African American',
      afr_drug_groups,'Asian\Pacific Islander',asian_drug_groups,'Native American',nat_drug_groups,'Multi-Racial',mul_drug_groups)

print('1-19',drug_groups_1,'20-29',drug_groups_2,'30-39',drug_groups_3,'40-49',drug_groups_4,'50-59',drug_groups_5,
      '60-69',drug_groups_6,'70-79',drug_groups_7,'80-89',drug_groups_8,'90 +',drug_groups_9)

print('Caucasians in Denver', cauc_den_drug_groups, 'Hispanics in Denver',hisp_den_drug_groups,'African Americans in Denver',
     afr_den_drug_groups)

print('Caucasians in Las Vegas', cauc_lv_drug_groups, 'Hispanics in Las Vegas',hisp_lv_drug_groups,'African Americans in Las Vegas',
     afr_lv_drug_groups)

print('Caucasians in Milwaukee', cauc_ml_drug_groups, 'Hispanics in Milwaukee',hisp_ml_drug_groups,'African Americans in Milwaukee',
     afr_ml_drug_groups)

print('Males in Denver', male_den_drug_groups, 'Females in Denver',female_den_drug_groups)

print('Males in Las Vegas', male_lv_drug_groups, 'Females in Las Vegas',female_lv_drug_groups)

print('Males in Milwaukee', male_ml_drug_groups, 'Females in Milwaukee',female_ml_drug_groups)


# In[249]:


#PLot frequency/count of # drug groups in victims system at TOD in regards to sex in all 3 cities
x = np.arange(len(drug_group_list))  
width=.45
y=np.array(male_drug_groups)
y1=np.array(female_drug_groups)
fig, ax = plt.subplots()
rects1 = ax.bar(x - width/2, y/6827*100, width, label='Male')
rects2 = ax.bar(x + width/2, y1/6827*100, width, label='Female')
ax.set_ylabel('Frequency')
ax.set_title('Drug Groups by Sex')
ax.set_xticks(x)
ax.set_xticklabels(drug_group_list,rotation=25)
plt.yticks(np.arange(0, 60, 10))
ax.legend()
fig.tight_layout()
for xpos, ypos, yval in zip(x-width/2,y/6827*100,y):
   plt.text(xpos, ypos,"N=%d"%yval, ha="center", va="bottom")
for xpos, ypos, yval in zip(x+width/1.95,y1/6827*100,y1):
   plt.text(xpos, ypos,"N=%d"%yval, ha="center", va="bottom")
plt.grid()
plt.show()
plt.rcParams['figure.figsize']=[15,8]


# In[250]:


#PLot frequency/count of # drug groups in victims system at TOD in regards to sex for Denver
mf=(suicidedata['City'].values == 'Denver').sum()
x = np.arange(len(drug_group_list))  
width=.45
y=np.array(male_den_drug_groups)
y1=np.array(female_den_drug_groups)
fig, ax = plt.subplots()
rects1 = ax.bar(x - width/2, y/1946*100, width, label='Male')
rects2 = ax.bar(x + width/2, y1/1946*100, width, label='Female')
ax.set_ylabel('Frequency')
ax.set_title('Drug Groups by Sex in Denver')
ax.set_xticks(x)
ax.set_xticklabels(drug_group_list,rotation=25)
plt.yticks(np.arange(0, 60, 10))
ax.legend()
fig.tight_layout()
for xpos, ypos, yval in zip(x-width/2,y/1946*100,y):
   plt.text(xpos, ypos,"N=%d"%yval, ha="center", va="bottom")
for xpos, ypos, yval in zip(x+width/1.95,y1/1946*100,y1):
   plt.text(xpos, ypos,"N=%d"%yval, ha="center", va="bottom")
plt.grid()
plt.show()
plt.rcParams['figure.figsize']=[15,8]


# In[251]:


#PLot frequency/count of # drug groups in victims system at TOD in regards to sex for Las Vegas
x = np.arange(len(drug_group_list))  
width=.45
y=np.array(male_lv_drug_groups)
y1=np.array(female_lv_drug_groups)
fig, ax = plt.subplots()
rects1 = ax.bar(x - width/2, y/3958*100, width, label='Male')
rects2 = ax.bar(x + width/2, y1/3958*100, width, label='Female')
ax.set_ylabel('Frequency')
ax.set_title('Drug Groups by Sex in Las Vegas')
ax.set_xticks(x)
ax.set_xticklabels(drug_group_list,rotation=25)
plt.yticks(np.arange(0, 60, 10))
ax.legend()
fig.tight_layout()
for xpos, ypos, yval in zip(x-width/2,y/3958*100,y):
   plt.text(xpos, ypos,"N=%d"%yval, ha="center", va="bottom")
for xpos, ypos, yval in zip(x+width/1.95,y1/3958*100,y1):
   plt.text(xpos, ypos,"N=%d"%yval, ha="center", va="bottom")
plt.grid()
plt.show()
plt.rcParams['figure.figsize']=[15,8]


# In[252]:


#PLot frequency/count of # drug groups in victims system at TOD in regards to city 
x = np.arange(len(drug_group_list))  
width=.3
y=np.array(den_drug_groups)
y1=np.array(lv_drug_groups)
y2=np.array(ml_drug_groups)
fig, ax = plt.subplots()
rects1 = ax.bar(x - width, y/6827*100, width, label='Denver')
rects2 = ax.bar(x, y1/6827*100, width, label='Las Vegas')
rects3 = ax.bar(x + width, y2/6827*100, width, label='Milwaukee')
ax.set_ylabel('Frequency')
ax.set_title('Drug Groups by City')
ax.set_xticks(x)
ax.set_xticklabels(drug_group_list,rotation=25)
plt.yticks(np.arange(0, 60, 10))
ax.legend()
fig.tight_layout()
for xpos, ypos, yval in zip(x-width/.9,y/6827*100,y):
   plt.text(xpos, ypos,"N=%d"%yval, ha="center", va="bottom")
for xpos, ypos, yval in zip(x,y1/6827*100,y1):
   plt.text(xpos, ypos,"N=%d"%yval, ha="center", va="bottom")
for xpos, ypos, yval in zip(x+width,y2/6827*100,y2):
   plt.text(xpos, ypos,"N=%d"%yval, ha="center", va="bottom")
plt.grid()
plt.show()
plt.rcParams['figure.figsize']=[15,8]


# In[253]:


#Plot frequency/count of # drug groups in victims system at TOD in regards to race in all 3 cities
x = np.arange(len(drug_group_list))  
width=.3
y=np.array(cauc_drug_groups)
y2=np.array(hisp_drug_groups)
y3=np.array(afr_drug_groups)
fig, ax = plt.subplots()
rects1 = ax.bar(x - width, y/6827*100, width, label='Caucasian')
rects3 = ax.bar(x , y2/6827*100, width, label='Hispanic')
rects3 = ax.bar(x + width, y3/6827*100, width, label='African American')
ax.set_ylabel('Frequency')
ax.set_title('Drug Groups by Race')
ax.set_xticks(x)
ax.set_xticklabels(drug_group_list,rotation=25)
plt.yticks(np.arange(0, 60, 10))
ax.legend()
fig.tight_layout()
for xpos, ypos, yval in zip(x-width,y/6827*100,y):
   plt.text(xpos, ypos,"N=%d"%yval, ha="center", va="bottom")
for xpos, ypos, yval in zip(x,y2/6827*100,y2):
   plt.text(xpos, ypos,"N=%d"%yval, ha="center", va="bottom")
for xpos, ypos, yval in zip(x+width,y3/6827*100,y3):
   plt.text(xpos, ypos,"N=%d"%yval, ha="center", va="bottom")  
plt.grid()
plt.show()
plt.rcParams['figure.figsize']=[15,8]


# In[254]:


#Plot frequency/count of # drug groups in victims system at TOD in regards to race in Las Vegas 
x = np.arange(len(drug_group_list))  
width=.3
y=np.array(cauc_lv_drug_groups)
y2=np.array(hisp_lv_drug_groups)
y3=np.array(afr_lv_drug_groups)
fig, ax = plt.subplots()
rects1 = ax.bar(x - width, y/3958*100, width, label='Caucasian')
rects3 = ax.bar(x , y2/3958*100, width, label='Hispanic')
rects3 = ax.bar(x + width, y3/3958*100, width, label='African American')
ax.set_ylabel('Frequency')
ax.set_title('Drug Groups by Race in Las Vegas')
ax.set_xticks(x)
ax.set_xticklabels(drug_group_list,rotation=25)
plt.yticks(np.arange(0, 60, 10))
ax.legend()
fig.tight_layout()
for xpos, ypos, yval in zip(x-width,y/3958*100,y):
   plt.text(xpos, ypos,"N=%d"%yval, ha="center", va="bottom")
for xpos, ypos, yval in zip(x,y2/3958*100,y2):
   plt.text(xpos, ypos,"N=%d"%yval, ha="center", va="bottom")
for xpos, ypos, yval in zip(x+width,y3/3958*100,y3):
   plt.text(xpos, ypos,"N=%d"%yval, ha="center", va="bottom")  
plt.grid()
plt.show()
plt.rcParams['figure.figsize']=[15,8]


# In[255]:


#Plot frequency/count of # drug groups in victims system at TOD in regards to race in Denver
x = np.arange(len(drug_group_list))  
width=.3
y=np.array(cauc_den_drug_groups)
y2=np.array(hisp_den_drug_groups)
y3=np.array(afr_den_drug_groups)
fig, ax = plt.subplots()
rects1 = ax.bar(x - width, y/1946*100, width, label='Caucasian')
rects3 = ax.bar(x , y2/1946*100, width, label='Hispanic')
rects3 = ax.bar(x + width, y3/1946*100, width, label='African American')
ax.set_ylabel('Frequency')
ax.set_title('Drug Groups by Race in Denver')
ax.set_xticks(x)
ax.set_xticklabels(drug_group_list,rotation=25)
plt.yticks(np.arange(0, 60, 10))
ax.legend()
fig.tight_layout()
for xpos, ypos, yval in zip(x-width,y/1946*100,y):
   plt.text(xpos, ypos,"N=%d"%yval, ha="center", va="bottom")
for xpos, ypos, yval in zip(x,y2/1946*100,y2):
   plt.text(xpos, ypos,"N=%d"%yval, ha="center", va="bottom")
for xpos, ypos, yval in zip(x+width,y3/1946*100,y3):
   plt.text(xpos, ypos,"N=%d"%yval, ha="center", va="bottom")  
plt.grid()
plt.show()
plt.rcParams['figure.figsize']=[15,8]


# In[256]:


#Plot the distribution of Age against each drug group
sns.set(style="whitegrid")
ax = sns.violinplot(x='CNS Depressant', y='Age', data=suicidedata, inner="quartile")
plt.show()
ax = sns.violinplot(x='CNS Stimulant', y='Age', data=suicidedata, inner="quartile")
plt.show()
ax = sns.violinplot(x='Cannabis', y='Age', data=suicidedata, inner="quartile")
plt.show()
ax = sns.violinplot(x='Dissociative Anesthetic', y='Age', data=suicidedata, inner="quartile")
plt.show()
ax = sns.violinplot(x='Hallucinogen', y='Age', data=suicidedata, inner="quartile")
plt.show()
ax = sns.violinplot(x='Inhalant', y='Age', data=suicidedata, inner="quartile")
plt.show()
ax = sns.violinplot(x='Narcotic Analgesic', y='Age', data=suicidedata, inner="quartile")
plt.show()
ax = sns.violinplot(x='Other', y='Age', data=suicidedata, inner="quartile")
plt.show()
ax = sns.violinplot(x='Drug', y='Age', data=suicidedata, inner="quartile")
plt.show()
plt.rcParams['figure.figsize']=[5,5]


# In[257]:


#Drop rows with Nan entries in Age column
suicidedata = suicidedata.dropna(subset=['Age'])


# In[258]:


#Getting rid of spaces in Drug Groups Names     
suicidedata.columns = suicidedata.columns.str.replace(' ','_') 


# In[259]:


#Create arrays of age data for each drug group 
cd=suicidedata['Age'][suicidedata['CNS_Depressant']]
cs=suicidedata['Age'][suicidedata['CNS_Stimulant']]
c=suicidedata['Age'][suicidedata['Cannabis']]
da=suicidedata['Age'][suicidedata['Dissociative_Anesthetic']]
h=suicidedata['Age'][suicidedata['Hallucinogen']]
i=suicidedata['Age'][suicidedata['Inhalant']]
na=suicidedata['Age'][suicidedata['Narcotic_Analgesic']]
o=suicidedata['Age'][suicidedata['Other']]


# In[260]:


#Calculating Average Age and Standard Error
print('Mean and Standard Error for each drug group','\n','CNS Depressant Mean =',cd.mean(),'SE =',sem(cd),'\n',
      'CNS Stimulant Mean =',cs.mean(),'SE =',sem(cs),'\n','Cannabis Mean=',c.mean(),'SE =',sem(c),
      '\n','Dissociative Anesthetic Mean =',da.mean(),'SE =',sem(da),'\n','Hallucinogen Mean =',h.mean(),'SE =', sem(h),
      '\n','Inhalant Mean =',i.mean(),'SE =',sem(i),'\n','Narcotic Analgesic Mean =',na.mean(),'SE =',sem(na),
      '\n','Other Mean =',o.mean(),'SE =',sem(o))
y=suicidedata['Age'][suicidedata['Drug']].mean()
n=suicidedata['Age'][suicidedata['Drug']==0].mean()
print('Victims who had a drug in their system at TOD Mean =',y,'SE =',sem(suicidedata['Age'][suicidedata['Drug']]),'\n',
      'Victims without a drug in their system at TOD Mean =',n,'SE =',sem(suicidedata['Age'][suicidedata['Drug']==0]),'\n',
     'All Victims Mean =',suicidedata['Age'].mean(), 'SE =',sem(suicidedata['Age']))

