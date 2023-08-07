import pandas as pd
from data_process import merge, frequencies_from_origin_departamento_by_year, m_basemap_properties, draw_basemap
#import datetime
import networkx as nx  
from mpl_toolkits.basemap import Basemap 
import matplotlib.pyplot as plt

convert = {'terminal':str, 'clase_vehiculo':str, 'nivel_servicio':str, 'municipio_origen_ruta':str,
       'municipio_destino_ruta':str,  'hora_despacho':int,
       'tipo_despacho':str, 'despachos':int, 'pasajeros':int}

convert_dict = {'departamento_codigo':str, 'departamento_nombre':str, 'municipio_codigo':str,
       'municipio_nombre':str, 'tipo':str, 'latitud':str, 'longitud':str
                } 

df_departure_terminal = pd.read_csv("https://www.datos.gov.co/resource/eh75-8ah6.csv", dtype=convert )


df_info_municipality = pd.read_csv("https://github.com/nrrf/nrrf/files/12229980/DIVIPOLA_Municipios_tabla.csv", 
                sep=";", dtype = convert_dict)
 
# Rename info municipality column values because we don't want duplicate column problems in 
# the merge
rename = list(df_info_municipality.keys())
rename.remove('municipio_codigo')

origen_rename = ['origen_'+i for i in rename]
destino_rename = ['destino_'+i for i in rename] 

df_merge = merge(df_departure_terminal, df_info_municipality, left_key=['municipio_origen_ruta'], 
            right_key = ['municipio_codigo'], columns_rename=rename, new_names =origen_rename) 

# Merge dataset with inner joins between municipality codes
df_merge = merge(df_merge, df_info_municipality, left_key=['municipio_destino_ruta'], 
            right_key = ['municipio_codigo'], columns_rename=rename, new_names =destino_rename)  

departamentos_origin = df_merge["origen_departamento_nombre"].unique()

# Frequeny's tables by columns

frequencies_from_origin_departamento_by_year(df_merge, departamentos_origin,
'destino_departamento_nombre','2021')

frequencies_from_origin_departamento_by_year(df_merge, departamentos_origin,'hora_despacho' , '2021') 

frequencies_from_origin_departamento_by_year(df_merge, departamentos_origin,'clase_vehiculo' , '2021') 

frequencies_from_origin_departamento_by_year(df_merge, departamentos_origin,'nivel_servicio' , '2021')  

# To describe monthly frequency we need a new column  

df_merge["mes"] = pd.to_datetime(df_merge["fecha_despacho"]).dt.strftime('%m') 

frequency_by_month = frequencies_from_origin_departamento_by_year(df_merge, departamentos_origin,'mes' 
                    , '2021')   
number_departures = frequency_by_month.pop("numero_salidas")
relative_frequency_by_month = frequency_by_month.div(frequency_by_month.sum(axis=1), axis=0).round(2) 
relative_frequency_by_month["numero_salidas"]=number_departures 
relative_frequency_by_month.to_csv("assets/frequency_relative_by_month_2021.csv") 

#### Associated Graph ##### 

G = nx.from_pandas_edgelist(df_merge, source='municipio_origen_ruta', target='municipio_destino_ruta') 

# we need the values of latitude and longitude as a values in tuple 

df_info_municipality["pos"] = list(zip(df_info_municipality["latitud"].replace(',','.', regex=True)
                        .astype(float), df_info_municipality["longitud"].replace(',','.', regex=True)
                        .astype(float)))   

df_positions = df_info_municipality[["municipio_codigo","pos"]]
node_attr = df_positions.set_index('municipio_codigo').to_dict('index')
nx.set_node_attributes(G, node_attr) 
pos = nx.get_node_attributes(G, 'pos') 

nx.draw_networkx(G, pos, node_size=1, with_labels=False, font_size=6,width=0.1) 

##Draw with poitions in Colombia ### 

west, south, east, north = -82.47,-4.50, -66.56, 13.84 

m = m_basemap_properties(west, south, east, north)

mx,my = m(list(df_info_municipality["longitud"].replace(',','.', regex=True).astype(float)),
        list(df_info_municipality["latitud"].replace(',','.', regex=True).astype(float))) 
pos_map=list(zip(mx, my)) 
df_info_municipality["pos_map"] =  pos_map 

df_positions_map = df_info_municipality[["municipio_codigo", "pos","pos_map"]] 
node_attr = df_positions_map.set_index('municipio_codigo').to_dict('index')
nx.set_node_attributes(G, node_attr)
pos_map = nx.get_node_attributes(G,"pos_map") 
pos_map 

nx.draw_networkx_nodes(G, pos_map, node_size=10, nodelist = G.nodes())
draw_basemap(m)

#m.drawmapboundary(fill_color='aqua')


plt.title("Transporte Terrestre Colombia") 
plt.savefig('assets/nodes_transport_colombia.png') 
plt.clf()

nx.draw_networkx_edges(G, pos_map, edge_color='r', alpha=0.4, width=.6)  
draw_basemap(m)
plt.title("Transporte Terrestre Colombia") 
plt.savefig('assets/edges_transport_colombia.png') 