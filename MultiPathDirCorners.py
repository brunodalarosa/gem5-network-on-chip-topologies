# -*- coding: utf-8 -*-
# 2018
# Author: Bruno Cesar Puli Dala Rosa, bcesar.g6@gmail.com

from m5.params import *
from m5.objects import *
from math import *

from BaseTopology import SimpleTopology

# Cria uma topologia MultiPath com 4 diretórios, um em cada canto da topologia.
class MultiPathDirCorners_XY(SimpleTopology):
    description='MultiPathDirCorners_XY'

    def __init__(self, controllers):
        self.nodes = controllers

    def makeTopology(self, options, network, IntLink, ExtLink, Router):
        nodes = self.nodes

        # 1-ary (parametrizar?)
        cpu_per_router = 2

        num_clusters = options.num_cpus / 8
        num_routers = num_clusters * 6

        if(num_clusters > 1):
            for i in xrange(1, int( log(num_clusters , 2) + 1) ):
                num_routers += num_clusters / i

        print("\nMultipath number of routers = " + str(num_routers))

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

        # O número de cpus deve ser multiplo de 8
        # O número de diretórios deve ser igual a 4.
        assert(options.num_cpus%8 == 0)
        assert(len(dir_nodes) == 4)

        # Cria os roteadores
        routers = [Router(router_id=i, latency = router_latency) \
            for i in range(num_routers)]
        network.routers = routers

        # Contador de ID's para gerar ID's únicos das ligações.
        link_count = 0

        # Conecta cada nodo ao seu roteador apropriado
        ext_links = []
        node_id = 0
        print("Conectando os nodes aos roteadores\n")
        for c in xrange(0, num_routers, 8):
            for i in xrange(c+1, c+5):
                for j in xrange(2):
                    print("Conectado o node " + str(node_id) + " ao roteador " + str(i) + "\n")
                    ext_links.append(ExtLink(link_id=link_count, ext_node=nodes[node_id],
                                            int_node=routers[i],
                                            latency = link_latency))
                    link_count += 1
                    node_id += 1

        # Conecta os diretórios aos 4 "cantos" : nesta topologia depende do numero de "clusters"
        print("Conectando os diretorios\n")
        if(num_clusters <= 1):
            for i in xrange(1,5):
                print("Diretorio " + str(i-1) + " ligado ao roteador " + str(i))
                ext_links.append(ExtLink(link_id=link_count, ext_node=dir_nodes[i-1],
                                         int_node=routers[i],
                                         latency = link_latency))
                link_count += 1

        elif(num_clusters < 4):
            print("Diretorio 0 ligado ao roteador 1")
            ext_links.append(ExtLink(link_id=link_count, ext_node=dir_nodes[0],
                                     int_node=routers[1],
                                     latency = link_latency))
            link_count += 1

            print("Diretorio 1 ligado ao roteador 3")
            ext_links.append(ExtLink(link_id=link_count, ext_node=dir_nodes[1],
                                     int_node=routers[3],
                                     latency = link_latency))
            link_count += 1

            print("Diretorio 2 ligado ao roteador 10")
            ext_links.append(ExtLink(link_id=link_count, ext_node=dir_nodes[2],
                                     int_node=routers[10],
                                     latency = link_latency))
            link_count += 1

            print("Diretorio 3 ligado ao roteador 12")
            ext_links.append(ExtLink(link_id=link_count, ext_node=dir_nodes[3],
                                     int_node=routers[12],
                                     latency = link_latency))
            link_count += 1

        else:
            dir_id = 0
            for i in xrange(1, 26, 8):
                print("Diretorio " + str(dir_id) + " ligado ao roteador " + str(i))
                ext_links.append(ExtLink(link_id=link_count, ext_node=dir_nodes[dir_id],
                                         int_node=routers[i],
                                         latency = link_latency))
                link_count += 1
                dir_id += 1

        # Conecta os nodos de DMA ao roteador 0. These should only be DMA nodes.
        for (i, node) in enumerate(dma_nodes):
            assert(node.type == 'DMA_Controller')
            ext_links.append(ExtLink(link_id=link_count, ext_node=node,
                                     int_node=routers[0],
                                     latency = link_latency))

        network.ext_links = ext_links

        # Cria as conexões entre os roteadores em Butterfly
        print("\nConectando os roteadores entre eles")
        int_links = []

        for i in xrange(0, num_routers, 8):
                print("cluster " + str(i/8+1))
                for j in xrange(1,5):
                    _out = i

                    _in = i + j

                    print("Ligação bidirecional entre " +  str(_out) + " e " +  str(_in))
                    int_links.append(IntLink(link_id=link_count,
                    src_node=routers[_out],
                    dst_node=routers[_in],
                    src_outport="East",
                    dst_inport="West",
                    latency = link_latency,
                    weight=1))

                    link_count += 1

                    int_links.append(IntLink(link_id=link_count,
                    src_node=routers[_in],
                    dst_node=routers[_out],
                    src_outport="West",
                    dst_inport="East",
                    latency = link_latency,
                    weight=1))

                    link_count += 1


                for j in xrange(1,5):
                    _out = i + 5

                    _in = (i + 5) - j

                    print("Ligação bidirecional entre " +  str(_out) + " e " +  str(_in))
                    int_links.append(IntLink(link_id=link_count,
                    src_node=routers[_out],
                    dst_node=routers[_in],
                    src_outport="East",
                    dst_inport="West",
                    latency = link_latency,
                    weight=1))

                    link_count += 1

                    int_links.append(IntLink(link_id=link_count,
                    src_node=routers[_in],
                    dst_node=routers[_out],
                    src_outport="West",
                    dst_inport="East",
                    latency = link_latency,
                    weight=1))

                    link_count += 1

        # A partir de 2 clusters exige mais conexoes!
        if(num_clusters > 1):
            print("\nConexoes entre os clusters:")

            for i in xrange(num_clusters/2):
                _out = 6 + (i * 16)
                for j in xrange(2):
                    if(j%2 == 0):
                        _in = _out - 6
                    else:
                        _in = _out + 6

                    print("Ligação bidirecional entre " +  str(_out) + " e " +  str(_in))
                    int_links.append(IntLink(link_id=link_count,
                    src_node=routers[_out],
                    dst_node=routers[_in],
                    src_outport="South",
                    dst_inport="North",
                    latency = link_latency,
                    weight=1))

                    link_count += 1

                    int_links.append(IntLink(link_id=link_count,
                    src_node=routers[_in],
                    dst_node=routers[_out],
                    src_outport="North",
                    dst_inport="South",
                    latency = link_latency,
                    weight=1))

                    link_count += 1

                    if(j%2 == 0):
                        _in = _out + 2
                    else:
                        _in = _out - 2

                    print("Ligação bidirecional entre " +  str(_out) + " e " +  str(_in))
                    int_links.append(IntLink(link_id=link_count,
                    src_node=routers[_out],
                    dst_node=routers[_in],
                    src_outport="South",
                    dst_inport="North",
                    latency = link_latency,
                    weight=1))

                    link_count += 1

                    int_links.append(IntLink(link_id=link_count,
                    src_node=routers[_in],
                    dst_node=routers[_out],
                    src_outport="North",
                    dst_inport="South",
                    latency = link_latency,
                    weight=1))

                    link_count += 1

                    _out += 1

            for i in xrange(num_clusters/2):
                for j in xrange(2):
                    _out = (i*16) + (j * 5)
                    _in = (i * 16) + 8 + (j * 5)

                    print("Ligação bidirecional entre " +  str(_out) + " e " +  str(_in))
                    int_links.append(IntLink(link_id=link_count,
                    src_node=routers[_out],
                    dst_node=routers[_in],
                    src_outport="East",
                    dst_inport="West",
                    latency = link_latency,
                    weight=1))

                    link_count += 1

                    int_links.append(IntLink(link_id=link_count,
                    src_node=routers[_in],
                    dst_node=routers[_out],
                    src_outport="West",
                    dst_inport="East",
                    latency = link_latency,
                    weight=1))

                    link_count += 1

            if(num_clusters > 2):

                _out = 14
                for i in xrange(2):

                    _in = _out - 8

                    print("Ligação bidirecional entre " +  str(_out) + " e " +  str(_in))
                    int_links.append(IntLink(link_id=link_count,
                    src_node=routers[_out],
                    dst_node=routers[_in],
                    src_outport="South",
                    dst_inport="North",
                    latency = link_latency,
                    weight=1))

                    link_count += 1

                    int_links.append(IntLink(link_id=link_count,
                    src_node=routers[_in],
                    dst_node=routers[_out],
                    src_outport="North",
                    dst_inport="South",
                    latency = link_latency,
                    weight=1))

                    link_count += 1

                    _in = _out + 8

                    print("Ligação bidirecional entre " +  str(_out) + " e " +  str(_in))
                    int_links.append(IntLink(link_id=link_count,
                    src_node=routers[_out],
                    dst_node=routers[_in],
                    src_outport="South",
                    dst_inport="North",
                    latency = link_latency,
                    weight=1))

                    link_count += 1

                    int_links.append(IntLink(link_id=link_count,
                    src_node=routers[_in],
                    dst_node=routers[_out],
                    src_outport="North",
                    dst_inport="South",
                    latency = link_latency,
                    weight=1))

                    link_count += 1

                    _out += 1

                for i in xrange(6,8):
                    _out = i
                    _in = i + 16

                    print("Ligação bidirecional entre " +  str(_out) + " e " +  str(_in))
                    int_links.append(IntLink(link_id=link_count,
                    src_node=routers[_out],
                    dst_node=routers[_in],
                    src_outport="East",
                    dst_inport="West",
                    latency = link_latency,
                    weight=1))

                    link_count += 1

                    int_links.append(IntLink(link_id=link_count,
                    src_node=routers[_in],
                    dst_node=routers[_out],
                    src_outport="West",
                    dst_inport="East",
                    latency = link_latency,
                    weight=1))

                    link_count += 1


        network.int_links = int_links
