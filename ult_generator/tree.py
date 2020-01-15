class Node(object):
    def __init__(self, value, left = None, right = None):
        self.value = value
        self.lchild = left
        self.rchild = right

class Tree(object):

    lis = []

    def __init__(self):
        self.root = None

    def add(self,number):
        node = Node(number)
        if not self.root:
            self.root=node
            Tree.lis.append(self.root)
        else:
            while True:
                point=Tree.lis[0]

                if point.lchild==None:
                    point.lchild=node
                    Tree.lis.append(point.lchild)
                    return
                elif point.rchild==None:
                    point.rchild=node
                    Tree.lis.append(point.rchild)
                    Tree.lis.pop(0)
                    return