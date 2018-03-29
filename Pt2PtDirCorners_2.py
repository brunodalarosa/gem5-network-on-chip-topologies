# -*- coding: utf-8 -*-
# 2018
# Author: Bruno Cesar Puli Dala Rosa, bcesar.g6@gmail.com

from m5.params import *
from m5.objects import *

from BaseTopology import SimpleTopology

class Pt2PtDirCorners_2(SimpleTopology):
    description='Pt2PtDirCorners_2'

    def __init__(self, controllers):
        self.nodes = controllers

    def makeTopology(self, options, network, IntLink, ExtLink, Router):
        nodes = self.nodes

        # Radix dos roteadores
        cpu_per_router = 2

        num_routers = options.num_cpus / cpu_per_router

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
            cntrl_level, router_id = divmod(i, num_routers)
            assert(cntrl_level < cpu_per_router)
            print("Conectado o node " + str(n) + " ao roteador " + str(router_id) + "\n")
            ext_links.append(ExtLink(link_id=link_count, ext_node=n,
                                    int_node=routers[router_id],
                                    latency = link_latency))
            link_count += 1

        # Adicionado os 4 diretórios em 4 posições distintas
        print("Diretorio 0 ligado ao roteador 0")
        ext_links.append(ExtLink(link_id=link_count, ext_node=dir_nodes[0],
                                int_node=routers[0],
                                latency = link_latency))
        link_count += 1

        print("Diretorio 1 ligado ao roteador " + str(num_routers/2 - 1))
        ext_links.append(ExtLink(link_id=link_count, ext_node=dir_nodes[1],
                                int_node=routers[num_routers/2 - 1],
                                latency = link_latency))
        link_count += 1

        print("Diretorio 2 ligado ao roteador " + str(num_routers/2))
        ext_links.append(ExtLink(link_id=link_count, ext_node=dir_nodes[2],
                                int_node=routers[num_routers/2],
                                latency = link_latency))
        link_count += 1

        print("Diretorio 3 ligado ao roteador " + str(num_routers -1))
        ext_links.append(ExtLink(link_id=link_count, ext_node=dir_nodes[3],
                                int_node=routers[num_routers - 1],
                                latency = link_latency))
        link_count += 1

        network.ext_links = ext_links

        print("\nConectando os roteadores entre eles")
        int_links = []
        for i in xrange(num_routers):
            for j in xrange(num_routers):
                if (i != j):
                    link_count += 1
                    print("Ligou o " +  str(i) + " no " +  str(j))
                    int_links.append(IntLink(link_id=link_count,
                                             src_node=routers[i],
                                             dst_node=routers[j],
                                             latency = link_latency))

        network.int_links = int_links
