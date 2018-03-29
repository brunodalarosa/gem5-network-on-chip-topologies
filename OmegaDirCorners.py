# -*- coding: utf-8 -*-
# 2018
# Author: Bruno Cesar Puli Dala Rosa, bcesar.g6@gmail.com

from m5.params import *
from m5.objects import *
from math import *

from BaseTopology import SimpleTopology

# Cria uma topologia Omega   com 4 diretórios, um em cada canto da topologia.
class OmegaDirCorners_XY(SimpleTopology):
    description='OmegaDirCorners_XY'

    def __init__(self, controllers):
        self.nodes = controllers

    def makeTopology(self, options, network, IntLink, ExtLink, Router):
        nodes = self.nodes

        # 2-ary (parametrizar?)
        cpu_per_router = 1

        num_routers = int((options.num_cpus * (log(options.num_cpus,2) + 1)) / cpu_per_router)
        print("Butterfly number of routers = " + str(num_routers))
        num_rows = int(log(options.num_cpus, 2) + (2 - cpu_per_router))
        print("With " + str(num_rows) + " Ranks")

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

        # O número de linhas deve ser <= ao número de roteadores e divisivel por ele.
        # O número de diretórios deve ser igual a 4.
        assert(num_rows > 0 and num_rows <= num_routers)
        assert(len(dir_nodes) == 4)

        # Cria os roteadores
        routers = [Router(router_id=i, latency = router_latency) \
            for i in range(num_routers)]
        network.routers = routers

        # Contador de ID's para gerar ID's únicos das ligações.
        link_count = 0

        # Conecta cada nodo ao seu roteador apropriado
        ext_links = []
        print("Conectando os nodes aos roteadores\n")
        for (i, n) in enumerate(cache_nodes):
            cntrl_level, router_id = divmod(i, options.num_cpus / cpu_per_router)
            print("Conectado o node " + str(n) + " ao roteador " + str(router_id) + "\n")
            ext_links.append(ExtLink(link_id=link_count, ext_node=n,
                                    int_node=routers[router_id],
                                    latency = link_latency))
            link_count += 1

        # Conecta os diretórios aos 4 "cantos" : 1 no inicio, 1 no fim, 2 no centro.
        print("Diretorio 1 ligado ao roteador 0")
        ext_links.append(ExtLink(link_id=link_count, ext_node=dir_nodes[0],
                                int_node=routers[0],
                                latency = link_latency))
        link_count += 1

        print("Diretorio 2 ligado ao roteador " + str((options.num_cpus / cpu_per_router / 2) - 1))
        ext_links.append(ExtLink(link_id=link_count, ext_node=dir_nodes[1],
                                int_node=routers[(options.num_cpus / cpu_per_router / 2) - 1],
                                latency = link_latency))
        link_count += 1

        print("Diretorio 3 ligado ao roteador " + str(options.num_cpus/cpu_per_router / 2))
        ext_links.append(ExtLink(link_id=link_count, ext_node=dir_nodes[2],
                                int_node=routers[options.num_cpus / cpu_per_router / 2],
                                latency = link_latency))
        link_count += 1

        print("Diretorio 4 ligado ao roteador " + str((options.num_cpus / cpu_per_router) - 1))
        ext_links.append(ExtLink(link_id=link_count, ext_node=dir_nodes[3],
                                int_node=routers[(options.num_cpus / cpu_per_router) - 1],
                                latency = link_latency))
        link_count += 1

        # Conecta os nodos de DMA ao roteador 0. These should only be DMA nodes.
        for (i, node) in enumerate(dma_nodes):
            assert(node.type == 'DMA_Controller')
            ext_links.append(ExtLink(link_id=link_count, ext_node=node,
                                     int_node=routers[0],
                                     latency = link_latency))

        network.ext_links = ext_links

        # Cria as conexões entre os roteadores em Omega
        print("\nConectando os roteadores entre eles")
        int_links = []

        for i in xrange(num_rows - 1):
            aux = 0
            for j in xrange(options.num_cpus / cpu_per_router):
                print("\nO node [" +str(i)+ ","+str(j)+"] se conecta em:")
                print("[" + str(i+1) + "," + str(aux) + "]")

                _out = (i * options.num_cpus / cpu_per_router) + j
                _in = ((i+1) * options.num_cpus / cpu_per_router) + aux

                print("Ligou o " +  str(_out) + " no " +  str(_in))
                int_links.append(IntLink(link_id=link_count,
                                         src_node=routers[_out],
                                         dst_node=routers[_in],
                                         src_outport="South",
                                         dst_inport="North",
                                         latency = link_latency,
                                         weight=1))
                link_count += 1

                print("Ligou o " +  str(_in) + " no " +  str(_out))
                int_links.append(IntLink(link_id=link_count,
                                         src_node=routers[_in],
                                         dst_node=routers[_out],
                                         src_outport="North",
                                         dst_inport="South",
                                         latency = link_latency,
                                         weight=1))
                link_count += 1


                aux += 1

                print("\nE em [" + str(i+1) + "," + str(aux) + "]")
                _in = ((i+1) * options.num_cpus / cpu_per_router) + aux

                print("Ligou o " +  str(_out) + " no " +  str(_in))
                int_links.append(IntLink(link_id=link_count,
                                         src_node=routers[_out],
                                         dst_node=routers[_in],
                                         src_outport="South",
                                         dst_inport="North",
                                         latency = link_latency,
                                         weight=1))
                link_count += 1

                print("Ligou o " +  str(_in) + " no " +  str(_out))
                int_links.append(IntLink(link_id=link_count,
                                         src_node=routers[_in],
                                         dst_node=routers[_out],
                                         src_outport="North",
                                         dst_inport="South",
                                         latency = link_latency,
                                         weight=1))
                link_count += 1

                if(j == (options.num_cpus / cpu_per_router / 2) - 1):
                    print("---RESETOU AUX!!!---")
                    aux = 0
                else:
                    aux += 1

        network.int_links = int_links
