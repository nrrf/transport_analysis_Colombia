import pandas as pd
from mpl_toolkits.basemap import Basemap 
def merge(df,df1,left_key=[], right_key=[], columns_rename=[], new_names=[]):
  df_merge = pd.merge(df, df1,  how='inner', left_on=left_key, right_on = right_key)
  columns_dict= dict(zip(columns_rename, new_names))
  df_merge.rename(columns=columns_dict, inplace=True)
  df_merge.drop(right_key, axis = 1, inplace=True)
  return df_merge

def frequencies_from_origin_departamento_by_year(df2, departamentos_origin, group_column, year):
  arrive_departure_list = list()
  # pivot column to make sure that the reference column is not the same as the grouping column
  pivot = df2.columns
  if(pivot[0] != group_column):
    pivot=pivot[0]
  else:
    pivot = pivot[1]
  for i in departamentos_origin:
    arrive_departure = df2.loc[(df2['origen_departamento_nombre'] == i) & (df2['fecha_despacho'].str.contains(year))].groupby(group_column)[pivot].count()
    arrive_departure = dict(arrive_departure)
    #print(arrive_departure)
    total_salidas = sum(arrive_departure.values() )
    arrive_departure["numero_salidas"]=total_salidas
    arrive_departure["departamento_origen"]=i
    arrive_departure_list.append(arrive_departure)
  df_frequency = pd.DataFrame.from_records(arrive_departure_list,index = ["departamento_origen"])
  df_frequency.insert(0, 'numero_salidas', df_frequency.pop('numero_salidas'))
  df_frequency.fillna(0, inplace = True)
  df_frequency.head()
  df_frequency.to_csv("assets/frequency_"+group_column+"_"+str(year)+".csv")

  return df_frequency

def m_basemap_properties(west, south, east, north): 
    m = Basemap(
         projection='merc',
         llcrnrlon=west,
         llcrnrlat=south,
         urcrnrlon=east,
         urcrnrlat=north,
         lat_ts=0,
         resolution='l',
         suppress_ticks=True)  
    return m

def draw_basemap(m):
    m.drawcountries(linewidth = 1)
    m.drawstates(linewidth = 0.2)
    m.drawcoastlines(linewidth=1)