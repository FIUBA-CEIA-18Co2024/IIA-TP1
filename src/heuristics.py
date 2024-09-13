from src import hanoi_states


def heuristic_func_astar_1 (nodeState: hanoi_states.StatesHanoi) -> int:
    """
    Quita -1 al costo por cada disco en la barilla de destino que  está en la posición correcta. 

    Args:
        nodeState (hanoi_states.StatesHanoi): Objeto StatesHanoi que representa el estado actual del problema.

    Returns:
        int: Costo total que quita la heuristica dado el estado actual
    """
    return (-1 * sum(nodeState.rods[-1]))

def heuristic_func_astar_2(nodeState: hanoi_states.StatesHanoi, num_of_disks: int = 5) -> int:
    """
    Solo quita costo cuando las posiciones de los discos en la barilla de destino son finales.
    Ejemplo para 5 discos: 
    [4,3,2,1] no quita nada de costo ya que hay que reacomodar todo para que el 5to disco quede debajo.
    [5,4,3] quita costo dado que los discos mas abajo estan en su posición final.
    
    Args:
        nodeState (hanoi_states.StatesHanoi): Objeto StatesHanoi que representa el estado actual del problema.
        num_of_disks (int, optional): Numero de discos del problem. Defecto 5.

    Returns:
        int: Costo total que quita la heuristica dado el estado actual
    """
    def compute_rod(current_rod, number_of_disks):
        goal_rod = list(range(number_of_disks, 0, -1))
        result = [0] * number_of_disks
        for i in range(min(len(current_rod), number_of_disks)):
            if current_rod[i] == goal_rod[i]:
                result[i] = 1
        return result
    num_of_disks = max(max(rod) for rod in nodeState.rods if len(rod) > 0)
    current_target_rod_disks = nodeState.rods[-1]
    computed_rod = compute_rod(current_target_rod_disks, num_of_disks)
    reward = sum([-2**(num_of_disks-idx-1)*i for idx, i in enumerate(computed_rod)])
    return reward

def heuristic_func_greedy (nodeState: hanoi_states.StatesHanoi) -> int:
    """
    Args:
        nodeState (hanoi_states.StatesHanoi): Objeto StatesHanoi que representa el estado actual del problema.

    Returns:
        int: Costo total que quita la heuristica dado el estado actual
    """
    return sum(nodeState.rods[-1])-sum(nodeState.rods[0])
