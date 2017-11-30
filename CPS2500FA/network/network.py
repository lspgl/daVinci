import matplotlib.pyplot as plt
import matplotlib.patches as patches

import sys
import os
__location__ = os.path.realpath(
    os.path.join(os.getcwd(), os.path.dirname(__file__)))
sys.path.append(__location__ + '/../')

from psu import PSU


class Network:

    def __init__(self, controller):
        self.controller = controller
        # self.adrBlocks = [[0x01, 0x02]]  # 1 Domain with 2 Adrs
        self.adrBlocks = [0x01, 0x02]  # 0 Domains with 2 Adrs
        # self.adrBlocks = [[0x01], [0x02]] # 2 Domains with 1 Adrs
        # self.adrBlocks = [[0x01, 0x02], [0x03]]  # 2 Domains with 2 & 1 Adrs
        self.nDomains = len(self.adrBlocks)
        if not isinstance(self.adrBlocks[0], list):
            self.adrBlocks = [self.adrBlocks]
            self.nDomains = 0

        self.psus = []

    def setupNetwork(self):
        if self.nDomains != 0:
            raise Exception('Multicasting Domains are not yet implemented')
        else:
            adrs = self.adrBlocks[0]
            self.controller.resetAddr()
            for adr in adrs:
                x5 = self.controller.stateDigital()['ADDR-OUT']
                print('x5:', x5)
                self.controller.setAddr(adr)
                member = PSU(self.controller, adr)
                connCheck = member.psu_connected
                if not member.psu_connected:
                    print(adr, 'cant be connected')
                self.psus.append(member)

    def crawlNetwork(self):
        self.psus = []
        adrs = []
        adr = 0
        self.controller.resetAddr()

        # x5 = self.controller.stateDigital()['ADDR-OUT']
        self.controller.listenAdr()
        while True:
            adr += 1
            self.controller.setAddr(adr)
            member = PSU(self.controller, adr)
            x5 = self.controller.stateDigital()['ADDR-OUT']
            if member.psu_connected:
                self.psus.append(member)
                adrs.append(adr)
            else:
                if not x5:
                    print('Network Error')
                else:
                    print('Network Closed')
                break
        self.controller.closeAdr()

    def visualize(self):
        blockHeight = 3
        blockWidth = 5
        controllerHeight = 1
        controllerWidth = 3
        scale = 0.5
        spacing = 1
        margin = spacing * 0.2
        if self.nDomains != 0:
            h = (self.nDomains) * (blockHeight + spacing) + spacing
        else:
            h = blockHeight + 2 * spacing
        w = max(len(b) for b in self.adrBlocks) * blockWidth + controllerWidth + spacing * 2
        fig = plt.figure(figsize=(w * scale, h * scale))
        ax = fig.add_subplot(111)
        for i, d in enumerate(self.adrBlocks):
            localOrigin = (controllerWidth + spacing, i * (blockHeight + spacing) + spacing)
            if self.nDomains != 0:
                domainZone = patches.Rectangle(localOrigin,
                                               blockWidth * len(d) - (len(d) - 1) * margin,
                                               blockHeight,
                                               linewidth=1,
                                               edgecolor='blue',
                                               facecolor='none')
                ax.add_patch(domainZone)

            for j, b in enumerate(d):
                blockOrigin = (localOrigin[0] + margin + j * (blockWidth - margin), localOrigin[1] + margin)
                blockZone = patches.Rectangle(blockOrigin,
                                              blockWidth - 2 * margin,
                                              blockHeight - 4 * margin,
                                              linewidth=1,
                                              edgecolor='black',
                                              facecolor='none')
                ax.add_patch(blockZone)

        controllerZone = patches.Rectangle((0, spacing),
                                           controllerWidth,
                                           controllerHeight,
                                           linewidth=1,
                                           edgecolor='red',
                                           facecolor='none')
        ax.add_patch(controllerZone)
        ax.set_aspect('equal')
        ax.axis('off')
        ax.set_xlim([0, w])
        ax.set_ylim([0, h])
        fig.savefig('network.png', dpi=300)

if __name__ == '__main__':
    from controller import Controller
    c = Controller()
    n = Network(c)
    n.crawlNetwork()
    # n.visualize()
