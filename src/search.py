from typing import Callable
from collections import deque
from src import aima
from src import tree_hanoi
from src import hanoi_states
from src.heuristics import heuristic_func_astar_1, heuristic_func_astar_2, heuristic_func_greedy



def breadth_first_tree_search(problem: hanoi_states.ProblemHanoi, display: bool = False):
    """
    Realiza una búsqueda en anchura para encontrar una solución a un problema de Hanoi.
    Esta función no chequea si un estado se visito, por lo que puede entrar en Loop infinitos muy fácilmente. No
    usarla con más de 3 discos.

    Parameters:
        problem (hanoi_states.ProblemHanoi): El problema de la Torre de Hanoi a resolver.

    Returns:
        tree_hanoi.NodeHanoi: El nodo que contiene la solución encontrada.
    """
    frontier = deque([tree_hanoi.NodeHanoi(problem.initial)])  # Creamos una cola FIFO con el nodo inicial
    while frontier:
        node = frontier.popleft()  # Extraemos el primer nodo de la cola
        if problem.goal_test(node.state):  # Comprobamos si hemos alcanzado el estado objetivo
            return node
        frontier.extend(node.expand(problem))  # Agregamos a la cola todos los nodos sucesores del nodo actual

    return None

def breadth_first_graph_search(problem: hanoi_states.ProblemHanoi, display: bool = False):
    """
    Realiza una búsqueda en anchura para encontrar una solución a un problema de Hanoi. Pero ahora si recuerda si ya
    paso por un estado e ignora seguir buscando en ese nodo para evitar recursividad.

    Parameters:
        problem (hanoi_states.ProblemHanoi): El problema de la Torre de Hanoi a resolver.
        display (bool, optional): Muestra un mensaje de cuantos caminos se expandieron y cuantos quedaron sin expandir.
                                  Por defecto es False.

    Returns:
        tree_hanoi.NodeHanoi: El nodo que contiene la solución encontrada.
    """

    frontier = deque([tree_hanoi.NodeHanoi(problem.initial)])  # Creamos una cola FIFO con el nodo inicial

    explored = set()  # Este set nos permite ver si ya exploramos un estado para evitar repetir indefinidamente
    while frontier:
        node = frontier.popleft()  # Extraemos el primer nodo de la cola

        # Agregamos nodo al set. Esto evita guardar duplicados, porque set nunca tiene elementos repetidos, esto sirve
        # porque heredamos el método __eq__ en tree_hanoi.NodeHanoi de aima.Node
        explored.add(node.state)

        if problem.goal_test(node.state):  # Comprobamos si hemos alcanzado el estado objetivo
            if display:
                print(len(explored), "caminos se expandieron y", len(frontier), "caminos quedaron en la frontera")
            return (node, len(explored), len(frontier))
        # Agregamos a la cola todos los nodos sucesores del nodo actual que no haya visitados
        frontier.extend(child for child in node.expand(problem)
                        if child.state not in explored and child not in frontier)

    return None

def astar_search(problem: hanoi_states.ProblemHanoi, heuristic_func: Callable, display: bool = False):
    """
    A* search algorithm for the Tower of Hanoi problem using tree_hanoi.NodeHanoi.
    
    Parameters:
        problem (hanoi_states.ProblemHanoi): The Tower of Hanoi problem instance.

    Returns:
        tree_hanoi.NodeHanoi: The node containing the solution, or "failure" if no solution is found.
    """
    
    def f(new_node):
        # The f(n) function combines the actual path cost (g) and the heuristic estimate (h)
        return heuristic_func(new_node.state) + new_node.path_cost

    node = tree_hanoi.NodeHanoi(problem.initial)

    if problem.goal_test(node.state):
        return node
    
    if "greedy" in getattr(heuristic_func, '__name__', 'Unknown'):
        frontier = aima.PriorityQueue(order='max', f=f)         #greedy considere weight (higher the better)
    else:
        frontier = aima.PriorityQueue(order='min', f=f)         #a_star considere cost (lower the better)
    frontier.append(node)

    # Dictionary to track the best-known path to a state
    reached = {node.state: node}
    
    while len(frontier) > 0:
        node = frontier.pop()
        
        if problem.goal_test(node.state):
            if display:
                print(len(reached), "caminos se expandieron y", len(frontier), "caminos quedaron en la frontera")
            return (node, len(reached), len(frontier))
        
        # Expand the node to generate successors
        for child in node.expand(problem):
            s = child.state  
            
            # If this state has not been reached before, or we found a better path
            if s not in reached or f(child) < f(reached[s]):
                reached[s] = child  # Update the reached dictionary with the better node
                # If the child is already in the frontier with a higher cost, remove it
                if child in frontier:
                    del frontier[child]
                # Add the child node to the frontier
                frontier.append(child)

    return "failure"

def greedy_search(problem: hanoi_states.ProblemHanoi, heuristic_func: Callable, display: bool = False):
    """
    Greedy Search search algorithm for the Tower of Hanoi problem using tree_hanoi.NodeHanoi.
    
    Parameters:
        problem (hanoi_states.ProblemHanoi): The Tower of Hanoi problem instance.

    Returns:
        tree_hanoi.NodeHanoi: The node containing the solution, or "failure" if no solution is found.
    """
    
    def f(new_node):
        return heuristic_func(new_node.state) 

    node = tree_hanoi.NodeHanoi(problem.initial)
    if problem.goal_test(node.state):
        return node
    
    if "greedy" in getattr(heuristic_func, '__name__', 'Unknown'):
        frontier = aima.PriorityQueue(order='max', f=f)     #greedy considere weight (higher the better)
    else:
        frontier = aima.PriorityQueue(order='min', f=f)     #a_star considere cost (lower the better)
    frontier.append(node)
    
    # Dictionary to track the best-known path to a state
    reached = {node.state: node}
    
    while len(frontier) > 0:
        node: tree_hanoi.NodeHanoi = frontier.pop()
        
        if problem.goal_test(node.state):
            if display:
                print(len(reached), "caminos se expandieron y", len(frontier), "caminos quedaron en la frontera")
            return (node, len(reached), len(frontier))
        
        # Expand the node to generate successors
        for child in node.expand(problem):
            s = child.state  
            
            # If this state has not been reached before, or we found a better path
            if s not in reached or f(child) < f(reached[s]):
                reached[s] = child  # Update the reached dictionary with the better node
                # If the child is already in the frontier with a higher cost, remove it
                if child in frontier:
                    del frontier[child]
                # Add the child node to the frontier
                frontier.append(child)

    return "failure"



astar_search_heuristic1: Callable = lambda problem, display=False: astar_search(
    problem, 
    heuristic_func=heuristic_func_astar_1,
    display=display
)

astar_search_heuristic2: Callable = lambda problem, display=False: astar_search(
    problem, 
    heuristic_func=heuristic_func_astar_2,  
    display=display
)

astar_search_heuristic3: Callable = lambda problem, display=False: astar_search(
    problem, 
    heuristic_func=heuristic_func_greedy,  
    display=display
)

greedy_search_heuristic1: Callable = lambda problem, display=False: greedy_search(
    problem, 
    heuristic_func=heuristic_func_astar_1,
    display=display
)

greedy_search_heuristic2: Callable = lambda problem, display=False: greedy_search(
    problem, 
    heuristic_func=heuristic_func_astar_2,
    display=display
)

greedy_search_heuristic3: Callable = lambda problem, display=False: greedy_search(
    problem, 
    heuristic_func=heuristic_func_greedy,
    display=display
)

