# -*- coding: utf-8 -*-
# # Copyright (c) 2010 Advanced Micro Devices, Inc.
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are
# met: redistributions of source code must retain the above copyright
# notice, this list of conditions and the following disclaimer;
# redistributions in binary form must reproduce the above copyright
# notice, this list of conditions and the following disclaimer in the
# documentation and/or other materials provided with the distribution;
# neither the name of the copyright holders nor the names of its
# contributors may be used to endorse or promote products derived from
# this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
# A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
# OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
# LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
# DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
# THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#
# Authors: Brad Beckmann
#
# ^ ORIGINAL COPYRIGHT OF MESH TOPOLOGY WHICH WAS USED AS BASE TO THIS ^
#
# 2018
# Author: Bruno Cesar Puli Dala Rosa, bcesar.g6@gmail.com

from m5.params import *
from m5.objects import *
from math import *

from BaseTopology import SimpleTopology

# Cria uma topologia MultiPath com 4 diretórios, um em cada canto da topologia.
class MultiPath(SimpleTopology):
    description='MultiPath'

    def __init__(self, controllers):
        self.nodes = controllers

    def makeTopology(self, options, network, IntLink, ExtLink, Router):
        nodes = self.nodes

        ## Define as latencias associadas.
        # default values for link latency and router latency.
        # Can be over-ridden on a per link/router basis
        link_latency = options.link_latency # used by simple and garnet
        router_latency = options.router_latency # only used by garnet

        print(options)

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
        assert(options.num_cpus%8 == 0)

        num_clusters = options.num_cpus / ( 4 * options.cntrls_per_router )
        num_routers = num_clusters * 6

        if(num_clusters > 1):
            for i in xrange(1, int( log(num_clusters , 2) + 1) ):
                num_routers += num_clusters / i

        print("number of clusters = " + str(num_clusters))
        print("\nMultipath number of routers = " + str(num_routers))

        # Cria os roteadores
        routers = [Router(router_id=i, latency = router_latency) for i in range(num_routers)]
        network.routers = routers

        # Contador de ID's para gerar ID's únicos das ligações.
        link_count = 0

        # Conecta cada nodo ao seu roteador apropriado
        ext_links = []
        node_id = 0

        c = 1
        gap = 1

        print("Conectando os nodes aos roteadores:\n")
        for l in xrange(len(cache_nodes)):
            print("Conectado o node (" + cache_nodes[node_id].type + ") " + str(node_id) + " ao roteador " + str(c))
            ext_links.append(ExtLink(link_id=link_count, ext_node=cache_nodes[node_id],
                                     int_node=routers[c],
                                     latency = link_latency))

            link_count += 1
            node_id += 1

            if (gap%4==0):
                if (num_clusters==1) or ((gap)/4 == num_clusters):
                    c = 1
                    gap = 0
                else:
                    c += 5
            else:
                c += 1

            gap += 1

        print("Conectando os diretorios:\n")
        if (num_clusters == 1):
            for i in xrange(1,5):
                print("Diretorio " + str(i-1) + " ligado ao roteador " + str(i))
                ext_links.append(ExtLink(link_id=link_count, ext_node=dir_nodes[i-1],
                                         int_node=routers[i],
                                         latency = link_latency))
                link_count += 1

        elif (num_clusters == 2) or (num_clusters == 4):
            first_router_id = iter([3, 2, 4, 0])
            router_id = 1
            for d in xrange(len(dir_nodes)):
                print("Diretorio " + str(d) + " ligado ao roteador " + str(router_id))
                ext_links.append(ExtLink(link_id=link_count, ext_node=dir_nodes[d],
                                         int_node=routers[router_id],
                                         latency = link_latency))

                if ((d + 1) % num_clusters == 0):
                    router_id = next(first_router_id)
                else:
                    router_id += 8

                link_count += 1

        else:
            first_router_id = iter([3, 2, 4, 0])
            router_id = 1
            for d in xrange(len(dir_nodes)):
                print("Diretorio " + str(d) + " ligado ao roteador " + str(router_id))
                ext_links.append(ExtLink(link_id=link_count, ext_node=dir_nodes[d],
                                         int_node=routers[router_id],
                                         latency = link_latency))

                if ((d + 1) % num_clusters == 0):
                    router_id = next(first_router_id)
                else:
                    router_id += 16

                link_count += 1

        # Conecta os nodos de DMA ao roteador 0. These should only be DMA nodes.
        for (i, node) in enumerate(dma_nodes):
            assert(node.type == 'DMA_Controller')
            ext_links.append(ExtLink(link_id=link_count, ext_node=node,
                                     int_node=routers[0],
                                     latency = link_latency))
	    link_count += 1

        network.ext_links = ext_links

        # Cria as conexões entre os roteadores
        print("\nConectando os roteadores entre eles")
        int_links = []
        ports = ["ZERO", "UM", "DOIS", "TRES", "QUATRO"]

        i = 0
        for c in xrange(num_clusters):
           print("cluster " + str(i/8+1))
           for j in xrange(1,5):
               _out = i
               _in = i + j

               print("Ligação bidirecional entre " +  str(_out) + " e " +  str(_in) + " | outport: " + ports[j] + " -> North")
               int_links.append(IntLink(link_id=link_count,
               src_node=routers[_out],
               dst_node=routers[_in],
               src_outport=ports[j],
               dst_inport="North",
               latency = link_latency,
               weight=1))
               link_count += 1

               int_links.append(IntLink(link_id=link_count,
               src_node=routers[_in],
               dst_node=routers[_out],
               src_outport="North",
               dst_inport=ports[j],
               latency = link_latency,
               weight=1))
               link_count += 1


           for j in xrange(1,5):
                _out = i + 5

                _in = (i + 5) - j

                print("Ligação bidirecional entre " +  str(_out) + " e " +  str(_in) + " | outport: " + ports[5 - j] + " -> South")
                int_links.append(IntLink(link_id=link_count,
                src_node=routers[_out],
                dst_node=routers[_in],
                src_outport=ports[5 - j],
                dst_inport="South",
                latency = link_latency,
                weight=1))
                link_count += 1

                int_links.append(IntLink(link_id=link_count,
                src_node=routers[_in],
                dst_node=routers[_out],
                src_outport="South",
                dst_inport=ports[5 - j],
                latency = link_latency,
                weight=1))
                link_count += 1

           i += 8

        # A partir de 2 clusters exige mais conexoes!
        if(num_clusters > 1):
            print("\nConexoes entre os clusters:")

    	    i = 0
    	    index = 1
    	    i_out = 6
    	    gap_out = 16
    	    gap_in1 = 6
    	    gap_in2 = 2

            for w in xrange(int(log(num_clusters,2)), 0, -1):
                print("Level: "+str(w)+" i_out: "+str(i_out))
                i = 0

                for k in xrange(2**(w-1)):
                    _out = i_out + (i * gap_out)

                    for j in xrange(2):
                        if(j%2 == 0):
                            _in1 = _out - gap_in1
                            out_ports = ["West", "South", "West"]
                            in_ports = ["North", "North", "East"]
                        else:
                            _in1 = _out + gap_in1
                            out_ports = ["North", "West", "West"]
                            in_ports = ["South", "South", "East"]

                        print("Ligação bidirecional entre " +  str(_out) + " e " +  str(_in1) + " | outport: " + out_ports[0] + " -> " + in_ports[0])
                        int_links.append(IntLink(link_id=link_count,
                        src_node=routers[_out],
                        dst_node=routers[_in1],
                        src_outport=out_ports[0],
                        dst_inport=in_ports[0],
                        latency = link_latency,
                        weight=1))
                        link_count += 1

                        int_links.append(IntLink(link_id=link_count,
                        src_node=routers[_in1],
                        dst_node=routers[_out],
                        src_outport=in_ports[0],
                        dst_inport=out_ports[0],
                        latency = link_latency,
                        weight=1))
                        link_count += 1

                        if(j%2 == 0):
                            _in2 = _out + gap_in2
                        else:
                            _in2 = _out - gap_in2

                        print("Ligação bidirecional entre " +  str(_out) + " e " +  str(_in2) + " | outport: " + out_ports[1] + " -> " + in_ports[1])
                        int_links.append(IntLink(link_id=link_count,
                        src_node=routers[_out],
                        dst_node=routers[_in2],
                        src_outport=out_ports[1],
                        dst_inport=in_ports[1],
                        latency = link_latency,
                        weight=1))
                        link_count += 1

                        int_links.append(IntLink(link_id=link_count,
                        src_node=routers[_in2],
                        dst_node=routers[_out],
                        src_outport=in_ports[1],
                        dst_inport=out_ports[1],
                        latency = link_latency,
                        weight=1))
                        link_count += 1

                        print("Ligação bidirecional entre " +  str(_in1) + " e " +  str(_in2) + " | outport: " + out_ports[2] + " -> " + in_ports[2])
                        int_links.append(IntLink(link_id=link_count,
                        src_node=routers[_in1],
                        dst_node=routers[_in2],
                        src_outport=out_ports[2],
                        dst_inport=in_ports[2],
                        latency = link_latency,
                        weight=1))
                        link_count += 1

                        int_links.append(IntLink(link_id=link_count,
                        src_node=routers[_in2],
                        dst_node=routers[_in1],
                        src_outport=in_ports[2],
                        dst_inport=out_ports[2],
                        latency = link_latency,
                        weight=1))
                        link_count += 1

                        _out += 1

                    i += 1

                i_out += (8 * index)
                gap_out += 16

                if (w == int(log(num_clusters,2))):
                    gap_in1 = gap_in2 = 8
                else:
                    gap_in1 += 8
                    gap_in2 += 8

                index += 1

        network.int_links = int_links
