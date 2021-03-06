import socket
import threading

from debugging import print

class CommunicationThread(threading.Thread):

    def __init__(self, connection, addr, shareGameData, id):
        super().__init__(name="CommunicationThread to " + str(addr))

        # todo : check id limit and print error
        
        self.connection = connection
        self.address = addr
        self.shareGameData = shareGameData
        self.id = id

    ##############
    ## OVERRIDE ##
    ##############
    def run(self):
        print('start handling gameClientConnection', self.address)
        
        while True:
            data = self.connection.recv(1024)
            data = data.decode('utf-8')
            print('received data from', self.address, ':', data)
            threading.Thread(target=self.respondClient,args=[data]).start()                       

    def respondClient(self,data):
        result = self.__executeCommand(data)

        if result is not None:
            self.connection.send(str.encode(str(result)))

    ############
    ## PUBLIC ##
    ############
    def getConnection(self):
        return self.connection

    def getAddress(self):
        return self.address

    def getPlayerData(self):
        return self.shareGameData.players[self.id]
    
    #####################
    ## PRIVATE HELPERS ##
    #####################
    def __executeCommand(self, strDataIn):
        try: #to call method according to header
            dataIn =    self.__convertToTuple(strDataIn) #convert to tuple
            header =    self.__extractHeader(dataIn)
            values =    self.__extractParameters(dataIn)

            actionMethod = self.__getCorrespondingMethod(header)
            output = self.__performAction(actionMethod, values)
            
            return output
            
        except Exception as e:
            print('error found for request:', strDataIn)
            print('with exception:', e)
            
            return None

    def __convertToTuple(self, strData):
        # <--example--> convert "'getGameState'," to ('gameState',)
        manipulatedString = '('+strData+')'
        return eval(manipulatedString)
    
    def __extractHeader(self, tupleData):
        return tupleData[0]
    
    def __extractParameters(self, tupleData):
        return tupleData[1:]

    def __getCorrespondingMethod(self, header):
        #admin actions
        if header == 'reset':
            return self.shareGameData.reset

        if header == 'start':
            return self.shareGameData.start
        
        #client actions
        playerData = self.shareGameData.players[self.id]
        return getattr(playerData, header)

    def __performAction(self, actionMethod, values):
        return actionMethod(*values)
        


