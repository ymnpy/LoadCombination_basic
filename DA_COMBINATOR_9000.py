from pyNastran.bdf.bdf import read_bdf
from pyNastran.op2.op2 import read_op2
import numpy as np
import pandas as pd

#questionable class usage
class Sources():
    def __init__(self,bdf_mech,op2_mech,bdf_ther,op2_ther):
        try:
            self.mech_bdf=read_bdf(bdf_mech)
            self.mech_op2=read_op2(op2_mech,build_dataframe=True)
            self.ther_op2=read_op2(op2_ther,build_dataframe=True)
        except:
            raise Exception("Something is wrong with source files.")
    
    #apply the main formula, but before calculate the std
    def do_addition(self,df1_col,df2_col,f=2):
        if np.mean(df1_col)*np.std(df1_col)>=0: std=np.std(df1_col)
        else: std1=np.std(df1_col)*-1
        
        if np.mean(df2_col)*np.std(df2_col)>=0: std=np.std(df2_col)
        else: std2=np.std(df2_col)*-1
         
        nij=(np.mean(df1_col)+std1*f)*1.5+(np.mean(df2_col)+std2*f)*1.0
        
        return nij
    
    #looking for matched mechanical and thermal cases and goes to addition from there
    def do_combine(self,given_prop):
        pid2eid=self.mech_bdf.get_property_id_to_element_ids_map()
        ll=[]
        for prop in given_prop:
            elems=pid2eid[prop]
            for lcid_mech,dfish_mech in self.mech_op2.cquad4_force.items():
                for lcid_ther,dfish_ther in self.ther_op2.cquad4_force.items():
                    if str(lcid_mech)[1:3]==str(lcid_ther)[1:3]:
                        df_mech_f=dfish_mech.dataframe.query('ElementID in @elems')
                        df_ther_f=dfish_ther.dataframe.query('ElementID in @elems')
                        
                        nxx=self.do_addition(df_mech_f["mx"],df_ther_f["mx"])
                        nyy=self.do_addition(df_mech_f["my"],df_ther_f["my"])    
                        nxy=self.do_addition(df_mech_f["mxy"],df_ther_f["mxy"])    
                        
                    if int(str(lcid_ther)[1:3])%2==0: 
                        lcid_combined=str(lcid_mech)+"_HOT"
                    else:
                        lcid_combined=str(lcid_mech)+"_COLD"
                    
                    ll.append((prop,lcid_mech,lcid_ther,lcid_combined,nxx,nyy,nxy))
        
        return ll
    
#FILES
f1='C:/Users/User/Desktop/v/HM/updated_model_220619_2249/yo/mek.bdf'
f2='C:/Users/User/Desktop/v/HM/updated_model_220619_2249/yo/mek.op2'
f3='C:/Users/User/Desktop/v/HM/updated_model_220619_2249/yo/ther.op2'

#STUFF
source=Sources(f1,f2,f3)
given_prop=[100,101,102,103,104,105,106,107,108,109,110,111,112]

#MAIN
ll=source.do_combine(given_prop)

#OUTPUT
df_out=pd.DataFrame(ll,columns=['PID','LCID_M','LCID_T','LCID','NXX','NYY','NXY'])
df_out.to_excel("combined_stuff.xlsx")
