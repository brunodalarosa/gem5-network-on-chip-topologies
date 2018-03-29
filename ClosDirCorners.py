# -*- coding: utf-8 -*-
# 2018
# Author: Bruno Cesar Puli Dala Rosa, bcesar.g6@gmail.com

from m5.params import *
from m5.objects import *
from math import *

from BaseTopology import SimpleTopology

# Cria uma topologia Clos com 4 diretórios, um em cada canto da topologia.
class ClosDirCorners_XY(SimpleTopology):
    description='ClosDirCorners_XY'

    def __init__(self, controllers):
        self.nodes = controllers

    def makeTopology(self, options, network, IntLink, ExtLink, Router):
        nodes = self.nodes

        num_rows = 4 #Parametro r
        num_columns = 5 #Parametro m
        cpu_per_router = options.num_cpus / (num_rows * 2)
        num_routers = num_rows * 2 + num_columns
        print("3-Stage Clos. Number of routers = " + str(num_routers))

        ## Define as latencias associadas.
        # default values for link latency and router latency.
        # Can be over-ridden on a per link/router basis
        link_latency = options.link_latency # used by simple and garnet
        router_latency = options.router_latency # only used by garnet

        # Determina quais nodos são controladores de cache vs diretórios vs DMA
        cache_nodes = []
        dir_nodes = []
        dma_nodes = []
        for node in nodes:
            if node.type == 'L1Cache_Controller' or \
            node.type == 'L2Cache_Controller':
                cache_nodes.append(node)
            elif node.type == 'Directory_Controller':
                dir_nodes.append(node)
            elif node.type == 'DMA_Controller':
                dma_nodes.append(node)

        # Cria os roteadores (Indirect type)
        routers = [Router(router_id=i, latency = router_latency) \
            for i in range(num_routers)]
        network.routers = routers

        # Contador de ID's para gerar ID's únicos das ligações.
        link_count = 0

        # Conecta cada nodo ao seu roteador apropriado
        ext_links = []
        print("Conectando os nodes aos roteadores\n")

        for i in xrange(num_rows):
            for j in xrange(cpu_per_router):
                node = cache_nodes[i * cpu_per_router + j]
                print("Conectado o node " + str(node) + " ao roteador " + str(i) + "\n")
                ext_links.append(ExtLink(link_id=link_count, ext_node=node,
                                        int_node=routers[i],
                                        latency = link_latency))
                link_count += 1

        for i in xrange(num_rows+5, num_routers):
            for j in xrange(cpu_per_router):
                node = cache_nodes[(options.num_cpus/2) + (i - num_rows -5) * cpu_per_router + j]
                print("Conectado o node " + str(node) + " ao roteador " + str(i) + "\n")
                ext_links.append(ExtLink(link_id=link_count, ext_node=node,
                                        int_node=routers[i],
                                        latency = link_latency))
                link_count += 1


        # Conecta os diretórios aos 4 "cantos" : 1 no inicio, 1 no fim, 2 no centro.
        print("Diretorio 1 ligado ao roteador 0")
        ext_links.append(ExtLink(link_id=link_count, ext_node=dir_nodes[0],
                                int_node=routers[0],
                                latency = link_latency))
        link_count += 1

        print("Diretorio 2 ligado ao roteador " + str(num_rows - 1))
        ext_links.append(ExtLink(link_id=link_count, ext_node=dir_nodes[1],
                                int_node=routers[num_rows - 1],
                                latency = link_latency))
        link_count += 1

        print("Diretorio 3 ligado ao roteador " + str(num_rows + 5))
        ext_links.append(ExtLink(link_id=link_count, ext_node=dir_nodes[2],
                                int_node=routers[num_rows + 5],
                                latency = link_latency))
        link_count += 1

        print("Diretorio 4 ligado ao roteador " + str(num_routers-1))
        ext_links.append(ExtLink(link_id=link_count, ext_node=dir_nodes[3],
                                int_node=routers[num_routers-1],
                                latency = link_latency))
        link_count += 1


        # Conecta os nodos de DMA ao roteador 0. These should only be DMA nodes.
        for (i, node) in enumerate(dma_nodes):
            assert(node.type == 'DMA_Controller')
            ext_links.append(ExtLink(link_id=link_count, ext_node=node,
                                     int_node=routers[0],
                                     latency = link_latency))

        network.ext_links = ext_links

        # Cria as conexões entre os roteadores em Flattened Butterfly
        print("\nConectando os roteadores entre eles")
        int_links = []

        # East output to West input links (weight = 1)
        print("\nEsquerda\n")
        for row in xrange(num_rows):
            for col in xrange(num_rows, num_rows + num_columns):
                _out = row
                _in = col
                print("Ligou o " +  str(_out) + " no " +  str(_in))
                int_links.append(IntLink(link_id=link_count,
                                         src_node=routers[_out],
                                         dst_node=routers[_in],
                                         src_outport="East",
                                         dst_inport="West",
                                         latency = link_latency,
                                         weight=1))
                link_count += 1

                _out = col
                _in = row
                print("Ligou o " +  str(_out) + " no " +  str(_in))
                int_links.append(IntLink(link_id=link_count,
                                         src_node=routers[_out],
                                         dst_node=routers[_in],
                                         src_outport="West",
                                         dst_inport="East",
                                         latency = link_latency,
                                         weight=1))
                link_count += 1


            print("---")

        # East output to West input links (weight = 1)
        print("\nDireita\n")
        for row in xrange(num_rows, num_rows + num_columns):
            for col in xrange(num_rows + num_columns, num_routers):
                _out = row
                _in = col
                print("Ligou o " +  str(_out) + " no " +  str(_in))
                int_links.append(IntLink(link_id=link_count,
                                         src_node=routers[_out],
                                         dst_node=routers[_in],
                                         src_outport="East",
                                         dst_inport="West",
                                         latency = link_latency,
                                         weight=1))
                link_count += 1

                _out = col
                _in = row
                print("Ligou o " +  str(_out) + " no " +  str(_in))
                int_links.append(IntLink(link_id=link_count,
                                         src_node=routers[_out],
                                         dst_node=routers[_in],
                                         src_outport="West",
                                         dst_inport="East",
                                         latency = link_latency,
                                         weight=1))
                link_count += 1


            print("---")
        network.int_links = int_links
