
############################ IMPORT ############################

import time
import numpy as np
import pdb
import pandas as pd
import matplotlib.pyplot as plt
from scipy.sparse import diags
from sklearn.cluster import AgglomerativeClustering, KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.metrics.pairwise import pairwise_distances

############################ MAIN ############################

def main():

  #load wind time series
  ts1 = time_serie('wind1.xlsx')

  #time series is aggregated
  ts1.agg(48,method='days')

  #aggregated time series is plotted
  ts1.plot(1,168)

############################ CODE ############################

class time_serie:

  #Inizialization
  def __init__(self,file_data):
    self.file_data = file_data
    self.df = pd.read_excel(file_data,sheet_name='input')
  
  #Agregate data
  def agg(self,nper,method='chrono'): 

    if method=='chrono':
      clus = 'chrono'
      dur = 1
    elif method=='days':
      clus = 'hier'
      dur = 24
    elif method=='week':
      clus = 'hier'
      dur = 168
  
    arr0 = self.df.values.reshape(int(self.df.shape[0]/dur),int(self.df.shape[1]*dur))
    nclus = int(nper/dur)
    arr1 = np.zeros((nclus,arr0.shape[1]))
    arr2 = np.zeros((int(self.df.shape[0]/dur),arr0.shape[1]))
  
    if clus=='chrono':     
      conec = diags([np.ones(arr0.shape[0]-1),np.ones(arr0.shape[0]-1)], [-1, 1])
      model = AgglomerativeClustering(linkage='ward',connectivity=conec,n_clusters=nclus, compute_full_tree=False)  
      model.fit(StandardScaler().fit_transform(arr0))    
      res = np.unique(model.labels_,return_index=True,return_counts=True) 
      for i in res[0]:
        arr1[i,:] = arr0[model.labels_==i,:].mean(axis=0)
      for i,j in enumerate(model.labels_):
        arr2[i,:] = arr1[j,:] 
      arr1 = arr1[model.labels_[np.sort(res[1])],:]
      arr1 = np.column_stack((arr1,np.repeat(res[2][model.labels_[np.sort(res[1])]],dur)))
      arr1 = np.column_stack((arr1,np.ones(nclus)))
      arr1 = np.column_stack((arr1,np.append(nclus-1,np.zeros(nclus-1))))   
         
    elif clus=='hier':
      model = AgglomerativeClustering(linkage='ward',n_clusters=nclus,compute_full_tree=False)
      model.fit(StandardScaler().fit_transform(arr0))
      res = np.unique(model.labels_,return_index=True,return_counts=True) 
      for i in res[0]:
        index = np.argmin(pairwise_distances(arr0[model.labels_==i,:]).mean(axis=0))
        arr1[i,:] = arr0[model.labels_==i,:][index,:]  
      for i,j in enumerate(model.labels_):
        arr2[i,:] = arr1[j,:]    
      arr1 = arr1.reshape(nclus*dur,self.df.shape[1])
      arr2 = arr2.reshape(self.df.shape[0],self.df.shape[1])
      arr1 = np.column_stack((arr1,np.ones(nclus*dur)))
      arr1 = np.column_stack((arr1,np.repeat(res[2][model.labels_[np.sort(res[1])]],dur)))
      arr1 = np.column_stack((arr1,np.zeros(nclus*dur)))    
      arr1[np.array(range(0,nclus*dur,dur)),-1] = np.array(range(0,nclus*dur,dur))-1+dur       
  
    self.df1 = pd.DataFrame(arr1,columns=np.append(self.df.columns.values,('tau','weg','chr')))
    self.df2 = pd.DataFrame(arr2,columns=self.df.columns)
    with pd.ExcelWriter(self.file_data[:-5]+'_output.xlsx') as writer:
        self.df1.to_excel(writer,'agg1')
        self.df2.to_excel(writer,'agg2')

  # Plot
  def plot(self,plot_start,plot_end):
    for k in self.df2.columns:
      df3 = pd.concat([self.df[k].loc[plot_start:plot_end],self.df2[k].loc[plot_start:plot_end]],axis=1)   
      df3.columns = ['original', 'aggregated']     
      df3.plot(title=k)   
      plt.show()

############################ RUN ############################

if __name__ == '__main__':
    main()

