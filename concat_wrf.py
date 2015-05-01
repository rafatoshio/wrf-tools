# -*- coding: UTF-8 -*-
from netCDF4 import Dataset
import numpy
import argparse
import sys
import os

############################################################################################################################################
#################################################
__author__ = 'rafa.toshio'
modificado = "01/05/2015"
versao = "v1.0" 
#################################################
#Tratamento dos argumentos
descricao="++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++\n\
+     Intituto Tecnologico SIMEPAR - www.simepar.br                      +\n\
+                                                                        +\n\
+ autor: %-20s                                            +\n\
+ modificado: %-10s                                                 +\n\
++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++\n\n\
description:\nConcatena saidas o wrf. Procura por arquivos wrfout_dxx dentro do diretorio dir_arq\n\
++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++\n\n\
" % (__author__,modificado)

epilogo="++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++"

parser = argparse.ArgumentParser(description=descricao,epilog=epilogo,formatter_class=argparse.RawTextHelpFormatter,add_help=False)
parser.add_argument("-h","--help",help="mostra essa mensagem e sai\n\n",action="help")
parser.add_argument("-dir_arq",help="caminho do diretorio onde se encontram os arquivos\n\n", \
                    action="store", metavar="/path/",default='./',required=True)
parser.add_argument("-d",help="dominio do arquivo wrf\n\n", \
                    action="store", metavar="1",default=1,required=True,type=int)                    
parser.add_argument('--version', help="mostra a versao do programa e sai",action='version', version='%s %s'%('%(prog)s',versao))
args = parser.parse_args()
#Fim tratamento dos argumentos
############################################################################################################################################

dir_arq = args.dir_arq
dominio = args.d

arquivos = []
for i in os.listdir(dir_arq):
    if os.path.isfile(os.path.join(dir_arq,i)) and 'wrfout_d%2.2i'%dominio in i:
        arquivos.append(i)
arquivos.sort()

print "CONCATENANDO ARQUIVOS:\n"
print arquivos

nome_out = arquivos[0]+"_concat"
concat_out =  Dataset(nome_out,'w',format='NETCDF4_CLASSIC')



#calcula quantos tempos tem no total (dimensao de Times)
dim_t = 0
for arq in arquivos:
	f = Dataset(dir_arq+arq)
	dim_t = dim_t + f.dimensions["Time"].__len__()
	f.close()

#copia dimensoes do primerio arquivo
f = Dataset(dir_arq+arquivos[0])
for d in f.dimensions.keys():
	if not d == "Time": #se nao for a dimensao tempo copia para o arquivo concatenado
		concat_out.createDimension(d,f.dimensions[d].__len__())
	else:
		concat_out.createDimension(d,dim_t)	

#copia variaveis globais
for g in f.ncattrs():
	setattr(concat_out,g,getattr(f,g))


#cria variaveis
for var in f.variables.keys():
	var_in = f.variables[var]
	x = concat_out.createVariable(var,var_in.dtype,var_in.dimensions) #cria a varaivel
	#concatena a mesma variavel de todos os arquivos
	for arq in arquivos:
		g = Dataset(dir_arq+arq)
		if "conteudo_var" in locals():
			conteudo_var=numpy.concatenate((conteudo_var, g.variables[var][:]), axis=0)
		else:
			conteudo_var = g.variables[var][:]
	#copia atributos da variavel original
	x.setncatts({k: var_in.getncattr(k) for k in var_in.ncattrs()})
	#adiciona os valores concatenados na variavel
	x[:] = conteudo_var
	del conteudo_var

#combina as variaveis e adiciona ao arquivo


f.close()
concat_out.close()	

########################### 

# Esquema para copiar todas as dimensoes do arquivo
# for dname, the_dim in dsin.dimensions.iteritems():
#     print dname, len(the_dim)
#     dsout.createDimension(dname, len(the_dim) if not the_dim.isunlimited() else None)
