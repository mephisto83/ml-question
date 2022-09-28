from nodetype import TokenType


class Graph:
    @staticmethod
    def buildEquationImage(data, max_variables=20, max_terms=100):
        mathNode = data.findMathNode()
        res = data.buildTree(mathNode)
        graph = {}
        res.buildGraph(graph)
        ids = Graph.enumerateAndSort(graph)
        termList = Graph.buildTermList(res, ids)
        image = []
        rowlength = None
        for i in range(len(ids)):
            row = Graph.buildOneShotNode(graph, res, termList, ids, ids[i])
            image.append(row)
            if rowlength == None:
                rowlength = len(row)
        if 100 - len(ids) > 0:
            for i in range(100 - len(ids)):
                temp = []
                for j in range(rowlength):
                    temp.append(0)
                image.append(temp)
        return image

    @staticmethod
    def buildTermList(equationData, ids):
        termList = ['NUMBER']
        for i in range(len(ids)):
            id = ids[i]
            foundNode = equationData.findNode(id)
            if foundNode.getTokenType() == TokenType.T_VARIABLE:
                val = foundNode.getValue()
                if termList.index(val) == -1:
                    termList.append(val)
        return termList

    @staticmethod
    def buildOneShotNode(graph, equationData, termVar, ids, id, maxVars=20, connectionDepth=4):
        foundNode = equationData.findNode(id)
        termVarList = []
        termindex = []
        for i in range(maxVars):
            termVarList.append(0)
            termindex.append(0)
        if foundNode == None:
            raise Exception("node not found")
        if foundNode.getTokenType() == TokenType.T_NUM:
            termVarList[0] = 1
        elif foundNode.getTokenType() == TokenType.T_VARIABLE:
            index = termVarList.index(foundNode.getValue())
            if index == -1:
                raise Exception('variable should be in the term list')
            else:
                termVarList[index] = 1
        if len(ids) > maxVars:
            raise Exception("to many ids for the number of vars")
        connectionDepthDic = {}

        for i in range(connectionDepth):
            connectionDepthDic[i+1] = []
            for j in range(maxVars):
                connectionDepthDic[i+1].append(0)
        for i in range(len(ids)):
            id_ = ids[i]
            if id == id_:
                termindex[i]
                continue
            shortest = Graph.find_shortest_path(graph, id, id_)
            if len(shortest) < connectionDepth:
                connectionDepthDic[len(shortest)][i] = 1
        nodeType = []
        for i in TokenType:
            if foundNode.getTokenType() == i:
                nodeType.append(1)
            else:
                nodeType.append(0)
        res = []
        res = res + termindex
        for i in range(connectionDepth):
            res = res + connectionDepthDic[i+1]
        return res

    @staticmethod
    def enumerateAndSort(graph):
        keys = graph.keys()
        res = sorted(keys)
        return res

    @staticmethod
    def find_shortest_path(graph, start, end, path=[]):
        """
        __source__='https://www.python.org/doc/essays/graphs/'
        __author__='Guido van Rossum'
        """
        path = path + [start]
        if start == end:
            return path
        if start not in graph.keys():
            return None
        shortest = None
        for node in graph[start]:
            if node not in path:
                newpath = Graph.find_shortest_path(graph, node, end, path)
                if newpath:
                    if not shortest or len(newpath) < len(shortest):
                        shortest = newpath
        return shortest
